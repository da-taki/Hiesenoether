from __future__ import annotations

from collections import defaultdict
from fractions import Fraction

from common import (
    RESULTS_DIR,
    evaluate_configuration,
    fraction_text,
    markdown_table,
    write_csv,
    write_json,
)

BODY_LENGTHS = [3, 5, 8, 10, 15, 20, 30, 50]
OBSERVATION_COUNTS = list(range(0, 11))
CAP_DEGREES = list(range(1, 9))
DRIFT_SCHEDULES = ["constant", "linear_decay", "exponential_decay"]
SEEDS = [101, 202, 303, 404, 505]
EXHAUSTIVE_CUTOFF = 2_000
SAMPLE_BUDGET_PER_SEED = 64

CSV_PATH = RESULTS_DIR / "expanded_mechanism_sweep.csv"
SUMMARY_PATH = RESULTS_DIR / "expanded_mechanism_sweep_summary.json"
TABLES_PATH = RESULTS_DIR / "expanded_mechanism_sweep_tables.md"

def as_fraction(text: str) -> Fraction:
    return Fraction(text) if text else Fraction(0)

def summarize(rows: list[dict]) -> dict:
    total_executions = sum(int(row["executions"]) for row in rows)
    zero_observation = [row for row in rows if int(row["observation_count"]) == 0]
    zero_observation_counterexamples = [
        row for row in zero_observation if as_fraction(row["exact_range"]) != 0
    ]

    linear_positive = [
        row for row in rows
        if int(row["cap_degree"]) == 1
        and int(row["observation_count"]) > 0
        and as_fraction(row["exact_range"]) > 0
    ]

    by_base: dict[tuple[int, int, str], dict[int, dict]] = defaultdict(dict)
    for row in rows:
        key = (
            int(row["body_length"]),
            int(row["observation_count"]),
            str(row["drift_schedule"]),
        )
        by_base[key][int(row["cap_degree"])] = row

    nonlinear_amplifications = []
    nonlinear_counterexamples = []
    for (body_length, observations, schedule), degree_rows in sorted(by_base.items()):
        linear = degree_rows.get(1)
        if linear is None:
            continue
        linear_range = as_fraction(linear["exact_range"])
        for degree in CAP_DEGREES[1:]:
            row = degree_rows.get(degree)
            if row is None:
                continue
            row_range = as_fraction(row["exact_range"])
            comparison = {
                "body_length": body_length,
                "observation_count": observations,
                "drift_schedule": schedule,
                "cap_degree": degree,
                "linear_range": fraction_text(linear_range),
                "nonlinear_range": fraction_text(row_range),
            }
            if observations > 0 and row_range > linear_range:
                nonlinear_amplifications.append(comparison)
            elif observations > 0:
                nonlinear_counterexamples.append(comparison)

    return {
        "total_configurations_run": len(rows),
        "total_executions": total_executions,
        "body_lengths": BODY_LENGTHS,
        "observation_counts": [OBSERVATION_COUNTS[0], OBSERVATION_COUNTS[-1]],
        "cap_degrees": [CAP_DEGREES[0], CAP_DEGREES[-1]],
        "drift_schedules": DRIFT_SCHEDULES,
        "sampling": {
            "seeds": SEEDS,
            "sample_budget_per_seed": SAMPLE_BUDGET_PER_SEED,
            "exhaustive_cutoff_unique_permutations": EXHAUSTIVE_CUTOFF,
        },
        "zero_observation_configurations": len(zero_observation),
        "zero_observation_all_zero_divergence": not zero_observation_counterexamples,
        "zero_observation_counterexamples": zero_observation_counterexamples,
        "linear_cap_positive_divergence_configurations": len(linear_positive),
        "linear_cap_positive_examples": linear_positive[:10],
        "nonlinear_cap_amplified_over_linear_configurations": len(nonlinear_amplifications),
        "nonlinear_cap_amplification_examples": nonlinear_amplifications[:10],
        "nonlinear_cap_counterexamples": nonlinear_counterexamples,
        "exact_rational_arithmetic_used": True,
    }

def write_tables(rows: list[dict], summary: dict) -> None:
    top_ranges = sorted(rows, key=lambda row: float(row["range"]), reverse=True)[:20]
    zero_rows = [row for row in rows if int(row["observation_count"]) == 0][:12]
    linear_positive = summary["linear_cap_positive_examples"]

    lines = [
        "# Expanded Mechanism Sweep Tables",
        "",
        f"Total configurations: {summary['total_configurations_run']}",
        f"Total executions: {summary['total_executions']}",
        f"Zero-observation all zero divergence: {summary['zero_observation_all_zero_divergence']}",
        "",
        "## Largest Ranges",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "body_length",
                "observation_count",
                "cap_degree",
                "drift_schedule",
                "sampled_permutations",
                "exhaustive_enumeration_used",
                "range",
                "exact_range",
            ],
            top_ranges,
        )
    )
    lines.extend(["", "## Zero-Observation Check", ""])
    lines.extend(
        markdown_table(
            [
                "body_length",
                "observation_count",
                "cap_degree",
                "drift_schedule",
                "range",
                "exact_range",
            ],
            zero_rows,
        )
    )
    lines.extend(["", "## Linear Cap Already Diverges", ""])
    lines.extend(
        markdown_table(
            [
                "body_length",
                "observation_count",
                "cap_degree",
                "drift_schedule",
                "sampled_permutations",
                "range",
                "exact_range",
            ],
            linear_positive,
        )
    )
    TABLES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def run() -> dict:
    rows: list[dict] = []
    for schedule in DRIFT_SCHEDULES:
        for body_length in BODY_LENGTHS:
            for observations in OBSERVATION_COUNTS:
                for degree in CAP_DEGREES:
                    row, _ = evaluate_configuration(
                        reads=body_length,
                        observations=observations,
                        degree=degree,
                        schedule=schedule,
                        exhaustive_cutoff=EXHAUSTIVE_CUTOFF,
                        sample_budget_per_seed=SAMPLE_BUDGET_PER_SEED,
                        seeds=SEEDS,
                    )
                    rows.append(row)

    write_csv(CSV_PATH, rows)
    summary = summarize(rows)
    summary["csv"] = "results/review_experiments/expanded_mechanism_sweep.csv"
    write_json(SUMMARY_PATH, summary)
    write_tables(rows, summary)
    return summary

def main() -> int:
    summary = run()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(f"wrote {TABLES_PATH}")
    print(f"configurations={summary['total_configurations_run']}")
    print(f"executions={summary['total_executions']}")
    print(f"zero_observation_all_zero_divergence={summary['zero_observation_all_zero_divergence']}")
    print(f"counterexamples={len(summary['nonlinear_cap_counterexamples'])}")
    return 0 if not summary["zero_observation_counterexamples"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
