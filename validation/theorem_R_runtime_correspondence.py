from __future__ import annotations
from fractions import Fraction
from itertools import permutations
from typing import Tuple

from validation.exact_semantics import evaluate as osds_eval, Params
from validation.exact_semantics_runtime import run_program as rt_eval

def divergence_osds(L: int, m: int, d: int,
                    kind: str = "compositional", self_k: int = 0) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    p = Params()
    vals = [osds_eval(perm, d, p, kind=kind, self_k=self_k)
            for perm in set(permutations(body))]
    return max(vals) - min(vals)

def divergence_runtime(L: int, m: int, d: int) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    vals = [rt_eval(perm, d) for perm in set(permutations(body))]
    return max(vals) - min(vals)

def rho_empirical(L: int, m: int, d: int) -> Tuple[Fraction, Fraction, Fraction]:
    if d == 4:
        d_osds = divergence_osds(L, m, 4, kind="self_referential", self_k=2)
    else:
        d_osds = divergence_osds(L, m, d, kind="compositional", self_k=0)
    d_rt = divergence_runtime(L, m, d)
    ratio = d_osds / d_rt if d_rt != 0 else None
    return d_osds, d_rt, ratio

def rho_predicted(L: int, m: int, d: int) -> Fraction:
    d_osds, d_rt, ratio = rho_empirical(L, m, d)
    return ratio

def check() -> dict:
    cases = [
        (6, 0, 2, "compositional"),
        (6, 1, 2, "compositional"),
        (6, 2, 2, "compositional"),
        (6, 3, 2, "compositional"),
        (6, 4, 2, "compositional"),
        (6, 5, 2, "compositional"),
        (6, 1, 1, "compositional"),
        (6, 1, 3, "compositional"),
        (6, 1, 4, "self_referential_k2"),
        (3, 1, 2, "compositional"),
        (3, 0, 1, "compositional"),
    ]
    rows = []
    for (L, m, d, kind) in cases:
        d_osds, d_rt, ratio = rho_empirical(L, m, d)
        rows.append({
            "L": L, "m": m, "d": d, "kind": kind,
            "Delta_OSDS_exact":    str(d_osds),
            "Delta_runtime_exact": str(d_rt),
            "ratio_exact":         (None if ratio is None
                                    else f"{ratio.numerator}/{ratio.denominator}"),
            "ratio_float":         (None if ratio is None else float(ratio)),
        })
    return {"theorem": "R",
            "status": "EMPIRICAL_TABLE_BUILT",
            "rows": rows,
            "note":
                "Exact rational ratios rho(L, m, d) = Delta_OSDS / "
                "Delta_runtime computed for every summary.csv case. "
                "Next iteration replaces rho_predicted with a closed "
                "form proven by induction on body length."}

if __name__ == "__main__":
    import json
    r = check()
    print(json.dumps(r, indent=2))
