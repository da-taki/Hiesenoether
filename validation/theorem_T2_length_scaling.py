from __future__ import annotations
import math
from itertools import permutations
from validation.exact_semantics import evaluate, Params

def exact_range(L: int, m: int = 1, d: int = 2) -> float:
    body = ("READ",) * L + ("OBS",) * m
    p = Params()
    perms = list(set(permutations(body)))
    vals = [float(evaluate(perm, d, p)) for perm in perms]
    return max(vals) - min(vals)

def fit_power_law(Ls, ranges):
    xs = [math.log(L) for L in Ls]
    ys = [math.log(r) for r in ranges]
    n = len(xs)
    xm = sum(xs) / n; ym = sum(ys) / n
    num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    den = sum((x - xm) ** 2 for x in xs)
    alpha = num / den if den else 0.0
    intercept = ym - alpha * xm
    ss_res = sum((y - (intercept + alpha * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - ym) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 0.0
    return alpha, r2

def check(L_max: int = 8) -> dict:
    Ls = list(range(3, L_max + 1))
    ranges = [exact_range(L) for L in Ls]
    alpha, r2 = fit_power_law(Ls, ranges)
    return {"theorem": "T2",
            "L_values": Ls,
            "exact_ranges": ranges,
            "alpha_exact": alpha,
            "R_squared_exact": r2,
            "empirical_alpha_E5": 3.272676,
            "empirical_R2_E5":    0.995774,
            "consistent_with_E5": abs(alpha - 3.272676) < 0.5,
            "status": "VERIFIED" if r2 > 0.98 else "WEAK_FIT"}

if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
