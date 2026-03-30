# exp_descriptor.py

import csv
import math
import random
import statistics
import sys
from pathlib import Path

# Path guard: ensures 'core' is importable when called from repo root
_RWV = Path(__file__).parent.parent
if str(_RWV) not in sys.path:
    sys.path.insert(0, str(_RWV))

from core.unstable_object import UnstableObject

RAW_DIR = Path("real_world_validation/results/raw")

try:
    import config
    NUM_RUNS = config.NUM_RUNS
    BASE_VALUE = config.BASE_VALUE
    DEFAULT_STEPS = config.DEFAULT_STEPS
    DEFAULT_OBSERVES = config.DEFAULT_OBSERVES
    OBSERVE_COUNTS = config.OBSERVE_COUNTS
    STEP_COUNTS = config.STEP_COUNTS
    NONLINEARITY_LEVELS = config.NONLINEARITY_LEVELS
    RANDOM_SEED = config.RANDOM_SEED
    RAW_DIR = config.RESULTS_RAW_DIR
except ImportError:
    NUM_RUNS = 10_000
    BASE_VALUE = 10.0
    DEFAULT_STEPS = 6
    DEFAULT_OBSERVES = 1
    OBSERVE_COUNTS = [0, 1, 2, 3, 4, 5]
    STEP_COUNTS = [3, 6, 9, 12, 15, 20]
    NONLINEARITY_LEVELS = ["linear", "quadratic", "cubic", "extreme"]
    RANDOM_SEED = 42


DEGREE_MAP = {"linear": 1, "quadratic": 2, "cubic": 3, "extreme": 4}


def _apply_cap(y: float, obj: UnstableObject, nonlinearity: str) -> float:
    if nonlinearity == "linear":
        return y
    elif nonlinearity == "quadratic":
        return y * obj.read()
    elif nonlinearity == "cubic":
        return y * obj.read() * obj.read()
    elif nonlinearity == "extreme":
        return y * y * obj.read()
    raise ValueError(f"Unknown nonlinearity: {nonlinearity}")


def build_op_sequence(add_steps: int, observe_count: int) -> list:
    ops = ["add"] * add_steps + ["observe"] * observe_count
    random.shuffle(ops)
    return ops


def run_single(ops: list, nonlinearity: str) -> float:
    obj = UnstableObject(base=BASE_VALUE)
    y = 0.0
    for op in ops:
        if op == "add":
            y += obj.read()
        elif op == "observe":
            obj.observe()
    return _apply_cap(y, obj, nonlinearity)


def run_single_cached(add_steps: int, nonlinearity: str) -> float:
    obj = UnstableObject(base=BASE_VALUE)
    cached_val = obj.read()
    y = cached_val * add_steps
    return _apply_cap(y, obj, nonlinearity)


def _compute_stats(values: list) -> dict:
    n = len(values)
    if n < 2:
        return {"mean": values[0] if values else 0.0, "std": 0.0,
                "min": values[0] if values else 0.0, "max": values[0] if values else 0.0,
                "range": 0.0, "log_range": 0.0, "cv": 0.0, "n": n}
    mean_ = statistics.mean(values)
    std_ = statistics.stdev(values)
    min_ = min(values)
    max_ = max(values)
    range_ = max_ - min_
    log_range = math.log(range_) if range_ > 1.0 else 0.0
    cv = std_ / abs(mean_) if mean_ != 0 else float("inf")
    return {
        "mean": round(mean_, 4),
        "std": round(std_, 4),
        "min": round(min_, 4),
        "max": round(max_, 4),
        "range": round(range_, 4),
        "log_range": round(log_range, 6),
        "cv": round(cv, 6),
        "n": n,
    }


def _write_raw_csv(values: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["value"])
        for v in values:
            writer.writerow([v])


def run_axis_a1_analogue(num_runs: int = NUM_RUNS) -> list:
    rows = []
    nonlinearity = "quadratic"
    steps = DEFAULT_STEPS
    for obs_count in OBSERVE_COUNTS:
        shuffled_results = []
        cached_results = []
        for _ in range(num_runs):
            ops = build_op_sequence(steps, obs_count)
            shuffled_results.append(run_single(ops, nonlinearity))
            cached_results.append(run_single_cached(steps, nonlinearity))

        _write_raw_csv(shuffled_results,
                       RAW_DIR / f"descriptor_a1_obs{obs_count}_shuffled.csv")
        _write_raw_csv(cached_results,
                       RAW_DIR / f"descriptor_a1_obs{obs_count}_cached.csv")

        stats_shuffled = _compute_stats(shuffled_results)
        stats_cached = _compute_stats(cached_results)
        rows.append({
            "axis": "A1_py",
            "config": f"obs_{obs_count}",
            "steps": steps,
            "observes": obs_count,
            "nonlinearity": nonlinearity,
            "access_mode": "shuffled",
            **stats_shuffled,
        })
        rows.append({
            "axis": "A1_py",
            "config": f"obs_{obs_count}",
            "steps": steps,
            "observes": obs_count,
            "nonlinearity": nonlinearity,
            "access_mode": "cached",
            **stats_cached,
        })
    return rows


def run_axis_a3_analogue(num_runs: int = NUM_RUNS) -> list:
    rows = []
    nonlinearity = "quadratic"
    obs_count = DEFAULT_OBSERVES
    for steps in STEP_COUNTS:
        results = []
        for _ in range(num_runs):
            ops = build_op_sequence(steps, obs_count)
            results.append(run_single(ops, nonlinearity))
        _write_raw_csv(results, RAW_DIR / f"descriptor_a3_steps{steps}.csv")
        stats = _compute_stats(results)
        rows.append({
            "axis": "A3_py",
            "config": f"steps_{steps}",
            "steps": steps,
            "observes": obs_count,
            "nonlinearity": nonlinearity,
            "access_mode": "shuffled",
            **stats,
        })
    return rows


def run_experiment(num_runs: int = NUM_RUNS) -> list:
    random.seed(RANDOM_SEED)
    a1 = run_axis_a1_analogue(num_runs)
    a3 = run_axis_a3_analogue(num_runs)
    return a1 + a3