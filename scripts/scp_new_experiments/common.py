from __future__ import annotations

import csv
import json
import math
import random
import re
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RESULTS_DIR = REPO / "results" / "scp_new_experiments"
GAPS_PATH = RESULTS_DIR / "NEW_EXPERIMENT_GAPS.md"

SCHEDULES: dict[str, Fraction] = {
    "constant": Fraction(0),
    "linear_decay": Fraction(1, 20),
    "exponential_decay": Fraction(1, 20),
}

def ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path)

def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

def fraction_decimal(value: Fraction) -> float:
    return float(value)

def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    ensure_results_dir()
    if fieldnames is None and rows:
        fieldnames = list(rows[0].keys())
    if fieldnames is None:
        fieldnames = []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def write_json(path: Path, payload: dict) -> None:
    ensure_results_dir()
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")

def append_gap(title: str, detail: str) -> None:
    ensure_results_dir()
    existing = GAPS_PATH.read_text(encoding="utf-8") if GAPS_PATH.exists() else "# New Experiment Gaps\n\n"
    entry = f"## {title}\n\n{detail.strip()}\n"
    pattern = rf"(?ms)^## {re.escape(title)}\n\n.*?(?=^## |\Z)"
    pruned = re.sub(pattern, "", existing.rstrip()).rstrip()
    updated = pruned + "\n\n" + entry
    GAPS_PATH.write_text(updated.rstrip() + "\n", encoding="utf-8")

def unique_order_count(reads: int, observations: int) -> int:
    return math.comb(reads + observations, observations)

def unique_orders(reads: int, observations: int) -> Iterable[tuple[str, ...]]:
    total = reads + observations
    for obs_positions in combinations(range(total), observations):
        obs_positions = set(obs_positions)
        yield tuple("OBS" if index in obs_positions else "READ" for index in range(total))

def random_order(reads: int, observations: int, rng: random.Random) -> tuple[str, ...]:
    order = ["READ"] * reads + ["OBS"] * observations
    rng.shuffle(order)
    return tuple(order)

def sampled_orders(reads: int, observations: int, budget: int, seed: int) -> list[tuple[str, ...]]:
    total_unique = unique_order_count(reads, observations)
    if budget >= total_unique:
        return list(unique_orders(reads, observations))

    rng = random.Random(seed)
    seen: set[tuple[str, ...]] = set()
    attempts = 0
    max_attempts = budget * 20
    while len(seen) < budget and attempts < max_attempts:
        seen.add(random_order(reads, observations, rng))
        attempts += 1
    return sorted(seen)

def entropy_increment(schedule: str, beta: Fraction, access_count: int, de_access: Fraction) -> Fraction:
    if schedule == "constant":
        return de_access
    if schedule == "linear_decay":
        factor = max(Fraction(0), Fraction(1) - beta * access_count)
        return de_access * factor
    if schedule == "exponential_decay":
        return de_access * (Fraction(1) / (Fraction(1) + beta)) ** access_count
    raise ValueError(f"unknown drift schedule: {schedule}")

def read_value(state: tuple[Fraction, int, Fraction], schedule: str, beta: Fraction) -> tuple[Fraction, tuple[Fraction, int, Fraction]]:
    base, access_count, entropy = state
    drift = Fraction(access_count) * entropy
    value = base + drift
    next_state = (
        base,
        access_count + 1,
        entropy + entropy_increment(schedule, beta, access_count, Fraction(1, 10)),
    )
    return value, next_state

def observe_state(state: tuple[Fraction, int, Fraction]) -> tuple[Fraction, int, Fraction]:
    base, access_count, entropy = state
    return base, access_count, entropy + Fraction(1)

def evaluate_order(
    order: tuple[str, ...],
    degree: int,
    schedule: str = "constant",
    beta: Fraction | None = None,
    base: Fraction = Fraction(10),
) -> Fraction:
    if beta is None:
        beta = SCHEDULES[schedule]

    x = (base, 0, Fraction(1))
    y = Fraction(0)
    for op in order:
        if op == "READ":
            value, x = read_value(x, schedule, beta)
            y += value
        elif op == "OBS":
            x = observe_state(x)
        else:
            raise ValueError(f"unknown operation: {op}")

    output = y
    for _ in range(max(0, degree - 1)):
        value, x = read_value(x, schedule, beta)
        output *= value
    return output

def evaluate_orders(
    orders: Iterable[tuple[str, ...]],
    degree: int,
    schedule: str,
    beta: Fraction | None = None,
) -> list[Fraction]:
    return [evaluate_order(order, degree, schedule, beta) for order in orders]

def output_stats(values: list[Fraction]) -> dict:
    if not values:
        return {
            "mean_output": "",
            "std_dev": "",
            "range": "",
            "coefficient_of_variation": "",
            "min_output": "",
            "max_output": "",
            "exact_min_output": "",
            "exact_max_output": "",
            "exact_range": "",
        }

    exact_min = min(values)
    exact_max = max(values)
    exact_range = exact_max - exact_min
    exact_mean = sum(values, Fraction(0)) / len(values)
    float_values = [float(value) for value in values]
    std_value = stdev(float_values) if len(float_values) > 1 else 0.0
    mean_value = mean(float_values)
    cv_value = std_value / abs(mean_value) if mean_value else 0.0

    return {
        "mean_output": round(float(exact_mean), 12),
        "std_dev": round(std_value, 12),
        "range": round(float(exact_range), 12),
        "coefficient_of_variation": round(cv_value, 12),
        "min_output": round(float(exact_min), 12),
        "max_output": round(float(exact_max), 12),
        "exact_min_output": fraction_text(exact_min),
        "exact_max_output": fraction_text(exact_max),
        "exact_range": fraction_text(exact_range),
    }

def evaluate_configuration(
    reads: int,
    observations: int,
    degree: int,
    schedule: str,
    exhaustive_cutoff: int,
    sample_budget_per_seed: int,
    seeds: list[int],
) -> tuple[dict, list[Fraction]]:
    unique_count = unique_order_count(reads, observations)
    exhaustive = unique_count <= exhaustive_cutoff
    if exhaustive:
        orders = list(unique_orders(reads, observations))
        seed_count = 0
    else:
        seen: set[tuple[str, ...]] = set()
        for seed in seeds:
            seen.update(sampled_orders(reads, observations, sample_budget_per_seed, seed))
        orders = sorted(seen)
        seed_count = len(seeds)

    beta = SCHEDULES[schedule]
    values = evaluate_orders(orders, degree, schedule, beta)
    row = {
        "body_length": reads,
        "observation_count": observations,
        "cap_degree": degree,
        "drift_schedule": schedule,
        "schedule_beta": fraction_text(beta),
        "unique_permutations": unique_count,
        "sampled_permutations": len(orders),
        "seed_count": seed_count,
        "exhaustive_enumeration_used": exhaustive,
        "exact_rational_arithmetic_used": True,
        "executions": len(values),
    }
    row.update(output_stats(values))
    return row, values

def markdown_table(headers: list[str], rows: list[dict], max_rows: int | None = None) -> list[str]:
    selected = rows if max_rows is None else rows[:max_rows]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in selected:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    if max_rows is not None and len(rows) > max_rows:
        lines.append(f"| ... | ... | ... | ... | ... |")
    return lines
