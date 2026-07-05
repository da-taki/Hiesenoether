from __future__ import annotations

from collections import Counter
from fractions import Fraction

from examples.running_example import SEQUENCE_A, SEQUENCE_B, build_example


def test_running_example_uses_same_multiset_with_observation_and_reads():
    assert Counter(SEQUENCE_A) == Counter(SEQUENCE_B)
    assert Counter(SEQUENCE_A)["OBS"] == 1
    assert Counter(SEQUENCE_A)["READ"] >= 2


def test_running_example_diverges_exactly():
    example = build_example()

    output_a = Fraction(example["sequence_A_final_output"])
    output_b = Fraction(example["sequence_B_final_output"])
    divergence = Fraction(example["divergence"]["exact"])

    assert output_a == Fraction(7956, 25)
    assert output_b == Fraction(7596, 25)
    assert divergence == Fraction(72, 5)
    assert output_a != output_b


def test_running_example_records_intermediate_exact_states():
    example = build_example()

    sequence_a_states = example["sequence_A_intermediate_states"]
    sequence_b_states = example["sequence_B_intermediate_states"]

    assert sequence_a_states[0]["x"]["base_b"] == "10"
    assert sequence_a_states[0]["x"]["access_count_a"] == 0
    assert sequence_a_states[1]["operation"] == "OBS"
    assert sequence_a_states[2]["read_value"] == "10"
    assert sequence_a_states[3]["drift_d"] == "21/10"

    assert sequence_b_states[1]["operation"] == "READ"
    assert sequence_b_states[2]["drift_d"] == "11/10"
    assert sequence_b_states[3]["operation"] == "OBS"
    assert sequence_b_states[-1]["operation"] == "CAP"
