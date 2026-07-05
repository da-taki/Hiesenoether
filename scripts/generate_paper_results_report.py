from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from analysis.oc_static_benchmark import evaluate_benchmark

SUMMARY_JSON = REPO / "results" / "paper_results_summary.json"
TABLES_MD = REPO / "results" / "paper_results_tables.md"
PYPI_REVIEWED_CSV = REPO / "results" / "pypi_reviewed_findings.csv"
GAPS_MD = REPO / "REPRODUCIBILITY_GAPS.md"

STATUS_CODE = "reproduced_from_code"
STATUS_EXISTING = "reproduced_from_existing_results"
STATUS_NO_SCRIPT = "missing_reproduction_script"
STATUS_NO_DATA = "missing_raw_data"
STATUS_MISMATCH = "mismatch"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number_entry(name: str, expected, actual, status: str, source: str, note: str = "") -> dict:
    return {
        "name": name,
        "expected": expected,
        "actual": actual,
        "status": status,
        "source": source,
        "note": note,
    }


def status_for_match(expected, actual, base_status: str) -> str:
    return base_status if expected == actual else STATUS_MISMATCH


def collect_execution_count(entries: list[dict]) -> dict:
    path = REPO / "results" / "summary.csv"
    if not path.exists():
        entries.append(number_entry("2.2 million executions", 2_200_000, None, STATUS_NO_DATA, "results/summary.csv"))
        return {"status": STATUS_NO_DATA, "rows": []}

    rows = read_csv(path)
    total = sum(int(float(row["n_valid"])) for row in rows if row.get("n_valid"))
    status = status_for_match(2_200_000, total, STATUS_EXISTING)
    entries.append(
        number_entry(
            "2.2 million executions",
            2_200_000,
            total,
            status,
            "results/summary.csv",
            f"{len(rows)} configurations with n_valid summed from existing results",
        )
    )
    return {"status": status, "configuration_count": len(rows), "total_executions": total}


def collect_table(path: Path, table_name: str, key_fields: list[str], value_fields: list[str]) -> dict:
    rel = str(path.relative_to(REPO))
    if not path.exists():
        return {"status": STATUS_NO_DATA, "source": rel, "rows": []}
    rows = read_csv(path)
    slim_rows = []
    for row in rows:
        slim = {field: row.get(field, "") for field in key_fields + value_fields}
        slim["status"] = STATUS_EXISTING
        slim_rows.append(slim)
    return {"status": STATUS_EXISTING, "source": rel, "rows": slim_rows}


def collect_exhaustive(entries: list[dict]) -> dict:
    path = REPO / "results" / "exhaustive_enumeration_summary.json"
    if not path.exists():
        entries.append(
            number_entry(
                "exhaustive enumeration configurations",
                112,
                None,
                STATUS_NO_DATA,
                "results/exhaustive_enumeration_summary.json",
            )
        )
        return {"status": STATUS_NO_DATA, "source": str(path.relative_to(REPO))}

    data = json.loads(path.read_text(encoding="utf-8"))
    total = data.get("total_configurations")
    mismatches = data.get("mismatched_configurations")
    entries.append(
        number_entry(
            "exhaustive enumeration configurations",
            112,
            total,
            status_for_match(112, total, STATUS_CODE),
            "results/exhaustive_enumeration_summary.json",
        )
    )
    entries.append(
        number_entry(
            "exhaustive enumeration mismatches",
            0,
            mismatches,
            status_for_match(0, mismatches, STATUS_CODE),
            "results/exhaustive_enumeration_summary.json",
        )
    )
    data["status"] = STATUS_CODE if total == 112 and mismatches == 0 else STATUS_MISMATCH
    return data


