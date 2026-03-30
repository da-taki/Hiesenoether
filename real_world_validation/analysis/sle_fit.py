# sle_fit.py

import math
import random
import statistics
from dataclasses import dataclass, field


@dataclass
class SLEResult:
    sle: float
    r_squared: float
    ci_low: float
    ci_high: float
    n_degrees: int
    degrees: list
    log_ranges: list
    intercept: float = 0.0


def fit_sle(degrees: list, log_ranges: list) -> tuple:
    if len(degrees) != len(log_ranges) or len(degrees) < 2:
        raise ValueError("fit_sle requires parallel lists of length >= 2.")
    n = len(degrees)
    x_mean = sum(degrees) / n
    y_mean = sum(log_ranges) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(degrees, log_ranges))
    den = sum((x - x_mean) ** 2 for x in degrees)
    slope = num / den if den != 0 else 0.0
    intercept = y_mean - slope * x_mean
    ss_res = sum(
        (y - (intercept + slope * x)) ** 2
        for x, y in zip(degrees, log_ranges)
    )
    ss_tot = sum((y - y_mean) ** 2 for y in log_ranges)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    return round(slope, 6), round(r2, 6)


def _percentile(sorted_data: list, pct: float) -> float:
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * pct / 100.0
    lo = int(k)
    hi = min(lo + 1, len(sorted_data) - 1)
    frac = k - lo
    return sorted_data[lo] * (1.0 - frac) + sorted_data[hi] * frac


def bootstrap_sle_ci(
    values_by_degree: dict,
    n_resamples: int = 1000,
    ci_level: float = 0.95,
) -> tuple:
    degrees = sorted(values_by_degree.keys())
    sle_samples = []
    for _ in range(n_resamples):
        resampled_log_ranges = []
        for d in degrees:
            vals = values_by_degree[d]
            sample = random.choices(vals, k=len(vals))
            r = max(sample) - min(sample)
            resampled_log_ranges.append(math.log(r) if r > 1.0 else 0.0)
        try:
            sle_i, _ = fit_sle(degrees, resampled_log_ranges)
            sle_samples.append(sle_i)
        except ValueError:
            continue
    if not sle_samples:
        return 0.0, 0.0
    sle_samples.sort()
    alpha = 1.0 - ci_level
    lo = _percentile(sle_samples, 100.0 * alpha / 2.0)
    hi = _percentile(sle_samples, 100.0 * (1.0 - alpha / 2.0))
    return round(lo, 6), round(hi, 6)


def predict_range(degree: int, sle: float, intercept: float) -> float:
    return math.exp(intercept + sle * degree)


def build_sle_result(
    degrees: list,
    log_ranges: list,
    values_by_degree: dict = None,
    n_resamples: int = 1000,
    ci_level: float = 0.95,
) -> SLEResult:
    sle, r2 = fit_sle(degrees, log_ranges)
    n = len(degrees)
    x_mean = sum(degrees) / n
    y_mean = sum(log_ranges) / n
    intercept = y_mean - sle * x_mean
    ci_low, ci_high = 0.0, 0.0
    if values_by_degree and len(values_by_degree) >= 2:
        ci_low, ci_high = bootstrap_sle_ci(values_by_degree, n_resamples, ci_level)
    return SLEResult(
        sle=sle,
        r_squared=r2,
        ci_low=ci_low,
        ci_high=ci_high,
        n_degrees=len(degrees),
        degrees=degrees,
        log_ranges=log_ranges,
        intercept=round(intercept, 6),
    )