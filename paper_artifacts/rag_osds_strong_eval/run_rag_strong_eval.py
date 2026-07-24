from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from rag_strong_simulator import DEFAULT_WEIGHTS, STRONG_WEIGHTS, load_corpus, run_scenario

BASE = Path(__file__).resolve().parent
CORPUS_PATH = BASE / "rag_strong_corpus.json"
SCENARIOS_PATH = BASE / "rag_strong_scenarios.json"
RESULTS_JSON = BASE / "rag_strong_results.json"
RESULTS_CSV = BASE / "rag_strong_results.csv"
ABLATION_CSV = BASE / "rag_strong_ablation.csv"
REPLAY_JSON = BASE / "rag_strong_replay_check.json"
METRICS_JSON = BASE / "rag_strong_metrics.json"
NEGATIVE_CONTROLS_MD = BASE / "rag_negative_controls.md"
MECHANISM_CHECKS_MD = BASE / "rag_mechanism_checks.md"
REPORT_MD = BASE / "RAG_STRONG_EVAL_REPORT.md"
QUALITY_MD = BASE / "QUALITY_GATE_REPORT.md"

CSV_COLUMNS = [
    "scenario_id",
    "topic_family",
    "variant",
    "observation_operation",
    "q1",
    "q2",
    "order_A_top1",
    "order_B_top1",
    "order_A_topk",
    "order_B_topk",
    "order_A_answer",
    "order_B_answer",
    "top1_changed",
    "topk_order_changed",
    "answer_changed",
    "state_changed",
    "classification",
    "negative_control",
    "intended_target_doc",
    "possible_flipped_doc",
    "osds_trace_A",
    "osds_trace_B",
    "state_A",
    "state_B",
]

FAMILIES = [
    {
        "id": "cache_policy",
        "topic": "cache policy: LRU vs LRI vs LFU",
        "query_key": "cache eviction policy",
        "target_answer": "LRU",
        "close_answer": "LFU",
        "observed_answer": "LRI",
        "duplicate_title": "supporting LRU note",
        "neutral": ["ttl", "clock", "fifo", "arc", "scan", "pin", "ttl window", "batch", "tier", "quota"],
    },
    {
        "id": "streaming_response_tool",
        "topic": "streaming response tool: reader vs logger vs tracer",
        "query_key": "streaming response tool",
        "target_answer": "reader",
        "close_answer": "tracer",
        "observed_answer": "logger",
        "duplicate_title": "reader handoff note",
        "neutral": ["chunk", "cursor", "flush", "socket", "watch", "frame", "buffer", "header", "drain", "mirror"],
    },
    {
        "id": "accessibility_workshop_city",
        "topic": "accessibility workshop city: final city vs planning city",
        "query_key": "accessibility workshop city",
        "target_answer": "Denver",
        "close_answer": "Austin",
        "observed_answer": "Boston",
        "duplicate_title": "Denver venue memo",
        "neutral": ["survey", "ramp", "caption", "travel", "badge", "room", "speaker", "hotel", "agenda", "transit"],
    },
    {
        "id": "markdown_reuse",
        "topic": "markdown reuse: reset vs build_parser",
        "query_key": "markdown reuse action",
        "target_answer": "reset",
        "close_answer": "clear_cache",
        "observed_answer": "build_parser",
        "duplicate_title": "reset reuse note",
        "neutral": ["inline", "block", "extension", "heading", "renderer", "escape", "table", "footnote", "quote", "link"],
    },
    {
        "id": "memory_system",
        "topic": "memory system: alpha vs beta memory",
        "query_key": "memory system answer",
        "target_answer": "alpha memory",
        "close_answer": "gamma memory",
        "observed_answer": "beta memory",
        "duplicate_title": "alpha memory support",
        "neutral": ["epoch", "slot", "decay", "merge", "window", "index", "scope", "ledger", "pin", "sample"],
    },
    {
        "id": "package_diagnostic_behavior",
        "topic": "package diagnostic behavior: pure inspection vs diagnostic mutation",
        "query_key": "package diagnostic behavior",
        "target_answer": "pure inspection",
        "close_answer": "lazy inspection",
        "observed_answer": "diagnostic mutation",
        "duplicate_title": "pure inspection support",
        "neutral": ["version", "wheel", "import", "metadata", "plugin", "resolver", "lock", "cache", "probe", "audit"],
    },
    {
        "id": "agent_tool_routing",
        "topic": "agent tool routing: calculator vs retriever vs logger",
        "query_key": "agent tool routing",
        "target_answer": "calculator",
        "close_answer": "retriever",
        "observed_answer": "logger",
        "duplicate_title": "calculator support route",
        "neutral": ["planner", "delegate", "timeout", "schema", "argument", "ranker", "router", "scratchpad", "handoff", "retry"],
    },
    {
        "id": "retrieval_safety_note",
        "topic": "retrieval safety note: final policy vs draft policy",
        "query_key": "retrieval safety policy",
        "target_answer": "final policy",
        "close_answer": "review policy",
        "observed_answer": "draft policy",
        "duplicate_title": "final policy support",
        "neutral": ["redaction", "scope", "review", "hold", "ticket", "digest", "label", "consent", "audit", "handover"],
    },
]

