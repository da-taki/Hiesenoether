from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Iterable

from validation.exact_semantics import Params, evaluate

REPO = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO / "results_validation"
CSV_OUT = RESULTS_DIR / "polynomial_degree_extended.csv"
SUMMARY_OUT = RESULTS_DIR / "polynomial_degree_extended_summary.md"

@dataclass(frozen=True)
class CaseResult:
    m: int
    d: int
    method: str
    l_values: str
    holdout_l: int
    detected_degree_finite_difference: int
    interpolated_degree: int
    expected_d_plus_2: int
    expected_d_plus_2_pass: bool
    observed_2d_pass: bool
    leading_coefficient: Fraction
    holdout_exact: Fraction
    holdout_predicted: Fraction
    holdout_pass: bool
    exhaustive_extremal_checks: int
    exhaustive_l_values: str
    exhaustive_extremal_pass: bool
    status: str
    reason: str
    elapsed_seconds: float

def read_value(base: Fraction, n: int, e: Fraction) -> Fraction:
    return base + Fraction(n) * e

def osds_extremal_delta(
    L: int,
    m: int,
    d: int,
    params: Params = Params(),
    base: Fraction = Fraction(10),
) -> Fraction:

    body_delta = params.de_obs * Fraction(m) * Fraction(L * (L - 1), 2)
    cap = Fraction(1)
    n0 = L
    e0 = Fraction(1) + Fraction(L) * params.de_access + Fraction(m) * params.de_obs
    for r in range(max(0, d - 1)):
        cap *= read_value(base, n0 + r, e0 + Fraction(r) * params.de_access)
    return body_delta * cap

def exhaustive_delta(L: int, m: int, d: int) -> Fraction:
    body = ("READ",) * L + ("OBS",) * m
    vals = [evaluate(order, d, Params(), kind="compositional") for order in set(permutations(body))]
    return max(vals) - min(vals)

def forward_differences(seq: list[Fraction]) -> list[list[Fraction]]:
    rows = [seq[:]]
    while len(rows[-1]) > 1:
        prev = rows[-1]
        rows.append([prev[i + 1] - prev[i] for i in range(len(prev) - 1)])
    return rows

def finite_difference_degree(seq: list[Fraction]) -> int:
    for degree, row in enumerate(forward_differences(seq)):
        if row and all(x == row[0] for x in row):
            return degree
    return -1

def lagrange_polynomial(points: list[tuple[int, Fraction]]) -> list[Fraction]:
    coeffs = [Fraction(0)] * len(points)
    for i, (xi, yi) in enumerate(points):
        basis = [Fraction(1)]
        denom = Fraction(1)
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            next_basis = [Fraction(0)] * (len(basis) + 1)
            for k, coeff in enumerate(basis):
                next_basis[k] -= coeff * xj
                next_basis[k + 1] += coeff
            basis = next_basis
            denom *= xi - xj
        scale = yi / denom
        for k, coeff in enumerate(basis):
            coeffs[k] += coeff * scale
    return coeffs

def polynomial_degree(coeffs: list[Fraction]) -> int:
    for idx in range(len(coeffs) - 1, -1, -1):
        if coeffs[idx] != 0:
            return idx
    return -1

def eval_polynomial(coeffs: list[Fraction], x: int) -> Fraction:
    total = Fraction(0)
    power = Fraction(1)
    for coeff in coeffs:
        total += coeff * power
        power *= x
    return total

def leading_coefficient(coeffs: list[Fraction]) -> Fraction:
    deg = polynomial_degree(coeffs)
    return Fraction(0) if deg < 0 else coeffs[deg]

def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"

def analyze_case(m: int, d: int) -> CaseResult:
    started = time.time()
    Ls = list(range(2, 15))
    holdout_l = 15
    exhaustive_Ls = list(range(2, 9))

    values = [osds_extremal_delta(L, m, d) for L in Ls]
    exhaustive_passes = []
    for L in exhaustive_Ls:
        exhaustive_passes.append(exhaustive_delta(L, m, d) == osds_extremal_delta(L, m, d))

    diff_degree = finite_difference_degree(values)
    coeffs = lagrange_polynomial(list(zip(Ls, values)))
    interp_degree = polynomial_degree(coeffs)
    holdout_exact = osds_extremal_delta(holdout_l, m, d)
    holdout_pred = eval_polynomial(coeffs, holdout_l)

    expected = d + 2
    expected_pass = interp_degree == expected
    observed_2d_pass = interp_degree == 2 * d
    holdout_pass = holdout_exact == holdout_pred
    exhaustive_pass = all(exhaustive_passes)

    status = "pass" if expected_pass and holdout_pass and exhaustive_pass else "fail"
    reason_parts = []
    if not expected_pass:
        reason_parts.append(f"detected degree {interp_degree}, not expected d+2={expected}")
    if not holdout_pass:
        reason_parts.append("holdout interpolation prediction mismatch")
    if not exhaustive_pass:
        reason_parts.append("extremal-order formula did not match exhaustive enumeration")
    if not reason_parts:
        reason_parts.append("detected degree matches d+2 and holdout/exhaustive checks pass")

    return CaseResult(
        m=m,
        d=d,
        method="exhaustive small-L check plus exact extremal-order interpolation",
        l_values=f"{Ls[0]}..{Ls[-1]}",
        holdout_l=holdout_l,
        detected_degree_finite_difference=diff_degree,
        interpolated_degree=interp_degree,
        expected_d_plus_2=expected,
        expected_d_plus_2_pass=expected_pass,
        observed_2d_pass=observed_2d_pass,
        leading_coefficient=leading_coefficient(coeffs),
        holdout_exact=holdout_exact,
        holdout_predicted=holdout_pred,
        holdout_pass=holdout_pass,
        exhaustive_extremal_checks=len(exhaustive_passes),
        exhaustive_l_values=f"{exhaustive_Ls[0]}..{exhaustive_Ls[-1]}",
        exhaustive_extremal_pass=exhaustive_pass,
        status=status,
        reason="; ".join(reason_parts),
        elapsed_seconds=time.time() - started,
    )

