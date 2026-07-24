from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Tuple

@dataclass(frozen=True)
class UV:
    b: Fraction
    n: int = 0
    e: Fraction = Fraction(1, 1)

DE = Fraction(1, 10)
DOBS = Fraction(1, 1)

def read(u: UV) -> Tuple[Fraction, UV]:
    drift = Fraction(u.n) * u.e
    v = u.b + drift
    return v, UV(b=u.b, n=u.n + 1, e=u.e + DE)

def observe(u: UV) -> UV:
    return UV(b=u.b, n=u.n + 1, e=u.e + DE)

def wrap(value: Fraction) -> UV:
    return UV(b=value, n=0, e=Fraction(1, 1))

def run_program(body: tuple, degree: int,
                x_init: Fraction = Fraction(10),
                y_init: Fraction = Fraction(0)) -> Fraction:
    x = UV(b=x_init)
    y = UV(b=y_init)

    for op in body:
        if op == "READ":
            yv, y = read(y)
            xv, x = read(x)
            y = wrap(yv + xv)
        elif op == "OBS":
            x = observe(x)
        else:
            raise ValueError(op)

    if degree == 1:
        pass
    elif degree == 2:
        yv, y = read(y)
        xv, x = read(x)
        y = wrap(yv * xv)
    elif degree == 3:
        yv, y = read(y)
        xv1, x = read(x)
        xv2, x = read(x)
        y = wrap(yv * xv1 * xv2)
    elif degree == 4:
        yv1, y = read(y)
        yv2, y = read(y)
        xv, x = read(x)
        y = wrap(yv1 * yv2 * xv)
    else:
        raise ValueError(f"unsupported degree: {degree}")

    final_v, _ = read(y)
    return final_v

def divergence_runtime(body_template: tuple, degree: int) -> Fraction:
    from itertools import permutations
    vals = [run_program(perm, degree)
            for perm in set(permutations(body_template))]
    return max(vals) - min(vals)
