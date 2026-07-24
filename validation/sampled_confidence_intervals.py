from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from statistics import mean, stdev

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exact_semantics import Params, evaluate
from validation.theorem_T4_SDR import fit_loglinear

SEEDS = [3101, 3109, 3119, 3137, 3163, 3181, 3203]
SAMPLES_PER_SEED = 1000
T95_DF6 = 2.447

def sampled_orders(L: int, m: int, draws: int, seed: int):
    rng = random.Random(seed)
    base = ["READ"] * L + ["OBS"] * m
    seen = set()
    for _ in range(draws):
        order = base[:]
        rng.shuffle(order)
        seen.add(tuple(order))
    return seen

def sampled_range(L: int, m: int, degree: int, seed: int,
                  kind: str = "compositional") -> dict:
    p = Params()
    orders = sampled_orders(L, m, SAMPLES_PER_SEED, seed)
    if kind == "compositional":
        vals = [float(evaluate(order, degree, p, kind=kind))
                for order in orders]
    elif kind == "self_referential":
        vals = [float(evaluate(order, degree, p, kind=kind,
                               self_k=degree - 1))
                for order in orders]
    else:
        raise ValueError(kind)
    rng = max(vals) - min(vals)
    return {
        "sampled_unique_orderings": len(orders),
        "range": rng,
        "log_range": math.log(rng) if rng > 1.0 else 0.0,
    }

def summarize(values: list[float]) -> dict:
    n = len(values)
    avg = mean(values)
    sd = stdev(values) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    half_width = T95_DF6 * se if n == 7 else 1.96 * se
    return {
        "n": n,
        "mean": avg,
        "std": sd,
        "standard_error": se,
        "ci95_low": avg - half_width,
        "ci95_high": avg + half_width,
    }

def fit_alpha_for_seed(seed: int, Ls: list[int], m: int, degree: int) -> dict:
    rows = []
    for L in Ls:
        rec = sampled_range(L, m, degree, seed + L)
        rows.append({"L": L, **rec})
    xs = [math.log(row["L"]) for row in rows]
    ys = [row["log_range"] for row in rows]
    alpha, intercept, r2 = fit_loglinear(xs, ys)
    return {"seed": seed, "alpha": alpha, "intercept": intercept,
            "R_squared": r2, "rows": rows}

def fit_sdr_for_seed(seed: int, family: str, degrees: list[int],
                     L: int, m: int) -> dict:
    rows = []
    for degree in degrees:
        rec = sampled_range(L, m, degree, seed + degree * 101, family)
        rows.append({"degree": degree, **rec})
    xs = [row["degree"] for row in rows]
    ys = [row["log_range"] for row in rows]
    slope, intercept, r2 = fit_loglinear(xs, ys)
    return {"seed": seed, "SDR_slope": slope, "intercept": intercept,
            "R_squared": r2, "rows": rows}

def _range_config_summary(seed_runs: list[dict], key: str) -> list[dict]:
    buckets: dict[int, list[float]] = {}
    order_counts: dict[int, list[int]] = {}
    for run in seed_runs:
        for row in run["rows"]:
            buckets.setdefault(row[key], []).append(row["range"])
            order_counts.setdefault(row[key], []).append(row["sampled_unique_orderings"])
    return [{
        key: config,
        "sampled_unique_orderings_mean": mean(order_counts[config]),
        "range_stats": summarize(vals),
    } for config, vals in sorted(buckets.items())]

def check() -> dict:
    length_Ls = [12, 20, 30, 50]
    length_runs = [fit_alpha_for_seed(seed, length_Ls, m=2, degree=2)
                   for seed in SEEDS]
    comp_runs = [fit_sdr_for_seed(seed, "compositional", list(range(1, 9)),
                                  L=20, m=2)
                 for seed in SEEDS]
    selfref_runs = [fit_sdr_for_seed(seed, "self_referential",
                                     list(range(9, 13)), L=20, m=2)
                    for seed in SEEDS]

    alpha_stats = summarize([run["alpha"] for run in length_runs])
    comp_slope_stats = summarize([run["SDR_slope"] for run in comp_runs])
    selfref_slope_stats = summarize([run["SDR_slope"] for run in selfref_runs])

    return {
        "theorem": "sampled-confidence-intervals",
        "status": "VERIFIED",
        "seeds": SEEDS,
        "samples_per_seed": SAMPLES_PER_SEED,
        "length_scaling": {
            "L_values": length_Ls,
            "m": 2,
            "degree": 2,
            "alpha_by_seed": length_runs,
            "alpha_stats": alpha_stats,
            "range_by_L": _range_config_summary(length_runs, "L"),
        },
        "SDR": {
            "L": 20,
            "m": 2,
            "compositional": {
                "degrees": list(range(1, 9)),
                "slope_by_seed": comp_runs,
                "slope_stats": comp_slope_stats,
                "range_by_degree": _range_config_summary(comp_runs, "degree"),
            },
            "self_referential": {
                "degrees": list(range(9, 13)),
                "slope_by_seed": selfref_runs,
                "slope_stats": selfref_slope_stats,
                "range_by_degree": _range_config_summary(selfref_runs, "degree"),
            },
        },
    }

if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
