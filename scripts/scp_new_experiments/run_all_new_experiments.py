from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO / "results" / "scp_new_experiments"

COMMANDS = [
    ("expanded mechanism sweep", [sys.executable, "scripts/scp_new_experiments/run_expanded_mechanism_sweep.py"]),
    ("extended exhaustive enumeration", [sys.executable, "scripts/scp_new_experiments/run_extended_exhaustive_enumeration.py"]),
    ("sampling convergence", [sys.executable, "scripts/scp_new_experiments/run_sampling_convergence.py"]),
    ("extended controlled benchmark", [sys.executable, "scripts/scp_new_experiments/run_extended_controlled_benchmark.py"]),
    (
        "expanded PyPI screen",
        [sys.executable, "scripts/scp_new_experiments/run_pypi_expanded_screen.py", "--no-downloads", "--target", "150"],
    ),
    ("case-study report", [sys.executable, "scripts/scp_new_experiments/generate_case_study_report.py"]),
    ("master report", [sys.executable, "scripts/scp_new_experiments/generate_master_report.py"]),
]

def run_command(label: str, command: list[str]) -> dict:
    print(f"[run] {label}", flush=True)
    proc = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if output:
        print(output, flush=True)
    status = "PASS" if proc.returncode == 0 else "FAIL"
    print(f"[{status}] {label}", flush=True)
    return {
        "label": label,
        "command": command,
        "returncode": proc.returncode,
        "output": output,
    }

def read_json(name: str) -> dict:
    path = RESULTS_DIR / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def print_final_summary(results: list[dict]) -> None:
    expanded = read_json("expanded_mechanism_sweep_summary.json")
    exhaustive = read_json("extended_exhaustive_enumeration_summary.json")
    convergence = read_json("sampling_convergence_summary.json")
    benchmark = read_json("extended_controlled_benchmark_summary.json")
    pypi = read_json("pypi_expanded_screen_summary.json")
    master_path = RESULTS_DIR / "scp_new_experiments_master_report.md"

    print()
    print("Final new-experiment summary")
    print(f"- failed commands: {sum(1 for result in results if result['returncode'] != 0)}")
    print(f"- expanded sweep configurations: {expanded.get('total_configurations_run', 'missing')}")
    print(f"- expanded sweep executions: {expanded.get('total_executions', 'missing')}")
    print(f"- zero-observation all zero divergence: {expanded.get('zero_observation_all_zero_divergence', 'missing')}")
    print(f"- extended exhaustive configurations: {exhaustive.get('total_configurations', 'missing')}")
    print(f"- exhaustive feasible configurations: {exhaustive.get('exhaustive_feasible_configurations', 'missing')}")
    print(f"- sampling convergence rows: {convergence.get('rows', 'missing')}")
    print(
        "- extended benchmark precision/recall/specificity/F1: "
        f"{benchmark.get('precision', 'missing')}/"
        f"{benchmark.get('recall', 'missing')}/"
        f"{benchmark.get('specificity', 'missing')}/"
        f"{benchmark.get('F1', 'missing')}"
    )
    print(
        "- PyPI packages/classes SAFE/LOW/MEDIUM/HIGH: "
        f"{pypi.get('packages_analyzed', 'missing')}/"
        f"{pypi.get('classes_scanned', 'missing')} "
        f"{pypi.get('SAFE', 'missing')}/"
        f"{pypi.get('LOW', 'missing')}/"
        f"{pypi.get('MEDIUM', 'missing')}/"
        f"{pypi.get('HIGH', 'missing')}"
    )
    print(f"- manual review queue rows: {pypi.get('manual_review_queue_rows', 'missing')}")
    print(f"- master report: {master_path}")

def main() -> int:
    results = [run_command(label, command) for label, command in COMMANDS]
    print_final_summary(results)
    return 1 if any(result["returncode"] != 0 for result in results) else 0

if __name__ == "__main__":
    raise SystemExit(main())
