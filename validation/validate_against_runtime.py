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


# Hiesenoether interpreter (the actual runtime that produced summary.csv).
try:
    import io
    from contextlib import redirect_stdout
    from src.parser import parse as hn_parse
    from src.runtime import Runtime
    HIESENOETHER_INTERPRETER_AVAILABLE = True
except ImportError:
    HIESENOETHER_INTERPRETER_AVAILABLE = False


TEMPLATE = """\
energy[100]

x <- 10
y <- 0

{BODY}

print y
"""

NONLINEAR_LINE = {
    1: None,
    2: "y <- y * x",
    3: "y <- y * x * x",
    4: "y <- y * y * x",
}


def _perm_to_hn_body(perm: tuple, degree: int) -> str:
    """Translate an OSDS permutation into the Hiesenoether program body
    used by run_experiments.py: READ becomes 'y <- y + x',
    OBS becomes 'inspect x'. The nonlinear cap line is appended last
    (matching run_experiments.py's build_body, which appends after
    shuffle so the cap is never interleaved)."""
    lines = []
    for op in perm:
        if op == "READ":
            lines.append("y <- y + x")
        elif op == "OBS":
            lines.append("inspect x")
        else:
            raise ValueError(op)
    nl = NONLINEAR_LINE[degree]
    if nl is not None:
        lines.append(nl)
    return "\n".join(lines)


def run_hiesenoether(perm: tuple, degree: int) -> float:
    """Execute a permutation by running the actual Hiesenoether
    interpreter (src.runtime). Returns the float printed by `print y`.

    This is the function that should agree with the exact Fraction
    emulator in exact_semantics_runtime.py and with summary.csv."""
    if not HIESENOETHER_INTERPRETER_AVAILABLE:
        raise RuntimeError("Hiesenoether interpreter not importable; "
                           "run from repo root with src/ on path")
    body = _perm_to_hn_body(perm, degree)
    program = TEMPLATE.format(BODY=body)
    ast = hn_parse(program)
    rt = Runtime()
    buf = io.StringIO()
    with redirect_stdout(buf):
        rt.run(ast)
    out_lines = [ln for ln in buf.getvalue().strip().split("\n") if ln]
    # Last non-empty line is the print y output (some inspects also print).
    for ln in reversed(out_lines):
        try:
            return float(ln)
        except ValueError:
            continue
    raise RuntimeError(f"no numeric output from interpreter for perm={perm}, d={degree}")


def cross_check(L: int = 3, m: int = 1, degree: int = 2,
                tol: float = 1e-9) -> dict:
    """Cross-check the exact Fraction emulator against the actual
    Hiesenoether interpreter on the same permutation+template that
    summary.csv was generated from.

    Agreement here means: the exact Fraction emulator in
    exact_semantics_runtime.py is a faithful symbolic model of
    src/runtime.py. Combined with check_against_summary_csv, this
    closes the loop: emulator <-> interpreter <-> summary.csv all
    agree to machine precision.
    """
    from validation.exact_semantics_runtime import run_program as rt_exact
    body = ("READ",) * L + ("OBS",) * m
    rows = []
    max_diff = 0.0
    if not HIESENOETHER_INTERPRETER_AVAILABLE:
        return {"status": "SKIPPED",
                "reason": "Hiesenoether interpreter not importable"}
    for perm in sorted(set(permutations(body))):
        exact_v = float(rt_exact(perm, degree))
        actual_v = run_hiesenoether(perm, degree)
        diff = abs(exact_v - actual_v)
        max_diff = max(max_diff, diff)
        rows.append({"perm": "|".join(perm),
                     "emulator_exact_fraction": exact_v,
                     "interpreter_float":       actual_v,
                     "abs_diff":                diff})
    return {"L": L, "m": m, "degree": degree,
            "max_abs_diff": max_diff,
            "agreement": max_diff < tol,
            "rows": rows,
            "note": "exact_semantics_runtime.py vs src/runtime.py on "
                    "the run_experiments.py program template. Must "
                    "agree to machine precision."}


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