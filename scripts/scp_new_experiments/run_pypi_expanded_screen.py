from __future__ import annotations

import argparse
import csv
import random
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from common import RESULTS_DIR, append_gap, markdown_table, write_csv, write_json

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from analysis.oc_static import analyze_file
from analysis.pypi_static_benchmark import (
    DOWNLOAD_DIR,
    SOURCE_DIR,
    PACKAGES as EXISTING_PACKAGES,
    count_defs,
    extract_archive,
    iter_python_files,
    normalize_name,
    version_from_metadata,
)

TARGET_PACKAGES = 150
MAX_CONSECUTIVE_DOWNLOAD_FAILURES = 8
DOWNLOAD_TIMEOUT_SECONDS = 60
MANIFEST_PATH = RESULTS_DIR / "pypi_expanded_manifest.csv"
SCREEN_PATH = RESULTS_DIR / "pypi_expanded_screen.csv"
SUMMARY_PATH = RESULTS_DIR / "pypi_expanded_screen_summary.json"
TABLES_PATH = RESULTS_DIR / "pypi_expanded_screen_tables.md"
REVIEW_QUEUE_PATH = RESULTS_DIR / "pypi_expanded_manual_review_queue.csv"

EXTRA_PACKAGES = [
    "rich", "pydantic", "fastapi", "starlette", "httpx", "httpcore", "certifi",
    "charset-normalizer", "idna", "PyYAML", "typing_extensions", "pytest",
    "black", "isort", "virtualenv", "distlib", "tox", "coverage", "hypothesis",
    "python-dateutil", "pytz", "tzdata", "six", "decorator", "attrs-strict",
    "traitlets", "ipython", "jedi", "parso", "prompt-toolkit", "wcwidth",
    "executing", "asttokens", "pure-eval", "stack-data", "matplotlib-inline",
    "networkx", "sympy", "mpmath", "lxml", "defusedxml", "cryptography",
    "cffi", "pycparser", "Pillow", "contourpy", "cycler", "fonttools",
    "kiwisolver", "numpy", "pandas", "pytz-deprecation-shim", "sqlparse",
    "greenlet", "sqlalchemy", "alembic", "Mako", "orjson", "ujson",
    "msgpack", "redis", "kombu", "vine", "amqp", "billiard", "celery",
    "click-didyoumean", "click-repl", "croniter", "watchdog", "uvicorn",
    "gunicorn", "hpack", "hyperframe", "h5py", "zipp", "importlib-resources",
    "tomli-w", "toml", "requests-toolbelt", "oauthlib", "requests-oauthlib",
    "pyjwt", "python-multipart", "email-validator", "rfc3986", "rfc3339-validator",
    "fqdn", "uri-template", "webcolors", "jsonschema-specifications",
    "referencing", "rpds-py", "Pygments", "Sphinx", "alabaster",
    "snowballstemmer", "imagesize", "sphinxcontrib-applehelp",
    "sphinxcontrib-devhelp", "sphinxcontrib-htmlhelp", "sphinxcontrib-jsmath",
    "sphinxcontrib-qthelp", "sphinxcontrib-serializinghtml", "python-slugify",
    "text-unidecode", "validators", "phonenumbers", "pyrsistent", "fsspec",
    "cloudpickle", "dill", "multiprocess", "xxhash", "joblib", "threadpoolctl",
    "scipy", "seaborn", "tabulate", "openpyxl", "et-xmlfile", "xlrd",
    "XlsxWriter", "python-docx", "reportlab", "pypdf", "pdfminer.six",
    "pdfplumber", "chardet", "regex", "rapidfuzz",
]


def package_candidates() -> list[str]:
    seen = set()
    out = []
    for name in list(EXISTING_PACKAGES) + EXTRA_PACKAGES:
        normalized = normalize_name(name)
        if normalized not in seen:
            seen.add(normalized)
            out.append(name)
    return out


def existing_archive(package: str) -> Path | None:
    normalized = normalize_name(package)
    candidates = sorted(DOWNLOAD_DIR.glob("*"))
    matches = [
        path for path in candidates
        if normalize_name(path.name).startswith(normalized)
        and (path.suffix in {".zip", ".gz", ".whl"} or path.name.endswith(".tar.gz"))
    ]
    return matches[-1] if matches else None