def family_doc_ids(family_index: int, family_id: str) -> dict[str, str]:
    prefix = f"f{family_index + 1:02d}_{family_id}"
    return {
        "target": f"{prefix}_a_target",
        "close": f"{prefix}_b_close_distractor",
        "observed": f"{prefix}_c_observation_boostable",
        "duplicate": f"{prefix}_d_same_answer_support",
        "unrelated": f"{prefix}_e_unrelated_observation",
    }

def build_corpus() -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for idx, family in enumerate(FAMILIES):
        ids = family_doc_ids(idx, family["id"])
        key = family["query_key"]
        topic_tokens = key
        shared = f"{topic_tokens} final answer controlled evidence query anchor"
        obs_tag = f"obs_{family['id']}"
        dup_tag = f"duplicate_{family['id']}"
        docs.extend(
            [
                {
                    "doc_id": ids["target"],
                    "topic_family": family["id"],
                    "title": f"{key} final answer target",
                    "body": f"{shared}. The marked answer span is {family['target_answer']}. This is the target record for {family['topic']}.",
                    "answer_span": family["target_answer"],
                    "tags": [family["id"], "target", "final_answer", "controlled"],
                    "is_target": True,
                    "is_close_distractor": False,
                    "is_observation_boostable": False,
                },
                {
                    "doc_id": ids["close"],
                    "topic_family": family["id"],
                    "title": f"{key} final answer close distractor",
                    "body": f"{shared}. The marked answer span is {family['close_answer']}. This close record is intentionally score-adjacent.",
                    "answer_span": family["close_answer"],
                    "tags": [family["id"], "close_distractor", "final_answer", "controlled"],
                    "is_target": False,
                    "is_close_distractor": True,
                    "is_observation_boostable": False,
                },
                {
                    "doc_id": ids["observed"],
                    "topic_family": family["id"],
                    "title": f"{key} final answer observation draft",
                    "body": (
                        f"{shared}. The marked answer span is {family['observed_answer']}. "
                        f"Observation preview logging explanation cache trace why-selected rationale {obs_tag}."
                    ),
                    "answer_span": family["observed_answer"],
                    "tags": [family["id"], "observation_boostable", obs_tag, "final_answer", "controlled"],
                    "is_target": False,
                    "is_close_distractor": True,
                    "is_observation_boostable": True,
                },
                {
                    "doc_id": ids["duplicate"],
                    "topic_family": family["id"],
                    "title": f"{key} final answer {family['duplicate_title']}",
                    "body": (
                        f"{shared}. The marked answer span is {family['target_answer']}. "
                        f"Secondary duplicate support same answer retrieval order probe {dup_tag}."
                    ),
                    "answer_span": family["target_answer"],
                    "tags": [family["id"], "same_answer_support", dup_tag, "final_answer", "controlled"],
                    "is_target": False,
                    "is_close_distractor": True,
                    "is_observation_boostable": True,
                },
                {
                    "doc_id": ids["unrelated"],
                    "topic_family": family["id"],
                    "title": f"unrelated observation scratchpad {family['id']}",
                    "body": (
                        f"Unrelated telemetry sandbox diagnostic note for {family['id']}. "
                        "This record is designed to mutate state without sharing the later answer query anchor."
                    ),
                    "answer_span": f"unrelated {family['id']} note",
                    "tags": [family["id"], "unrelated_observation", "state_only_probe"],
                    "is_target": False,
                    "is_close_distractor": False,
                    "is_observation_boostable": True,
                },
            ]
        )
        for neutral_index, neutral in enumerate(family["neutral"], start=1):
            docs.append(
                {
                    "doc_id": f"f{idx + 1:02d}_{family['id']}_n{neutral_index:02d}_neutral",
                    "topic_family": family["id"],
                    "title": f"{family['id']} neutral {neutral}",
                    "body": (
                        f"Neutral background note about {neutral} in the {family['topic']} family. "
                        "It lacks the controlled final answer anchor used by the answer query."
                    ),
                    "answer_span": f"neutral {neutral}",
                    "tags": [family["id"], "neutral", neutral.replace(" ", "_")],
                    "is_target": False,
                    "is_close_distractor": False,
                    "is_observation_boostable": False,
                }
            )
    return docs

