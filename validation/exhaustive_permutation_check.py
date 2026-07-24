from __future__ import annotations

import math
import random
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exact_semantics import Params, evaluate

def unique_orders(L: int, m: int):
    n = L + m
    for obs_positions in combinations(range(n), m):
        obs_positions = set(obs_positions)
        yield tuple("OBS" if i in obs_positions else "READ" for i in range(n))

def sampled_orders(L: int, m: int, draws: int, seed: int):
    rng = random.Random(seed)
    base = ["READ"] * L + ["OBS"] * m
    seen = set()
    for _ in range(draws):
        order = base[:]
        rng.shuffle(order)
        seen.add(tuple(order))
    return seen

def _num(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def exact_row(L: int, m: int, degree: int, sample_draws: int = 10_000) -> dict:
    p = Params()
    orders = list(unique_orders(L, m))
    vals = [evaluate(order, degree, p) for order in orders]
    exact_min = min(vals)
    exact_max = max(vals)
    exact_range = exact_max - exact_min

    sampled = sampled_orders(L, m, sample_draws, seed=(L * 10_000 + m * 100 + degree))
    sampled_vals = [evaluate(order, degree, p) for order in sampled]
    sampled_min = min(sampled_vals)
    sampled_max = max(sampled_vals)
    sampled_range = sampled_max - sampled_min

    return {
        "L": L,
        "m": m,
        "degree": degree,
        "unique_orderings": math.comb(L + m, m),
        "exact_min": _num(exact_min),
        "exact_max": _num(exact_max),
        "exact_range": _num(exact_range),
        "sampled_unique_orderings": len(sampled),
        "sampled_min": _num(sampled_min),
        "sampled_max": _num(sampled_max),
        "sampled_range": _num(sampled_range),
        "sampled_range_matched_exact": sampled_min == exact_min and sampled_max == exact_max,
    }

def check(L_min: int = 2, L_max: int = 8, m_min: int = 1, m_max: int = 4,
          degree_min: int = 1, degree_max: int = 4) -> dict:
    rows = []
    mismatches = []
    for L in range(L_min, L_max + 1):
        for m in range(m_min, m_max + 1):
            for degree in range(degree_min, degree_max + 1):
                row = exact_row(L, m, degree)
                rows.append(row)
                if not row["sampled_range_matched_exact"]:
                    mismatches.append(row)

    return {
        "theorem": "P-exhaustive",
        "status": "VERIFIED" if not mismatches else "PARTIAL",
        "scope": f"{L_min}<=L<={L_max}, {m_min}<=m<={m_max}, "
                 f"{degree_min}<=degree<={degree_max}",
        "configurations_checked": len(rows),
        "all_sampled_ranges_matched_exact": not mismatches,
        "mismatches": mismatches,
        "rows": rows,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
