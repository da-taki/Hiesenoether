from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
sys.path.insert(0, str(BASE))

from agent_bp.execution import sha256_text
from causal_controls.run_model_failure_causal_controls import (  # noqa: E402
    KNOWN_FAILURES,
    candidate_path,
    load_result_row,
    run_controls,
)


def test_all_known_verified_failures_are_represented():
    assert len(KNOWN_FAILURES) == 5
    assert {failure.model for failure in KNOWN_FAILURES} == {"gpt-5.6-terra", "gpt-5.6-luna"}
    assert sum(failure.task_id.startswith("pytest_catching_logs") for failure in KNOWN_FAILURES) == 4
    assert sum(failure.task_id.startswith("pyyaml_representer") for failure in KNOWN_FAILURES) == 1


def test_causal_controls_use_exact_generated_artifacts():
    for failure in KNOWN_FAILURES:
        path = candidate_path(failure)
        replay_row = load_result_row(failure)
        assert path.exists()
        assert sha256_text(path.read_text(encoding="utf-8")) == replay_row["candidate_source_sha256"]


def test_causal_controls_reproduce_original_divergence_and_neutralize_mechanism():
    records = run_controls(write_outputs=False)
    assert len(records) == 5
    for record in records:
        assert record["osds_result"] == "fail"
        assert record["ordinary_test_result"] == "pass"
        assert record["controlled_osds_result"] == "pass"
        assert record["causal_status"] == "mechanism_neutralized_divergence_disappeared"


def test_causal_controls_do_not_modify_generated_code():
    before = {failure.task_id + failure.model: sha256_text(candidate_path(failure).read_text(encoding="utf-8")) for failure in KNOWN_FAILURES}
    run_controls(write_outputs=False)
    after = {failure.task_id + failure.model: sha256_text(candidate_path(failure).read_text(encoding="utf-8")) for failure in KNOWN_FAILURES}
    assert after == before


def test_causal_control_classification_is_deterministic():
    first = run_controls(write_outputs=False)
    second = run_controls(write_outputs=False)
    assert first == second