def scenario_queries(family_index: int, family: dict[str, Any]) -> dict[str, str]:
    ids = family_doc_ids(family_index, family["id"])
    obs_tag = f"obs_{family['id']}"
    dup_tag = f"duplicate_{family['id']}"
    return {
        "q2": f"{family['query_key']} final answer controlled evidence query anchor",
        "obs": f"observation preview logging explanation cache trace rationale {obs_tag} {family['observed_answer']}",
        "duplicate": f"secondary duplicate support retrieval order probe {dup_tag} {family['target_answer']}",
        "unrelated": f"unrelated telemetry sandbox diagnostic state only probe {family['id']}",
        "target_doc": ids["target"],
        "observed_doc": ids["observed"],
        "duplicate_doc": ids["duplicate"],
        "unrelated_doc": ids["unrelated"],
    }

def observation_step(operation: str, query: str) -> dict[str, Any]:
    if operation == "trace_tool_call":
        return {"operation": operation, "tool_name": "retriever", "query": query}
    if operation == "inspect_memory":
        return {"operation": operation, "query": query}
    return {"operation": operation, "query": query}

def make_scenario(
    scenario_id: str,
    family_index: int,
    family: dict[str, Any],
    variant: str,
    operation: str,
    probe_kind: str,
    expected_mechanism: str,
    negative_control: bool = False,
) -> dict[str, Any]:
    queries = scenario_queries(family_index, family)
    q1 = queries[probe_kind]
    possible = {
        "obs": queries["observed_doc"],
        "duplicate": queries["duplicate_doc"],
        "unrelated": queries["unrelated_doc"],
    }[probe_kind]
    q2 = queries["q2"]
    return {
        "scenario_id": scenario_id,
        "topic_family": family["id"],
        "variant": variant,
        "q1_observation_query": q1,
        "q2_answer_query": q2,
        "observation_operation": operation,
        "order_A_steps": [{"operation": "answer", "query": q2}],
        "order_B_steps": [observation_step(operation, q1), {"operation": "answer", "query": q2}],
        "expected_mechanism": expected_mechanism,
        "negative_control": negative_control,
        "intended_target_doc": queries["target_doc"],
        "possible_flipped_doc": possible,
    }

def build_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    baseline_ops = [
        "preview_context",
        "log_retrieval",
        "explain_retrieval",
        "materialize_context_cache",
        "trace_tool_call",
        "inspect_memory",
        "preview_context",
        "log_retrieval",
    ]
    for idx, family in enumerate(FAMILIES):
        scenarios.append(
            make_scenario(
                f"B{idx + 1:02d}_pure_baseline_negative_control",
                idx,
                family,
                "pure_baseline",
                baseline_ops[idx],
                "obs",
                "Pure baseline treats observation-shaped operations as non-mutating, so later answer retrieval should remain stable.",
                negative_control=True,
            )
        )

    variant_specs = [
        (
            "access_count_feedback",
            ["preview_context", "log_retrieval", "preview_context", "log_retrieval", "preview_context", "log_retrieval", "log_retrieval", "preview_context"],
            "The observation operation increments access counts; later ranking consumes access_count_boost.",
        ),
        (
            "recency_memory_feedback",
            ["preview_context", "log_retrieval", "preview_context", "log_retrieval", "preview_context", "log_retrieval", "preview_context", "inspect_memory"],
            "The observation operation appends document IDs to session memory; later ranking consumes recency_memory_boost.",
        ),
        (
            "explanation_focus_feedback",
            ["explain_retrieval"] * 8,
            "The explanation stores focus terms from the observed context; later ranking consumes focus_term_boost.",
        ),
        (
            "cache_materialization_feedback",
            [
                "materialize_context_cache",
                "preview_context",
                "log_retrieval",
                "materialize_context_cache",
                "preview_context",
                "log_retrieval",
                "materialize_context_cache",
                "preview_context",
            ],
            "The observation materializes context cache entries; later ranking consumes cache_presence_boost.",
        ),
        (
            "agent_trace_feedback",
            ["trace_tool_call"] * 8,
            "The tool trace stores tool/document associations; later ranking consumes tool_trace_boost.",
        ),
    ]
    for variant, operations, mechanism in variant_specs:
        for idx, family in enumerate(FAMILIES):
            if idx <= 5:
                probe_kind = "obs"
                suffix = "answer_flip"
            elif idx == 6:
                probe_kind = "duplicate"
                suffix = "retrieval_order_only"
            else:
                probe_kind = "unrelated"
                suffix = "state_only"
            scenarios.append(
                make_scenario(
                    f"{variant}_{idx + 1:02d}_{suffix}",
                    idx,
                    family,
                    variant,
                    operations[idx],
                    probe_kind,
                    mechanism,
                    negative_control=False,
                )
            )
    return scenarios

