from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Union


Number = Union[int, Fraction]


def as_fraction(value: Number) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(value)


@dataclass(frozen=True)
class Interval:
    """Closed rational interval [lo, hi]."""

    lo: Fraction
    hi: Fraction

    def __init__(self, lo: Number, hi: Number | None = None):
        if hi is None:
            hi = lo
        lo_f = as_fraction(lo)
        hi_f = as_fraction(hi)
        if lo_f > hi_f:
            raise ValueError(f"invalid interval [{lo_f}, {hi_f}]")
        object.__setattr__(self, "lo", lo_f)
        object.__setattr__(self, "hi", hi_f)

    @classmethod
    def point(cls, value: Number) -> "Interval":
        return cls(value, value)

    @property
    def width(self) -> Fraction:
        return self.hi - self.lo

    def __add__(self, other: "Interval") -> "Interval":
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other: "Interval") -> "Interval":
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other: "Interval") -> "Interval":
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(min(products), max(products))

    def pow_nonnegative_int(self, exponent: int) -> "Interval":
        if exponent < 0:
            raise ValueError("exponent must be nonnegative")
        out = Interval.point(1)
        for _ in range(exponent):
            out = out * self
        return out

    def contains(self, value: Number) -> bool:
        value_f = as_fraction(value)
        return self.lo <= value_f <= self.hi

    def __str__(self) -> str:
        return f"[{self.lo}, {self.hi}]"


@dataclass(frozen=True)
class AbstractUnstable:
    """Intervals for an unstable value's base, access count, and entropy."""

    b: Interval
    n: Interval
    e: Interval


def abstract_read(
    value: AbstractUnstable,
    delta: Fraction = Fraction(1, 10),
) -> tuple[Interval, AbstractUnstable]:
    """Abstract rule for concrete read(b, n, e) = b + n*e.

    Concrete read also advances the unstable state to (b, n + 1, e + delta).
    """

    exposed = value.b + (value.n * value.e)
    updated = AbstractUnstable(
        b=value.b,
        n=value.n + Interval.point(1),
        e=value.e + Interval.point(delta),
    )
    return exposed, updated


def abstract_inspect(
    value: AbstractUnstable,
    eta: Fraction = Fraction(1, 1),
) -> AbstractUnstable:
    """Abstract rule for concrete inspect(b, n, e) = (b, n, e + eta)."""

    return AbstractUnstable(
        b=value.b,
        n=value.n,
        e=value.e + Interval.point(eta),
    )


def abstract_additive_update(
    y: Interval,
    x: AbstractUnstable,
    delta: Fraction = Fraction(1, 10),
) -> tuple[Interval, AbstractUnstable]:
    """Abstract rule for y <- y + x, where x is read once."""

    exposed, x_updated = abstract_read(x, delta)
    return y + exposed, x_updated


def abstract_cap(
    y: Interval,
    x: AbstractUnstable,
    degree: int,
    delta: Fraction = Fraction(1, 10),
) -> tuple[Interval, AbstractUnstable]:
    """Abstract rule for the compositional cap y * read(x)^(degree - 1)."""

    if degree < 1:
        raise ValueError("degree must be at least 1")

    out = y
    current = x
    for _ in range(degree - 1):
        exposed, current = abstract_read(current, delta)
        out = out * exposed
    return out, current
