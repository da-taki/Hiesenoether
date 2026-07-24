from __future__ import annotations

from fractions import Fraction

from common import (
    RESULTS_DIR,
    evaluate_orders,
    fraction_text,
    markdown_table,
    output_stats,
    sampled_orders,
    unique_order_count,
    unique_orders,
    write_csv,
    write_json,
)

CONFIGURATIONS = [
    {"body_length": 5, "observation_count": 3, "cap_degree": 2},
    {"body_length": 6, "observation_count": 4, "cap_degree": 3},
    {"body_length": 8, "observation_count": 4, "cap_degree": 4},
    {"body_length": 9, "observation_count": 5, "cap_degree": 5},
]
BUDGETS = [8, 16, 32, 64, 128, 256, 512, 1024]
SEEDS = [17, 29, 43, 71, 101]

CSV_PATH = RESULTS_DIR / "sampling_convergence.csv"
SUMMARY_PATH = RESULTS_DIR / "sampling_convergence_summary.json"
TABLES_PATH = RESULTS_DIR / "sampling_convergence_tables.md"

def row_for_sample(config: dict, budget: int, seed: int, true_stats: dict) -> dict:
    reads = config["body_length"]
    observations = config["observation_count"]
    degree = config["cap_degree"]
    total_unique = unique_order_count(reads, observations)
    sample = sampled_orders(reads, observations, min(budget, total_unique), seed)
    sample_values = evaluate_orders(sample, degree, "constant")
    sample_stats = output_stats(sample_values)

    true_range = Fraction(true_stats["exact_range"])
    sampled_range = Fraction(sample_stats["exact_range"])
    abs_error = abs(true_range - sampled_range)
    rel_error = float(abs_error / true_range) if true_range else 0.0
    extrema_match = (
        sample_stats["exact_min_output"] == true_stats["exact_min_output"]
        and sample_stats["exact_max_output"] == true_stats["exact_max_output"]
    )

    return {
        "body_length": reads,
        "observation_count": observations,
        "cap_degree": degree,
        "unique_permutations": total_unique,
        "budget": budget,
        "seed": seed,
        "sampled_permutations": len(sample),
        "sampled_min": sample_stats["min_output"],
        "sampled_max": sample_stats["max_output"],
        "sampled_range": sample_stats["range"],
        "sampled_exact_min": sample_stats["exact_min_output"],
        "sampled_exact_max": sample_stats["exact_max_output"],
        "sampled_exact_range": sample_stats["exact_range"],
        "true_exhaustive_range": true_stats["range"],
        "true_exhaustive_exact_range": true_stats["exact_range"],
        "absolute_error": round(float(abs_error), 12),
        "exact_absolute_error": fraction_text(abs_error),
        "relative_error": round(rel_error, 12),
        "sampled_extrema_matched_exact_extrema": extrema_match,
        "exact_rational_arithmetic_used": True,
    }

def exact_stats_for(config: dict) -> dict:
    values = evaluate_orders(
        unique_orders(config["body_length"], config["observation_count"]),
        config["cap_degree"],
        "constant",
    )
    return output_stats(values)

def summarize(rows: list[dict]) -> dict:
    by_budget: dict[int, list[dict]] = {}
    for row in rows:
        by_budget.setdefault(int(row["budget"]), []).append(row)

    budget_rows = []
    for budget in BUDGETS:
        group = by_budget.get(budget, [])
        if not group:
            continue
        exact_matches = sum(1 for row in group if row["sampled_extrema_matched_exact_extrema"])
        avg_rel_error = sum(float(row["relative_error"]) for row in group) / len(group)
        max_rel_error = max(float(row["relative_error"]) for row in group)
        budget_rows.append(
            {
                "budget": budget,
                "rows": len(group),
                "exact_extrema_matches": exact_matches,
                "exact_extrema_match_rate": round(exact_matches / len(group), 4),
                "average_relative_error": round(avg_rel_error, 12),
                "max_relative_error": round(max_rel_error, 12),
            }
        )

    failures_at_max_budget = [
        row for row in rows
        if int(row["budget"]) == max(BUDGETS)
        and not row["sampled_extrema_matched_exact_extrema"]
    ]
    return {
        "configurations": CONFIGURATIONS,
        "budgets": BUDGETS,
        "seeds": SEEDS,
        "rows": len(rows),
        "budget_summary": budget_rows,
        "max_budget_extrema_failures": failures_at_max_budget,
        "exact_rational_arithmetic_used": True,
    }

def write_tables(summary: dict) -> None:
    lines = [
        "# Sampling Convergence Tables",
        "",
        "## Budget Summary",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "budget",
                "rows",
                "exact_extrema_matches",
                "exact_extrema_match_rate",
                "average_relative_error",
                "max_relative_error",
            ],
            summary["budget_summary"],
        )
    )
    lines.extend(["", "## Max-Budget Extrema Failures", ""])
    failures = summary["max_budget_extrema_failures"]
    if failures:
        lines.extend(
            markdown_table(
                [
                    "body_length",
                    "observation_count",
                    "cap_degree",
                    "budget",
                    "seed",
                    "relative_error",
                    "sampled_exact_range",
                    "true_exhaustive_exact_range",
                ],
                failures,
            )
        )
    else:
        lines.append("None.")
    TABLES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def run() -> dict:
    rows = []
    for config in CONFIGURATIONS:
        true_stats = exact_stats_for(config)
        for budget in BUDGETS:
            for seed in SEEDS:
                rows.append(row_for_sample(config, budget, seed, true_stats))

    write_csv(CSV_PATH, rows)
    summary = summarize(rows)
    summary["csv"] = "results/scp_new_experiments/sampling_convergence.csv"
    write_json(SUMMARY_PATH, summary)
    write_tables(summary)
    return summary

def main() -> int:
    summary = run()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(f"wrote {TABLES_PATH}")
    print(f"rows={summary['rows']}")
    print(f"max_budget_extrema_failures={len(summary['max_budget_extrema_failures'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
