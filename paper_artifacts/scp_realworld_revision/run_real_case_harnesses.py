from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent
HARNESS_DIR = OUT / "real_case_harnesses"
OUTPUT_DIR = OUT / "real_case_outputs"
CSV_OUT = OUT / "real_case_results.csv"


def run() -> list[dict[str, object]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for harness in sorted(HARNESS_DIR.glob("case_*.py")):
        proc = subprocess.run([sys.executable, str(harness)], text=True, capture_output=True)
        json_path = OUTPUT_DIR / (harness.stem + ".json")
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
        else:
            data = {
                "case_id": harness.stem,
                "package": "",
                "version": "",
                "class_name": "",
                "file_path": "",
                "classification": "could_not_reproduce",
                "operation_A": "",
                "operation_B": "",
                "result_A": proc.stdout,
                "result_B": proc.stderr,
                "branch_flip": False,
                "output_diff": False,
                "state_diff": False,
                "read_or_observer_operation": "",
                "latent_state": "",
                "later_read_or_behavior": "",
                "notes": f"returncode={proc.returncode}",
            }
        rows.append(
            {
                "case_id": data.get("case_id", harness.stem),
                "package": data.get("package", ""),
                "version": data.get("version", ""),
                "class_name": data.get("class_name", ""),
                "file_path": data.get("file_path", ""),
                "reproduced": data.get("classification") not in {"could_not_reproduce", "structural_only_no_runtime_difference"},
                "classification": data.get("classification", "could_not_reproduce"),
                "operation_A": data.get("operation_A", ""),
                "result_A": json.dumps(data.get("result_A", ""), sort_keys=True),
                "operation_B": data.get("operation_B", ""),
                "result_B": json.dumps(data.get("result_B", ""), sort_keys=True),
                "branch_flip": data.get("branch_flip", False),
                "output_diff": data.get("output_diff", False),
                "state_diff": data.get("state_diff", False),
                "read_or_observer_operation": data.get("read_or_observer_operation", ""),
                "latent_state": data.get("latent_state", ""),
                "later_read_or_behavior": data.get("later_read_or_behavior", ""),
                "notes": data.get("notes", ""),
                "harness_path": str(harness),
                "json_output_path": str(json_path),
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = run()
    write_csv(rows)
    confirmed = [row for row in rows if str(row["classification"]).startswith("confirmed")]
    print(f"wrote {CSV_OUT}")
    print(f"confirmed={len(confirmed)} total={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
