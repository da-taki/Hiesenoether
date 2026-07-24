from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from analyzer.abstract_domain import AbstractUnstable, Interval, abstract_cap

DEFAULT_BASE = Fraction(10, 1)
DEFAULT_ENTROPY = Fraction(1, 1)
DEFAULT_DELTA = Fraction(1, 10)
DEFAULT_ETA = Fraction(1, 1)
CapKind = Literal["compositional", "self_referential"]

@dataclass(frozen=True)
class AnalysisResult:
    L: int
    m: int
    d: int
    cap_kind: CapKind
    self_power: int
    body_spread: Fraction
    cap_factor: Fraction
    cap_induced_spread: Fraction
    divergence_bound: Fraction
    y_interval_before_cap: Interval
    output_interval: Interval

def _validate_program_shape(L: int, m: int, d: int) -> None:
    if L < 0:
        raise ValueError("L must be nonnegative")
    if m < 0:
        raise ValueError("m must be nonnegative")
    if d < 1:
        raise ValueError("d must be at least 1")

def _read_value(base: Fraction, n: int, e: Fraction) -> Fraction:
    return base + Fraction(n) * e

def _body_accumulator_extrema(
    L: int,
    m: int,
    *,
    base: Fraction,
    e0: Fraction,
    delta: Fraction,
    eta: Fraction,
) -> tuple[Fraction, Fraction]:

    low = Fraction(0)
    high = Fraction(0)
    for k in range(L):
        n = k
        low += _read_value(base, n, e0 + Fraction(k) * delta)
        high += _read_value(base, n, e0 + Fraction(m) * eta + Fraction(k) * delta)
    return low, high

def cap_factor_upper_bound(
    L: int,
    m: int,
    d: int,
    *,
    base: Fraction = DEFAULT_BASE,
    e0: Fraction = DEFAULT_ENTROPY,
    delta: Fraction = DEFAULT_DELTA,
    eta: Fraction = DEFAULT_ETA,
) -> Fraction:

    _validate_program_shape(L, m, d)
    factor = Fraction(1)
    cap_entropy = e0 + Fraction(L) * delta + Fraction(m) * eta
    for r in range(d - 1):
        factor *= _read_value(base, L + r, cap_entropy + Fraction(r) * delta)
    return factor

def self_referential_cap_factor(
    L: int,
    m: int,
    *,
    base: Fraction = DEFAULT_BASE,
    e0: Fraction = DEFAULT_ENTROPY,
    delta: Fraction = DEFAULT_DELTA,
    eta: Fraction = DEFAULT_ETA,
) -> Fraction:

    cap_entropy = e0 + Fraction(L) * delta + Fraction(m) * eta
    return _read_value(base, L, cap_entropy)

def analyze_program_result(
    L: int,
    m: int,
    d: int,
    *,
    cap_kind: CapKind = "compositional",
    self_power: int = 0,
    base: Fraction = DEFAULT_BASE,
    e0: Fraction = DEFAULT_ENTROPY,
    delta: Fraction = DEFAULT_DELTA,
    eta: Fraction = DEFAULT_ETA,
) -> AnalysisResult:

    _validate_program_shape(L, m, d)
    if cap_kind not in ("compositional", "self_referential"):
        raise ValueError(f"unknown cap kind: {cap_kind}")
    if self_power < 0:
        raise ValueError("self_power must be nonnegative")

    y_low, y_high = _body_accumulator_extrema(
        L, m, base=base, e0=e0, delta=delta, eta=eta
    )
    body_spread = y_high - y_low

    cap_induced_spread = Fraction(0)
    x_at_cap = AbstractUnstable(
        b=Interval.point(base),
        n=Interval.point(L),
        e=Interval.point(e0 + Fraction(L) * delta + Fraction(m) * eta),
    )
    y_before_cap = Interval(y_low, y_high)

    if cap_kind == "compositional":
        cap_factor = cap_factor_upper_bound(
            L, m, d, base=base, e0=e0, delta=delta, eta=eta
        )
        divergence_bound = body_spread * cap_factor + cap_induced_spread
        output_interval, _ = abstract_cap(y_before_cap, x_at_cap, d, delta)
    else:
        cap_factor = self_referential_cap_factor(
            L, m, base=base, e0=e0, delta=delta, eta=eta
        )
        y_power_interval = y_before_cap.pow_nonnegative_int(self_power)
        output_interval = y_power_interval * Interval.point(cap_factor)
        divergence_bound = output_interval.width + cap_induced_spread

    if output_interval.width > divergence_bound:
        divergence_bound = output_interval.width

    return AnalysisResult(
        L=L,
        m=m,
        d=d,
        cap_kind=cap_kind,
        self_power=self_power,
        body_spread=body_spread,
        cap_factor=cap_factor,
        cap_induced_spread=cap_induced_spread,
        divergence_bound=divergence_bound,
        y_interval_before_cap=y_before_cap,
        output_interval=output_interval,
    )

def analyze_program(
    L: int,
    m: int,
    d: int,
    *,
    cap_kind: CapKind = "compositional",
    self_power: int = 0,
) -> Fraction:

    return analyze_program_result(
        L, m, d, cap_kind=cap_kind, self_power=self_power
    ).divergence_bound
