"""Exact-rational running example for the SCP paper.

The example is deliberately tiny: two READ operations and one OBS operation
are arranged in two different orders. The operation multiset is identical,
but observation changes the later access trajectory.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exact_semantics import Params, Value, do_obs


BASE_VALUE = Fraction(10)
CAP_DEGREE = 2
SEQUENCE_A = ("OBS", "READ", "READ")
SEQUENCE_B = ("READ", "READ", "OBS")


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def state_dict(x: Value) -> dict:
    return {
        "base_b": fraction_text(x.b),
        "access_count_a": x.n,
        "entropy": fraction_text(x.e),
    }


def read_with_details(x: Value, p: Params) -> tuple[Fraction, Fraction, Value]:
    drift = Fraction(x.n) * x.e if p.P1 else Fraction(0)
    value = x.b + drift
    next_x = Value(b=x.b, n=x.n + 1, e=x.e + p.de_access)
    return value, drift, next_x


def simulate(operations: tuple[str, ...], degree: int = CAP_DEGREE, p: Params | None = None) -> dict:
    if p is None:
        p = Params()

    x = Value(b=BASE_VALUE)
    y = Fraction(0)
    states = [
        {
            "step": 0,
            "operation": "INITIAL",
            "accumulator_y": fraction_text(y),
            "x": state_dict(x),
            "drift_d": "0",
        }
    ]

    for index, op in enumerate(operations, start=1):
        if op == "READ":
            read_value, drift, x = read_with_details(x, p)
            y += read_value
            states.append(
                {
                    "step": index,
                    "operation": "READ",
                    "read_value": fraction_text(read_value),
                    "drift_d": fraction_text(drift),
                    "accumulator_y": fraction_text(y),
                    "x": state_dict(x),
                }
            )
        elif op == "OBS":
            before = state_dict(x)
            x = do_obs(x, p)
            states.append(
                {
                    "step": index,
                    "operation": "OBS",
                    "observation": {
                        "before": before,
                        "after": state_dict(x),
                        "delta_entropy": fraction_text(p.de_obs if p.P2 else Fraction(0)),
                    },
                    "drift_d": "0",
                    "accumulator_y": fraction_text(y),
                    "x": state_dict(x),
                }
            )
        else:
            raise ValueError(f"unknown operation: {op}")

    cap_factors = []
    final_output = y
    cap_x = x
    for cap_read in range(max(0, degree - 1)):
        read_value, drift, cap_x = read_with_details(cap_x, p)
        cap_factors.append(
            {
                "cap_read": cap_read + 1,
                "read_value": fraction_text(read_value),
                "drift_d": fraction_text(drift),
                "x_after_read": state_dict(cap_x),
            }
        )
        final_output *= read_value

    states.append(
        {
            "step": len(operations) + 1,
            "operation": "CAP",
            "degree": degree,
            "input_y": fraction_text(y),
            "cap_factors": cap_factors,
            "final_output": fraction_text(final_output),
        }
    )

    return {
        "operations": list(operations),
        "intermediate_states": states,
        "final_output": fraction_text(final_output),
        "final_output_decimal": float(final_output),
    }


def build_example() -> dict:
    if Counter(SEQUENCE_A) != Counter(SEQUENCE_B):
        raise AssertionError("running-example sequences must use the same operation multiset")

    a = simulate(SEQUENCE_A)
    b = simulate(SEQUENCE_B)
    divergence = abs(Fraction(a["final_output"]) - Fraction(b["final_output"]))

    return {
        "initial_state": {
            "base_value_b": fraction_text(BASE_VALUE),
            "access_count_a": 0,
            "entropy": "1",
            "initial_drift_d": "0",
            "access_entropy_increment": "1/10",
            "observation_entropy_increment": "1",
        },
        "cap": {
            "kind": "compositional",
            "degree": CAP_DEGREE,
            "formula": "final = accumulated_reads * next_read",
        },
        "sequence_A_operations": a["operations"],
        "sequence_A_intermediate_states": a["intermediate_states"],
        "sequence_A_final_output": a["final_output"],
        "sequence_A_final_output_decimal": a["final_output_decimal"],
        "sequence_B_operations": b["operations"],
        "sequence_B_intermediate_states": b["intermediate_states"],
        "sequence_B_final_output": b["final_output"],
        "sequence_B_final_output_decimal": b["final_output_decimal"],
        "divergence": {
            "exact": fraction_text(divergence),
            "decimal": float(divergence),
        },
        "explanation": (
            "Both executions use exactly two READ operations and one OBS operation. "
            "When OBS occurs first, it raises entropy before the second body read, "
            "so the accumulated read sum entering the cap is larger. The cap then "
            "uses the same exact-rational next-read factor in both orders, producing "
            "different deterministic final outputs from the same operation multiset."
        ),
    }


def write_running_example(path: Path | None = None) -> Path:
    if path is None:
        path = REPO / "results" / "running_example.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_example(), indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    path = write_running_example()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