def source_root(package: str) -> Path | None:
    target = SOURCE_DIR / normalize_name(package)
    return target if target.exists() else None


def download_package(package: str) -> tuple[Path | None, str | None]:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for binary_mode in (["--no-binary", ":all:"], ["--only-binary", ":all:"]):
        command = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            *binary_mode,
            "--dest",
            str(DOWNLOAD_DIR),
            package,
        ]
        try:
            proc = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=DOWNLOAD_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return None, f"download timed out after {DOWNLOAD_TIMEOUT_SECONDS}s"
        if proc.returncode == 0:
            archive = existing_archive(package)
            if archive is not None:
                return archive, None
        last_error = (proc.stderr or proc.stdout or "").strip()
    return None, last_error or "download failed"


def get_package_root(package: str, allow_downloads: bool) -> tuple[Path | None, str, str]:
    existing_root = source_root(package)
    if existing_root is not None:
        return existing_root, "local_cache", ""

    archive = existing_archive(package)
    if archive is not None:
        try:
            return extract_archive(package, archive), "local_archive", ""
        except Exception as exc:
            return None, "extract_failed", str(exc)

    if not allow_downloads:
        return None, "not_cached", "downloads disabled"

    archive, error = download_package(package)
    if archive is None:
        return None, "download_failed", error or "unknown download failure"
    try:
        return extract_archive(package, archive), "downloaded", ""
    except Exception as exc:
        return None, "extract_failed", str(exc)


def mechanisms_for(cls: dict) -> str:
    bits = []
    if cls["P1_access_sensitive"]:
        bits.append("P1_access_sensitive")
    if cls["P2_observation_mutates"]:
        bits.append("P2_observation_mutates")
    if cls["P3_nonlinear_composition"]:
        bits.append("P3_nonlinear_composition")
    return "; ".join(bits)


def short_reason(cls: dict) -> str:
    for key in ("P1", "P2", "P3"):
        values = cls.get("evidence", {}).get(key) or []
        if values:
            return values[0]
    return ""


def suspected_pattern(row: dict) -> str:
    text = " ".join(str(row.get(key, "")) for key in ("class", "short_reason", "detected_mechanisms")).lower()
    if "cache" in text or "cached" in text or "memo" in text:
        return "cache_or_memoization"
    if "context" in text or "__enter__" in text:
        return "context_manager_bookkeeping"
    if "builder" in text or "fluent" in text or "return self" in text:
        return "builder_or_fluent_mutator"
    if "__get__" in text or "descriptor" in text:
        return "descriptor_or_proxy"
    if "counter" in text or "count" in text or "mutates" in text:
        return "state_mutating_reader"
    return "other"


def code_excerpt(path: Path, line: int, radius: int = 4) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    excerpt_lines = []
    for idx in range(start, end + 1):
        source_line = lines[idx - 1].rstrip()
        excerpt_lines.append(f"{idx}: {source_line}" if source_line else f"{idx}:")
    return "\n".join(excerpt_lines)


def scan_package(package: str, root: Path, source: str) -> tuple[dict, list[dict]]:
    version = version_from_metadata(root)
    labels: Counter[str] = Counter()
    files_scanned = classes_scanned = functions_scanned = 0
    class_rows: list[dict] = []

    for py_file in iter_python_files(root):
        class_count, function_count = count_defs(py_file)
        classes_scanned += class_count
        functions_scanned += function_count
        try:
            result = analyze_file(py_file)
        except Exception:
            continue
        files_scanned += 1
        rel_file = str(py_file.relative_to(root))
        for cls in result["classes"]:
            label = cls["risk_label"]
            labels[label] += 1
            row = {
                "package": package,
                "version": version,
                "source": source,
                "file": rel_file,
                "source_file": str(py_file),
                "class": cls["class"],
                "line": cls["line"],
                "analyzer_label": label,
                "detected_mechanisms": mechanisms_for(cls),
                "short_reason": short_reason(cls),
            }
            row["suspected_pattern"] = suspected_pattern(row)
            class_rows.append(row)

    package_row = {
        "package": package,
        "version": version,
        "status": "analyzed",
        "source": source,
        "error": "",
        "files_scanned": files_scanned,
        "classes_scanned": classes_scanned,
        "functions_scanned": functions_scanned,
        "SAFE": labels["SAFE"],
        "LOW": labels["LOW"],
        "MEDIUM": labels["MEDIUM"],
        "HIGH": labels["HIGH"],
    }
    return package_row, class_rows


