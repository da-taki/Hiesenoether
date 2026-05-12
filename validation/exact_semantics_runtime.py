from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class UV:
    """Mirror of UnstableValue: base, access_count, entropy."""
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
    return UV(b=u.b, n=u.n, e=u.e + DOBS)


def wrap(value: Fraction) -> UV:
    """Hiesenoether runtime wraps every assignment RHS in a fresh
    UnstableValue with reset access_count and entropy."""
    return UV(b=value, n=0, e=Fraction(1, 1))


def run_program(body: tuple, degree: int,
                x_init: Fraction = Fraction(10),
                y_init: Fraction = Fraction(0)) -> Fraction:
    """Emulate the exact program template from run_experiments.py:

        energy[100]
        x <- 10
        y <- 0
        {BODY}            -- 'y <- y + x' and 'inspect x', shuffled
        {NONLINEAR_LINE}  -- 'y <- y * x', 'y <- y * x * x', or 'y <- y * y * x'
        print y           -- final read of y (drift advances)

    Each statement that appears as `y <- ...` does:
        evaluate RHS (which reads y and/or x, advancing them)
        wrap result into fresh UV
        store as new `y`.

    `inspect x` increases x's entropy by 1.0.

    Returns the value printed by `print y`, i.e. one additional read of
    the final wrapped y.
    """
    x = UV(b=x_init)
    y = UV(b=y_init)

    # BODY: list of either 'add' (y <- y + x) or 'inspect' (inspect x).
    for op in body:
        if op == "READ":           # 'y <- y + x' in the .hn program
            yv, y = read(y)
            xv, x = read(x)
            y = wrap(yv + xv)
        elif op == "OBS":          # 'inspect x'
            x = observe(x)
        else:
            raise ValueError(op)

    # CAP line: degree d means d-1 multiplications of fresh x reads.
    # In the runtime: 'y <- y * x'    (d=2): read y once, read x once
    #                 'y <- y * x * x'(d=3): read y once, read x, read x
    #                 'y <- y * y * x'(extreme): read y twice, read x once
    if degree == 1:
        pass                       # no cap line; print y reads y once below
    elif degree == 2:
        yv, y = read(y)
        xv, x = read(x)
        y = wrap(yv * xv)
    elif degree == 3:
        yv, y = read(y)
        xv1, x = read(x)
        xv2, x = read(x)
        y = wrap(yv * xv1 * xv2)
    elif degree == 4:              # 'extreme' = y*y*x in run_experiments
        yv1, y = read(y)
        yv2, y = read(y)
        xv, x = read(x)
        y = wrap(yv1 * yv2 * xv)
    else:
        raise ValueError(f"unsupported degree: {degree}")

    # `print y` performs one final read of y.
    final_v, _ = read(y)
    return final_v


def divergence_runtime(body_template: tuple, degree: int) -> Fraction:
    """All permutations of the body multiset; return max - min of program
    outputs under the Hiesenoether runtime semantics."""
    from itertools import permutations
    vals = [run_program(perm, degree)
            for perm in set(permutations(body_template))]
    return max(vals) - min(vals)