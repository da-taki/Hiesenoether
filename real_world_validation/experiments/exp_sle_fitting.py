# exp_sle_fitting.py

import csv
import math
import random
import statistics
from pathlib import Path

from core.unstable_object import UnstableObject

RAW_DIR = Path("real_world_validation/results/raw")
SUMMARY_DIR = Path("real_world_validation/results/summary")

try:
    import config
    NUM_RUNS = config.NUM_RUNS
    BASE_VALUE = config.BASE_VALUE
    DEFAULT_STEPS = config.DEFAULT_STEPS
    DEFAULT_OBSERVES = config.DEFAULT_OBSERVES
    NONLINEARITY_LEVELS = config.NONLINEARITY_LEVELS
    RANDOM_SEED = config.RANDOM_SEED
    RAW_DIR = config.RESULTS_RAW_DIR
    SUMMARY_DIR = config.RESULTS_SUMMARY_DIR
    BOOTSTRAP_RESAMPLES = config.BOOTSTRAP_RESAMPLES
    SLE_CI_LEVEL = config.SLE_CI_LEVEL
except ImportError:
    NUM_RUNS = 10_000
    BASE_VALUE = 10.0
    DEFAULT_STEPS = 6
    DEFAULT_OBSERVES = 1
    NONLINEARITY_LEVELS = ["linear", "quadratic", "cubic", "extreme"]
    RANDOM_SEED = 42
    BOOTSTRAP_RESAMPLES = 1000
    SLE_CI_LEVEL = 0.95

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


def _run_single(steps: int, observe_count: int, nonlinearity: str) -> float:
    ops = ["add"] * steps + ["observe"] * observe_count
    random.shuffle(ops)
    obj = UnstableObject(base=BASE_VALUE)
    y = 0.0
    for op in ops:
        if op == "add":
            y += obj.read()
        elif op == "observe":
            obj.observe()
    return _apply_cap(y, obj, nonlinearity)


def _compute_stats(values: list) -> dict:
    n = len(values)
    if n < 2:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0,
                "range": 0.0, "log_range": 0.0, "n": n}
    mean_ = statistics.mean(values)
    std_ = statistics.stdev(values)
    min_ = min(values)
    max_ = max(values)
    range_ = max_ - min_
    log_range = math.log(range_) if range_ > 1.0 else 0.0
    return {
        "mean": round(mean_, 4),
        "std": round(std_, 4),
        "min": round(min_, 4),
        "max": round(max_, 4),
        "range": round(range_, 4),
        "log_range": round(log_range, 6),
        "n": n,
    }


def _write_raw_csv(values: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["value"])
        for v in values:
            writer.writerow([v])


def _write_summary_csv(rows: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _fit_sle_inline(degrees: list, log_ranges: list) -> tuple:
    n = len(degrees)
    x_mean = sum(degrees) / n
    y_mean = sum(log_ranges) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(degrees, log_ranges))
    den = sum((x - x_mean) ** 2 for x in degrees)
    slope = num / den if den != 0 else 0.0
    ss_res = sum((y - (y_mean + slope * (x - x_mean))) ** 2
                 for x, y in zip(degrees, log_ranges))
    ss_tot = sum((y - y_mean) ** 2 for y in log_ranges)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    return round(slope, 6), round(r2, 6)


def _bootstrap_ci(values_by_degree: dict, n_resamples: int,
                  ci_level: float) -> tuple:
    degrees = sorted(values_by_degree.keys())
    sle_samples = []
    for _ in range(n_resamples):
        resampled_log_ranges = []
        for d in degrees:
            vals = values_by_degree[d]
            sample = random.choices(vals, k=len(vals))
            r = max(sample) - min(sample)
            resampled_log_ranges.append(math.log(r) if r > 1.0 else 0.0)
        sle_i, _ = _fit_sle_inline(degrees, resampled_log_ranges)
        sle_samples.append(sle_i)
    sle_samples.sort()
    alpha = 1.0 - ci_level
    lo_idx = max(0, int(alpha / 2 * n_resamples))
    hi_idx = min(n_resamples - 1, int((1.0 - alpha / 2) * n_resamples))
    return round(sle_samples[lo_idx], 6), round(sle_samples[hi_idx], 6)


def run_nonlinearity_sweep(num_runs: int = NUM_RUNS) -> tuple:
    steps = DEFAULT_STEPS
    observes = DEFAULT_OBSERVES
    sweep_rows = []
    values_by_degree = {}

    for nonlinearity in NONLINEARITY_LEVELS:
        results = [_run_single(steps, observes, nonlinearity)
                   for _ in range(num_runs)]
        degree = DEGREE_MAP[nonlinearity]
        _write_raw_csv(results, RAW_DIR / f"sle_nonlin_{nonlinearity}.csv")
        stats = _compute_stats(results)
        values_by_degree[degree] = results
        sweep_rows.append({
            "nonlinearity": nonlinearity,
            "degree": degree,
            **stats,
        })

    return sweep_rows, values_by_degree


def run_experiment(num_runs: int = NUM_RUNS) -> dict:
    random.seed(RANDOM_SEED)
    sweep_rows, values_by_degree = run_nonlinearity_sweep(num_runs)

    valid = [(row["degree"], row["log_range"])
             for row in sweep_rows if row["range"] > 1.0]
    degrees = [v[0] for v in valid]
    log_ranges = [v[1] for v in valid]

    sle, r_squared = (0.0, 0.0)
    ci_low, ci_high = (0.0, 0.0)

    if len(degrees) >= 2:
        try:
            from analysis.sle_fit import fit_sle, bootstrap_sle_ci
            sle, r_squared = fit_sle(degrees, log_ranges)
            ci_low, ci_high = bootstrap_sle_ci(
                values_by_degree, BOOTSTRAP_RESAMPLES, SLE_CI_LEVEL)
        except ImportError:
            sle, r_squared = _fit_sle_inline(degrees, log_ranges)
            ci_low, ci_high = _bootstrap_ci(
                values_by_degree, BOOTSTRAP_RESAMPLES, SLE_CI_LEVEL)

    summary_rows = []
    for row in sweep_rows:
        summary_rows.append({
            **row,
            "sle": sle,
            "r_squared": r_squared,
            "ci_low": ci_low,
            "ci_high": ci_high,
        })

    _write_summary_csv(summary_rows, SUMMARY_DIR / "sle_python_substrate.csv")

    return {
        "sweep_rows": sweep_rows,
        "sle": sle,
        "r_squared": r_squared,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }