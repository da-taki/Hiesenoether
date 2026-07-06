from __future__ import annotations

import ast
import csv
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SNAPSHOT = OUT / "source_snapshot"
DOWNLOADS = OUT / "downloads"
MANIFEST = OUT / "source_snapshot_manifest.csv"
NOTES = OUT / "SOURCE_SNAPSHOT_NOTES.md"
STATIC_SUMMARY = REPO / "results_static" / "pypi_static_benchmark.csv"
TEMP_SOURCES = Path.home() / "AppData" / "Local" / "Temp" / "hiesenoether_pypi_static_benchmark" / "sources"


def norm(name: str) -> str:
    return name.replace("_", "-").lower()


def count_py(root: Path) -> int:
    return sum(1 for _ in root.rglob("*.py")) if root.exists() else 0


def count_classes(root: Path) -> int:
    total = 0
    for path in root.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        total += sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    return total


def version_from_metadata(root: Path) -> str:
    for name in ("METADATA", "PKG-INFO"):
        for path in root.rglob(name):
            try:
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
            except OSError:
                pass
    return ""


def original_root(package: str) -> Path | None:
    root = TEMP_SOURCES / norm(package)
    if not root.exists():
        return None
    if count_py(root):
        return root
    children = [child for child in root.iterdir() if child.is_dir()]
    for child in children:
        if count_py(child):
            return child
    return None


def safe_copy(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def unpack(archive: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    if archive.suffix == ".whl" or archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    elif archive.name.endswith(".tar.gz") or archive.suffixes[-2:] == [".tar", ".gz"]:
        with tarfile.open(archive) as tf:
            tf.extractall(dest)
    else:
        raise ValueError(f"unsupported archive: {archive}")


def download_package(package: str, version: str, timeout: int) -> tuple[Path | None, str]:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    before = {p.resolve() for p in DOWNLOADS.glob("*")}
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--no-deps",
        "--only-binary=:all:",
        "--dest",
        str(DOWNLOADS),
        f"{package}=={version}",
    ]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"pip download timed out after {timeout}s"
    after = [p for p in DOWNLOADS.glob("*") if p.resolve() not in before]
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout).replace("\n", " ")[:500]
    if not after:
        matches = sorted(DOWNLOADS.glob(f"{package.replace('-', '*')}*{version}*"))
        after = matches
    return (after[-1] if after else None), "downloaded exact version"


def write_csv(rows: list[dict[str, object]]) -> None:
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "package",
                "version_requested",
                "version_obtained",
                "source_status",
                "source_path",
                "files_count",
                "classes_count_if_analyzed",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def run(download: bool, timeout: int) -> list[dict[str, object]]:
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    rows_in = list(csv.DictReader(STATIC_SUMMARY.open(encoding="utf-8")))
    rows: list[dict[str, object]] = []
    for item in rows_in:
        package = item["package"]
        version = item["version"]
        dest = SNAPSHOT / f"{norm(package)}-{version}"
        status = "missing"
        notes = ""
        obtained = ""
        src = original_root(package)
        if src is not None:
            safe_copy(src, dest)
            status = "original_available"
            obtained = version_from_metadata(dest) or version
            notes = "copied from temp cache"
        elif download:
            archive, note = download_package(package, version, timeout)
            notes = note
            if archive is not None:
                try:
                    unpack(archive, dest)
                    obtained = version_from_metadata(dest) or version
                    status = "reacquired_exact" if obtained == version else "reacquired_different_version"
                except Exception as exc:
                    status = "missing"
                    notes = f"unpack failed: {exc}"
        rows.append(
            {
                "package": package,
                "version_requested": version,
                "version_obtained": obtained,
                "source_status": status,
                "source_path": str(dest) if dest.exists() else "",
                "files_count": count_py(dest),
                "classes_count_if_analyzed": count_classes(dest) if count_py(dest) else 0,
                "notes": notes,
            }
        )
        print(f"{package}=={version}: {status} files={rows[-1]['files_count']}")
    write_csv(rows)
    write_notes(rows, download)
    return rows


def write_notes(rows: list[dict[str, object]], download: bool) -> None:
    statuses: dict[str, int] = {}
    for row in rows:
        statuses[str(row["source_status"])] = statuses.get(str(row["source_status"]), 0) + 1
    lines = [
        "# Source Snapshot Notes",
        "",
        f"Download attempted: {download}.",
        "",
        "| source_status | packages |",
        "| --- | ---: |",
    ]
    for status, count in sorted(statuses.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(
        [
            "",
            f"Manifest: `{MANIFEST}`",
            f"Snapshot directory: `{SNAPSHOT}`",
            "",
            "Reviewed-corpus recall may be computed only for packages with usable source snapshots. Missing packages remain excluded and are reported explicitly.",
        ]
    )
    NOTES.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    download = "--download" in sys.argv
    timeout = 45
    if "--timeout" in sys.argv:
        timeout = int(sys.argv[sys.argv.index("--timeout") + 1])
    rows = run(download=download, timeout=timeout)
    missing = sum(row["source_status"] == "missing" for row in rows)
    print(f"wrote {MANIFEST}")
    print(f"missing={missing} total={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
