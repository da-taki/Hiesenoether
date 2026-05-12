from __future__ import annotations
import csv
import math
import sys
from fractions import Fraction
from itertools import permutations
from pathlib import Path
print("module loaded")
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exact_semantics import evaluate, Params
from real_world_validation.core.unstable_object import UnstableObject


def run_runtime(perm: tuple, degree: int) -> float:
    x = UnstableObject(base=10.0)
    y = 0.0
    for op in perm:
        if op == "READ":
            y += x.read()
        elif op == "OBS":
            x.observe()
    if degree == 1:
        return y
    out = y
    for _ in range(degree - 1):
        out *= x.read()
    return out


def cross_check(L: int = 3, m: int = 1, degree: int = 2,
                tol: float = 1e-9) -> dict:
    """Cross-check the Hiesenoether RUNTIME against the
    HIESENOETHER-RUNTIME exact Fraction semantics (not the OSDS calculus).
    The OSDS calculus is checked separately by check_against_summary_csv.
    """
    from validation.exact_semantics_runtime import run_program as rt_exact
    body = ("READ",) * L + ("OBS",) * m
    rows = []
    max_diff = 0.0
    for perm in sorted(set(permutations(body))):
        exact_runtime = float(rt_exact(perm, degree))
        runtime_float = run_runtime(perm, degree)
        diff = abs(exact_runtime - runtime_float)
        max_diff = max(max_diff, diff)
        rows.append({"perm": "|".join(perm),
                     "runtime_exact_fraction": exact_runtime,
                     "runtime_float":          runtime_float,
                     "abs_diff":               diff})
    return {"L": L, "m": m, "degree": degree,
            "max_abs_diff": max_diff,
            "agreement": max_diff < tol,
            "rows": rows,
            "note": "Cross-checks the floating-point runtime against an "
                    "EXACT Fraction emulation of that same runtime. "
                    "Confirms the runtime has no numerical bug. "
                    "OSDS-vs-runtime calculus gap is a separate check."}


def check_against_summary_csv() -> dict:
    """Compare summary.csv 'range' against TWO exact semantics:

      (a) OSDS abstract calculus     (validation.exact_semantics)
      (b) Hiesenoether runtime calculus (validation.exact_semantics_runtime)

    The runtime calculus must agree with summary.csv to floating-point
    precision. The OSDS calculus is expected to differ systematically;
    we report the ratio for paper Table N.
    """
    from validation.exact_semantics_runtime import divergence_runtime
    csv_path = REPO / "results" / "summary.csv"
    if not csv_path.exists():
        return {"status": "SKIPPED", "reason": f"{csv_path} not present"}
    p = Params()
    matches = []
    deg_map = {"linear": 1, "quadratic": 2, "cubic": 3, "extreme": 4}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            try:
                L = int(row["add_steps"]); m = int(row["inspects"])
                nonl = row["nonlinear"]
                if nonl not in deg_map: continue
                d = deg_map[nonl]
                if L < 1 or m < 0 or L > 6 or m > 5:
                    continue
                body = ("READ",) * L + ("OBS",) * m
                # OSDS abstract
                vals_osds = [float(evaluate(perm, d, p))
                             for perm in set(permutations(body))]
                osds_range = max(vals_osds) - min(vals_osds)
                # Hiesenoether runtime exact
                rt_range = float(divergence_runtime(body, d))
                csv_range = float(row["range"])
                rt_rel  = (abs(rt_range  - csv_range) / csv_range
                           if csv_range else 0.0)
                ratio_osds_over_rt = (osds_range / rt_range
                                      if rt_range else None)
                matches.append({"config": row["config"],
                                "L": L, "m": m, "degree": d,
                                "csv_range":   csv_range,
                                "runtime_exact_range": rt_range,
                                "osds_exact_range":    osds_range,
                                "runtime_rel_err":     rt_rel,
                                "osds_over_runtime_ratio": ratio_osds_over_rt,
                                "ok_runtime": rt_rel < 1e-6})
            except (KeyError, ValueError):
                continue
    runtime_all_ok = all(r["ok_runtime"] for r in matches)
    return {"status": "OK" if runtime_all_ok else "MISMATCH_RUNTIME",
            "comparisons": len(matches),
            "rows": matches,
            "note":
                "runtime_exact_range must equal csv_range (machine precision); "
                "osds_exact_range systematically differs because the OSDS "
                "abstract calculus and the Hiesenoether runtime are distinct "
                "calculi. The ratio osds_over_runtime_ratio is a measurable "
                "invariant of that difference."}

if __name__ == "__main__":
    import json
    print("--- runtime vs Fraction cross-check (L=3,m=1,d=2) ---")
    print(json.dumps(cross_check(L=3, m=1, degree=2), indent=2))
    print()
    print("--- exact Fraction vs results/summary.csv ---")
    print(json.dumps(check_against_summary_csv(), indent=2))