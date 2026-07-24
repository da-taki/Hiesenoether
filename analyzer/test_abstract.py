from __future__ import annotations

import sys
from fractions import Fraction
from itertools import permutations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from analyzer.abstract_interpreter import analyze_program_result
from validation.exact_semantics import Params, evaluate

CASES = (
    (1, 0, 1, "no divergence expected"),
    (3, 1, 1, "small divergence expected"),
    (3, 2, 2, "large divergence expected"),
)

def concrete_divergence(L: int, m: int, d: int) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    values = [
        evaluate(order, d, Params(), kind="compositional")
        for order in set(permutations(body))
    ]
    return max(values) - min(values)

def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

def decimal_text(value: Fraction, places: int = 6) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    whole = value.numerator // value.denominator
    rem = value.numerator % value.denominator
    digits = []
    for _ in range(places):
        rem *= 10
        digits.append(str(rem // value.denominator))
        rem %= value.denominator
    return f"{sign}{whole}.{''.join(digits)}"

def main() -> int:
    print("Access-counter-indexed abstract-domain smoke tests")
    print()
    all_sound = True
    for L, m, d, label in CASES:
        result = analyze_program_result(L, m, d)
        actual = concrete_divergence(L, m, d)
        ratio = None if actual == 0 else result.divergence_bound / actual
        all_sound = all_sound and result.divergence_bound >= actual

        print(f"{label}:")
        print(f"  config: L={L}, m={m}, d={d}")
        print(
            "  computed bound B: "
            f"{fraction_text(result.divergence_bound)} "
            f"({decimal_text(result.divergence_bound)})"
        )
        print(
            "  reference concrete divergence: "
            f"{fraction_text(actual)} ({decimal_text(actual)})"
        )
        print(
            "  precision ratio B/actual: "
            f"{'undefined' if ratio is None else fraction_text(ratio)}"
        )
        print(
            "  y interval before cap: "
            f"{result.y_interval_before_cap}"
        )
        print(
            "  output interval: "
            f"{result.output_interval}"
        )
        print()

    if not all_sound:
        print("FAIL: at least one abstract bound was below the concrete divergence")
        return 1
    print("PASS: every abstract bound covered the exhaustive concrete divergence")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
