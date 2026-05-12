"""Fraction-based exact OSDS semantics. Zero floating-point error."""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class Value:
    b: Fraction
    n: int = 0
    e: Fraction = Fraction(1, 1)


@dataclass(frozen=True)
class Params:
    de_access: Fraction = Fraction(1, 10)
    de_obs:    Fraction = Fraction(1, 1)
    P1: bool = True
    P2: bool = True
    P3: bool = True


def do_read(x: Value, p: Params) -> Tuple[Fraction, Value]:
    drift = Fraction(x.n) * x.e if p.P1 else Fraction(0)
    v = x.b + drift
    x2 = Value(b=x.b, n=x.n + 1, e=x.e + p.de_access)
    return v, x2


def do_obs(x: Value, p: Params) -> Value:
    if not p.P2:
        return x
    return Value(b=x.b, n=x.n, e=x.e + p.de_obs)


def do_cap(y: Fraction, x: Value, degree: int, p: Params,
           kind: str = "compositional", self_k: int = 0) -> Fraction:
    if not p.P3:
        return y
    if kind == "compositional":
        cur = x
        out = y
        for _ in range(degree - 1):
            v, cur = do_read(cur, p)
            out = out * v
        return out
    if kind == "self_referential":
        cur = x
        out = y ** self_k
        for _ in range(degree - self_k):
            v, cur = do_read(cur, p)
            out = out * v
        return out
    raise ValueError(f"unknown cap kind: {kind}")


def evaluate(body: Tuple[str, ...], degree: int, p: Params,
             x0: Fraction = Fraction(10),
             kind: str = "compositional",
             self_k: int = 0) -> Fraction:
    x = Value(b=x0)
    y = Fraction(0)
    for op in body:
        if op == "READ":
            v, x = do_read(x, p)
            y = y + v
        elif op == "OBS":
            x = do_obs(x, p)
        else:
            raise ValueError(f"unknown op: {op}")
    return do_cap(y, x, degree, p, kind, self_k)


def trace(body: Tuple[str, ...], degree: int, p: Params,
          x0: Fraction = Fraction(10)) -> list:
    x = Value(b=x0)
    y = Fraction(0)
    hist = [(None, y, x)]
    for op in body:
        if op == "READ":
            v, x = do_read(x, p)
            y = y + v
        elif op == "OBS":
            x = do_obs(x, p)
        hist.append((op, y, x))
    y_final = do_cap(y, x, degree, p)
    hist.append(("CAP", y_final, x))
    return hist