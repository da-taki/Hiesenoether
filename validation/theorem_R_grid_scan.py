from __future__ import annotations
import json
import sys
from fractions import Fraction
from itertools import permutations
from pathlib import Path

from validation.exact_semantics import evaluate as osds_eval, Params
from validation.exact_semantics_runtime import run_program as rt_eval


def divergence_osds(L: int, m: int, d: int,
                    kind: str, self_k: int) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    p = Params()
    vals = [osds_eval(perm, d, p, kind=kind, self_k=self_k)
            for perm in set(permutations(body))]
    return max(vals) - min(vals)


def divergence_runtime(L: int, m: int, d: int) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    vals = [rt_eval(perm, d) for perm in set(permutations(body))]
    return max(vals) - min(vals)


def kind_for(d: int):
    # Match the Hiesenoether NONLINEAR_LINE mapping:
    #   d=1 -> no cap, d=2 -> y*x, d=3 -> y*x*x  (all compositional)
    #   d=4 -> y*y*x  (self-referential with k=2)
    if d == 4:
        return "self_referential", 2
    return "compositional", 0


def grid(L_range, m_range, d_range):
    out = []
    for d in d_range:
        kind, self_k = kind_for(d)
        for L in L_range:
            for m in m_range:
                try:
                    d_osds = divergence_osds(L, m, d, kind, self_k)
                    d_rt   = divergence_runtime(L, m, d)
                except Exception as e:
                    out.append({"L": L, "m": m, "d": d, "error": str(e)})
                    continue
                ratio = (d_osds / d_rt) if d_rt != 0 else None
                out.append({
                    "L": L, "m": m, "d": d, "kind": kind,
                    "Delta_OSDS":    f"{d_osds.numerator}/{d_osds.denominator}",
                    "Delta_runtime": f"{d_rt.numerator}/{d_rt.denominator}",
                    "ratio_exact": (None if ratio is None
                                    else f"{ratio.numerator}/{ratio.denominator}"),
                    "ratio_float": (None if ratio is None else float(ratio)),
                })
    return out


def check() -> dict:
    # Keep ranges small. L! grows fast and L=8 with m=3 is 11! permutations.
    return {"d2_compositional": grid(L_range=range(2, 7),
                                     m_range=range(0, 6),
                                     d_range=[2]),
            "d_sweep_at_L6_m1": grid(L_range=[6],
                                     m_range=[1],
                                     d_range=[1, 2, 3, 4]),
            "L_sweep_at_m1_d2": grid(L_range=range(2, 9),
                                     m_range=[1],
                                     d_range=[2]),
            "m_sweep_at_L6_d2": grid(L_range=[6],
                                     m_range=range(0, 6),
                                     d_range=[2])}


if __name__ == "__main__":
    out = check()
    print(json.dumps(out, indent=2))