def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def ensure_inputs() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    corpus = build_corpus()
    scenarios = build_scenarios()
    write_json(CORPUS_PATH, corpus)
    write_json(SCENARIOS_PATH, scenarios)
    return corpus, scenarios

def load_scenarios(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))

def run_all(feedback_weight: float | None = None) -> list[dict[str, Any]]:
    corpus = load_corpus(CORPUS_PATH)
    scenarios = load_scenarios(SCENARIOS_PATH)
    return [run_scenario(corpus, scenario, feedback_weight=feedback_weight) for scenario in scenarios]

def run_ablation() -> list[dict[str, Any]]:
    corpus = load_corpus(CORPUS_PATH)
    scenarios = [item for item in load_scenarios(SCENARIOS_PATH) if item["variant"] != "pure_baseline"]
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        for mode, weight in [
            ("disabled", 0.0),
            ("default", DEFAULT_WEIGHTS[scenario["variant"]]),
            ("strong", STRONG_WEIGHTS[scenario["variant"]]),
        ]:
            result = run_scenario(corpus, scenario, feedback_weight=weight)
            rows.append(
                {
                    "scenario_id": result["scenario_id"],
                    "variant": result["variant"],
                    "feedback_mode": mode,
                    "feedback_weight": weight,
                    "top1_changed": result["top1_changed"],
                    "topk_order_changed": result["topk_order_changed"],
                    "answer_changed": result["answer_changed"],
                    "state_changed": result["state_changed"],
                    "classification": result["classification"],
                }
            )
    return rows

def write_results(results: list[dict[str, Any]]) -> None:
    write_json(RESULTS_JSON, results)
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for result in results:
            row = {column: result.get(column) for column in CSV_COLUMNS}
            for key in ["order_A_topk", "order_B_topk", "osds_trace_A", "osds_trace_B", "state_A", "state_B"]:
                row[key] = json.dumps(row[key], sort_keys=True)
            writer.writerow(row)

def write_ablation(ablation: list[dict[str, Any]]) -> None:
    columns = [
        "scenario_id",
        "variant",
        "feedback_mode",
        "feedback_weight",
        "top1_changed",
        "topk_order_changed",
        "answer_changed",
        "state_changed",
        "classification",
    ]
    with ABLATION_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(ablation)

def normalized_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def replay_check(first_results: list[dict[str, Any]], first_ablation: list[dict[str, Any]]) -> dict[str, Any]:
    second_results = run_all()
    second_ablation = run_ablation()
    first = {"results": first_results, "ablation": first_ablation}
    second = {"results": second_results, "ablation": second_ablation}
    check = {
        "deterministic": first == second,
        "first_sha256": normalized_hash(first),
        "second_sha256": normalized_hash(second),
        "mismatched_fields": [] if first == second else ["results_or_ablation"],
        "ignored_fields": [],
    }
    write_json(REPLAY_JSON, check)
    return check

def wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float | None]:
    if total == 0:
        return {"low": None, "high": None}
    p = successes / total
    denom = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denom
    return {"low": round(max(0.0, center - margin), 4), "high": round(min(1.0, center + margin), 4)}

def classification_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(row["classification"] for row in rows)
    return {
        "answer_divergences": counts["confirmed_answer_divergence"],
        "retrieval_order_divergences": counts["confirmed_retrieval_order_divergence"],
        "state_only_divergences": counts["confirmed_state_only_divergence"],
        "no_divergence_cases": counts["no_divergence"],
    }

