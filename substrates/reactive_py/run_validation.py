"""Reactive-substrate validation runner.

Reproduces Hiesenoether axes A1/A2/A3 in a MobX-pattern reactive
substrate (Observable + Computed + reaction). Tests whether the three
preconditions {P1, P2, P3} produce ordered chaos when re-instantiated
in a reactive-framework shape rather than the Python descriptor shape
used in real_world_validation/.

Usage:
    python -m substrates.reactive_py.run_validation              # 100k runs
    python -m substrates.reactive_py.run_validation --runs 1000  # smoke
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from substrates.reactive_py.experiments.exp_reactive_axes import (
    run_experiment, NUM_RUNS,
)


def main():
    parser = argparse.ArgumentParser(
        description="Ordered Chaos — Reactive Substrate Validation"
    )
    parser.add_argument("--runs", type=int, default=NUM_RUNS)
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 60)
    print("  Ordered Chaos — Reactive Substrate Validation")
    print(f"  Runs/config: {args.runs:,}")
    print("=" * 60)

    result = run_experiment(args.runs)

    print("\nA1 — Observation Multiplicity")
    for r in result["a1"]:
        print(f"  m={r['observes']}  std={r['std']:>12}  range={r['range']}")

    print("\nA2 — Nonlinearity Depth (SLE)")
    for r in result["a2"]:
        print(f"  {r['nonlinearity']:<10} deg={r['degree']}  "
              f"range={r['range']}  log_range={r['log_range']}")
    print(f"  SLE = {result['sle']['sle']}  R² = {result['sle']['r_squared']}")

    print("\nA3 — Length Scaling")
    for r in result["a3"]:
        print(f"  L={r['steps']:<3}  std={r['std']:>12}  range={r['range']}")

    print(f"\nTotal runtime: {time.time() - t0:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()