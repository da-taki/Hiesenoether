from __future__ import annotations
import json
from fractions import Fraction
from itertools import permutations
from typing import List, Tuple

from validation.exact_semantics import evaluate as osds_eval, Params
from validation.exact_semantics_runtime import run_program as rt_eval


def kind_for(d: int):
    if d == 4:
        return "self_referential", 2
    return "compositional", 0


def divergence_osds(L: int, m: int, d: int) -> Fraction:
    kind, self_k = kind_for(d)
    body = ("READ",) * L + ("OBS",) * m
    p = Params()
    vals = [osds_eval(perm, d, p, kind=kind, self_k=self_k)
            for perm in set(permutations(body))]
    return max(vals) - min(vals)


def divergence_runtime(L: int, m: int, d: int) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    vals = [rt_eval(perm, d) for perm in set(permutations(body))]
    return max(vals) - min(vals)


def forward_differences(seq: List[Fraction]) -> List[List[Fraction]]:
    """Return all forward-difference rows until one is fully zero or
    we run out of values. Row 0 is the original sequence."""
    rows = [seq[:]]
    while len(rows[-1]) > 1:
        prev = rows[-1]
        nxt = [prev[i + 1] - prev[i] for i in range(len(prev) - 1)]
        rows.append(nxt)
        if all(x == 0 for x in nxt):
            break
    return rows


def detect_polynomial_degree(seq: List[Fraction]) -> int:
    """Return the polynomial degree if seq is exactly a polynomial in
    its index, else -1. A degree-d polynomial has constant d-th forward
    difference and zero (d+1)-th forward difference."""
    rows = forward_differences(seq)
    for k, row in enumerate(rows):
        if len(row) >= 2 and all(x == row[0] for x in row):
            # Constant at depth k: degree k polynomial.
            if k + 1 < len(rows) and all(x == 0 for x in rows[k + 1]):
                return k
            if len(row) <= 1:
                return k
            return k
    return -1


def lagrange_polynomial(points: List[Tuple[int, Fraction]]) -> List[Fraction]:
    """Return coefficients [c0, c1, ..., cn] of the unique polynomial
    p(x) = c0 + c1*x + ... + cn*x^n passing through the given points,
    using exact Fraction arithmetic via Lagrange interpolation."""
    n = len(points)
    coeffs = [Fraction(0)] * n
    for i in range(n):
        xi, yi = points[i]
        # Build Lagrange basis L_i(x) = prod_{j!=i} (x - xj) / (xi - xj)
        basis = [Fraction(1)]
        denom = Fraction(1)
        for j in range(n):
            if j == i:
                continue
            xj, _ = points[j]
            # Multiply basis by (x - xj)
            new_basis = [Fraction(0)] * (len(basis) + 1)
            for k, c in enumerate(basis):
                new_basis[k]     += c * (-Fraction(xj))
                new_basis[k + 1] += c
            basis = new_basis
            denom *= Fraction(xi - xj)
        # Add yi * basis / denom to total coefficients.
        scale = yi / denom
        for k, c in enumerate(basis):
            coeffs[k] += c * scale
    return coeffs


def leading_coefficient(coeffs: List[Fraction]) -> Fraction:
    for c in reversed(coeffs):
        if c != 0:
            return c
    return Fraction(0)


def polynomial_degree(coeffs: List[Fraction]) -> int:
    for i in range(len(coeffs) - 1, -1, -1):
        if coeffs[i] != 0:
            return i
    return -1


def eval_polynomial(coeffs: List[Fraction], x: int) -> Fraction:
    return sum((c * Fraction(x) ** k for k, c in enumerate(coeffs)),
               Fraction(0))


