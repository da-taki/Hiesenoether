from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "runners"))

from agent_bp.execution import evaluate_source
from runners.run_benchmark import load_tasks
from runners.validate_existing_witnesses import run_branch_cases, run_candidate_without_writing, run_controls
import metamorphic_candidates as C
import metamorphic_fixtures as F

OUT_DIR = BASE / "validation"
OUT_JSONL = OUT_DIR / "baseline_validation.jsonl"
OUT_JSON = OUT_DIR / "baseline_validation_summary.json"
OUT_MD = OUT_DIR / "baseline_validation.md"
TASKS = BASE / "benchmark" / "tasks.jsonl"


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    F.add_snapshot_paths()
    tasks = load_tasks(TASKS)
    witness_ids = sorted({str(task["witness_id"]) for task in tasks})
    witness_records = {}
    for witness_id in witness_ids:
        witness_records[witness_id] = run_candidate_without_writing(C.CANDIDATES_BY_ID[witness_id])
    branch_records = {row.get("underlying_candidate_id"): row for row in run_branch_cases() if row.get("underlying_candidate_id")}
    controls_by_witness: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in run_controls():
        controls_by_witness[str(row.get("candidate_id"))].append(row)

    rows = []
    for task in tasks:
        baseline = evaluate_source(str(task["source_context"]))
        ordinary = baseline.get("ordinary", {}) if isinstance(baseline, dict) else {}
        witness = witness_records[str(task["witness_id"])]
        branch = branch_records.get(str(task["witness_id"]))
        controls = controls_by_witness.get(str(task["witness_id"]), [])
        baseline_executes = baseline.get("status") == "successful_execution"
        ordinary_pass = ordinary.get("kind") == "value" and ordinary.get("value") is True
        metamorphic_ok = str(witness.get("classification", "")).startswith("confirmed")
        caller_ok = branch is not None and str(branch.get("classification")) == "confirmed_branch_flip"
        controls_applicable = bool(controls)
        controls_ok = all(row.get("divergence_removed") is True for row in controls) if controls_applicable else True
        eligible = baseline_executes and ordinary_pass and metamorphic_ok and caller_ok and controls_ok
        exclusion_reasons = []
        if not baseline_executes:
            exclusion_reasons.append(str(baseline.get("status")))
        if baseline_executes and not ordinary_pass:
            exclusion_reasons.append("ordinary_baseline_failed")
        if not metamorphic_ok:
            exclusion_reasons.append("metamorphic_witness_not_reproduced")
        if not caller_ok:
            exclusion_reasons.append("caller_wrapper_not_reproduced")
        if controls_applicable and not controls_ok:
            exclusion_reasons.append("controls_not_reproduced")
        rows.append(
            {
                "task_id": task["task_id"],
                "pair_id": task["pair_id"],
                "case_id": task["case_id"],
                "witness_id": task["witness_id"],
                "package": task["package"],
                "package_version": task["package_version"],
                "evidence_role": task["evidence_role"],
                "prompt_condition": task["prompt_condition"],
                "baseline_constructed": baseline.get("status") not in {"syntax_failure", "import_failure"},
                "baseline_executes": baseline_executes,
                "ordinary_baseline_pass": ordinary_pass,
                "metamorphic_witness_reproduced": metamorphic_ok,
                "caller_wrapper_reproduced": caller_ok,
                "controls_applicable": controls_applicable,
                "controls_reproduced": controls_ok,
                "eligible_for_primary_analysis": eligible,
                "exclusion_reason": ";".join(exclusion_reasons) if exclusion_reasons else None,
                "baseline_result": baseline,
                "metamorphic_classification": witness.get("classification"),
                "caller_classification": branch.get("classification") if branch else None,
                "controls_count": len(controls),
            }
        )
    with OUT_JSONL.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "python_executable": sys.executable,
        "tasks": len(rows),
        "eligible_tasks": sum(1 for row in rows if row["eligible_for_primary_analysis"]),
        "ineligible_tasks": sum(1 for row in rows if not row["eligible_for_primary_analysis"]),
        "unique_witnesses": len(witness_ids),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        "# Baseline Validation",
        "",
        f"Eligible tasks: {summary['eligible_tasks']} / {summary['tasks']}",
        "",
        "| Task | Package | Baseline | Ordinary | Metamorphic | Caller | Controls | Eligible | Exclusion |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        md.append(
            f"| {row['task_id']} | {row['package']} {row['package_version']} | {row['baseline_executes']} | {row['ordinary_baseline_pass']} | {row['metamorphic_witness_reproduced']} | {row['caller_wrapper_reproduced']} | {row['controls_reproduced']} | {row['eligible_for_primary_analysis']} | {row['exclusion_reason'] or ''} |"
        )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["eligible_tasks"] == summary["tasks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