def build_review_queue(class_rows: list[dict]) -> list[dict]:
    rng = random.Random(20260705)
    high = [row for row in class_rows if row["analyzer_label"] == "HIGH"]
    medium = [row for row in class_rows if row["analyzer_label"] == "MEDIUM"]
    low = [row for row in class_rows if row["analyzer_label"] == "LOW"]
    safe = [row for row in class_rows if row["analyzer_label"] == "SAFE"]

    medium_sample = rng.sample(medium, min(150, len(medium)))
    low_budget = min(50, len(low))
    safe_budget = min(100 - low_budget, len(safe))
    low_safe_sample = []
    if low_budget:
        low_safe_sample.extend(rng.sample(low, low_budget))
    if safe_budget:
        low_safe_sample.extend(rng.sample(safe, safe_budget))
    remaining = 100 - len(low_safe_sample)
    if remaining > 0:
        leftovers = [row for row in safe + low if row not in low_safe_sample]
        low_safe_sample.extend(rng.sample(leftovers, min(remaining, len(leftovers))))

    selected = high + medium_sample + low_safe_sample
    queue = []
    for index, row in enumerate(selected, start=1):
        source_file = Path(row["source_file"])
        line = int(row["line"]) if row["line"] else 1
        queue.append(
            {
                "review_id": f"EXP-{index:04d}",
                "package": row["package"],
                "version": row["version"],
                "file": row["file"],
                "class": row["class"],
                "analyzer_label": row["analyzer_label"],
                "short_reason": row["short_reason"],
                "code_excerpt": code_excerpt(source_file, line),
                "suspected_pattern": row["suspected_pattern"],
                "manual_label_blank": "",
                "reviewer_note_blank": "",
            }
        )
    return queue


