# exp_real_system_case.py

import csv
import math
import random
import statistics
import sys
from pathlib import Path

_RWV = Path(__file__).parent.parent
if str(_RWV) not in sys.path:
    sys.path.insert(0, str(_RWV))

from core.unstable_object import UnstableObject

RAW_DIR = Path("real_world_validation/results/raw")
SUMMARY_DIR = Path("real_world_validation/results/summary")

try:
    import config
    RANDOM_SEED = config.RANDOM_SEED
    RAW_DIR = config.RESULTS_RAW_DIR
    SUMMARY_DIR = config.RESULTS_SUMMARY_DIR
except ImportError:
    RANDOM_SEED = 42

NUM_RUNS_PER_DEPTH = 1_000_000
READ_DEPTHS = [1, 2, 3, 5, 8, 12, 20]

RISK_HIGH_THRESHOLD = 0.65
TIER_PRO_THRESHOLD = 500.0
TIER_ENTERPRISE_THRESHOLD = 2000.0
ML_POSITIVE_THRESHOLD = 0.50

# Unified fieldnames used by every row written to the summary CSV
SUMMARY_FIELDS = [
    "experiment",
    "case",
    "read_depth",
    "num_runs",
    "mean_absolute_error",
    "max_absolute_error",
    "decision_flips",
    "flip_rate",
    "monotonic_drift",
    "ci_low",
    "ci_high",
    "threshold_primary",
    "threshold_secondary",
    "label_low",
    "label_high",
]


def _make_row(case: str, read_depth: int, num_runs: int,
              mae: float, max_err: float, flips: int, flip_rate: float,
              ci_lo: float, ci_hi: float,
              threshold_primary: float, label_low: str, label_high: str,
              threshold_secondary: float = None) -> dict:
    return {
        "experiment": "real_system_case",
        "case": case,
        "read_depth": read_depth,
        "num_runs": num_runs,
        "mean_absolute_error": round(mae, 6),
        "max_absolute_error": round(max_err, 6),
        "decision_flips": flips,
        "flip_rate": round(flip_rate, 6),
        "monotonic_drift": None,
        "ci_low": ci_lo,
        "ci_high": ci_hi,
        "threshold_primary": threshold_primary,
        "threshold_secondary": threshold_secondary,
        "label_low": label_low,
        "label_high": label_high,
    }


# ── Shared helpers ───────────────────────────────────────────────────────────

def _bootstrap_ci_mean(values: list, n_resamples: int = 500,
                       ci_level: float = 0.95) -> tuple:
    if len(values) < 2:
        v = values[0] if values else 0.0
        return round(v, 6), round(v, 6)
    means = []
    k = min(len(values), 10_000)
    for _ in range(n_resamples):
        sample = random.choices(values, k=k)
        means.append(statistics.mean(sample))
    means.sort()
    alpha = 1.0 - ci_level
    lo_idx = max(0, int(alpha / 2 * n_resamples))
    hi_idx = min(n_resamples - 1, int((1.0 - alpha / 2) * n_resamples))
    return round(means[lo_idx], 6), round(means[hi_idx], 6)