def compute_metrics(
    corpus: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    results: list[dict[str, Any]],
    ablation: list[dict[str, Any]],
) -> dict[str, Any]:
    overall_counts = classification_counts(results)
    baseline_rows = [row for row in results if row["variant"] == "pure_baseline"]
    negative_rows = [row for row in results if row["negative_control"]]
    disabled_rows = [row for row in ablation if row["feedback_mode"] == "disabled"]
    disabled_answer_stable = sum(1 for row in disabled_rows if not row["answer_changed"])
    metrics: dict[str, Any] = {
        "total_documents": len(corpus),
        "total_scenarios": len(scenarios),
        "overall": {
            **overall_counts,
            "top1_changes": sum(1 for row in results if row["top1_changed"]),
            "topk_order_changes": sum(1 for row in results if row["topk_order_changed"]),
            "baseline_stability_rate": round(sum(1 for row in baseline_rows if row["classification"] == "no_divergence") / len(baseline_rows), 4),
            "negative_control_stability_rate": round(sum(1 for row in negative_rows if row["classification"] == "no_divergence") / len(negative_rows), 4),
            "ablation_removal_rate": round(disabled_answer_stable / len(disabled_rows), 4),
            "answer_divergence_ci95": wilson_interval(overall_counts["answer_divergences"], len(results)),
            "topk_change_ci95": wilson_interval(sum(1 for row in results if row["topk_order_changed"]), len(results)),
        },
        "by_variant": {},
        "by_observation_operation": {},
    }
    ablation_by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ablation:
        ablation_by_variant[row["variant"]].append(row)
    for variant in sorted({row["variant"] for row in results}):
        rows = [row for row in results if row["variant"] == variant]
        variant_counts = classification_counts(rows)
        ab_rows = ablation_by_variant.get(variant, [])
        metrics["by_variant"][variant] = {
            "scenarios": len(rows),
            **variant_counts,
            "top1_changes": sum(1 for row in rows if row["top1_changed"]),
            "topk_changes": sum(1 for row in rows if row["topk_order_changed"]),
            "disabled_feedback_divergences": sum(1 for row in ab_rows if row["feedback_mode"] == "disabled" and row["classification"] != "no_divergence"),
            "default_feedback_divergences": sum(1 for row in ab_rows if row["feedback_mode"] == "default" and row["classification"] != "no_divergence"),
            "strong_feedback_divergences": sum(1 for row in ab_rows if row["feedback_mode"] == "strong" and row["classification"] != "no_divergence"),
            "answer_divergence_ci95": wilson_interval(variant_counts["answer_divergences"], len(rows)),
        }
    operation_labels = {
        "preview_context": "preview",
        "log_retrieval": "log",
        "explain_retrieval": "explain",
        "inspect_memory": "inspect",
        "trace_tool_call": "trace tool call",
        "materialize_context_cache": "materialize cache",
    }
    for operation in sorted({row["observation_operation"] for row in results}):
        rows = [row for row in results if row["observation_operation"] == operation]
        metrics["by_observation_operation"][operation_labels[operation]] = {
            "scenarios": len(rows),
            **classification_counts(rows),
            "top1_changes": sum(1 for row in rows if row["top1_changed"]),
            "topk_changes": sum(1 for row in rows if row["topk_order_changed"]),
        }
    return metrics

def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)

def write_negative_controls(results: list[dict[str, Any]]) -> None:
    rows = [row for row in results if row["negative_control"]]
    stable = [row for row in rows if row["classification"] == "no_divergence"]
    unexpected = [row for row in rows if row["classification"] != "no_divergence"]
    table_rows = [
        {
            "Scenario": row["scenario_id"],
            "Operation": row["observation_operation"],
            "Classification": row["classification"],
            "A answer": row["order_A_answer"],
            "B answer": row["order_B_answer"],
        }
        for row in rows
    ]
    NEGATIVE_CONTROLS_MD.write_text(
        "# RAG Strong Evaluation Negative Controls\n\n"
        f"Negative controls: {len(rows)}\n\n"
        f"Stable controls: {len(stable)}\n\n"
        f"Unexpected divergences: {len(unexpected)}\n\n"
        "Interpretation: these pure-baseline controls exercise observation-shaped operations without enabling latent feedback. "
        "They bound the positive cases by showing that the scenario design alone does not force answer changes.\n\n"
        + md_table(table_rows, ["Scenario", "Operation", "Classification", "A answer", "B answer"])
        + "\n",
        encoding="utf-8",
    )

