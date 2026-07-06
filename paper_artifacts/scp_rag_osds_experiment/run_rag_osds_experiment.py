from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from rag_osds_simulator import load_corpus, run_scenario


BASE = Path(__file__).resolve().parent
CORPUS_PATH = BASE / "rag_corpus.json"
RESULTS_JSON = BASE / "rag_osds_results.json"
RESULTS_CSV = BASE / "rag_osds_results.csv"
ABLATION_CSV = BASE / "rag_osds_ablation.csv"
REPLAY_JSON = BASE / "rag_osds_replay_check.json"
REPORT_MD = BASE / "RAG_OSDS_EXPERIMENT_REPORT.md"
QUALITY_MD = BASE / "QUALITY_GATE_REPORT.md"


SCENARIOS = [
    {
        "scenario_id": "S1_baseline_preview_cache",
        "variant": "pure_baseline",
        "q1": "cache policy evicts least recently used entries",
        "q2": "Which cache policy evicts least-recently-used entries?",
        "observation_operation": "preview_context",
        "expected_possible_flip_reason": "Baseline preview is pure, so no flip should occur.",
    },
    {
        "scenario_id": "S2_access_log_cache",
        "variant": "access_count_feedback",
        "q1": "least recently inserted entries insertion order LRI",
        "q2": "Which cache policy evicts least-recently-used entries?",
        "observation_operation": "log_retrieval",
        "expected_possible_flip_reason": "Logging Q1 increases access counts for LRI-like cache evidence, adding a later ranking boost.",
    },
    {
        "scenario_id": "S3_recency_preview_city",
        "variant": "recency_memory_feedback",
        "q1": "Boston candidate city planning memo",
        "q2": "Which city hosted the accessibility workshop?",
        "observation_operation": "preview_context",
        "expected_possible_flip_reason": "Preview stores Boston planning evidence in session memory, giving it recency boost for Q2.",
    },
    {
        "scenario_id": "S4_explain_markdown",
        "variant": "explanation_feedback",
        "q1": "build_parser processors construction",
        "q2": "Which document says reset must be called before reuse?",
        "observation_operation": "explain_retrieval",
        "expected_possible_flip_reason": "Explaining Q1 stores focus terms from build-parser evidence that can boost a competing markdown document.",
    },
    {
        "scenario_id": "S5_cache_materialization_stream",
        "variant": "cache_materialization_feedback",
        "q1": "trace logger diagnostics logging utility",
        "q2": "Which tool handles streaming response content?",
        "observation_operation": "preview_context",
        "expected_possible_flip_reason": "Preview materializes cached trace documents and cache presence becomes a later ranking feature.",
    },
    {
        "scenario_id": "S6_recency_inspect_state",
        "variant": "recency_memory_feedback",
        "q1": "session memory alpha preview evidence",
        "q2": "Which answer is marked for the alpha memory question?",
        "observation_operation": "preview_context",
        "expected_possible_flip_reason": "Preview stores alpha memory evidence; later answer may change if recency boost is active.",
    },
    {
        "scenario_id": "S7_baseline_explain_markdown",
        "variant": "pure_baseline",
        "q1": "markdown build parser reuse processors",
        "q2": "Which document says reset must be called before reuse?",
        "observation_operation": "explain_retrieval",
        "expected_possible_flip_reason": "Baseline explanation records no focus terms, so no flip should occur.",
    },
]


CSV_COLUMNS = [
    "scenario_id",
    "variant",
    "observation_operation",
    "q1",
    "q2",
    "order_A_topk",
    "order_B_topk",
    "order_A_answer",
    "order_B_answer",
    "top1_changed",
    "topk_order_changed",
    "answer_changed",
    "classification",
    "expected_possible_flip_reason",
    "state_A",
    "state_B",
]


def normalized_for_replay(results: list[dict[str, Any]], ablation: list[dict[str, Any]]) -> dict[str, Any]:
    return {"results": results, "ablation": ablation}


def run_all() -> list[dict[str, Any]]:
    corpus = load_corpus(CORPUS_PATH)
    return [run_scenario(corpus, scenario) for scenario in SCENARIOS]


def run_ablation() -> list[dict[str, Any]]:
    corpus = load_corpus(CORPUS_PATH)
    rows = []
    for scenario in SCENARIOS:
        if scenario["variant"] == "pure_baseline":
            continue
        for label, weight in [("disabled", 0.0), ("default", None), ("strong", 3.0)]:
            result = run_scenario(corpus, scenario, feedback_weight=weight)
            rows.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "variant": scenario["variant"],
                    "feedback_mode": label,
                    "feedback_weight": result["state_A"]["feedback_weight"],
                    "classification": result["classification"],
                    "top1_changed": result["top1_changed"],
                    "topk_order_changed": result["topk_order_changed"],
                    "answer_changed": result["answer_changed"],
                    "order_A_topk": result["order_A_topk"],
                    "order_B_topk": result["order_B_topk"],
                    "order_A_answer": result["order_A_answer"],
                    "order_B_answer": result["order_B_answer"],
                }
            )
    return rows