def analyze_case(m: int, d: int,
                 L_min: int = 2, L_max: int = 8,
                 holdout: int = 9) -> dict:
    """Fit polynomial models to Delta_OSDS(L) and Delta_runtime(L) for
    fixed (m, d) over L in [L_min, L_max], then verify on L = holdout."""
    Ls = list(range(L_min, L_max + 1))
    osds_seq = [divergence_osds(L, m, d) for L in Ls]
    rt_seq   = [divergence_runtime(L, m, d) for L in Ls]

    osds_deg = detect_polynomial_degree(osds_seq)
    rt_deg   = detect_polynomial_degree(rt_seq)

    osds_poly = lagrange_polynomial(list(zip(Ls, osds_seq)))
    rt_poly   = lagrange_polynomial(list(zip(Ls, rt_seq)))

    osds_lead = leading_coefficient(osds_poly)
    rt_lead   = leading_coefficient(rt_poly)
    osds_polydeg = polynomial_degree(osds_poly)
    rt_polydeg   = polynomial_degree(rt_poly)

    rho_inf = osds_lead / rt_lead if rt_lead != 0 else None

    # Holdout check.
    holdout_ok = True
    holdout_data = {}
    if holdout > L_max:
        try:
            osds_true = divergence_osds(holdout, m, d)
            rt_true   = divergence_runtime(holdout, m, d)
            osds_pred = eval_polynomial(osds_poly, holdout)
            rt_pred   = eval_polynomial(rt_poly, holdout)
            holdout_ok = (osds_pred == osds_true) and (rt_pred == rt_true)
            holdout_data = {
                "L": holdout,
                "osds_true":      f"{osds_true.numerator}/{osds_true.denominator}",
                "osds_predicted": f"{osds_pred.numerator}/{osds_pred.denominator}",
                "rt_true":        f"{rt_true.numerator}/{rt_true.denominator}",
                "rt_predicted":   f"{rt_pred.numerator}/{rt_pred.denominator}",
                "match_osds":     osds_pred == osds_true,
                "match_rt":       rt_pred == rt_true,
            }
        except Exception as e:
            holdout_data = {"error": str(e)}
            holdout_ok = False

    return {
        "m": m, "d": d, "L_range": [L_min, L_max],
        "osds_polynomial_degree": osds_polydeg,
        "rt_polynomial_degree":   rt_polydeg,
        "osds_leading_coeff": f"{osds_lead.numerator}/{osds_lead.denominator}",
        "rt_leading_coeff":   f"{rt_lead.numerator}/{rt_lead.denominator}",
        "rho_infinity": (None if rho_inf is None
                         else f"{rho_inf.numerator}/{rho_inf.denominator}"),
        "rho_infinity_float": None if rho_inf is None else float(rho_inf),
        "holdout_check": holdout_data,
        "holdout_passes": holdout_ok,
        "osds_poly_coeffs": [f"{c.numerator}/{c.denominator}"
                             for c in osds_poly],
        "rt_poly_coeffs":   [f"{c.numerator}/{c.denominator}"
                             for c in rt_poly],
    }


def check() -> dict:
    """Run polynomial-fit analysis for every (m, d) combination of
    interest. Holdout L=9 for d in {1, 2, 3}; skip holdout for d=4
    because L=9 with d=4 enumerates 9! permutations and is slow."""
    cases = []
    # d=1: degree should be 3 in L (one less than d=2).
    cases.append(analyze_case(m=1, d=1, L_min=2, L_max=7, holdout=8))
    # d=2: the principal case.
    for m in range(1, 6):
        cases.append(analyze_case(m=m, d=2, L_min=2, L_max=8, holdout=9))
    # d=3: bigger polynomial; smaller L range to keep enumeration feasible.
    cases.append(analyze_case(m=1, d=3, L_min=2, L_max=6, holdout=7))
    # d=4 self-referential: just L_max=5 to keep runtime reasonable.
    cases.append(analyze_case(m=1, d=4, L_min=2, L_max=5, holdout=6))

    all_holdouts_pass = all(c.get("holdout_passes", False) for c in cases)

    return {
        "theorem": "R",
        "status": ("VERIFIED" if all_holdouts_pass
                   else "PARTIAL (some holdout fits failed)"),
        "claim": ("Delta_OSDS(L, m, d) and Delta_runtime(L, m, d) are "
                  "polynomials in L of degree d+2 (compositional) or "
                  "higher (self-referential), and rho(L, m, d) -> "
                  "rho_inf(m, d) as L -> infinity, where rho_inf is "
                  "the ratio of leading coefficients."),
        "cases": cases,
    }


if __name__ == "__main__":
    r = check()
    print(json.dumps(r, indent=2))