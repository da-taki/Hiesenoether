from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
AGENT_BP = BASE / "experiments" / "agent_behavior_preservation"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(AGENT_BP))

from agent_bp.schema import FORBIDDEN_NORMAL_PROMPT_TERMS, validate_tasks
from benchmark_expansion.build_expansion import build_tasks, candidate_rows


def test_candidate_witness_ledger_covers_all_confirmed_real_code_witnesses():
    rows = candidate_rows()
    assert len(rows) == 20
    assert sum(row["current_primary_benchmark_member"] == "true" for row in rows) == 9
    assert sum(row["current_primary_benchmark_member"] == "false" for row in rows) == 11
    assert sum(row["eligible"] == "true" for row in rows) == 7
    assert all(row["exclusion_reason"] for row in rows if row["eligible"] == "false")


def test_expansion_tasks_are_separate_valid_normal_warned_pairs():
    tasks = build_tasks()
    assert len(tasks) == 14
    assert len({task["witness_id"] for task in tasks}) == 7
    validate_tasks(tasks)
    assert all(not task["task_id"].startswith("httpcore_response") for task in tasks)


def test_expansion_normal_prompts_do_not_leak_forbidden_terms():
    from agent_bp.cases import render_prompt

    for task in build_tasks():
        if task["prompt_condition"] != "normal":
            continue
        prompt = render_prompt(task).lower()
        assert not [term for term in FORBIDDEN_NORMAL_PROMPT_TERMS if term in prompt]


def test_expansion_baselines_and_witnesses_validate_in_frozen_manifest():
    rows = json.loads((BASE / "benchmark_expansion" / "validation.json").read_text(encoding="utf-8"))
    assert len(rows) == 7
    assert all(row["baseline_executes"] for row in rows)
    assert all(row["ordinary_smoke_pass"] for row in rows)
    assert all(row["witness_reproduces"] for row in rows)
    assert all(row["eligible_for_model_execution"] for row in rows)


def test_written_expansion_artifacts_match_builder():
    tasks_path = BASE / "benchmark_expansion" / "tasks.jsonl"
    candidates_path = BASE / "benchmark_expansion" / "candidate_witnesses.csv"
    assert tasks_path.exists()
    assert candidates_path.exists()
    written_tasks = [json.loads(line) for line in tasks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert written_tasks == build_tasks()
    with candidates_path.open(newline="", encoding="utf-8") as handle:
        written_candidates = list(csv.DictReader(handle))
    assert written_candidates == candidate_rows()



