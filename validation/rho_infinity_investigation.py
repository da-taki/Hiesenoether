from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from validation.exact_semantics import Params
from validation.polynomial_degree_extended import (
    eval_polynomial,
    fraction_text,
    lagrange_polynomial,
    osds_extremal_delta,
    polynomial_degree,
)

REPO = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO / "results_validation"
CSV_OUT = RESULTS_DIR / "rho_infinity_investigation.csv"
SUMMARY_OUT = RESULTS_DIR / "rho_infinity_investigation_summary.md"

@dataclass(frozen=True)
class RhoCase:
    experiment: str
    m: int
    d: int
    eta: Fraction
    delta: Fraction
    base: Fraction
    L_values: str
    holdout_L: int
    osds_degree: int
    runtime_degree: int
    osds_leading_coefficient: Fraction
    runtime_leading_coefficient: Fraction
    rho_infinity: Fraction | None
    expected_eta_over_2delta: Fraction | None
    rho_matches_expected: bool
    holdout_osds_pass: bool
    holdout_runtime_pass: bool

def runtime_read_value(base: Fraction, n: int, delta: Fraction) -> Fraction:
    return base + Fraction(n) * (Fraction(1) + Fraction(n) * delta)

def runtime_compositional_delta(
    L: int,
    m: int,
    d: int,
    delta: Fraction = Fraction(1, 10),
    base: Fraction = Fraction(10),
) -> Fraction:

    body_delta = sum(
        runtime_read_value(base, i + m, delta) - runtime_read_value(base, i, delta)
        for i in range(L)
    )
    cap = Fraction(1)
    for r in range(max(0, d - 1)):
        cap *= runtime_read_value(base, L + m + r, delta)
    return body_delta * cap

def leading_data(values: list[tuple[int, Fraction]]) -> tuple[list[Fraction], int, Fraction]:
    coeffs = lagrange_polynomial(values)
    degree = polynomial_degree(coeffs)
    leading = Fraction(0) if degree < 0 else coeffs[degree]
    return coeffs, degree, leading

def analyze_case(
    experiment: str,
    m: int,
    d: int,
    eta: Fraction = Fraction(1),
    delta: Fraction = Fraction(1, 10),
    base: Fraction = Fraction(10),
) -> RhoCase:
    Ls = list(range(2, 15))
    holdout = 15
    params = Params(de_access=delta, de_obs=eta)
    osds_values = [(L, osds_extremal_delta(L, m, d, params=params, base=base)) for L in Ls]
    runtime_values = [(L, runtime_compositional_delta(L, m, d, delta=delta, base=base)) for L in Ls]

    osds_coeffs, osds_degree, osds_lead = leading_data(osds_values)
    runtime_coeffs, runtime_degree, runtime_lead = leading_data(runtime_values)
    rho = osds_lead / runtime_lead if runtime_lead != 0 else None
    expected = eta / (2 * delta) if delta != 0 else None

    osds_holdout = osds_extremal_delta(holdout, m, d, params=params, base=base)
    runtime_holdout = runtime_compositional_delta(holdout, m, d, delta=delta, base=base)

    return RhoCase(
        experiment=experiment,
        m=m,
        d=d,
        eta=eta,
        delta=delta,
        base=base,
        L_values=f"{Ls[0]}..{Ls[-1]}",
        holdout_L=holdout,
        osds_degree=osds_degree,
        runtime_degree=runtime_degree,
        osds_leading_coefficient=osds_lead,
        runtime_leading_coefficient=runtime_lead,
        rho_infinity=rho,
        expected_eta_over_2delta=expected,
        rho_matches_expected=(rho == expected),
        holdout_osds_pass=eval_polynomial(osds_coeffs, holdout) == osds_holdout,
        holdout_runtime_pass=eval_polynomial(runtime_coeffs, holdout) == runtime_holdout,
    )

def row(case: RhoCase) -> dict:
    return {
        "experiment": case.experiment,
        "m": case.m,
        "d": case.d,
        "eta": fraction_text(case.eta),
        "delta": fraction_text(case.delta),
        "base": fraction_text(case.base),
        "L_values": case.L_values,
        "holdout_L": case.holdout_L,
        "osds_degree": case.osds_degree,
        "runtime_degree": case.runtime_degree,
        "osds_leading_coefficient": fraction_text(case.osds_leading_coefficient),
        "runtime_leading_coefficient": fraction_text(case.runtime_leading_coefficient),
        "rho_infinity": "" if case.rho_infinity is None else fraction_text(case.rho_infinity),
        "rho_infinity_float": "" if case.rho_infinity is None else f"{float(case.rho_infinity):.12g}",
        "expected_eta_over_2delta": "" if case.expected_eta_over_2delta is None else fraction_text(case.expected_eta_over_2delta),
        "rho_matches_expected": case.rho_matches_expected,
        "holdout_osds_pass": case.holdout_osds_pass,
        "holdout_runtime_pass": case.holdout_runtime_pass,
    }