def write_tables(package_rows: list[dict], summary: dict) -> None:
    largest = sorted(package_rows, key=lambda row: int(row["MEDIUM"]) + int(row["HIGH"]), reverse=True)[:25]
    lines = [
        "# Expanded PyPI Screen Tables",
        "",
        "## Aggregate",
        "",
        f"- packages analyzed: {summary['packages_analyzed']}",
        f"- files scanned: {summary['files_scanned']}",
        f"- classes scanned: {summary['classes_scanned']}",
        f"- functions scanned: {summary['functions_scanned']}",
        f"- SAFE/LOW/MEDIUM/HIGH: {summary['SAFE']}/{summary['LOW']}/{summary['MEDIUM']}/{summary['HIGH']}",
        "",
        "## Packages With Most MEDIUM/HIGH Findings",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "package",
                "version",
                "files_scanned",
                "classes_scanned",
                "functions_scanned",
                "SAFE",
                "LOW",
                "MEDIUM",
                "HIGH",
            ],
            largest,
        )
    )
    lines.extend(["", "## Top False-Positive-Risk Patterns", ""])
    pattern_rows = [
        {"pattern": pattern, "count": count}
        for pattern, count in summary["top_false_positive_risk_patterns"]
    ]
    lines.extend(markdown_table(["pattern", "count"], pattern_rows))
    TABLES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(target_packages: int = TARGET_PACKAGES, allow_downloads: bool = True) -> dict:
    started = time.time()
    candidates = package_candidates()
    manifest_rows = []
    package_rows = []
    class_rows = []
    consecutive_failures = 0
    stopped_reason = ""

    for package in candidates:
        if len(package_rows) >= target_packages:
            break
        root, source, error = get_package_root(package, allow_downloads)
        manifest_row = {
            "package": package,
            "version": version_from_metadata(root) if root is not None else "",
            "status": "available" if root is not None else source,
            "source": source,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "error": error,
        }
        manifest_rows.append(manifest_row)
        if root is None:
            consecutive_failures += 1
            if allow_downloads and consecutive_failures >= MAX_CONSECUTIVE_DOWNLOAD_FAILURES:
                stopped_reason = (
                    f"stopped after {consecutive_failures} consecutive package acquisition failures"
                )
            break
            continue

        consecutive_failures = 0
        package_row, rows = scan_package(package, root, source)
        package_rows.append(package_row)
        class_rows.extend(rows)

    if len(package_rows) < target_packages and not stopped_reason:
        stopped_reason = "candidate list exhausted or packages unavailable in local cache"

    runtime_seconds = round(time.time() - started, 3)
    write_csv(MANIFEST_PATH, manifest_rows)
    write_csv(SCREEN_PATH, package_rows)
    review_queue = build_review_queue(class_rows)
    write_csv(REVIEW_QUEUE_PATH, review_queue)

    aggregate = Counter()
    for row in package_rows:
        for label in ("SAFE", "LOW", "MEDIUM", "HIGH"):
            aggregate[label] += int(row[label])

    flagged_rows = [row for row in class_rows if row["analyzer_label"] in {"MEDIUM", "HIGH"}]
    pattern_counts = Counter(suspected_pattern(row) for row in flagged_rows)
    summary = {
        "target_packages": target_packages,
        "packages_attempted": len(manifest_rows),
        "packages_analyzed": len(package_rows),
        "target_met": len(package_rows) >= target_packages,
        "stopped_reason": stopped_reason,
        "downloads_allowed": allow_downloads,
        "runtime_seconds": runtime_seconds,
        "files_scanned": sum(int(row["files_scanned"]) for row in package_rows),
        "classes_scanned": sum(int(row["classes_scanned"]) for row in package_rows),
        "functions_scanned": sum(int(row["functions_scanned"]) for row in package_rows),
        "SAFE": aggregate["SAFE"],
        "LOW": aggregate["LOW"],
        "MEDIUM": aggregate["MEDIUM"],
        "HIGH": aggregate["HIGH"],
        "top_false_positive_risk_patterns": pattern_counts.most_common(10),
        "manual_review_queue_rows": len(review_queue),
        "manual_review_queue_policy": {
            "HIGH": "all HIGH findings",
            "MEDIUM": "up to 150 MEDIUM findings",
            "LOW_SAFE": "stratified random sample of 100 LOW/SAFE classes when available",
        },
        "outputs": {
            "manifest": "results/scp_new_experiments/pypi_expanded_manifest.csv",
            "screen": "results/scp_new_experiments/pypi_expanded_screen.csv",
            "manual_review_queue": "results/scp_new_experiments/pypi_expanded_manual_review_queue.csv",
        },
    }
    write_json(SUMMARY_PATH, summary)
    write_tables(package_rows, summary)

    if len(package_rows) < target_packages:
        append_gap(
            "Expanded PyPI target not met",
            (
                f"Target was {target_packages} packages, but only {len(package_rows)} packages "
                f"were analyzed. Reason: {stopped_reason or 'candidate list exhausted or downloads unavailable'}. "
                "The script reused all available local/cache packages it could acquire and left manual labels blank."
            ),
        )

    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=TARGET_PACKAGES)
    parser.add_argument("--no-downloads", action="store_true")
    args = parser.parse_args()

    summary = run(target_packages=args.target, allow_downloads=not args.no_downloads)
    print(f"wrote {MANIFEST_PATH}")
    print(f"wrote {SCREEN_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(f"wrote {TABLES_PATH}")
    print(f"wrote {REVIEW_QUEUE_PATH}")
    print(f"packages_analyzed={summary['packages_analyzed']}")
    print(f"classes_scanned={summary['classes_scanned']}")
    print(f"manual_review_queue_rows={summary['manual_review_queue_rows']}")
    if not summary["target_met"]:
        print(f"target_not_met: {summary['stopped_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
