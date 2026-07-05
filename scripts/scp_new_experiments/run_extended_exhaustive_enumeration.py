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

BODY_LENGTHS = list(range(2, 10))
OBSERVATION_COUNTS = list(range(0, 6))
CAP_DEGREES = list(range(1, 6))
EXHAUSTIVE_CUTOFF = 10_000
SAMPLE_BUDGET = 512
SAMPLE_SEED = 1729

CSV_PATH = RESULTS_DIR / "extended_exhaustive_enumeration.csv"
SUMMARY_PATH = RESULTS_DIR / "extended_exhaustive_enumeration_summary.json"
TABLES_PATH = RESULTS_DIR / "extended_exhaustive_enumeration_tables.md"


def row_for_config(reads: int, observations: int, degree: int) -> dict:
    unique_count = unique_order_count(reads, observations)
    feasible = unique_count <= EXHAUSTIVE_CUTOFF

    row = {
        "body_length": reads,
        "observation_count": observations,
        "cap_degree": degree,
        "unique_permutations": unique_count,
        "exhaustive_feasible": feasible,
        "exact_rational_arithmetic_used": True,
    }

    exact_values: list[Fraction] = []
    if feasible:
        exact_values = evaluate_orders(unique_orders(reads, observations), degree, "constant")
        exact_stats = output_stats(exact_values)
        row.update(
            {
                "exhaustive_min": exact_stats["min_output"],
                "exhaustive_max": exact_stats["max_output"],
                "exhaustive_range": exact_stats["range"],
                "exhaustive_exact_min": exact_stats["exact_min_output"],
                "exhaustive_exact_max": exact_stats["exact_max_output"],
                "exhaustive_exact_range": exact_stats["exact_range"],
            }
        )
    else:
        row.update(
            {
                "exhaustive_min": "",
                "exhaustive_max": "",
                "exhaustive_range": "",
                "exhaustive_exact_min": "",
                "exhaustive_exact_max": "",
                "exhaustive_exact_range": "",
            }
        )

    sample = sampled_orders(reads, observations, min(SAMPLE_BUDGET, unique_count), SAMPLE_SEED)
    sample_values = evaluate_orders(sample, degree, "constant")
    sample_stats = output_stats(sample_values)
    row.update(
        {
            "sampled_permutations": len(sample),
            "sampled_min": sample_stats["min_output"],
            "sampled_max": sample_stats["max_output"],
            "sampled_range": sample_stats["range"],
            "sampled_exact_min": sample_stats["exact_min_output"],
            "sampled_exact_max": sample_stats["exact_max_output"],
            "sampled_exact_range": sample_stats["exact_range"],
            "mismatch_if_both_available": (
                feasible and sample_stats["exact_range"] != row["exhaustive_exact_range"]
            ),
        }
    )
    return row


def summarize(rows: list[dict]) -> dict:
    feasible = [row for row in rows if row["exhaustive_feasible"]]
    infeasible = [row for row in rows if not row["exhaustive_feasible"]]
    mismatches = [row for row in rows if row["mismatch_if_both_available"]]
    original_112_scope = [
        row for row in rows
        if 2 <= int(row["body_length"]) <= 8
        and 1 <= int(row["observation_count"]) <= 4
        and 1 <= int(row["cap_degree"]) <= 4
    ]
    return {
        "total_configurations": len(rows),
        "exhaustive_feasible_configurations": len(feasible),
        "exhaustive_infeasible_configurations": len(infeasible),
        "original_112_scope_configurations": len(original_112_scope),
        "extended_beyond_original_configurations": len(rows) - len(original_112_scope),
        "safe_permutation_cutoff": EXHAUSTIVE_CUTOFF,
        "sample_budget": SAMPLE_BUDGET,
        "sample_seed": SAMPLE_SEED,
        "sample_range_mismatches_when_exact_known": len(mismatches),
        "mismatch_examples": mismatches[:20],
        "max_unique_permutations": max(int(row["unique_permutations"]) for row in rows),
        "exact_rational_arithmetic_used": True,
    }


def write_tables(rows: list[dict], summary: dict) -> None:
    largest = sorted(rows, key=lambda row: int(row["unique_permutations"]), reverse=True)[:20]
    mismatches = [row for row in rows if row["mismatch_if_both_available"]][:20]
    zero_obs = [row for row in rows if int(row["observation_count"]) == 0][:10]

    lines = [
        "# Extended Exhaustive Enumeration Tables",
        "",
        f"Total configurations: {summary['total_configurations']}",
        f"Exhaustive feasible: {summary['exhaustive_feasible_configurations']}",
        f"Extended beyond original 112 scope: {summary['extended_beyond_original_configurations']}",
        "",
        "## Largest Permutation Counts",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "body_length",
                "observation_count",
                "cap_degree",
                "unique_permutations",
                "exhaustive_feasible",
                "exhaustive_range",
                "sampled_range",
                "mismatch_if_both_available",
            ],
            largest,
        )
    )
    lines.extend(["", "## Sample-vs-Exact Range Mismatches", ""])
    if mismatches:
        lines.extend(
            markdown_table(
                [
                    "body_length",
                    "observation_count",
                    "cap_degree",
                    "unique_permutations",
                    "exhaustive_range",
                    "sampled_range",
                ],
                mismatches,
            )
        )
    else:
        lines.append("None.")
    lines.extend(["", "## Zero-Observation Rows", ""])
    lines.extend(
        markdown_table(
            [
                "body_length",
                "observation_count",
                "cap_degree",
                "unique_permutations",
                "exhaustive_range",
            ],
            zero_obs,
        )
    )
    TABLES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    rows = [
        row_for_config(reads, observations, degree)
        for reads in BODY_LENGTHS
        for observations in OBSERVATION_COUNTS
        for degree in CAP_DEGREES
    ]
    write_csv(CSV_PATH, rows)
    summary = summarize(rows)
    summary["csv"] = "results/scp_new_experiments/extended_exhaustive_enumeration.csv"
    write_json(SUMMARY_PATH, summary)
    write_tables(rows, summary)
    return summary


def main() -> int:
    summary = run()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(f"wrote {TABLES_PATH}")
    print(f"configurations={summary['total_configurations']}")
    print(f"exhaustive_feasible={summary['exhaustive_feasible_configurations']}")
    print(f"sample_range_mismatches={summary['sample_range_mismatches_when_exact_known']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
