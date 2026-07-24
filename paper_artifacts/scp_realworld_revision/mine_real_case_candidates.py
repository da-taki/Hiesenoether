from __future__ import annotations

import csv
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
REVIEWED = REPO / "results_static" / "pypi_static_benchmark_findings.csv"
EXPANDED = REPO / "results" / "scp_new_experiments" / "pypi_expanded_manual_review_queue.csv"
CSV_OUT = OUT / "real_case_candidates.csv"

HAND_CURATED = {
    ("httpcore", "Response"): ("high", "easy", "response.read() changes later response.content from exception to bytes"),
    ("pytest", "catching_logs"): ("high", "easy", "enter/exit changes handler level and later WARNING filtering"),
    ("PyYAML", "SafeRepresenter"): ("high", "moderate", "represent_data() alias cache returns stale node after object mutation"),
    ("rich", "RichHandler"): ("medium", "easy", "render_message() initializes keyword state"),
}

def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def mutated_state(reason: str) -> str:
    match = re.search(r"mutates self\.\{([^}]*)\}", reason)
    return match.group(1) if match else ""

def method(reason: str) -> str:
    match = re.search(r"method ([^(]+)\(\)", reason)
    return match.group(1) if match else ""

def base_row(row: dict[str, str], provenance: str) -> dict[str, object]:
    package = row.get("package", "")
    klass = row.get("name") or row.get("class", "")
    reason = row.get("short_reason", "")
    curated = HAND_CURATED.get((package, klass))
    strength, feasibility, expected = curated if curated else ("medium", "unknown", "structural state mutation may or may not affect later behavior")
    return {
        "rank": 0,
        "package": package,
        "version": row.get("version", ""),
        "file_path": row.get("file_path") or row.get("file", ""),
        "class_name": klass,
        "line_start": row.get("line", ""),
        "line_end": "",
        "read_or_observer_method": method(reason),
        "mutated_state": mutated_state(reason),
        "later_read_or_branch": expected,
        "composition_or_threshold_site": "",
        "candidate_strength": strength,
        "expected_behavior_difference": expected,
        "harness_feasibility": feasibility,
        "notes": f"source={provenance}; {row.get('manual_review_note') or row.get('suspected_pattern') or ''}",
    }

def run() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in read_csv(REVIEWED):
        if row.get("manual_review") == "likely true positive":
            rows.append(base_row(row, "reviewed_73_package_findings"))
    for row in read_csv(EXPANDED):
        key = (row.get("package", ""), row.get("class", ""))
        if key in HAND_CURATED:
            rows.append(base_row(row, "expanded_queue_available_source"))

    def sort_key(item: dict[str, object]) -> tuple[int, str, str]:
        strength_rank = {"high": 0, "medium": 1, "low": 2}.get(str(item["candidate_strength"]), 3)
        feasible_rank = {"easy": 0, "moderate": 1, "hard": 2, "unknown": 3}.get(str(item["harness_feasibility"]), 3)
        return (strength_rank * 10 + feasible_rank, str(item["package"]), str(item["class_name"]))

    rows = sorted(rows, key=sort_key)
    for idx, row in enumerate(rows, 1):
        row["rank"] = idx
    OUT.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows

def main() -> int:
    rows = run()
    print(f"wrote {CSV_OUT}")
    print(f"candidates={len(rows)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