def write_csv(cases: list[RhoCase]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    rows = [row(case) for case in cases]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def write_summary(cases: list[RhoCase]) -> None:
    default = [c for c in cases if c.experiment == "default"]
    variants = [c for c in cases if c.experiment != "default"]
    default_five = [c for c in default if c.rho_infinity == 5]
    default_not_five = [c for c in default if c.rho_infinity != 5]
    holdout_failures = [c for c in cases if not (c.holdout_osds_pass and c.holdout_runtime_pass)]
    expected_failures = [c for c in cases if not c.rho_matches_expected]

    representatives = [
        c for c in default
        if (c.m, c.d) in {(1, 1), (1, 2), (3, 4), (5, 5)}
    ]

    lines = [
        "# Rho Infinity Investigation",
        "",
        "## Scope",
        "",
        "- default grid: m=1..5, d=1..5",
        "- default parameters: eta=1, delta=1/10, base=10",
        "- variant sweeps: selected eta, delta, and base changes",
        "- arithmetic: exact `fractions.Fraction` rational arithmetic",
        "- runtime model: generalized compositional runtime formula external to core interpreter semantics",
        "",
        "## Default Cases",
        "",
        f"- default cases checked: {len(default)}",
        f"- default cases where rho_infinity = 5: {len(default_five)}",
        f"- default cases where rho_infinity != 5: {len(default_not_five)}",
        f"- interpolation holdout failures: {len(holdout_failures)}",
        "",
        "Representative leading coefficients:",
        "",
        "| m | d | OSDS lead | runtime lead | rho_infinity |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in representatives:
        lines.append(
            f"| {case.m} | {case.d} | {fraction_text(case.osds_leading_coefficient)} | "
            f"{fraction_text(case.runtime_leading_coefficient)} | {fraction_text(case.rho_infinity or Fraction(0))} |"
        )

    lines.extend([
        "",
        "## Parameter Variants",
        "",
        "The checked data match the simple pattern `rho_infinity = eta / (2 * delta)` for every default and variant case. Changing base did not affect the leading-coefficient ratio in the checked cases; changing eta or delta changed rho according to that expression.",
        "",
        f"- variant cases checked: {len(variants)}",
        f"- cases not matching eta/(2delta): {len(expected_failures)}",
        "",
        "## Supported Conjecture",
        "",
        "For the external generalized compositional runtime model and the OSDS extremal-order formula, the data support the conjecture that the leading cap factors cancel and `rho_infinity = eta / (2 * delta)` for positive delta. Under the default parameters eta=1 and delta=1/10, this gives rho_infinity=5.",
        "",
        "This is not a formal proof for the manuscript unless the algebraic derivation is completed and reviewed; it is exact computational evidence plus a proof sketch target.",
    ])

    if default_not_five:
        lines.extend(["", "Default non-5 cases:"])
        for case in default_not_five:
            lines.append(f"- m={case.m}, d={case.d}: rho={fraction_text(case.rho_infinity or Fraction(0))}")
    else:
        lines.extend(["", "Default non-5 cases: none"])

    SUMMARY_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

def run() -> list[RhoCase]:
    cases: list[RhoCase] = []
    for m in range(1, 6):
        for d in range(1, 6):
            cases.append(analyze_case("default", m, d))

    for eta in (Fraction(1, 2), Fraction(2), Fraction(3)):
        cases.append(analyze_case(f"eta={fraction_text(eta)}", 3, 4, eta=eta))
    for delta in (Fraction(1, 20), Fraction(1, 5), Fraction(1, 2)):
        cases.append(analyze_case(f"delta={fraction_text(delta)}", 3, 4, delta=delta))
    for base in (Fraction(1), Fraction(100), Fraction(-5)):
        cases.append(analyze_case(f"base={fraction_text(base)}", 3, 4, base=base))

    write_csv(cases)
    write_summary(cases)
    return cases

def main() -> int:
    cases = run()
    failures = [c for c in cases if not c.rho_matches_expected or not c.holdout_osds_pass or not c.holdout_runtime_pass]
    print(f"wrote {CSV_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"checked={len(cases)} failures={len(failures)}")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
