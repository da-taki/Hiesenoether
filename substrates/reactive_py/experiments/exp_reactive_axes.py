from __future__ import annotations
import csv
import math
import random
import statistics
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.observable import Observable, Computed

BASE = 10.0
NUM_RUNS = 100_000
SEED = 42

OBS_COUNTS = [0, 1, 2, 3, 4, 5]
STEP_COUNTS = [3, 6, 9, 12, 15, 20]
NONLINEARITIES = ["linear", "quadratic", "cubic", "extreme"]
DEGREE_MAP = {"linear": 1, "quadratic": 2, "cubic": 3, "extreme": 4}

RAW = _ROOT / "results" / "raw"
SUMMARY = _ROOT / "results" / "summary"
RAW.mkdir(parents=True, exist_ok=True)
SUMMARY.mkdir(parents=True, exist_ok=True)

def _cap(y: float, x: Observable, nonlin: str) -> float:
    if nonlin == "linear":
        return y
    if nonlin == "quadratic":
        return y * x.get()
    if nonlin == "cubic":
        return y * x.get() * x.get()
    if nonlin == "extreme":
        return y * y * x.get()
    raise ValueError(nonlin)

def _build_ops(L: int, m: int, rng: random.Random) -> list:
    ops = ["add"] * L + ["observe"] * m
    rng.shuffle(ops)
    return ops

def _one_run(L: int, m: int, nonlin: str, rng: random.Random) -> float:
    x = Observable(BASE, name="x")

    def body():
        y = 0.0
        for op in _build_ops(L, m, rng):
            if op == "add":
                y += x.get()
            elif op == "observe":
                x.observe()
        return _cap(y, x, nonlin)

    c = Computed(body, name="output")
    return c.get()

def _stats(values: list) -> dict:
    n = len(values)
    if n < 2:
        v = values[0] if values else 0.0
        return {"mean": v, "std": 0.0, "min": v, "max": v,
                "range": 0.0, "log_range": 0.0, "cv": 0.0, "n": n}
    mean_ = statistics.mean(values)
    std_ = statistics.stdev(values)
    mn, mx = min(values), max(values)
    rng_ = mx - mn
    log_r = math.log(rng_) if rng_ > 1.0 else 0.0
    cv = std_ / abs(mean_) if mean_ != 0 else float("inf")
    return {"mean": round(mean_, 4), "std": round(std_, 4),
            "min": round(mn, 4), "max": round(mx, 4),
            "range": round(rng_, 4), "log_range": round(log_r, 6),
            "cv": round(cv, 6), "n": n}

def _write_raw(values: list, name: str) -> None:
    p = RAW / f"{name}.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["value"])
        for v in values:
            w.writerow([round(v, 6)])

def _write_summary(rows: list, name: str) -> None:
    if not rows:
        return
    p = SUMMARY / name
    fields = sorted({k for r in rows for k in r.keys()})
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def run_a1(num_runs: int = NUM_RUNS) -> list:
    rows = []
    for m in OBS_COUNTS:
        rng = random.Random(SEED ^ (m * 17))
        vals = [_one_run(6, m, "quadratic", rng) for _ in range(num_runs)]
        _write_raw(vals, f"a1_obs{m}")
        rows.append({"axis": "A1_reactive", "config": f"obs_{m}",
                     "observes": m, "steps": 6,
                     "nonlinearity": "quadratic", **_stats(vals)})
    return rows

def run_a2(num_runs: int = NUM_RUNS) -> list:
    rows = []
    for nonlin in NONLINEARITIES:
        rng = random.Random(SEED ^ DEGREE_MAP[nonlin] * 101)
        vals = [_one_run(6, 1, nonlin, rng) for _ in range(num_runs)]
        _write_raw(vals, f"a2_{nonlin}")
        rows.append({"axis": "A2_reactive", "config": nonlin,
                     "nonlinearity": nonlin, "degree": DEGREE_MAP[nonlin],
                     "steps": 6, "observes": 1, **_stats(vals)})
    return rows

def run_a3(num_runs: int = NUM_RUNS) -> list:
    rows = []
    for L in STEP_COUNTS:
        rng = random.Random(SEED ^ (L * 31))
        vals = [_one_run(L, 1, "quadratic", rng) for _ in range(num_runs)]
        _write_raw(vals, f"a3_steps{L}")
        rows.append({"axis": "A3_reactive", "config": f"steps_{L}",
                     "steps": L, "observes": 1,
                     "nonlinearity": "quadratic", **_stats(vals)})
    return rows

def fit_sle(rows: list) -> dict:
    valid = [(r["degree"], r["log_range"]) for r in rows
             if r.get("degree") and r.get("log_range", 0) > 0]
    if len(valid) < 2:
        return {"sle": None, "r_squared": None}
    xs = [v[0] for v in valid]
    ys = [v[1] for v in valid]
    n = len(xs)
    xm, ym = sum(xs) / n, sum(ys) / n
    num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    den = sum((x - xm) ** 2 for x in xs)
    slope = num / den if den else 0.0
    ss_res = sum((y - (ym + slope * (x - xm))) ** 2
                 for x, y in zip(xs, ys))
    ss_tot = sum((y - ym) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return {"sle": round(slope, 6), "r_squared": round(r2, 6)}

def run_experiment(num_runs: int = NUM_RUNS) -> dict:
    random.seed(SEED)
    a1 = run_a1(num_runs)
    a2 = run_a2(num_runs)
    a3 = run_a3(num_runs)

    sle = fit_sle(a2)
    for r in a2:
        r["sle"] = sle["sle"]
        r["r_squared"] = sle["r_squared"]

    _write_summary(a1, "a1_observation_multiplicity.csv")
    _write_summary(a2, "a2_nonlinearity_depth.csv")
    _write_summary(a3, "a3_length_scaling.csv")

    merged = []
    for src, rs in (("A1", a1), ("A2", a2), ("A3", a3)):
        for r in rs:
            merged.append({"source": src, **r})
    _write_summary(merged, "all_experiments_merged.csv")

    return {"a1": a1, "a2": a2, "a3": a3, "sle": sle}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=int, default=NUM_RUNS)
    args = p.parse_args()
    result = run_experiment(args.runs)
    print(f"[reactive_py] A1 m=0 std={result['a1'][0]['std']} (should be 0.0)")
    print(f"[reactive_py] A1 m=5 std={result['a1'][-1]['std']}")
    print(f"[reactive_py] SLE={result['sle']['sle']}  "
          f"R²={result['sle']['r_squared']}")
