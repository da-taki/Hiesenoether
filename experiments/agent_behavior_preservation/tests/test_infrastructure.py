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


def test_tasks_are_exact_normal_warned_pairs():
    tasks = build_tasks()
    by_pair = {}
    for task in tasks:
        by_pair.setdefault(task["pair_id"], []).append(task)
    assert len(by_pair) == 13
    for pair in by_pair.values():
        assert {task["prompt_condition"] for task in pair} == {"normal", "warned"}
        normal = next(task for task in pair if task["prompt_condition"] == "normal")
        warned = next(task for task in pair if task["prompt_condition"] == "warned")
        assert normal["source_context"] == warned["source_context"]
        assert normal["witness_id"] == warned["witness_id"]
        assert warned["agent_instruction"].startswith(normal["agent_instruction"])


def test_tasks_include_witness_and_package_ids():
    for task in build_tasks():
        assert task["witness_id"]
        assert task["package_id"]
        assert task["pair_id"].startswith(task["case_id"])


def test_normal_prompts_do_not_leak_forbidden_terms():
    from agent_bp.cases import render_prompt
    from agent_bp.schema import FORBIDDEN_NORMAL_PROMPT_TERMS

    for task in build_tasks():
        if task["prompt_condition"] != "normal":
            continue
        prompt = render_prompt(task).lower()
        assert not [term for term in FORBIDDEN_NORMAL_PROMPT_TERMS if term in prompt]


def test_environment_reconstruction_record_shape():
    row = {
        "package": "boltons",
        "required_version": "25.0.0",
        "installed_version": "25.0.0",
        "version_match": True,
        "source": "repository-local venv exact pip install",
        "reconstruction_status": "exactly_reproduced",
        "failure_reason": None,
    }
    assert row["version_match"] is True
    assert row["reconstruction_status"] in {"exactly_reproduced", "approximately_reproduced", "failed_to_reproduce"}


def test_provider_discovery_record_shape():
    row = {
        "provider": "openai",
        "provider_configured": False,
        "authentication_usable": False,
        "models_discoverable": False,
        "secret_values_logged": False,
    }
    assert row["secret_values_logged"] is False
    assert set(row) >= {"provider", "provider_configured", "authentication_usable", "models_discoverable"}


def test_baseline_validation_record_shape():
    row = {
        "task_id": "t",
        "package": "p",
        "evidence_role": "hidden_observation",
        "baseline_constructed": True,
        "baseline_executes": True,
        "ordinary_baseline_pass": True,
        "metamorphic_witness_reproduced": True,
        "caller_wrapper_reproduced": True,
        "controls_reproduced": True,
        "eligible_for_primary_analysis": True,
        "exclusion_reason": None,
    }
    assert row["eligible_for_primary_analysis"] is True
    assert row["exclusion_reason"] is None


def test_jsonl_replay_provider_uses_self_assessment_parser(tmp_path):
    from agent_bp.providers import JsonlReplayProvider

    task = build_tasks()[0]
    replay = tmp_path / "responses.jsonl"
    replay.write_text(
        json.dumps({
            "task_id": task["task_id"],
            "provider": "example",
            "model": "example-model",
            "raw_response": "```python\n" + task["source_context"] + "```",
            "self_assessment": "YES. This preserves behavior.",
        }) + "\n",
        encoding="utf-8",
    )
    response = JsonlReplayProvider(replay).generate(task, "prompt")
    assert response["agent_claimed_preservation"] is True
    assert response["parsed_self_assessment"] == "YES"


def test_self_assessment_parser():
    from agent_bp.self_assessment import parse_preservation_claim

    assert parse_preservation_claim("YES. It preserves behavior.") == "YES"
    assert parse_preservation_claim("No, it changes behavior.") == "NO"
    assert parse_preservation_claim("Hard to tell") == "UNCLEAR"
