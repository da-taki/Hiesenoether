from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from agent_bp.cases import build_tasks
from agent_bp.execution import compare_behavior, evaluate_source, sha256_text
from agent_bp.patching import PatchExtractionError, extract_python
from agent_bp.providers import NoopProvider, StaticSemanticsBlindProvider
from agent_bp.results import summarize
from agent_bp.schema import SchemaError, validate_tasks
from runners.run_benchmark import unique_run_dir


def test_benchmark_schema_validation():
    tasks = build_tasks()
    validate_tasks(tasks)
    assert 20 <= len(tasks) <= 30
    assert {task["evidence_role"] for task in tasks} == {"hidden_observation", "expected_access_sensitive"}


def test_schema_rejects_duplicate_ids():
    task = build_tasks()[0]
    with pytest.raises(SchemaError):
        validate_tasks([task, dict(task)])


def test_patch_extraction_from_python_fence():
    code = extract_python("Here:\n```python\ndef subject():\n    return 1\n```")
    assert "def subject" in code


def test_patch_extraction_rejects_missing_subject():
    with pytest.raises(PatchExtractionError):
        extract_python("```python\nx = 1\n```")


def test_candidate_execution_isolated_and_preserves_baseline_fixture(tmp_path):
    task = build_tasks()[0]
    baseline_source = str(task["source_context"])
    before = sha256_text(baseline_source)
    result = evaluate_source(baseline_source, keep_dir=tmp_path / "candidate")
    after = sha256_text(baseline_source)
    assert result["status"] == "successful_execution"
    assert before == after


def test_classification_logic_detects_static_provider_divergence(tmp_path):
    task = build_tasks()[0]
    baseline = evaluate_source(str(task["source_context"]), keep_dir=tmp_path / "baseline")
    provider = StaticSemanticsBlindProvider()
    raw = provider.generate(task, "prompt")["raw_response"]
    candidate = evaluate_source(extract_python(raw), keep_dir=tmp_path / "candidate")
    comparison = compare_behavior(baseline, candidate)
    assert comparison["ordinary_tests_pass"] is True
    assert comparison["metamorphic_tests_pass"] is False
    assert comparison["behavior_preserved"] is False


def test_noop_provider_preserves_behavior(tmp_path):
    task = build_tasks()[0]
    baseline = evaluate_source(str(task["source_context"]), keep_dir=tmp_path / "baseline")
    raw = NoopProvider().generate(task, "prompt")["raw_response"]
    candidate = evaluate_source(extract_python(raw), keep_dir=tmp_path / "candidate")
    assert compare_behavior(baseline, candidate)["behavior_preserved"] is True


def test_timeout_handling():
    result = evaluate_source("def subject(flag=False):\n    while True:\n        pass\n", timeout_s=0.1)
    assert result["status"] == "timeout"


def test_failed_generation_handling_in_summary():
    rows = [
        {
            "raw_response": "",
            "patch_applied": False,
            "execution_status": "patch_application_failure",
            "behavior_preserved": False,
            "ordinary_tests_pass": False,
            "metamorphic_tests_pass": False,
            "agent_claimed_preservation": False,
            "divergence_type": "not_run",
            "evidence_role": "hidden_observation",
            "transformation_family": "instrumentation",
            "model": "x",
        }
    ]
    assert summarize(rows)["generations_successfully_applied"] == 0


def test_result_serialization_round_trip(tmp_path):
    path = tmp_path / "results.jsonl"
    row = {"task_id": "t", "behavior_preserved": True}
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8")) == row


def test_duplicate_run_ids_are_rejected(tmp_path, monkeypatch):
    import runners.run_benchmark as runner

    monkeypatch.setattr(runner, "RESULTS", tmp_path)
    unique_run_dir("same")
    with pytest.raises(SystemExit):
        unique_run_dir("same")