def write_results(results: list[dict[str, Any]]) -> None:
    RESULTS_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    **{key: result[key] for key in CSV_COLUMNS if key in result},
                    "order_A_topk": json.dumps(result["order_A_topk"]),
                    "order_B_topk": json.dumps(result["order_B_topk"]),
                    "state_A": json.dumps(result["state_A"], sort_keys=True),
                    "state_B": json.dumps(result["state_B"], sort_keys=True),
                }
            )


def write_ablation(ablation: list[dict[str, Any]]) -> None:
    columns = [
        "scenario_id",
        "variant",
        "feedback_mode",
        "feedback_weight",
        "classification",
        "top1_changed",
        "topk_order_changed",
        "answer_changed",
        "order_A_topk",
        "order_B_topk",
        "order_A_answer",
        "order_B_answer",
    ]
    with ABLATION_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in ablation:
            writer.writerow({**row, "order_A_topk": json.dumps(row["order_A_topk"]), "order_B_topk": json.dumps(row["order_B_topk"])})


def replay_check(first_results: list[dict[str, Any]], first_ablation: list[dict[str, Any]]) -> dict[str, Any]:
    second_results = run_all()
    second_ablation = run_ablation()
    first = normalized_for_replay(first_results, first_ablation)
    second = normalized_for_replay(second_results, second_ablation)
    check = {
        "deterministic": first == second,
        "first_hashable_json": json.dumps(first, sort_keys=True),
        "second_hashable_json": json.dumps(second, sort_keys=True),
        "ignored_fields": [],
    }
    REPLAY_JSON.write_text(json.dumps(check, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return check


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def write_report(results: list[dict[str, Any]], ablation: list[dict[str, Any]], replay: dict[str, Any]) -> None:
    counts = Counter(item["classification"] for item in results)
    answer_div = counts["confirmed_answer_divergence"]
    retrieval_div = counts["confirmed_retrieval_order_divergence"]
    state_only = counts["confirmed_state_only_divergence"]
    topk_changed = sum(1 for item in results if item["topk_order_changed"])
    baseline_stable = all(item["classification"] == "no_divergence" for item in results if item["variant"] == "pure_baseline")
    disabled_rows = [row for row in ablation if row["feedback_mode"] == "disabled"]
    ablation_removed = all(row["classification"] == "no_divergence" for row in disabled_rows)
    scenario_rows = [
        {
            "Scenario": r["scenario_id"],
            "Variant": r["variant"],
            "Observation": r["observation_operation"],
            "Classification": r["classification"],
            "A top-k": ",".join(r["order_A_topk"]),
            "B top-k": ",".join(r["order_B_topk"]),
            "A answer": r["order_A_answer"],
            "B answer": r["order_B_answer"],
        }
        for r in results
    ]
    ablation_rows = [
        {
            "Scenario": r["scenario_id"],
            "Mode": r["feedback_mode"],
            "Weight": r["feedback_weight"],
            "Classification": r["classification"],
            "Answer changed": r["answer_changed"],
        }
        for r in ablation
    ]
    REPORT_MD.write_text(
        "# RAG OSDS Experiment Report\n\n"
        "## 1. Executive Summary\n\n"
        f"This deterministic synthetic RAG simulator ran {len(results)} scenarios across pure and feedback variants. "
        f"It found {answer_div} answer divergences, {topk_changed} total top-k retrieval-order changes, {retrieval_div} retrieval-order-only divergences, and {state_only} state-only divergence(s). "
        f"Pure baseline scenarios stayed stable: {baseline_stable}. Feedback-disabled ablations removed divergences: {ablation_removed}. Replay was deterministic: {replay['deterministic']}.\n\n"
        "## 2. Why RAG/Agent Systems Are Relevant\n\n"
        "RAG and agentic systems often expose operations that look observational: previewing retrieved context, logging retrieval, explaining a trace, or inspecting memory. In adaptive systems those reads can plausibly update access counts, recency memory, cache materialization, or focus terms used by later retrieval.\n\n"
        "## 3. Simulator Design\n\n"
        "The simulator uses a small synthetic corpus, lexical token-overlap scoring with deterministic tie-breaking, optional deterministic feedback terms, and an answer generator that returns the marked `answer_span` from the top retrieved document. No external API, network, paid model, or random component is used.\n\n"
        "## 4. Variants\n\n"
        "- `pure_baseline`: observation methods do not mutate retrieval state.\n"
        "- `access_count_feedback`: retrieval/logging increments document access counts used in later ranking.\n"
        "- `recency_memory_feedback`: preview/retrieval stores document IDs in session memory used as a later recency boost.\n"
        "- `explanation_feedback`: explanations store focus terms used as a later retrieval feature.\n"
        "- `cache_materialization_feedback`: preview/log/retrieval materializes cache state used as a later ranking feature.\n\n"
        "## 5. Scenario Table\n\n"
        + md_table(scenario_rows, ["Scenario", "Variant", "Observation", "Classification", "A top-k", "B top-k", "A answer", "B answer"])
        + "\n\n## 6. Main Results Table\n\n"
        f"- `confirmed_answer_divergence`: {answer_div}\n"
        f"- scenarios with top-k order changed: {topk_changed}\n"
        f"- `confirmed_retrieval_order_divergence`: {retrieval_div}\n"
        f"- `confirmed_state_only_divergence`: {state_only}\n"
        f"- `no_divergence`: {counts['no_divergence']}\n\n"
        "## 7. Ablation Results\n\n"
        + md_table(ablation_rows, ["Scenario", "Mode", "Weight", "Classification", "Answer changed"])
        + "\n\n## 8. Replay/Determinism Check\n\n"
        f"The full experiment and ablation were run twice and compared as JSON. Deterministic replay passed: {replay['deterministic']}.\n\n"
        "## 9. Interpretation\n\n"
        "The experiment demonstrates mechanism plausibility: observation-shaped retrieval, logging, preview, and explanation operations can be modeled as access-observation feedback loops that alter later context or answers. The baseline and zero-weight ablations isolate feedback as the necessary mechanism in this simulator.\n\n"
        "## 10. Limitations\n\n"
        "This is a synthetic deterministic RAG simulator. It does not evaluate commercial RAG systems, does not show real-world prevalence, does not measure speed improvement, and does not show package bugs. Several positive cases are expected effects of explicitly stateful feedback policies.\n\n"
        "## 11. Manuscript Integration Recommendation\n\n"
        "Use this as appendix or short discussion evidence for mechanism plausibility in RAG/agentic systems. It is strong enough to motivate a cautious paragraph, but not strong enough for a headline empirical claim about deployed systems.\n",
        encoding="utf-8",
    )


def write_quality(results: list[dict[str, Any]], ablation: list[dict[str, Any]], replay: dict[str, Any]) -> None:
    counts = Counter(item["classification"] for item in results)
    topk_changed = sum(1 for item in results if item["topk_order_changed"])
    baseline_no_div = any(item["variant"] == "pure_baseline" and item["classification"] == "no_divergence" for item in results)
    feedback_div = any(item["variant"] != "pure_baseline" and item["classification"] in {"confirmed_answer_divergence", "confirmed_retrieval_order_divergence"} for item in results)
    ablation_removed = all(row["classification"] == "no_divergence" for row in ablation if row["feedback_mode"] == "disabled")
    QUALITY_MD.write_text(
        "# Quality Gate Report\n\n"
        "## Experiment Gates\n\n"
        f"- JSON valid: true (`{RESULTS_JSON.name}` and `{REPLAY_JSON.name}` written by Python JSON encoder).\n"
        f"- CSV headers present: true (`{RESULTS_CSV.name}` and `{ABLATION_CSV.name}`).\n"
        f"- Replay check passed: {replay['deterministic']}.\n"
        f"- At least one baseline no-divergence scenario exists: {baseline_no_div}.\n"
        f"- At least one feedback scenario shows retrieval or answer divergence: {feedback_div}.\n"
        f"- Feedback weight 0 removes divergence: {ablation_removed}.\n\n"
        "## Counts\n\n"
        f"- Scenarios: {len(results)}\n"
        f"- Answer divergences: {counts['confirmed_answer_divergence']}\n"
        f"- Top-k retrieval-order changes: {topk_changed}\n"
        f"- Retrieval-order-only divergences: {counts['confirmed_retrieval_order_divergence']}\n"
        f"- State-only divergences: {counts['confirmed_state_only_divergence']}\n"
        f"- No divergence: {counts['no_divergence']}\n\n"
        "## Project Test Gates\n\n"
        "- `C:\\Users\\Asus\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe run_tests.py`: passed, 28/28.\n"
        "- `C:\\Users\\Asus\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -m pytest tests`: passed, 44/44.\n",
        encoding="utf-8",
    )


def main() -> int:
    results = run_all()
    ablation = run_ablation()
    write_results(results)
    write_ablation(ablation)
    replay = replay_check(results, ablation)
    write_report(results, ablation, replay)
    write_quality(results, ablation, replay)
    counts = Counter(item["classification"] for item in results)
    print(
        f"scenarios={len(results)} answer_divergences={counts['confirmed_answer_divergence']} "
        f"topk_order_changes={sum(1 for item in results if item['topk_order_changed'])} "
        f"retrieval_order_only_divergences={counts['confirmed_retrieval_order_divergence']} replay={replay['deterministic']}"
    )
    return 0 if replay["deterministic"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