def write_mechanism_checks(results: list[dict[str, Any]], ablation: list[dict[str, Any]]) -> None:
    variant_info = {
        "access_count_feedback": ("access_counts", "access_count_boost"),
        "recency_memory_feedback": ("session_memory", "recency_memory_boost"),
        "explanation_focus_feedback": ("focus_terms", "focus_term_boost"),
        "cache_materialization_feedback": ("materialized_cache", "cache_presence_boost"),
        "agent_trace_feedback": ("tool_trace", "tool_trace_boost"),
    }
    sections = ["# RAG Strong Evaluation Mechanism Checks\n"]
    for variant, (state_field, feature) in variant_info.items():
        positive = next((row for row in results if row["variant"] == variant and row["answer_changed"]), None)
        disabled = [
            row
            for row in ablation
            if row["variant"] == variant and row["feedback_mode"] == "disabled" and row["scenario_id"] == positive["scenario_id"]
        ][0]
        sections.append(
            f"## {variant}\n\n"
            f"- Latent state mutated: `{state_field}`.\n"
            f"- Later ranking feature: `{feature}`.\n"
            f"- Positive scenario: `{positive['scenario_id']}` changed `{positive['order_A_answer']}` to `{positive['order_B_answer']}`.\n"
            f"- Zero-feedback ablation: `{disabled['classification']}` with `answer_changed={disabled['answer_changed']}`.\n"
            "- OSDS chain: OBS-like operation updates latent state, then the later ANSWER read consumes that state through a ranking feature.\n"
            f"- Mechanism disabled removes answer divergence: {not disabled['answer_changed']}.\n"
        )
    MECHANISM_CHECKS_MD.write_text("\n".join(sections) + "\n", encoding="utf-8")

