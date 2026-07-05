from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "proof_support" / "derive_running_example_symbolic.py"
RESULT = REPO / "results" / "proof_support" / "running_example_derivation.json"


def load_derivation() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=REPO, check=True)
    assert RESULT.exists()
    return json.loads(RESULT.read_text(encoding="utf-8"))


def walk_values(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from walk_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk_values(nested)
    else:
        yield value


def test_derivation_uses_exact_values_not_floats() -> None:
    payload = load_derivation()
    assert payload["uses_exact_arithmetic"] is True
    assert all(not isinstance(value, float) for value in walk_values(payload))


def test_derivation_has_two_orders_and_nonzero_divergence() -> None:
    payload = load_derivation()
    assert len(payload["orders"]) == 2
    assert payload["orders"][0]["operations"] == ["OBS", "READ", "READ"]
    assert payload["orders"][1]["operations"] == ["READ", "READ", "OBS"]
    assert payload["final_outputs"] == {"A": "7956/25", "B": "7596/25"}
    assert payload["final_divergence"] == "72/5"
