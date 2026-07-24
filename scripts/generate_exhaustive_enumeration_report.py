from __future__ import annotations

import csv
import json
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exhaustive_permutation_check import exact_row

CSV_PATH = REPO / "results" / "exhaustive_enumeration_report.csv"
SUMMARY_PATH = REPO / "results" / "exhaustive_enumeration_summary.json"

def parse_fraction(text: str) -> Fraction:
    return Fraction(text)

def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

def generate() -> dict:
    rows = []
    mismatches = []
    max_abs_mismatch = Fraction(0)

    for body_length in range(2, 9):
        for observations in range(1, 5):
            for cap_degree in range(1, 5):
                row = exact_row(body_length, observations, cap_degree)
                exact_range = parse_fraction(row["exact_range"])
                sampled_range = parse_fraction(row["sampled_range"])
                abs_mismatch = abs(exact_range - sampled_range)
                max_abs_mismatch = max(max_abs_mismatch, abs_mismatch)

                output_row = {
                    "body_length": body_length,
                    "observation_count": observations,
                    "cap_degree": cap_degree,
                    "unique_permutations": row["unique_orderings"],
                    "sampled_unique_permutations": row["sampled_unique_orderings"],
                    "sampled_min": row["sampled_min"],
                    "sampled_max": row["sampled_max"],
                    "sampled_range": row["sampled_range"],
                    "exhaustive_min": row["exact_min"],
                    "exhaustive_max": row["exact_max"],
                    "exhaustive_range": row["exact_range"],
                    "match": row["sampled_range_matched_exact"],
                    "absolute_range_mismatch": fraction_text(abs_mismatch),
                }
                rows.append(output_row)
                if not row["sampled_range_matched_exact"]:
                    mismatches.append(output_row)

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "total_configurations": len(rows),
        "expected_total_if_sweep_matches_paper": 112,
        "matched_configurations": len(rows) - len(mismatches),
        "mismatched_configurations": len(mismatches),
        "max_absolute_mismatch": fraction_text(max_abs_mismatch),
        "mismatches": mismatches,
        "scope": {
            "body_lengths": [2, 8],
            "observation_counts": [1, 4],
            "cap_degrees": [1, 4],
        },
        "csv": str(CSV_PATH.relative_to(REPO)),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

def main() -> int:
    summary = generate()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(
        "configurations={total_configurations} matched={matched_configurations} "
        "mismatched={mismatched_configurations}".format(**summary)
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
