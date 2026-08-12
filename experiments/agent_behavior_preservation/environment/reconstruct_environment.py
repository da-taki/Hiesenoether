from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ENV_DIR = BASE / "environment"
REQ = ENV_DIR / "requirements-exact.txt"
OUT_JSON = ENV_DIR / "reconstruction.json"
OUT_MD = ENV_DIR / "reconstruction.md"

PACKAGE_IMPORTS = {
    "httpcore": "httpcore",
    "pytest": "pytest",
    "PyYAML": "yaml",
    "h11": "h11",
    "cerberus": "cerberus",
    "boltons": "boltons",
    "dnspython": "dns",
    "markdown": "markdown",
    "beautifulsoup4": "bs4",
}


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=BASE.parents[1], text=True).strip()
    except Exception:
        return "unknown"


def read_required() -> dict[str, str]:
    required = {}
    for line in REQ.read_text(encoding="utf-8").splitlines():
        line = line.strip().lstrip("\ufeff")
        if not line or line.startswith("#"):
            continue
        name, version = line.split("==", 1)
        required[name] = version
    return required


def import_status(module_name: str) -> tuple[bool, str | None]:
    try:
        __import__(module_name)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def main() -> int:
    required = read_required()
    rows = []
    for package, required_version in required.items():
        try:
            installed_version = metadata.version(package)
        except metadata.PackageNotFoundError:
            installed_version = None
        ok_import, import_error = import_status(PACKAGE_IMPORTS[package])
        version_match = installed_version == required_version
        if version_match and ok_import:
            status = "exactly_reproduced"
            failure_reason = None
        elif installed_version and ok_import:
            status = "approximately_reproduced"
            failure_reason = f"installed {installed_version}, required {required_version}"
        else:
            status = "failed_to_reproduce"
            failure_reason = import_error or "package not installed"
        rows.append(
            {
                "package": package,
                "required_version": required_version,
                "installed_version": installed_version,
                "version_match": version_match,
                "import_module": PACKAGE_IMPORTS[package],
                "import_ok": ok_import,
                "source": "repository-local venv exact pip install" if version_match else "unavailable or mismatched",
                "reconstruction_status": status,
                "failure_reason": failure_reason,
            }
        )
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "os": platform.platform(),
        "packages": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_rows = ["| Package | Required version | Installed version | Status | Failure reason |", "|---|---:|---:|---|---|"]
    for row in rows:
        md_rows.append(
            f"| {row['package']} | {row['required_version']} | {row['installed_version'] or ''} | {row['reconstruction_status']} | {row['failure_reason'] or ''} |"
        )
    OUT_MD.write_text(
        "# Environment Reconstruction\n\n"
        f"Generated: {payload['timestamp']}\n\n"
        f"Python: `{sys.executable}`\n\n"
        + "\n".join(md_rows)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"packages": len(rows), "exactly_reproduced": sum(1 for r in rows if r["reconstruction_status"] == "exactly_reproduced")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