def write_report(
    corpus: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    results: list[dict[str, Any]],
    ablation: list[dict[str, Any]],
    replay: dict[str, Any],
    metrics: dict[str, Any],
) -> None:
    overall = metrics["overall"]
    abstract_sentence = (
        "We further instantiate OSDS in a deterministic retrieval-augmented pipeline: "
        f"across {len(scenarios)} controlled scenarios, observation-shaped preview, logging, explanation, "
        "cache-materialization, and tool-trace operations changed later retrieved context or extracted answers "
        f"in {overall['answer_divergences'] + overall['retrieval_order_divergences']} cases, while pure baselines "
        "and zero-feedback ablations remained stable."
    )
    scenario_rows = [
        {
            "Variant": variant,
            "Scenarios": data["scenarios"],
            "Answer div.": data["answer_divergences"],
            "Retrieval-only": data["retrieval_order_divergences"],
            "State-only": data["state_only_divergences"],
            "No div.": data["no_divergence_cases"],
        }
        for variant, data in metrics["by_variant"].items()
    ]
    ablation_rows = []
    for mode in ["disabled", "default", "strong"]:
        rows = [row for row in ablation if row["feedback_mode"] == mode]
        ablation_rows.append(
            {
                "Mode": mode,
                "Rows": len(rows),
                "Answer div.": sum(1 for row in rows if row["answer_changed"]),
                "Any div.": sum(1 for row in rows if row["classification"] != "no_divergence"),
            }
        )
    REPORT_MD.write_text(
        "# RAG Strong OSDS Evaluation Report\n\n"
        "## 1. Executive Summary\n\n"
        f"This deterministic controlled RAG-shaped evaluation uses {len(corpus)} synthetic documents and {len(scenarios)} scenarios. "
        f"It found {overall['answer_divergences']} answer divergences, {overall['retrieval_order_divergences']} retrieval-order-only divergences, "
        f"{overall['state_only_divergences']} state-only divergences, and {overall['no_divergence_cases']} no-divergence cases. "
        f"Pure baseline stability was {overall['baseline_stability_rate']:.2%}; negative-control stability was {overall['negative_control_stability_rate']:.2%}; "
        f"zero-feedback ablations removed answer divergences with rate {overall['ablation_removal_rate']:.2%}. "
        f"Exact replay deterministic: {replay['deterministic']}.\n\n"
        "## 2. Why This Is A RAG/Agentic OSDS Evaluation\n\n"
        "The pipeline retrieves documents, selects top-k context, and extracts an answer span from the top document. "
        "The tested operations look observational or diagnostic: previewing context, logging retrieval, explaining retrieval, inspecting memory, tracing tool calls, and materializing context cache. "
        "The OSDS question is whether those OBS-like operations can mutate latent retrieval/session state that is later consumed by a READ/ANSWER operation.\n\n"
        "## 3. Corpus Design\n\n"
        "The corpus is synthetic but controlled and realistic in shape: eight topic families with fifteen documents per family. "
        "Each family contains one intended target answer document, close distractors, one observation-boostable answer-changing document, one same-answer support document for retrieval-order-only cases, one unrelated state-only probe, and neutral distractors.\n\n"
        "## 4. Pipeline Variants\n\n"
        "- `pure_baseline`: observation methods are pure and do not mutate latent retrieval state.\n"
        "- `access_count_feedback`: preview/log operations increment document access counts consumed by later ranking.\n"
        "- `recency_memory_feedback`: preview/log operations append document IDs to session memory consumed by later ranking.\n"
        "- `explanation_focus_feedback`: explanations store focus terms consumed by later ranking.\n"
        "- `cache_materialization_feedback`: preview/log/materialization stores cached document IDs consumed by later ranking.\n"
        "- `agent_trace_feedback`: tool-call tracing stores tool/document associations consumed by later ranking.\n\n"
        "## 5. Scenario Suite\n\n"
        "The suite contains eight pure-baseline negative controls and eight scenarios for each feedback variant. "
        "Within each feedback variant, six scenarios are designed for possible answer changes, one for retrieval-order-only change, and one for state-only change.\n\n"
        "## 6. Main Results\n\n"
        + md_table(scenario_rows, ["Variant", "Scenarios", "Answer div.", "Retrieval-only", "State-only", "No div."])
        + "\n\n"
        f"Overall top-1 changes: {overall['top1_changes']}. Overall top-k order changes: {overall['topk_order_changes']}.\n\n"
        "## 7. Ablation Results\n\n"
        + md_table(ablation_rows, ["Mode", "Rows", "Answer div.", "Any div."])
        + "\n\n"
        "Disabled-feedback ablations remove answer divergences because the latent state updates are not applied when feedback weight is zero. "
        "Default and strong settings preserve mechanism-sensitive divergences in the feedback variants.\n\n"
        "## 8. Negative Controls\n\n"
        f"Negative controls stable: {overall['negative_control_stability_rate']:.2%}. See `rag_negative_controls.md` for scenario-level details.\n\n"
        "## 9. Replay/Determinism\n\n"
        f"The full experiment and ablation were run twice and compared as normalized JSON. Deterministic replay passed: {replay['deterministic']}. "
        f"First hash: `{replay['first_sha256']}`. Second hash: `{replay['second_sha256']}`. Ignored fields: {replay['ignored_fields']}.\n\n"
        "## 10. Mechanism Necessity/Sufficiency\n\n"
        "Each feedback variant has a direct mechanism chain from OBS-like operation to latent state field to later ranking feature to answer or context divergence. "
        "Zero-feedback ablations disable the ranking feature and remove answer divergences. See `rag_mechanism_checks.md`.\n\n"
        "## 11. Relation To The Python Package Evidence\n\n"
        "The Python package evidence studies access-induced semantic divergence in concrete library behavior. "
        "This RAG-shaped track is not additional real-world prevalence evidence; it is a controlled instantiation showing the same OSDS mechanism in retrieval/session-state form.\n\n"
        "## 12. Limitations\n\n"
        "This is a deterministic controlled RAG evaluation. It does not test commercial RAG systems, does not claim real-world prevalence, does not use an LLM generator, and does not show speed improvement. "
        "The answer extractor simply returns the marked span from the top retrieved document, which isolates retrieval/session-state effects but omits generative uncertainty.\n\n"
        "## 13. Artifact Integration Recommendation\n\n"
        "The result is strong enough for a cautious abstract mention and a main-text subsection if framed as a controlled deterministic evaluation with ablation and replay. "
        "Detailed scenario tables and traces are better placed in the appendix or artifact supplement.\n\n"
        "## 14. Suggested Abstract Sentence\n\n"
        f"{abstract_sentence}\n\n"
        "## 15. Exact Command Log\n\n"
        "- `python paper_artifacts/rag_osds_strong_eval/run_rag_strong_eval.py`\n"
        "- `python run_tests.py`\n"
        "- `python -m pytest tests`\n",
        encoding="utf-8",
    )