def collect_analyzer_benchmark(entries: list[dict]) -> dict:
    report = evaluate_benchmark()
    rows = report["rows"]
    tp = fp = tn = fn = 0
    for row in rows:
        expected_positive = row["expected"] != "SAFE"
        observed_positive = row["observed"] != "SAFE"
        if expected_positive and observed_positive:
            tp += 1
        elif not expected_positive and observed_positive:
            fp += 1
        elif not expected_positive and not observed_positive:
            tn += 1
        elif expected_positive and not observed_positive:
            fn += 1

    metrics = {
        "cases": report["cases"],
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": report["precision"],
        "recall": report["recall"],
        "exact_label_accuracy": report["exact_label_accuracy"],
        "rows": rows,
        "status": STATUS_CODE,
        "source": str(Path(report["benchmark_file"]).relative_to(REPO)),
    }
    expected = {
        "cases": 20,
        "precision": 0.9231,
        "recall": 1.0,
        "exact_label_accuracy": 0.95,
    }
    for name, expected_value in expected.items():
        actual = metrics[name]
        entries.append(
            number_entry(
                f"controlled analyzer benchmark {name}",
                expected_value,
                actual,
                status_for_match(expected_value, actual, STATUS_CODE),
                metrics["source"],
            )
        )
    entries.extend(
        [
            number_entry("controlled analyzer benchmark TP", 12, tp, status_for_match(12, tp, STATUS_CODE), metrics["source"]),
            number_entry("controlled analyzer benchmark FP", 1, fp, status_for_match(1, fp, STATUS_CODE), metrics["source"]),
            number_entry("controlled analyzer benchmark TN", 7, tn, status_for_match(7, tn, STATUS_CODE), metrics["source"]),
            number_entry("controlled analyzer benchmark FN", 0, fn, status_for_match(0, fn, STATUS_CODE), metrics["source"]),
        ]
    )
    return metrics


def write_gaps(gaps: list[str]) -> None:
    if not gaps:
        return
    lines = ["# Reproducibility Gaps", ""]
    for gap in gaps:
        lines.append(f"- {gap}")
    GAPS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def collect_pypi(entries: list[dict], gaps: list[str]) -> dict:
    summary_path = REPO / "results_static" / "pypi_static_benchmark.csv"
    findings_path = REPO / "results_static" / "pypi_static_benchmark_findings.csv"
    if not summary_path.exists() or not findings_path.exists():
        gaps.append(
            "PyPI reviewed finding labels are missing; expected results_static/pypi_static_benchmark.csv "
            "and results_static/pypi_static_benchmark_findings.csv."
        )
        write_gaps(gaps)
        return {"status": STATUS_NO_DATA, "source": "results_static/"}

    package_rows = read_csv(summary_path)
    findings = read_csv(findings_path)
    analyzed = [row for row in package_rows if row.get("status") == "analyzed"]
    packages = len(analyzed)
    files = sum(int(row["files_scanned"]) for row in analyzed)
    classes = sum(int(row["classes_scanned"]) for row in analyzed)
    functions = sum(int(row["functions_scanned"]) for row in analyzed)

    review_counts = Counter(row.get("manual_review", "") for row in findings)
    likely_tp = review_counts["likely true positive"]
    likely_fp = review_counts["likely false positive"]
    reviewed = likely_tp + likely_fp + review_counts["unclear"]
    precision = round(likely_tp / (likely_tp + likely_fp), 4) if likely_tp + likely_fp else None

    PYPI_REVIEWED_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PYPI_REVIEWED_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "package",
            "file",
            "class",
            "analyzer_label",
            "manual_review_label",
            "reason",
            "reviewer_note",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in findings:
            writer.writerow(
                {
                    "package": row.get("package", ""),
                    "file": row.get("file_path", ""),
                    "class": row.get("name", ""),
                    "analyzer_label": row.get("analyzer_label", ""),
                    "manual_review_label": row.get("manual_review", ""),
                    "reason": row.get("detected_mechanisms") or row.get("short_reason", ""),
                    "reviewer_note": row.get("manual_review_note", ""),
                }
            )

    expected_values = {
        "PyPI packages": (73, packages),
        "PyPI files": (1858, files),
        "PyPI classes": (4437, classes),
        "PyPI functions": (21530, functions),
        "reviewed MEDIUM/HIGH findings": (278, reviewed),
        "likely true positives": (203, likely_tp),
        "likely false positives": (75, likely_fp),
        "reviewed PyPI precision": (0.7302, precision),
    }
    for name, (expected, actual) in expected_values.items():
        entries.append(
            number_entry(
                name,
                expected,
                actual,
                status_for_match(expected, actual, STATUS_EXISTING),
                "results_static/pypi_static_benchmark_findings.csv",
            )
        )

    return {
        "status": STATUS_EXISTING,
        "summary_source": str(summary_path.relative_to(REPO)),
        "findings_source": str(findings_path.relative_to(REPO)),
        "reviewed_findings_csv": str(PYPI_REVIEWED_CSV.relative_to(REPO)),
        "packages": packages,
        "files": files,
        "classes": classes,
        "functions": functions,
        "reviewed_MEDIUM_HIGH_findings": reviewed,
        "likely_true_positives": likely_tp,
        "likely_false_positives": likely_fp,
        "reviewed_precision": precision,
    }


