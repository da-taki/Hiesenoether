from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from agent_bp.results import load_jsonl, summarize


def table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def pct(num: int, den: int) -> str:
    return "n/a" if den == 0 else f"{num}/{den} ({num / den:.1%})"


def make_report(run_dir: Path) -> str:
    rows = load_jsonl(run_dir / "results.jsonl")
    summary = summarize(rows)
    models = sorted(set(str(r["model"]) for r in rows))
    packages_by_role: dict[str, set[str]] = defaultdict(set)
    tasks_by_role = Counter()
    for row in rows:
        role = str(row["evidence_role"])
        packages_by_role[role].add(str(row["package"]))
        tasks_by_role[role] += 1

    table1 = table(
        ["Evidence role", "Packages", "Tasks"],
        [[role, ", ".join(sorted(packages)), tasks_by_role[role]] for role, packages in sorted(packages_by_role.items())],
    )

    table2_rows = []
    for model, group in summary["by_model"].items():
        model_rows = [r for r in rows if r["model"] == model]
        table2_rows.append(
            [
                model,
                len(model_rows),
                group["executable"],
                group["preserved"],
                group["diverged"],
                sum(1 for r in model_rows if r.get("ordinary_tests_pass") is True and r.get("behavior_preserved") is False),
                sum(1 for r in model_rows if r.get("metamorphic_tests_pass") is False and r.get("execution_status") == "successful_execution"),
            ]
        )
    table2 = table(["Model", "Tasks", "Executable", "Preserved", "Diverged", "Ordinary tests missed", "OSDS caught"], table2_rows)

    by_div = Counter(str(r.get("divergence_type")) for r in rows)
    table3 = table(
        ["Model", "Output", "Exception/value", "Branch", "State-only"],
        [
            [
                model,
                by_div.get("output divergence", 0),
                by_div.get("exception/value divergence", 0),
                by_div.get("branch/path divergence", 0),
                by_div.get("state-only divergence", 0),
            ]
            for model in models
        ],
    )

    role_rows = []
    for model in models:
        model_rows = [r for r in rows if r["model"] == model]
        hidden = [r for r in model_rows if r["evidence_role"] == "hidden_observation" and r["execution_status"] == "successful_execution"]
        expected = [r for r in model_rows if r["evidence_role"] == "expected_access_sensitive" and r["execution_status"] == "successful_execution"]
        role_rows.append(
            [
                model,
                pct(sum(1 for r in hidden if r["behavior_preserved"] is False), len(hidden)),
                pct(sum(1 for r in expected if r["behavior_preserved"] is False), len(expected)),
            ]
        )
    table4 = table(["Model", "Hidden observation divergence rate", "Expected access-sensitive divergence rate"], role_rows)

    family_rows = []
    for family, group in summary["by_transformation_family"].items():
        family_rows.append([family, group["tasks"], group["preserved"], group["diverged"]])
    table5 = table(["Transformation", "N", "Preserved", "Diverged"], family_rows)
    self_rows = []
    for model in models:
        model_rows = [r for r in rows if r["model"] == model and r.get("execution_status") == "successful_execution"]
        claims = sum(1 for r in model_rows if r.get("agent_claimed_preservation") is True)
        correct = sum(1 for r in model_rows if r.get("agent_claimed_preservation") is True and r.get("behavior_preserved") is True)
        false = sum(1 for r in model_rows if r.get("agent_claimed_preservation") is True and r.get("behavior_preserved") is False)
        self_rows.append([model, claims, correct, false])
    table6 = table(
        ["Model", "Claims preserved", "Correct claims", "False preservation claims"],
        self_rows,
    )

    representative = [
        r
        for r in rows
        if r.get("ordinary_tests_pass") is True
        and r.get("metamorphic_tests_pass") is False
        and r.get("agent_claimed_preservation") is True
    ][:3]
    failure_text = "\n".join(
        f"- `{r['task_id']}`: ordinary smoke passed, self-assessment claimed preservation, "
        f"but OSDS-aware comparison changed {r['divergence_type']}."
        for r in representative
    ) or "None in this run."

    return (
        "# Agent Behavior Preservation Pilot Report\n\n"
        "## Experiment Question\n\n"
        "Can coding-agent-style transformations that appear behavior-preserving change behavior when access-shaped operations mutate latent state?\n\n"
        "## Benchmark Composition\n\n"
        f"{table1}\n\n"
        "## Models\n\n"
        + "\n".join(f"- `{model}`" for model in models)
        + "\n\n"
        "Note: rows marked as control providers are deterministic local controls for validating the pipeline, not paid external model calls.\n\n"
        "## Execution Summary\n\n"
        f"- Total tasks: {summary['total_tasks']}\n"
        f"- Generations attempted: {summary['generations_attempted']}\n"
        f"- Successfully applied: {summary['generations_successfully_applied']}\n"
        f"- Executable generations: {summary['executable_generations']}\n"
        f"- Preserved: {summary['preserved']}\n"
        f"- Diverged: {summary['diverged']}\n"
        f"- Preservation-rate Wilson 95% CI: {summary['behavior_preservation_rate_wilson_95']}\n\n"
        "## Table 2: Overall Model Results\n\n"
        f"{table2}\n\n"
        "## Table 3: Divergence Type\n\n"
        f"{table3}\n\n"
        "## Table 4: By Evidence Role\n\n"
        f"{table4}\n\n"
        "## Table 5: By Transformation\n\n"
        f"{table5}\n\n"
        "## Table 6: Self-verification\n\n"
        f"{table6}\n\n"
        "## Ordinary Tests vs OSDS-aware Tests\n\n"
        f"Ordinary tests missed {summary['ordinary_tests_missed']} behavior-changing executable generations. "
        f"OSDS-aware testing caught {summary['osds_caught']} executable semantic failures.\n\n"
        "## Representative Failures\n\n"
        f"{failure_text}\n\n"
        "## Limitations\n\n"
        "This is a pilot benchmark and this run used a deterministic local control provider unless a JSONL replay is supplied. "
        "It validates the benchmark and execution pipeline, but it is not evidence about any named external coding model. "
        "Expected access-sensitive calibration cases are counted separately from hidden-observation cases.\n\n"
        "## Reproduction\n\n"
        "```powershell\n"
        "python experiments/agent_behavior_preservation/build_benchmark.py\n"
        "python experiments/agent_behavior_preservation/runners/run_benchmark.py --provider static --run-id <run-id>\n"
        "python experiments/agent_behavior_preservation/analysis/summarize_results.py --run-dir experiments/agent_behavior_preservation/results/<run-id>\n"
        "```\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    report = make_report(run_dir)
    out = run_dir / "summary.md"
    out.write_text(report, encoding="utf-8")
    summary = summarize(load_jsonl(run_dir / "results.jsonl"))
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

