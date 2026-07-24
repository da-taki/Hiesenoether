from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass

LOCAL_COMMANDS = [
    ("core validation", [sys.executable, "-m", "validation.run_all"]),
    ("toy static analyzer benchmark", [sys.executable, "-m", "analysis.oc_static_benchmark"]),
    ("extended polynomial degree evidence", [sys.executable, "-m", "validation.polynomial_degree_extended"]),
    ("rho infinity investigation", [sys.executable, "-m", "validation.rho_infinity_investigation"]),
]

PYPI_COMMAND = ("PyPI static analyzer benchmark", [sys.executable, "-m", "analysis.pypi_static_benchmark"])

@dataclass
class CommandResult:
    name: str
    command: list[str]
    returncode: int
    elapsed_seconds: float

def run_command(name: str, command: list[str]) -> CommandResult:
    print(f"[run] {name}: {' '.join(command)}", flush=True)
    started = time.time()
    proc = subprocess.run(command)
    elapsed = time.time() - started
    status = "PASS" if proc.returncode == 0 else "FAIL"
    print(f"[{status}] {name} ({elapsed:.1f}s)", flush=True)
    return CommandResult(name, command, proc.returncode, elapsed)

def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository-local replication checks.")
    parser.add_argument(
        "--include-pypi",
        action="store_true",
        help="include the network/cache-dependent PyPI static analyzer benchmark",
    )
    args = parser.parse_args()

    commands = LOCAL_COMMANDS[:]
    if args.include_pypi:
        commands.append(PYPI_COMMAND)

    results = [run_command(name, command) for name, command in commands]
    print("\nSummary")
    for result in results:
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"- {status}: {result.name} ({result.elapsed_seconds:.1f}s)")

    return 0 if all(result.returncode == 0 for result in results) else 1

if __name__ == "__main__":
    raise SystemExit(main())
