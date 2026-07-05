from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from common import RESULTS_DIR, markdown_table, repo_relative, write_csv, write_json

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from analysis.oc_static import analyze_file

BENCHMARK_FILES = [
    REPO / "analysis" / "benchmark_examples.py",
    REPO / "benchmarks" / "controlled_extended" / "extended_examples.py",
]
LABELS = ["SAFE", "LOW", "MEDIUM", "HIGH"]
LABEL_ORDER = {label: index for index, label in enumerate(LABELS)}

CSV_PATH = RESULTS_DIR / "extended_controlled_benchmark.csv"
SUMMARY_PATH = RESULTS_DIR / "extended_controlled_benchmark_summary.json"
TABLES_PATH = RESULTS_DIR / "extended_controlled_benchmark_tables.md"


def expected_labels(path: Path) -> dict[str, str]:
    namespace: dict = {}
    exec(path.read_text(encoding="utf-8"), namespace)
    return {
        name: getattr(obj, "expected_risk")
        for name, obj in namespace.items()
        if getattr(obj, "expected_risk", None) is not None
    }


def evidence_text(cls: dict) -> str:
    parts = []
    for key, values in cls.get("evidence", {}).items():
        for value in values:
            parts.append(f"{key}: {value}")
    return " | ".join(parts)


def evaluate_files() -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    module_findings: list[dict] = []
    for path in BENCHMARK_FILES:
        expected = expected_labels(path)
        analyzed = analyze_file(path)
        observed = {cls["class"]: cls for cls in analyzed["classes"]}
        module_findings.extend(analyzed.get("module_level_nonlinear_uses", []))

        for class_name, expected_label in sorted(expected.items()):
            cls = observed.get(class_name)
            observed_label = cls["risk_label"] if cls else "MISSING"
            expected_positive = expected_label != "SAFE"
            observed_positive = observed_label != "SAFE"
            rows.append(
                {
                    "file": repo_relative(path),
                    "class": class_name,
                    "line": cls.get("line", "") if cls else "",
                    "expected": expected_label,
                    "observed": observed_label,
                    "expected_positive": expected_positive,
                    "observed_positive": observed_positive,
                    "exact_match": expected_label == observed_label,
                    "severity_delta": (
                        "" if observed_label == "MISSING"
                        else LABEL_ORDER[observed_label] - LABEL_ORDER[expected_label]
                    ),
                    "evidence": evidence_text(cls) if cls else "",
                }
            )
    return rows, module_findings


def summarize(rows: list[dict], module_findings: list[dict]) -> dict:
    tp = fp = tn = fn = 0
    confusion = {expected: {observed: 0 for observed in LABELS + ["MISSING"]} for expected in LABELS}

    for row in rows:
        expected_positive = bool(row["expected_positive"])
        observed_positive = bool(row["observed_positive"])
        if expected_positive and observed_positive:
            tp += 1
        elif not expected_positive and observed_positive:
            fp += 1
        elif not expected_positive and not observed_positive:
            tn += 1
        elif expected_positive and not observed_positive:
            fn += 1
        confusion[row["expected"]][row["observed"]] += 1

    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    specificity = tn / (tn + fp) if tn + fp else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    exact = sum(1 for row in rows if row["exact_match"])

    new_cases = [
        row for row in rows
        if row["file"] == "benchmarks/controlled_extended/extended_examples.py"
    ]

    return {
        "benchmark_files": [repo_relative(path) for path in BENCHMARK_FILES],
        "cases": len(rows),
        "new_cases_added": len(new_cases),
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "F1": round(f1, 4),
        "exact_label_accuracy": round(exact / len(rows), 4) if rows else 1.0,
        "confusion_matrix": confusion,
        "module_level_nonlinear_uses": module_findings,
        "mismatches": [row for row in rows if not row["exact_match"]],
    }


def write_tables(rows: list[dict], summary: dict) -> None:
    metric_rows = [
        {"metric": key, "value": summary[key]}
        for key in ["cases", "new_cases_added", "TP", "FP", "TN", "FN", "precision", "recall", "specificity", "F1", "exact_label_accuracy"]
    ]
    mismatches = summary["mismatches"]

    lines = [
        "# Extended Controlled Benchmark Tables",
        "",
        "## Metrics",
        "",
    ]
    lines.extend(markdown_table(["metric", "value"], metric_rows))
    lines.extend(["", "## Confusion Matrix", ""])
    confusion_rows = []
    for expected, observed_counts in summary["confusion_matrix"].items():
        row = {"expected": expected}
        row.update(observed_counts)
        confusion_rows.append(row)
    lines.extend(markdown_table(["expected", "SAFE", "LOW", "MEDIUM", "HIGH", "MISSING"], confusion_rows))
    lines.extend(["", "## Label Mismatches", ""])
    if mismatches:
        lines.extend(markdown_table(["file", "class", "expected", "observed", "evidence"], mismatches))
    else:
        lines.append("None.")
    TABLES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    rows, module_findings = evaluate_files()
    write_csv(CSV_PATH, rows)
    summary = summarize(rows, module_findings)
    summary["csv"] = "results/scp_new_experiments/extended_controlled_benchmark.csv"
    write_json(SUMMARY_PATH, summary)
    write_tables(rows, summary)
    return summary


def main() -> int:
    summary = run()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(f"wrote {TABLES_PATH}")
    print(f"cases={summary['cases']}")
    print(f"new_cases_added={summary['new_cases_added']}")
    print(f"precision={summary['precision']}")
    print(f"recall={summary['recall']}")
    print(f"specificity={summary['specificity']}")
    print(f"F1={summary['F1']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
