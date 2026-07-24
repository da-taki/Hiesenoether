from __future__ import annotations

import csv
from pathlib import Path

from common import RESULTS_DIR

REPO = Path(__file__).resolve().parents[2]
CONTROLLED_CSV = RESULTS_DIR / "extended_controlled_benchmark.csv"
PYPI_QUEUE_CSV = RESULTS_DIR / "pypi_expanded_manual_review_queue.csv"
REPORT_PATH = RESULTS_DIR / "case_study_report.md"

def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def code_excerpt(path: Path, line: int, radius: int = 5) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    excerpt_lines = []
    for idx in range(start, end + 1):
        source_line = lines[idx - 1].rstrip()
        excerpt_lines.append(f"{idx}: {source_line}" if source_line else f"{idx}:")
    return "\n".join(excerpt_lines)

def controlled_excerpt(row: dict) -> str:
    path = REPO / row["file"]
    line = int(row["line"]) if row.get("line") else 1
    return code_excerpt(path, line)

def classify_latent_state(row: dict) -> tuple[str, str]:
    evidence = row.get("evidence", "")
    if row.get("expected") == "SAFE":
        return "none by controlled label", "none by controlled label"
    if "P2:" in evidence and "P1:" in evidence:
        return "observer-mutated fields in the class", "later access-sensitive read method/property"
    if "P1:" in evidence:
        return "reader-side counter/state mutation", "the same reader's returned value"
    if "P2:" in evidence:
        return "observer-side state mutation", "not modeled as a later read in this class"
    return "not captured in evidence text", "not captured in evidence text"

def controlled_case(row: dict, heading: str, expected_match: str) -> list[str]:
    latent, consumer = classify_latent_state(row)
    risk_text = (
        "Risky: the controlled label says this class exhibits the target OSDS-style mechanism."
        if row["expected"] != "SAFE"
        else "Benign: the controlled label says this is a near-miss rather than target OSDS behavior."
    )
    return [
        f"### {heading}: `{row['class']}`",
        "",
        f"- Source: `{row['file']}`",
        f"- Expected label: {row['expected']}",
        f"- Analyzer label: {row['observed']}",
        f"- Why analyzer flagged it: {row.get('evidence') or 'no analyzer evidence emitted'}",
        f"- Matches OSDS pattern: {expected_match}",
        f"- Latent state changes: {latent}",
        f"- Later read consumes: {consumer}",
        f"- Risk interpretation: {risk_text}",
        "",
        "```python",
        controlled_excerpt(row),
        "```",
        "",
    ]

def pypi_case(row: dict, index: int) -> list[str]:
    return [
        f"### PyPI flagged example {index}: `{row['package']}.{row['class']}`",
        "",
        f"- Package/version: {row['package']} {row['version']}",
        f"- File: `{row['file']}`",
        f"- Analyzer label: {row['analyzer_label']}",
        f"- Why analyzer flagged it: {row['short_reason'] or 'no short reason emitted'}",
        "- Matches OSDS pattern: pending manual review; no label is invented here.",
        "- Latent state changes: inferred syntactically from analyzer evidence, pending review.",
        "- Later read consumes: inferred syntactically from analyzer evidence, pending review.",
        "- Risk interpretation: review queue candidate, not a confirmed true positive.",
        "",
        "```python",
        row["code_excerpt"],
        "```",
        "",
    ]

def generate() -> dict:
    controlled = read_csv(CONTROLLED_CSV)
    pypi_queue = read_csv(PYPI_QUEUE_CSV)

    true_positive_style = [
        row for row in controlled
        if row["expected"] != "SAFE" and row["observed"] != "SAFE"
    ][:3]
    benign = [
        row for row in controlled
        if row["expected"] == "SAFE"
    ][:3]
    pypi_flagged = [
        row for row in pypi_queue
        if row.get("analyzer_label") in {"MEDIUM", "HIGH"}
    ][:3]

    lines = [
        "# Review Experiment Case Studies",
        "",
        "This report supplies concrete examples for presentation. Controlled examples use benchmark labels; PyPI examples remain pending manual review.",
        "",
        "## Controlled True-Positive Style Examples",
        "",
    ]
    for index, row in enumerate(true_positive_style, start=1):
        lines.extend(controlled_case(row, f"TP-style {index}", "yes by controlled benchmark label"))

    lines.extend(["## Controlled Benign Near-Misses", ""])
    for index, row in enumerate(benign, start=1):
        lines.extend(controlled_case(row, f"Benign {index}", "no by controlled benchmark label"))

    lines.extend(["## PyPI Flagged Examples", ""])
    if pypi_flagged:
        for index, row in enumerate(pypi_flagged, start=1):
            lines.extend(pypi_case(row, index))
    else:
        lines.append("No PyPI MEDIUM/HIGH review-queue rows were available.")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return {
        "controlled_true_positive_style_examples": len(true_positive_style),
        "controlled_benign_near_misses": len(benign),
        "pypi_flagged_examples": len(pypi_flagged),
        "report": "results/review_experiments/case_study_report.md",
    }

def main() -> int:
    summary = generate()
    print(f"wrote {REPORT_PATH}")
    print(f"controlled_true_positive_style_examples={summary['controlled_true_positive_style_examples']}")
    print(f"controlled_benign_near_misses={summary['controlled_benign_near_misses']}")
    print(f"pypi_flagged_examples={summary['pypi_flagged_examples']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
