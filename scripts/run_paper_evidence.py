from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


COMMANDS = [
    ("running example", [sys.executable, "examples/running_example.py"]),
    (
        "paper evidence tests",
        [sys.executable, "-m", "pytest", "-q", "tests/test_running_example.py", "tests/paper_evidence"],
    ),
    ("exhaustive enumeration report", [sys.executable, "scripts/generate_exhaustive_enumeration_report.py"]),
    ("paper results report", [sys.executable, "scripts/generate_paper_results_report.py"]),
]


def parse_pytest_counts(output: str) -> tuple[int, int]:
    passed = sum(int(value) for value in re.findall(r"(\d+) passed", output))
    failed = sum(int(value) for value in re.findall(r"(\d+) failed", output))
    return passed, failed


def run_command(label: str, command: list[str]) -> dict:
    print(f"[run] {label}")
    proc = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if output:
        print(output)
    status = "PASS" if proc.returncode == 0 else "FAIL"
    print(f"[{status}] {label}")
    return {
        "label": label,
        "command": command,
        "returncode": proc.returncode,
        "output": output,
    }


def artifact_status() -> list[str]:
    candidates = [
        "results/running_example.json",
        "results/paper_evidence/fixed_order_determinism.json",
        "results/paper_evidence/identity_observation_zero_divergence.json",
        "results/paper_evidence/access_insensitive_reads_zero_divergence.json",
        "results/paper_evidence/composition_amplification.json",
        "results/paper_evidence/bounded_computational_claims.json",
        "results/exhaustive_enumeration_report.csv",
        "results/exhaustive_enumeration_summary.json",
        "results/paper_results_summary.json",
        "results/paper_results_tables.md",
        "results/pypi_reviewed_findings.csv",
    ]
    return [path for path in candidates if (REPO / path).exists()]


def paper_number_status() -> tuple[list[str], list[str]]:
    path = REPO / "results" / "paper_results_summary.json"
    if not path.exists():
        return [], ["results/paper_results_summary.json missing"]
    data = json.loads(path.read_text(encoding="utf-8"))
    reproduced = [
        entry["name"]
        for entry in data.get("paper_numbers", [])
        if entry.get("status") in {"reproduced_from_code", "reproduced_from_existing_results"}
    ]
    missing = [
        f"{entry['name']} ({entry['status']})"
        for entry in data.get("paper_numbers", [])
        if entry.get("status") in {"missing_reproduction_script", "missing_raw_data", "mismatch"}
    ]
    missing.extend(data.get("gaps", []))
    return reproduced, missing


def main() -> int:
    results = [run_command(label, command) for label, command in COMMANDS]
    pytest_outputs = "\n".join(result["output"] for result in results if result["label"] == "paper evidence tests")
    passed, failed = parse_pytest_counts(pytest_outputs)
    generated = artifact_status()
    reproduced, missing = paper_number_status()
    failed_commands = [result for result in results if result["returncode"] != 0]

    print()
    print("Final paper-evidence summary")
    print(f"- passed tests: {passed}")
    print(f"- failed tests: {failed}")
    print(f"- failed commands: {len(failed_commands)}")
    print("- generated artifacts:")
    for artifact in generated:
        print(f"  - {artifact}")
    print("- reproduced paper numbers:")
    for name in reproduced:
        print(f"  - {name}")
    print("- missing reproducibility gaps:")
    if missing:
        for name in missing:
            print(f"  - {name}")
    else:
        print("  - none")

    return 1 if failed or failed_commands or missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
