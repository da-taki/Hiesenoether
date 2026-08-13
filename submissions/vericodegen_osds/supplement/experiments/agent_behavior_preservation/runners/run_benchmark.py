from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from agent_bp.cases import render_prompt
from agent_bp.execution import compare_behavior, evaluate_source, sha256_text
from agent_bp.patching import PatchExtractionError, extract_python
from agent_bp.providers import ProviderError, make_provider
from agent_bp.schema import validate_tasks


RESULTS = BASE / "results"
TASKS = BASE / "benchmark" / "tasks.jsonl"
REPO = BASE.parents[1]


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def load_tasks(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    validate_tasks(rows)
    return rows


def load_replay_task_ids(path: Path) -> set[str]:
    task_ids: set[str] = set()
    with path.open(encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                task_ids.add(str(json.loads(line)["task_id"]))
    return task_ids


def unique_run_dir(run_id: str) -> Path:
    root = RESULTS / run_id
    if root.exists():
        raise SystemExit(f"run_id already exists: {run_id}")
    root.mkdir(parents=True)
    (root / "candidates").mkdir()
    return root


def run(args: argparse.Namespace) -> int:
    tasks = load_tasks(Path(args.tasks))
    if args.task_id:
        tasks = [task for task in tasks if task["task_id"] == args.task_id]
        if not tasks:
            raise SystemExit(f"unknown task_id {args.task_id}")
    if args.task_ids_from_replay:
        if not args.replay_path:
            raise SystemExit("--task-ids-from-replay requires --replay-path")
        replay_task_ids = load_replay_task_ids(Path(args.replay_path))
        tasks = [task for task in tasks if str(task["task_id"]) in replay_task_ids]
        if not tasks:
            raise SystemExit("replay file did not match any task_id in the task file")
    provider = make_provider(args.provider, args.replay_path)
    run_dir = unique_run_dir(args.run_id)
    result_rows = []
    baseline_failures = []

    for task in tasks:
        prompt = render_prompt(task)
        baseline = evaluate_source(str(task["source_context"]), timeout_s=args.timeout_s)
        if baseline.get("status") != "successful_execution":
            baseline_failures.append({"task_id": task["task_id"], "baseline": baseline})
        try:
            generation = provider.generate(task, prompt)
            raw = str(generation["raw_response"])
            candidate_source = extract_python(raw)
            patch_applied = True
            extraction_error = ""
        except (ProviderError, PatchExtractionError) as exc:
            generation = {
                "provider": getattr(provider, "provider", "unknown"),
                "model": getattr(provider, "model", "unknown"),
                "raw_response": "",
                "agent_claimed_preservation": False,
                "self_assessment": "",
                "is_control_provider": getattr(provider, "is_control_provider", False),
            }
            raw = ""
            candidate_source = ""
            patch_applied = False
            extraction_error = f"{type(exc).__name__}: {exc}"

        candidate_dir = run_dir / "candidates" / str(task["task_id"])
        candidate = (
            evaluate_source(candidate_source, timeout_s=args.timeout_s, keep_dir=candidate_dir)
            if patch_applied
            else {"status": "patch_application_failure"}
        )
        comparison = compare_behavior(baseline, candidate)
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": args.run_id,
            "task_id": task["task_id"],
            "case_id": task["case_id"],
            "pair_id": task["pair_id"],
            "witness_id": task["witness_id"],
            "package_id": task["package_id"],
            "package": task["package"],
            "package_version": task["package_version"],
            "evidence_role": task["evidence_role"],
            "transformation_family": task["transformation_family"],
            "prompt_condition": task["prompt_condition"],
            "provider": generation.get("provider"),
            "model": generation.get("model"),
            "temperature": generation.get("temperature"),
            "seed": generation.get("seed"),
            "is_control_provider": generation.get("is_control_provider", False),
            "prompt": prompt,
            "raw_response": raw,
            "extracted_patch": candidate_source,
            "patch_applied": patch_applied,
            "patch_error": extraction_error,
            "agent_claimed_preservation": generation.get("agent_claimed_preservation", False),
            "self_assessment": generation.get("self_assessment", ""),
            "parsed_self_assessment": generation.get("parsed_self_assessment", ""),
            "baseline_source_sha256": sha256_text(str(task["source_context"])),
            "candidate_source_sha256": sha256_text(candidate_source) if candidate_source else "",
            "baseline_result": baseline,
            "candidate_result": candidate,
            "execution_status": candidate.get("status"),
            "ordinary_tests_pass": comparison.get("ordinary_tests_pass", False),
            "metamorphic_tests_pass": comparison.get("metamorphic_tests_pass", False),
            "behavior_preserved": comparison.get("behavior_preserved", False),
            "divergence_type": comparison.get("divergence_type", "not_run"),
            "oracle_candidate_id": task["oracle_candidate_id"],
            "branch_case_id": task["branch_case_id"],
            "notes": "",
        }
        result_rows.append(row)

    result_path = run_dir / "results.jsonl"
    with result_path.open("w", encoding="utf-8") as handle:
        for row in result_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    metadata = {
        "run_id": args.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "replay_path": args.replay_path,
        "task_count": len(tasks),
        "branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "os": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "baseline_failures": baseline_failures,
    }
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"run_dir": str(run_dir), "tasks": len(tasks), "baseline_failures": len(baseline_failures)}, indent=2))
    return 1 if baseline_failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default=str(TASKS))
    parser.add_argument("--task-id")
    parser.add_argument("--provider", choices=["noop", "static", "jsonl"], default="static")
    parser.add_argument("--replay-path")
    parser.add_argument("--task-ids-from-replay", action="store_true")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout-s", type=float, default=8.0)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())