def rows_from_cases(cases: Iterable[CaseResult]) -> list[dict]:
    rows = []
    for case in cases:
        rows.append({
            "m": case.m,
            "d": case.d,
            "method": case.method,
            "L_values": case.l_values,
            "holdout_L": case.holdout_l,
            "detected_degree_finite_difference": case.detected_degree_finite_difference,
            "interpolated_degree": case.interpolated_degree,
            "expected_d_plus_2": case.expected_d_plus_2,
            "expected_d_plus_2_pass": case.expected_d_plus_2_pass,
            "observed_2d_pass": case.observed_2d_pass,
            "leading_coefficient": fraction_text(case.leading_coefficient),
            "holdout_exact": fraction_text(case.holdout_exact),
            "holdout_predicted": fraction_text(case.holdout_predicted),
            "holdout_pass": case.holdout_pass,
            "exhaustive_extremal_checks": case.exhaustive_extremal_checks,
            "exhaustive_L_values": case.exhaustive_l_values,
            "exhaustive_extremal_pass": case.exhaustive_extremal_pass,
            "status": case.status,
            "reason": case.reason,
            "elapsed_seconds": f"{case.elapsed_seconds:.3f}",
        })
    return rows

def write_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def write_summary(cases: list[CaseResult]) -> None:
    pass_d_plus_2 = [c for c in cases if c.expected_d_plus_2_pass]
    fail_d_plus_2 = [c for c in cases if not c.expected_d_plus_2_pass]
    exhaustive_fail = [c for c in cases if not c.exhaustive_extremal_pass]
    holdout_fail = [c for c in cases if not c.holdout_pass]
    observed_2d = [c for c in cases if c.observed_2d_pass]

    lines = [
        "# Extended Polynomial Degree Verification",
        "",
        "## Scope",
        "",
        "- cap family: compositional OSDS caps",
        "- m range: 1..4",
        "- d range: 1..5",
        "- L interpolation range: 2..14",
        "- holdout L: 15",
        "- arithmetic: exact `fractions.Fraction` rational arithmetic",
        "",
        "## Method",
        "",
        "For each `(m,d)`, the script computes an exact extremal-order range formula and checks that formula against exhaustive permutation enumeration for small L values. It then performs finite-difference degree detection and rational Lagrange interpolation on the exact extremal-order values, followed by exact holdout prediction.",
        "",
        "The exhaustive checks are finite-grid checks over L=2..8. The larger-L interpolation evidence is exact extremal-order verification, not full exhaustive verification. It is not a formal proof for all L.",
        "",
        "## d+2 Result",
        "",
        f"- cases checked: {len(cases)}",
        f"- cases passing detected degree = d+2: {len(pass_d_plus_2)}",
        f"- cases failing detected degree = d+2: {len(fail_d_plus_2)}",
        f"- cases matching detected degree = 2d: {len(observed_2d)}",
        f"- holdout failures: {len(holdout_fail)}",
        f"- extremal-vs-exhaustive failures: {len(exhaustive_fail)}",
        "",
    ]

    if pass_d_plus_2:
        lines.append("Cases passing d+2:")
        for case in pass_d_plus_2:
            lines.append(f"- m={case.m}, d={case.d}, degree={case.interpolated_degree}")
    else:
        lines.append("Cases passing d+2: none")

    lines.extend(["", "Cases failing d+2:"])
    for case in fail_d_plus_2:
        lines.append(
            f"- m={case.m}, d={case.d}: detected degree {case.interpolated_degree}; "
            f"expected d+2={case.expected_d_plus_2}; reason: {case.reason}"
        )

    lines.extend([
        "",
        "## Skipped Or Timed Out",
        "",
        "No cases were skipped or timed out.",
        "",
        "## Mechanized Support Beyond d <= 2",
        "",
        "The script expands exact checked evidence beyond d <= 2 by evaluating d=3, d=4, and d=5 for m=1..4. The expanded evidence does not support the unqualified d+2 degree claim for the current compositional-degree parameterization; it instead detects degree 2d for every checked d=1..5 case.",
    ])

    SUMMARY_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

def run() -> list[CaseResult]:
    cases = [analyze_case(m, d) for m in range(1, 5) for d in range(1, 6)]
    rows = rows_from_cases(cases)
    write_csv(rows)
    write_summary(cases)
    return cases

def main() -> int:
    cases = run()
    failures = [case for case in cases if not case.holdout_pass or not case.exhaustive_extremal_pass]
    print(f"wrote {CSV_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"checked={len(cases)} d_plus_2_pass={sum(c.expected_d_plus_2_pass for c in cases)}")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
