from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
ORACLE_DIR = REPO / "paper_artifacts" / "scp_realcode_metamorphic_oracle"


PROBE = r"""
from __future__ import annotations
import importlib.util
import json
import sys
import traceback
from pathlib import Path

repo = Path(sys.argv[1])
module_path = Path(sys.argv[2])
oracle_dir = repo / "paper_artifacts" / "scp_realcode_metamorphic_oracle"
sys.path.insert(0, str(oracle_dir))
try:
    import metamorphic_fixtures as F
    F.add_snapshot_paths()
except Exception:
    pass

def cap(fn):
    try:
        return {"kind": "value", "value": fn()}
    except Exception as exc:
        return {"kind": "exception", "type": type(exc).__name__, "message": str(exc)[:500]}

try:
    spec = importlib.util.spec_from_file_location("candidate_module", module_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
except SyntaxError as exc:
    print(json.dumps({"status": "syntax_failure", "error": f"{exc.__class__.__name__}: {exc}"}))
    raise SystemExit(0)
except ImportError as exc:
    print(json.dumps({"status": "import_failure", "error": f"{exc.__class__.__name__}: {exc}"}))
    raise SystemExit(0)
except Exception as exc:
    print(json.dumps({"status": "runtime_failure", "phase": "import", "error": f"{exc.__class__.__name__}: {exc}", "traceback": traceback.format_exc()[-2000:]}))
    raise SystemExit(0)

if not hasattr(mod, "subject"):
    print(json.dumps({"status": "runtime_failure", "phase": "shape", "error": "missing subject"}))
    raise SystemExit(0)

ordinary = cap(lambda: bool(getattr(mod, "ordinary_smoke", lambda: True)()))
order_a = cap(lambda: mod.subject(False))
order_b = cap(lambda: mod.subject(True))
print(json.dumps({"status": "successful_execution", "ordinary": ordinary, "order_A": order_a, "order_B": order_b}, sort_keys=True))
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evaluate_source(source: str, timeout_s: float = 8.0, keep_dir: Path | None = None) -> dict[str, object]:
    if keep_dir is None:
        with tempfile.TemporaryDirectory(prefix="agent_bp_candidate_") as tmp:
            return _evaluate_in_dir(source, Path(tmp), timeout_s)
    keep_dir.mkdir(parents=True, exist_ok=False)
    return _evaluate_in_dir(source, keep_dir, timeout_s)


def _evaluate_in_dir(source: str, tmp: Path, timeout_s: float) -> dict[str, object]:
    module_path = tmp / "candidate.py"
    module_path.write_text(source, encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(REPO), str(ORACLE_DIR), env.get("PYTHONPATH", "")])
    try:
        proc = subprocess.run(
            [sys.executable, "-c", PROBE, str(REPO), str(module_path)],
            text=True,
            capture_output=True,
            timeout=timeout_s,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "module_path": str(module_path),
        }
    if proc.returncode != 0:
        return {
            "status": "environment_failure",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "module_path": str(module_path),
        }
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as exc:
        payload = {
            "status": "environment_failure",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "error": f"{type(exc).__name__}: {exc}",
        }
    payload["module_path"] = str(module_path)
    payload["source_sha256"] = sha256_text(source)
    return payload


def compare_behavior(baseline: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
    if baseline.get("status") != "successful_execution":
        return {"behavior_preserved": False, "divergence_type": "baseline_failure"}
    if candidate.get("status") != "successful_execution":
        return {"behavior_preserved": False, "divergence_type": str(candidate.get("status"))}
    ordinary = candidate.get("ordinary", {})
    ordinary_pass = ordinary.get("kind") == "value" and ordinary.get("value") is True
    changed_a = candidate.get("order_A") != baseline.get("order_A")
    changed_b = candidate.get("order_B") != baseline.get("order_B")
    if not changed_a and not changed_b:
        divergence = "no divergence"
        preserved = True
    elif _kind(candidate.get("order_A")) != _kind(baseline.get("order_A")) or _kind(candidate.get("order_B")) != _kind(baseline.get("order_B")):
        divergence = "exception/value divergence"
        preserved = False
    else:
        divergence = "branch/path divergence"
        preserved = False
    return {
        "ordinary_tests_pass": ordinary_pass,
        "metamorphic_tests_pass": preserved,
        "behavior_preserved": preserved,
        "divergence_type": divergence,
        "order_A_changed": changed_a,
        "order_B_changed": changed_b,
    }


def _kind(value: object) -> object:
    return value.get("kind") if isinstance(value, dict) else None