def _is_monotonic(values: list) -> bool:
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def _write_raw_csv(rows: list, path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# ── Case 1: Risk dashboard ───────────────────────────────────────────────────

def _risk_score_stale(base_signal: float, volatility: float,
                      read_depth: int) -> float:
    obj = UnstableObject(base=base_signal, initial_entropy=volatility)
    cached_raw = obj.read()
    for _ in range(read_depth):
        obj.read()
    return min(1.0, max(0.0, cached_raw / (cached_raw + 100.0)))


def _risk_score_true_at_depth(base_signal: float, volatility: float,
                               read_depth: int) -> float:
    obj = UnstableObject(base=base_signal, initial_entropy=volatility)
    for _ in range(read_depth):
        obj.read()
    raw = obj.read()
    return min(1.0, max(0.0, raw / (raw + 100.0)))


def run_risk_dashboard_case(num_runs: int = NUM_RUNS_PER_DEPTH) -> list:
    rows = []
    raw_rows = []

    for read_depth in READ_DEPTHS:
        errors = []
        flips = 0

        for _ in range(num_runs):
            base_signal = random.uniform(40.0, 120.0)
            volatility = random.uniform(0.8, 2.5)

            stale = _risk_score_stale(base_signal, volatility, read_depth)
            true_ = _risk_score_true_at_depth(base_signal, volatility, read_depth)
            err = abs(stale - true_)
            errors.append(err)

            stale_label = "HIGH_RISK" if stale >= RISK_HIGH_THRESHOLD else "LOW_RISK"
            true_label = "HIGH_RISK" if true_ >= RISK_HIGH_THRESHOLD else "LOW_RISK"
            if stale_label != true_label:
                flips += 1

            if len(raw_rows) < 50_000:
                raw_rows.append({
                    "case": "risk_dashboard",
                    "read_depth": read_depth,
                    "stale_score": round(stale, 6),
                    "true_score": round(true_, 6),
                    "error": round(err, 6),
                    "flip": int(stale_label != true_label),
                })

        flip_rate = flips / num_runs
        mae = statistics.mean(errors)
        max_err = max(errors)
        ci_lo, ci_hi = _bootstrap_ci_mean(errors)

        rows.append(_make_row(
            case="risk_dashboard",
            read_depth=read_depth,
            num_runs=num_runs,
            mae=mae,
            max_err=max_err,
            flips=flips,
            flip_rate=flip_rate,
            ci_lo=ci_lo,
            ci_hi=ci_hi,
            threshold_primary=RISK_HIGH_THRESHOLD,
            threshold_secondary=None,
            label_low="LOW_RISK",
            label_high="HIGH_RISK",
        ))

    monotonic = _is_monotonic([r["flip_rate"] for r in rows])
    for r in rows:
        r["monotonic_drift"] = monotonic

    _write_raw_csv(raw_rows, RAW_DIR / "real_system_risk_dashboard_sample.csv")
    return rows


# ── Case 2: ORM billing tier ─────────────────────────────────────────────────

def _usage_metric_stale(base_usage: float, entropy: float,
                        read_depth: int) -> float:
    obj = UnstableObject(base=base_usage, initial_entropy=entropy)
    cached_val = obj.read()
    for _ in range(read_depth):
        obj.read()
    return cached_val


def _usage_metric_true(base_usage: float, entropy: float,
                       read_depth: int) -> float:
    obj = UnstableObject(base=base_usage, initial_entropy=entropy)
    for _ in range(read_depth):
        obj.read()
    return obj.read()


def _tier_label(usage: float) -> str:
    if usage >= TIER_ENTERPRISE_THRESHOLD:
        return "ENTERPRISE"
    if usage >= TIER_PRO_THRESHOLD:
        return "PRO"
    return "FREE"


def run_orm_billing_case(num_runs: int = NUM_RUNS_PER_DEPTH) -> list:
    rows = []
    raw_rows = []

    for read_depth in READ_DEPTHS:
        errors = []
        flips = 0

        for _ in range(num_runs):
            base_usage = random.uniform(200.0, 3000.0)
            entropy = random.uniform(0.5, 3.0)

            stale = _usage_metric_stale(base_usage, entropy, read_depth)
            true_ = _usage_metric_true(base_usage, entropy, read_depth)
            err = abs(stale - true_)
            errors.append(err)

            stale_label = _tier_label(stale)
            true_label = _tier_label(true_)
            if stale_label != true_label:
                flips += 1

            if len(raw_rows) < 50_000:
                raw_rows.append({
                    "case": "orm_billing",
                    "read_depth": read_depth,
                    "stale_usage": round(stale, 4),
                    "true_usage": round(true_, 4),
                    "error": round(err, 4),
                    "stale_tier": stale_label,
                    "true_tier": true_label,
                    "flip": int(stale_label != true_label),
                })

        flip_rate = flips / num_runs
        mae = statistics.mean(errors)
        max_err = max(errors)
        ci_lo, ci_hi = _bootstrap_ci_mean(errors)

        rows.append(_make_row(
            case="orm_billing",
            read_depth=read_depth,
            num_runs=num_runs,
            mae=mae,
            max_err=max_err,
            flips=flips,
            flip_rate=flip_rate,
            ci_lo=ci_lo,
            ci_hi=ci_hi,
            threshold_primary=TIER_PRO_THRESHOLD,
            threshold_secondary=TIER_ENTERPRISE_THRESHOLD,
            label_low="FREE",
            label_high="ENTERPRISE",
        ))

    monotonic = _is_monotonic([r["flip_rate"] for r in rows])
    for r in rows:
        r["monotonic_drift"] = monotonic

    _write_raw_csv(raw_rows, RAW_DIR / "real_system_orm_billing_sample.csv")
    return rows


# ── Case 3: ML feature store ─────────────────────────────────────────────────

def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _ml_feature_stale(base_feature: float, entropy: float,
                      read_depth: int, weight: float) -> float:
    obj = UnstableObject(base=base_feature, initial_entropy=entropy)
    cached_val = obj.read()
    for _ in range(read_depth):
        obj.read()
    return _sigmoid(weight * cached_val)


def _ml_feature_true(base_feature: float, entropy: float,
                     read_depth: int, weight: float) -> float:
    obj = UnstableObject(base=base_feature, initial_entropy=entropy)
    for _ in range(read_depth):
        obj.read()
    true_val = obj.read()
    return _sigmoid(weight * true_val)


def run_ml_feature_case(num_runs: int = NUM_RUNS_PER_DEPTH) -> list:
    rows = []
    raw_rows = []

    for read_depth in READ_DEPTHS:
        errors = []
        flips = 0

        for _ in range(num_runs):
            base_feature = random.uniform(-2.0, 2.0)
            entropy = random.uniform(0.3, 1.5)
            weight = random.uniform(0.5, 3.0)

            stale = _ml_feature_stale(base_feature, entropy, read_depth, weight)
            true_ = _ml_feature_true(base_feature, entropy, read_depth, weight)
            err = abs(stale - true_)
            errors.append(err)

            stale_label = "POSITIVE" if stale >= ML_POSITIVE_THRESHOLD else "NEGATIVE"
            true_label = "POSITIVE" if true_ >= ML_POSITIVE_THRESHOLD else "NEGATIVE"
            if stale_label != true_label:
                flips += 1

            if len(raw_rows) < 50_000:
                raw_rows.append({
                    "case": "ml_feature_store",
                    "read_depth": read_depth,
                    "stale_prob": round(stale, 6),
                    "true_prob": round(true_, 6),
                    "error": round(err, 6),
                    "stale_label": stale_label,
                    "true_label": true_label,
                    "flip": int(stale_label != true_label),
                })

        flip_rate = flips / num_runs
        mae = statistics.mean(errors)
        max_err = max(errors)
        ci_lo, ci_hi = _bootstrap_ci_mean(errors)

        rows.append(_make_row(
            case="ml_feature_store",
            read_depth=read_depth,
            num_runs=num_runs,
            mae=mae,
            max_err=max_err,
            flips=flips,
            flip_rate=flip_rate,
            ci_lo=ci_lo,
            ci_hi=ci_hi,
            threshold_primary=ML_POSITIVE_THRESHOLD,
            threshold_secondary=None,
            label_low="NEGATIVE",
            label_high="POSITIVE",
        ))

    monotonic = _is_monotonic([r["flip_rate"] for r in rows])
    for r in rows:
        r["monotonic_drift"] = monotonic

    _write_raw_csv(raw_rows, RAW_DIR / "real_system_ml_feature_sample.csv")
    return rows


# ── Top-level runner ─────────────────────────────────────────────────────────

def run_experiment(num_runs: int = NUM_RUNS_PER_DEPTH) -> list:
    random.seed(RANDOM_SEED)

    risk_rows = run_risk_dashboard_case(num_runs)
    orm_rows = run_orm_billing_case(num_runs)
    ml_rows = run_ml_feature_case(num_runs)

    all_rows = risk_rows + orm_rows + ml_rows

    summary_path = SUMMARY_DIR / "real_system_cases.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    return all_rows