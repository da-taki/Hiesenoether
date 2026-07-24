from __future__ import annotations

import math
import random
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from analyzer.abstract_interpreter import AnalysisResult, analyze_program_result
from validation.exact_semantics import Params, evaluate

@dataclass(frozen=True)
class Case:
    L: int
    m: int
    d: int
    cap_kind: str = "compositional"
    self_power: int = 0

    @property
    def config(self) -> str:
        if self.cap_kind == "self_referential":
            return f"L={self.L}, m={self.m}, cap=y^{self.self_power} * read(x)"
        return f"L={self.L}, m={self.m}, d={self.d}"

@dataclass(frozen=True)
class TimedResult:
    case: Case
    abstract: AnalysisResult
    concrete: Fraction
    ratio: Fraction
    abstract_ms: Fraction
    concrete_ms: Fraction
    concrete_mode: str

CASES = (
    Case(4, 2, 3),
    Case(5, 3, 2),
    Case(6, 2, 4),
    Case(3, 2, 3, cap_kind="self_referential", self_power=2),
    Case(4, 2, 4, cap_kind="self_referential", self_power=3),
    Case(2, 0, 2),
    Case(1, 5, 3),
)

def unique_orders(L: int, m: int):
    n = L + m
    for obs_positions in combinations(range(n), m):
        obs_positions = set(obs_positions)
        yield tuple("OBS" if i in obs_positions else "READ" for i in range(n))

def sampled_orders(L: int, m: int, draws: int = 10_000):
    rng = random.Random(L * 10_000 + m * 100)
    base = ["READ"] * L + ["OBS"] * m
    seen = set()
    for _ in range(draws):
        order = base[:]
        rng.shuffle(order)
        seen.add(tuple(order))
    return seen

def orders_for_case(case: Case):
    if case.L + case.m > 8:
        return sampled_orders(case.L, case.m), "sampled"
    return list(unique_orders(case.L, case.m)), "exhaustive"

def concrete_value(order: tuple[str, ...], case: Case) -> Fraction:
    if case.cap_kind == "self_referential":
        return evaluate(
            order,
            case.d,
            Params(),
            kind="self_referential",
            self_k=case.self_power,
        )
    return evaluate(order, case.d, Params(), kind="compositional")

def concrete_divergence(case: Case) -> tuple[Fraction, str]:
    orders, mode = orders_for_case(case)
    values = [concrete_value(order, case) for order in orders]
    return max(values) - min(values), mode

def elapsed_ms(start_ns: int, end_ns: int) -> Fraction:
    return Fraction(end_ns - start_ns, 1_000_000)

def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

def decimal_text(value: Fraction, places: int = 3) -> str:
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

def ratio_for(bound: Fraction, concrete: Fraction) -> Fraction:
    if concrete == 0:
        return Fraction(1) if bound == 0 else math.inf
    return bound / concrete

def run_case(case: Case) -> TimedResult:
    start = time.perf_counter_ns()
    abstract = analyze_program_result(
        case.L,
        case.m,
        case.d,
        cap_kind=case.cap_kind,
        self_power=case.self_power,
    )
    end = time.perf_counter_ns()
    abstract_ms = elapsed_ms(start, end)

    start = time.perf_counter_ns()
    concrete, mode = concrete_divergence(case)
    end = time.perf_counter_ns()
    concrete_ms = elapsed_ms(start, end)

    return TimedResult(
        case=case,
        abstract=abstract,
        concrete=concrete,
        ratio=ratio_for(abstract.divergence_bound, concrete),
        abstract_ms=abstract_ms,
        concrete_ms=concrete_ms,
        concrete_mode=mode,
    )

def ratio_text(result: TimedResult) -> str:
    if result.ratio is math.inf:
        return f"slack {fraction_text(result.abstract.divergence_bound)}"
    return fraction_text(result.ratio)

def markdown_table(results: list[TimedResult]) -> str:
    rows = [
        "| Config | Abstract bound B | Concrete divergence | Precision ratio | Abstract time (ms) | Concrete time (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        concrete_note = (
            fraction_text(result.concrete)
            if result.concrete_mode == "exhaustive"
            else f"{fraction_text(result.concrete)} sampled lower bound"
        )
        rows.append(
            "| "
            f"{result.case.config} | "
            f"{fraction_text(result.abstract.divergence_bound)} | "
            f"{concrete_note} | "
            f"{ratio_text(result)} | "
            f"{decimal_text(result.abstract_ms)} | "
            f"{decimal_text(result.concrete_ms)} |"
        )
    return "\n".join(rows)

def main() -> int:
    results = [run_case(case) for case in CASES]
    unsound = [
        result for result in results
        if result.concrete_mode == "exhaustive"
        and result.abstract.divergence_bound < result.concrete
    ]

    for result in results:
        print(
            f"[Config {result.case.config}] "
            f"abstract={fraction_text(result.abstract.divergence_bound)} "
            f"concrete={fraction_text(result.concrete)} "
            f"ratio={ratio_text(result)} "
            f"time_abs={decimal_text(result.abstract_ms)}ms "
            f"time_con={decimal_text(result.concrete_ms)}ms"
        )

    if unsound:
        bad = ", ".join(result.case.config for result in unsound)
        print(f"FAIL: bound was unsound for config [{bad}]")
        return 1

    print("PASS: every abstract bound covered the exhaustive concrete divergence")
    print()
    print(markdown_table(results))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