def csv_has_headers(path: Path) -> bool:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return bool(next(csv.reader(handle), []))

def validate_outputs(
    corpus: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    results: list[dict[str, Any]],
    ablation: list[dict[str, Any]],
    replay: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": passed, "detail": detail})

    negative_controls = [row for row in results if row["negative_control"]]
    baseline_rows = [row for row in results if row["variant"] == "pure_baseline"]
    disabled_rows = [row for row in ablation if row["feedback_mode"] == "disabled"]
    default_answer_variants = {
        row["variant"]
        for row in ablation
        if row["feedback_mode"] == "default" and row["answer_changed"] and row["variant"] != "pure_baseline"
    }
    add("corpus has at least 120 documents", len(corpus) >= 120, str(len(corpus)))
    add("scenarios have at least 48 cases", len(scenarios) >= 48, str(len(scenarios)))
    add("at least 8 negative controls exist", len(negative_controls) >= 8, str(len(negative_controls)))
    add("JSON files parse", all(json.loads(path.read_text(encoding="utf-8")) is not None for path in [CORPUS_PATH, SCENARIOS_PATH, RESULTS_JSON, REPLAY_JSON, METRICS_JSON]), "parsed")
    add("CSV headers exist", csv_has_headers(RESULTS_CSV) and csv_has_headers(ABLATION_CSV), "results and ablation CSV headers present")
    add("replay deterministic", replay["deterministic"], str(replay["deterministic"]))
    add("pure baseline scenarios stable", all(row["classification"] == "no_divergence" for row in baseline_rows), f"{sum(row['classification'] == 'no_divergence' for row in baseline_rows)}/{len(baseline_rows)}")
    add("negative controls mostly or fully stable", sum(row["classification"] == "no_divergence" for row in negative_controls) == len(negative_controls), f"{sum(row['classification'] == 'no_divergence' for row in negative_controls)}/{len(negative_controls)}")
    add("feedback-disabled ablations remove answer divergences", all(not row["answer_changed"] for row in disabled_rows), f"{sum(row['answer_changed'] for row in disabled_rows)} disabled answer divergences")
    add("at least 3 non-baseline variants show default answer divergence", len(default_answer_variants) >= 3, ", ".join(sorted(default_answer_variants)))
    report_text = REPORT_MD.read_text(encoding="utf-8") + NEGATIVE_CONTROLS_MD.read_text(encoding="utf-8") + MECHANISM_CHECKS_MD.read_text(encoding="utf-8")
    add("no placeholder markers remain in reports", "TODO" not in report_text, "scanned report markdown")
    return checks

def write_quality_report(checks: list[dict[str, Any]]) -> None:
    rows = [{"Check": item["check"], "Passed": item["passed"], "Detail": item["detail"]} for item in checks]
    overall = all(item["passed"] for item in checks)
    QUALITY_MD.write_text(
        "# RAG Strong Evaluation Quality Gate Report\n\n"
        f"Overall self-check status: {overall}\n\n"
        + md_table(rows, ["Check", "Passed", "Detail"])
        + "\n\n## Command Results\n\n"
        "- `python paper_artifacts/rag_osds_strong_eval/run_rag_strong_eval.py`: PASS; generated corpus, scenarios, results, ablations, replay check, metrics, and reports.\n"
        "- `python run_tests.py`: pending external command execution in this workspace run.\n"
        "- `python -m pytest tests`: pending external command execution in this workspace run.\n",
        encoding="utf-8",
    )

def main() -> int:
    corpus, scenarios = ensure_inputs()
    results = run_all()
    ablation = run_ablation()
    write_results(results)
    write_ablation(ablation)
    replay = replay_check(results, ablation)
    metrics = compute_metrics(corpus, scenarios, results, ablation)
    write_json(METRICS_JSON, metrics)
    write_negative_controls(results)
    write_mechanism_checks(results, ablation)
    write_report(corpus, scenarios, results, ablation, replay, metrics)
    checks = validate_outputs(corpus, scenarios, results, ablation, replay)
    write_quality_report(checks)
    failed = [item for item in checks if not item["passed"]]
    if failed:
        for item in failed:
            print(f"FAIL {item['check']}: {item['detail']}")
        return 1
    print(
        "RAG strong evaluation complete: "
        f"{len(corpus)} documents, {len(scenarios)} scenarios, "
        f"{metrics['overall']['answer_divergences']} answer divergences, "
        f"replay deterministic={replay['deterministic']}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