def write_markdown(summary: dict) -> None:
    lines = [
        "# Paper Results Tables",
        "",
        "## Number Reproduction Status",
        "",
        "| Claim | Expected | Actual | Status | Source |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for entry in summary["paper_numbers"]:
        lines.append(
            f"| {entry['name']} | {entry['expected']} | {entry['actual']} | "
            f"{entry['status']} | `{entry['source']}` |"
        )

    for table_name, table in summary["tables"].items():
        lines.extend(["", f"## {table_name.replace('_', ' ').title()}", ""])
        lines.append(f"Status: {table['status']}. Source: `{table.get('source', '')}`.")
        rows = table.get("rows", [])
        if not rows:
            lines.append("")
            lines.append("No rows available.")
            continue
        fields = [field for field in rows[0].keys() if field != "status"]
        lines.append("")
        lines.append("| " + " | ".join(fields + ["status"]) + " |")
        lines.append("| " + " | ".join(["---"] * (len(fields) + 1)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields + ["status"]) + " |")

    lines.extend(
        [
            "",
            "## Boundary Notes",
            "",
            "- The analyzer metrics are reproduced from code on the controlled benchmark.",
            "- The PyPI precision is reproduced from existing reviewed labels, not from a production-prevalence claim.",
            "- Exhaustive enumeration is a bounded computational check over the stated 112 configurations.",
        ]
    )
    TABLES_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate() -> dict:
    entries: list[dict] = []
    gaps: list[str] = []
    tables = {
        "observation_count_sweep": collect_table(
            REPO / "results" / "A1.csv",
            "observation_count_sweep",
            ["config", "inspects"],
            ["std", "range", "n_valid"],
        ),
        "cap_degree_sweep": collect_table(
            REPO / "results" / "A2.csv",
            "cap_degree_sweep",
            ["config", "nonlinear"],
            ["std", "range", "log_range", "n_valid"],
        ),
        "ablation_table": collect_table(
            REPO / "results_extended" / "e3_ablation_comparison.csv",
            "ablation_table",
            ["config", "ablation"],
            ["std", "range", "std_vs_baseline", "range_vs_baseline"],
        ),
    }

    execution_count = collect_execution_count(entries)
    exhaustive = collect_exhaustive(entries)
    analyzer = collect_analyzer_benchmark(entries)
    pypi = collect_pypi(entries, gaps)

    summary = {
        "status_vocabulary": [
            STATUS_CODE,
            STATUS_EXISTING,
            STATUS_NO_SCRIPT,
            STATUS_NO_DATA,
            STATUS_MISMATCH,
        ],
        "paper_numbers": entries,
        "tables": tables,
        "exhaustive_enumeration_summary": exhaustive,
        "controlled_analyzer_benchmark": analyzer,
        "pypi_screening_metrics": pypi,
        "execution_count": execution_count,
        "gaps": gaps,
        "generated_artifacts": [
            "results/paper_results_summary.json",
            "results/paper_results_tables.md",
            "results/pypi_reviewed_findings.csv",
        ],
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary)
    write_gaps(gaps)
    return summary


def main() -> int:
    summary = generate()
    reproduced = [entry for entry in summary["paper_numbers"] if entry["status"] in {STATUS_CODE, STATUS_EXISTING}]
    mismatches = [entry for entry in summary["paper_numbers"] if entry["status"] == STATUS_MISMATCH]
    missing = [
        entry for entry in summary["paper_numbers"]
        if entry["status"] in {STATUS_NO_SCRIPT, STATUS_NO_DATA}
    ]
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {TABLES_MD}")
    print(f"wrote {PYPI_REVIEWED_CSV}")
    print(f"reproduced numbers: {len(reproduced)}")
    print(f"mismatches: {len(mismatches)}")
    print(f"missing: {len(missing)}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
