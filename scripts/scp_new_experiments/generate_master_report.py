from __future__ import annotations

import csv
import json
from pathlib import Path

from common import GAPS_PATH, RESULTS_DIR

REPORT_PATH = RESULTS_DIR / "scp_new_experiments_master_report.md"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def count_rows(path: Path) -> int:
    return len(read_csv(path))


def compute_new_total_executions() -> int:
    expanded = read_json(RESULTS_DIR / "expanded_mechanism_sweep_summary.json")
    total = int(expanded.get("total_executions", 0))

    exhaustive_rows = read_csv(RESULTS_DIR / "extended_exhaustive_enumeration.csv")
    for row in exhaustive_rows:
        if row.get("exhaustive_feasible") == "True":
            total += int(row.get("unique_permutations", 0))
        total += int(row.get("sampled_permutations", 0))

    sampling_rows = read_csv(RESULTS_DIR / "sampling_convergence.csv")
    total += sum(int(row.get("sampled_permutations", 0)) for row in sampling_rows)
    return total


def generate() -> dict:
    expanded = read_json(RESULTS_DIR / "expanded_mechanism_sweep_summary.json")
    exhaustive = read_json(RESULTS_DIR / "extended_exhaustive_enumeration_summary.json")
    convergence = read_json(RESULTS_DIR / "sampling_convergence_summary.json")
    benchmark = read_json(RESULTS_DIR / "extended_controlled_benchmark_summary.json")
    pypi = read_json(RESULTS_DIR / "pypi_expanded_screen_summary.json")
    case_report_exists = (RESULTS_DIR / "case_study_report.md").exists()
    gaps_text = GAPS_PATH.read_text(encoding="utf-8") if GAPS_PATH.exists() else ""
    new_total_executions = compute_new_total_executions()
    review_queue_size = count_rows(RESULTS_DIR / "pypi_expanded_manual_review_queue.csv")

    lines = [
        "# SCP New Experiments Master Report",
        "",
        "## 1. What New Experiments Were Run",
        "",
        "- Expanded exact-rational mechanism sweep.",
        "- Extended exhaustive enumeration.",
        "- Sampling convergence study.",
        "- Expanded controlled Python analyzer benchmark.",
        "- Expanded PyPI static screen, subject to package availability.",
        "- Manual review queue generation for expanded PyPI results.",
        "- Case-study report generation.",
        "",
        "## 2. New Total Executions",
        "",
        f"- New evaluated order executions across generated experiment artifacts: {new_total_executions}",
        "",
        "## 3. New Sweep Ranges",
        "",
        f"- Body lengths: {expanded.get('body_lengths', [])}",
        f"- Observation counts: {expanded.get('observation_counts', [])}",
        f"- Cap degrees: {expanded.get('cap_degrees', [])}",
        f"- Drift schedules: {expanded.get('drift_schedules', [])}",
        f"- Total mechanism-sweep configurations: {expanded.get('total_configurations_run', 'missing')}",
        f"- Mechanism-sweep executions: {expanded.get('total_executions', 'missing')}",
        "",
        "## 4. New Exhaustive Enumeration Coverage",
        "",
        f"- Total configurations: {exhaustive.get('total_configurations', 'missing')}",
        f"- Exhaustive feasible configurations: {exhaustive.get('exhaustive_feasible_configurations', 'missing')}",
        f"- Extended beyond original 112 scope: {exhaustive.get('extended_beyond_original_configurations', 'missing')}",
        f"- Sample-vs-exact range mismatches when exact is known: {exhaustive.get('sample_range_mismatches_when_exact_known', 'missing')}",
        "",
        "## 5. Sampling Convergence Findings",
        "",
    ]
    for row in convergence.get("budget_summary", []):
        lines.append(
            f"- Budget {row['budget']}: match rate {row['exact_extrema_match_rate']}, "
            f"average relative error {row['average_relative_error']}, max relative error {row['max_relative_error']}"
        )
    if not convergence.get("budget_summary"):
        lines.append("- Missing sampling convergence summary.")

    lines.extend(
        [
            "",
            "## 6. Extended Controlled Benchmark Performance",
            "",
            f"- Cases: {benchmark.get('cases', 'missing')}",
            f"- New cases added: {benchmark.get('new_cases_added', 'missing')}",
            f"- TP/FP/TN/FN: {benchmark.get('TP', 'missing')}/{benchmark.get('FP', 'missing')}/{benchmark.get('TN', 'missing')}/{benchmark.get('FN', 'missing')}",
            f"- Precision: {benchmark.get('precision', 'missing')}",
            f"- Recall: {benchmark.get('recall', 'missing')}",
            f"- Specificity: {benchmark.get('specificity', 'missing')}",
            f"- F1: {benchmark.get('F1', 'missing')}",
            f"- Exact-label accuracy: {benchmark.get('exact_label_accuracy', 'missing')}",
            "",
            "## 7. Expanded PyPI Screen Size and Label Counts",
            "",
            f"- Target packages: {pypi.get('target_packages', 'missing')}",
            f"- Packages analyzed: {pypi.get('packages_analyzed', 'missing')}",
            f"- Target met: {pypi.get('target_met', 'missing')}",
            f"- Files/classes/functions: {pypi.get('files_scanned', 'missing')}/{pypi.get('classes_scanned', 'missing')}/{pypi.get('functions_scanned', 'missing')}",
            f"- SAFE/LOW/MEDIUM/HIGH: {pypi.get('SAFE', 'missing')}/{pypi.get('LOW', 'missing')}/{pypi.get('MEDIUM', 'missing')}/{pypi.get('HIGH', 'missing')}",
            "",
            "## 8. Manual Review Queue Size",
            "",
            f"- Review queue rows: {review_queue_size}",
            "- Manual labels are intentionally blank.",
            "",
            "## 9. Case Studies Generated",
            "",
            f"- Case-study report generated: {case_report_exists}",
            "- Output: `results/scp_new_experiments/case_study_report.md`",
            "",
            "## 10. Counterexamples Found",
            "",
            f"- Zero-observation counterexamples: {len(expanded.get('zero_observation_counterexamples', []))}",
            f"- Nonlinear cap counterexamples over positive-observation configs: {len(expanded.get('nonlinear_cap_counterexamples', []))}",
            f"- Sampling max-budget extrema failures: {len(convergence.get('max_budget_extrema_failures', []))}",
            "",
            "## 11. Failed or Blocked Experiments",
            "",
        ]
    )
    if gaps_text.strip():
        lines.append(gaps_text.strip())
    else:
        lines.append("None recorded.")

    lines.extend(
        [
            "",
            "## 12. New Results Ready for the Manuscript",
            "",
            "- Expanded exact-rational mechanism sweep, with exact/sampled status per configuration.",
            "- Extended exhaustive enumeration coverage.",
            "- Sampling convergence tables.",
            "- Extended controlled benchmark metrics, including false positives and specificity.",
            "- Controlled case studies and benign near-misses.",
            "",
            "## 13. Results Requiring Manual Review Before Inclusion",
            "",
            "- Expanded PyPI precision/recall-style claims require manual review of `pypi_expanded_manual_review_queue.csv`.",
            "- PyPI flagged case studies are presentation candidates only until reviewed.",
            "- LOW/SAFE queue rows can support a limited false-negative estimate only after manual labeling.",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "report": "results/scp_new_experiments/scp_new_experiments_master_report.md",
        "new_total_executions": new_total_executions,
        "manual_review_queue_size": review_queue_size,
        "gaps_present": bool(gaps_text.strip()),
    }


def main() -> int:
    summary = generate()
    print(f"wrote {REPORT_PATH}")
    print(f"new_total_executions={summary['new_total_executions']}")
    print(f"manual_review_queue_size={summary['manual_review_queue_size']}")
    print(f"gaps_present={summary['gaps_present']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
