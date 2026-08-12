from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from agent_bp.cases import render_prompt
from agent_bp.schema import FORBIDDEN_NORMAL_PROMPT_TERMS
from runners.run_benchmark import load_tasks

OUT_JSON = BASE / "analysis" / "leakage_audit.json"
OUT_MD = BASE / "analysis" / "leakage_audit.md"
TASKS = BASE / "benchmark" / "tasks.jsonl"


def main() -> int:
    tasks = load_tasks(TASKS)
    leaks = []
    for task in tasks:
        prompt = render_prompt(task)
        lower = prompt.lower()
        if task["prompt_condition"] == "normal":
            hits = sorted(term for term in FORBIDDEN_NORMAL_PROMPT_TERMS if term in lower)
            if hits:
                leaks.append({"task_id": task["task_id"], "terms": hits})
    pair_errors = []
    pairs: dict[str, list[dict[str, object]]] = defaultdict(list)
    for task in tasks:
        pairs[str(task["pair_id"])].append(task)
    for pair_id, pair in pairs.items():
        normal = [task for task in pair if task["prompt_condition"] == "normal"]
        warned = [task for task in pair if task["prompt_condition"] == "warned"]
        if len(normal) != 1 or len(warned) != 1:
            pair_errors.append({"pair_id": pair_id, "error": "missing normal/warned member"})
            continue
        normal_task, warned_task = normal[0], warned[0]
        for field in ("source_context", "case_id", "witness_id", "package", "package_version", "transformation_family"):
            if normal_task[field] != warned_task[field]:
                pair_errors.append({"pair_id": pair_id, "error": f"field differs: {field}"})
        if not str(warned_task["agent_instruction"]).startswith(str(normal_task["agent_instruction"])):
            pair_errors.append({"pair_id": pair_id, "error": "warned instruction does not extend normal instruction"})
    payload = {"tasks": len(tasks), "normal_prompt_leaks": leaks, "pair_errors": pair_errors, "passed": not leaks and not pair_errors}
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Leakage Audit", "", f"Passed: {payload['passed']}", "", f"Normal prompt leaks: {len(leaks)}", f"Pairing errors: {len(pair_errors)}"]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
