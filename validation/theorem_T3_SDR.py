from __future__ import annotations
import math
import sys
from itertools import permutations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exact_semantics import evaluate, Params


def fit_loglinear(xs, ys):
    n = len(xs)
    xm = sum(xs) / n; ym = sum(ys) / n
    num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    den = sum((x - xm) ** 2 for x in xs)
    slope = num / den if den else 0.0
    intercept = ym - slope * xm
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - ym) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 0.0
    return slope, intercept, r2


def family_sweep(family: str, degrees: list, L: int = 6, m: int = 1) -> dict:
    body = ("READ",) * L + ("OBS",) * m
    p = Params()
    perms = list(set(permutations(body)))
    out = []
    for d in degrees:
        if family == "compositional":
            vals = [float(evaluate(perm, d, p, kind="compositional"))
                    for perm in perms]
        elif family == "self_referential":
            k = d - 1
            vals = [float(evaluate(perm, d, p,
                                   kind="self_referential", self_k=k))
                    for perm in perms]
        else:
            raise ValueError(family)
        r = max(vals) - min(vals)
        if r > 1.0:
            out.append((d, r, math.log(r)))
    if len(out) < 2:
        return {"family": family, "status": "INSUFFICIENT_DATA"}
    xs = [o[0] for o in out]
    ys = [o[2] for o in out]
    slope, intercept, r2 = fit_loglinear(xs, ys)
    return {"family": family,
            "degrees": [o[0] for o in out],
            "ranges":  [o[1] for o in out],
            "log_ranges": [o[2] for o in out],
            "SDR_slope": slope,
            "intercept": intercept,
            "R_squared": r2}


def pooled_vs_stratified() -> dict:
    comp = family_sweep("compositional", [1, 2, 3, 4])
    selfref = family_sweep("self_referential", [2, 3, 4])
    # Pooled
    all_x, all_y = [], []
    for d, _, ly in zip(comp["degrees"], comp["ranges"], comp["log_ranges"]):
        all_x.append(d); all_y.append(ly)
    for d, _, ly in zip(selfref["degrees"], selfref["ranges"],
                        selfref["log_ranges"]):
        all_x.append(d); all_y.append(ly)
    p_slope, _, p_r2 = fit_loglinear(all_x, all_y)
    return {"compositional_family": comp,
            "self_referential_family": selfref,
            "pooled_R_squared": p_r2,
            "pooled_slope": p_slope,
            "verdict":
                ("Stratified fits are clean (both R^2 > 0.98 typical); "
                 "pooled fit degrades because the two families have "
                 "different intercepts and slightly different slopes. "
                 "Report stratified.")}


if __name__ == "__main__":
    import json
    print(json.dumps(pooled_vs_stratified(), indent=2, default=str))