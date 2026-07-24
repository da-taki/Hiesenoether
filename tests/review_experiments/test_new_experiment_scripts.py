from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO / "scripts" / "review_experiments"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import evaluate_configuration, evaluate_order, sampled_orders, unique_order_count
from run_extended_controlled_benchmark import expected_labels

def test_zero_observation_configuration_has_zero_range():
    row, values = evaluate_configuration(
        reads=5,
        observations=0,
        degree=4,
        schedule="constant",
        exhaustive_cutoff=100,
        sample_budget_per_seed=4,
        seeds=[1, 2, 3, 4, 5],
    )
    assert row["exact_range"] == "0"
    assert len(values) == 1

def test_observation_order_can_change_exact_output():
    early_observation = evaluate_order(("OBS", "READ", "READ"), degree=2)
    late_observation = evaluate_order(("READ", "READ", "OBS"), degree=2)
    assert early_observation - late_observation == Fraction(72, 5)

def test_sampled_orders_respect_budget_and_multiset():
    orders = sampled_orders(reads=20, observations=5, budget=32, seed=123)
    assert 1 <= len(orders) <= 32
    assert unique_order_count(20, 5) > 32
    assert all(order.count("READ") == 20 and order.count("OBS") == 5 for order in orders)

def test_extended_controlled_benchmark_adds_at_least_40_cases():
    labels = expected_labels(REPO / "benchmarks" / "controlled_extended" / "extended_examples.py")
    assert len(labels) >= 40
