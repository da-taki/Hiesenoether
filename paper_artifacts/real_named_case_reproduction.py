from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
JSON_OUT = OUT_DIR / "real_named_case_reproduction_output.json"

CASE_URL = "https://github.com/python/cpython/issues/132385"


CHILD_CODE = r'''
import atexit

class A:
    touched = 0

    @classmethod
    def report(cls):
        print(f"TOUCHED_COUNT:{cls.touched}")

    def __getattr__(self, key):
        A.touched += 1
        print(f"GETATTR_CALLED:{key}")
        if key == "foo":
            raise SystemExit("SIDE_EFFECT_FROM_GETATTR")
        raise AttributeError(key)

    def bar(self):
        foo

atexit.register(A.report)
A().bar()
'''


def run_child() -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-c", CHILD_CODE],
        text=True,
        capture_output=True,
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    reproduced = "GETATTR_CALLED:foo" in combined and "TOUCHED_COUNT:1" in combined
    return {
        "case_name": "CPython issue #132385: instance attribute error suggestions can execute __getattr__",
        "source_url": CASE_URL,
        "python_executable": sys.executable,
        "python_version": sys.version.replace("\n", " "),
        "command": f"{sys.executable} -c <embedded CPython issue #132385 harness>",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "reproduced_locally": reproduced,
        "boundary": (
            "Direct named hazard if reproduced locally; otherwise documented upstream hazard "
            "and local non-reproduction on this runtime."
        ),
    }


def main() -> int:
    result = run_child()
    JSON_OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {JSON_OUT}")
    print(f"reproduced_locally={result['reproduced_locally']}")
    print(f"returncode={result['returncode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
