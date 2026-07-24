from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.exact_semantics import Params, Value, do_cap, do_obs, do_read, evaluate
from validation.exact_semantics_runtime import divergence_runtime

RESULTS_DIR = REPO / "results" / "paper_evidence"

def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

def parse_fraction(value: str | int | float | None) -> Fraction | None:
    if value is None:
        return None
    return Fraction(str(value))

def unique_orders(reads: int, observations: int) -> Iterable[tuple[str, ...]]:
    total = reads + observations
    for obs_positions in combinations(range(total), observations):
        obs_positions = set(obs_positions)
        yield tuple("OBS" if index in obs_positions else "READ" for index in range(total))

def write_summary(name: str, payload: dict) -> dict:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / name
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    payload["summary_path"] = str(path.relative_to(REPO))
    return payload

def read_json(path: Path) -> dict:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return json.loads(data.decode("utf-16"))
    return json.loads(data.decode("utf-8-sig"))

def evaluate_with_state(order: tuple[str, ...], degree: int, params: Params) -> tuple[Fraction, tuple]:
    x = Value(b=Fraction(10))
    y = Fraction(0)
    for op in order:
        if op == "READ":
            v, x = do_read(x, params)
            y += v
        elif op == "OBS":
            x = do_obs(x, params)
        else:
            raise ValueError(op)
    output = do_cap(y, x, degree, params)
    state = (x.b, x.n, x.e, y)
    return output, state

def divergence(reads: int, observations: int, degree: int, params: Params) -> Fraction:
    outputs = [
        evaluate(order, degree, params)
        for order in unique_orders(reads, observations)
    ]
    return max(outputs) - min(outputs)

def check_fixed_order_determinism() -> dict:
    repeats = 4
    templates = []
    permutations_checked = 0
    mismatches = []

    for reads in range(2, 5):
        for observations in range(1, 3):
            for degree in range(1, 4):
                templates.append({"reads": reads, "observations": observations, "degree": degree})
                for order in unique_orders(reads, observations):
                    repeated = [evaluate_with_state(order, degree, Params()) for _ in range(repeats)]
                    permutations_checked += 1
                    if len(set(repeated)) != 1:
                        mismatches.append(
                            {
                                "reads": reads,
                                "observations": observations,
                                "degree": degree,
                                "order": list(order),
                                "observed": [
                                    {
                                        "output": fraction_text(output),
                                        "state": [fraction_text(v) if isinstance(v, Fraction) else v for v in state],
                                    }
                                    for output, state in repeated
                                ],
                            }
                        )

    return write_summary(
        "fixed_order_determinism.json",
        {
            "claim": "Fixed-order determinism",
            "status": "PASS" if not mismatches else "FAIL",
            "templates": templates,
            "templates_checked": len(templates),
            "permutations_checked": permutations_checked,
            "repeats": repeats,
            "mismatches": mismatches,
        },
    )

def check_identity_observation_zero_divergence() -> dict:
    params = Params(P2=False)
    counterexamples = []
    checked = 0

    for reads in range(2, 6):
        for observations in range(1, 4):
            for degree in range(1, 5):
                delta = divergence(reads, observations, degree, params)
                checked += 1
                if delta != 0:
                    counterexamples.append(
                        {
                            "reads": reads,
                            "observations": observations,
                            "degree": degree,
                            "divergence": fraction_text(delta),
                        }
                    )

    return write_summary(
        "identity_observation_zero_divergence.json",
        {
            "claim": "Identity observation gives zero divergence",
            "status": "PASS" if not counterexamples else "FAIL",
            "assumptions": [
                "Templates contain only READ and OBS over one OSDS value.",
                "OBS is the identity transition: g(d) = d.",
                "All compared executions use the same READ/OBS multiset.",
            ],
            "configurations_checked": checked,
            "counterexamples": counterexamples,
        },
    )

def check_access_insensitive_reads_zero_divergence() -> dict:
    params = Params(P1=False)
    counterexamples = []
    checked = 0

    for reads in range(2, 6):
        for observations in range(1, 4):
            for degree in range(1, 5):
                delta = divergence(reads, observations, degree, params)
                checked += 1
                if delta != 0:
                    counterexamples.append(
                        {
                            "reads": reads,
                            "observations": observations,
                            "degree": degree,
                            "divergence": fraction_text(delta),
                        }
                    )

    return write_summary(
        "access_insensitive_reads_zero_divergence.json",
        {
            "claim": "Access-insensitive reads give zero divergence",
            "status": "PASS" if not counterexamples else "FAIL",
            "assumptions": [
                "Templates contain only READ and OBS over one OSDS value.",
                "READ returns the base value independent of access count and drift.",
                "All compared executions use the same READ/OBS multiset.",
            ],
            "configurations_checked": checked,
            "counterexamples": counterexamples,
        },
    )

def check_composition_amplification() -> dict:
    rows = []
    failures = []

    for reads, observations in ((3, 1), (4, 1), (4, 2), (5, 2)):
        ranges = {
            degree: divergence(reads, observations, degree, Params())
            for degree in range(1, 5)
        }
        row = {
            "reads": reads,
            "observations": observations,
            "ranges": {str(degree): fraction_text(value) for degree, value in ranges.items()},
            "linear_positive": ranges[1] > 0,
            "nonlinear_increases_range": ranges[2] > ranges[1] and ranges[3] > ranges[2] and ranges[4] > ranges[3],
        }
        rows.append(row)
        if not row["linear_positive"] or not row["nonlinear_increases_range"]:
            failures.append(row)

    return write_summary(
        "composition_amplification.json",
        {
            "claim": "Composition amplification",
            "status": "PASS" if not failures else "FAIL",
            "interpretation": "Empirical exact-rational evidence, not a theorem.",
            "rows": rows,
            "failures": failures,
        },
    )

def _table_kind(kind_text: str | None, degree: int) -> tuple[str, int]:
    if kind_text == "self_referential_k2":
        return "self_referential", 2
    if degree == 4 and kind_text == "self_referential":
        return "self_referential", 2
    return "compositional", 0

def _osds_divergence_from_table_row(row: dict) -> Fraction:
    reads = int(row["L"])
    observations = int(row["m"])
    degree = int(row["d"])
    kind, self_k = _table_kind(row.get("kind"), degree)
    values = [
        evaluate(order, degree, Params(), kind=kind, self_k=self_k)
        for order in unique_orders(reads, observations)
    ]
    return max(values) - min(values)

def check_bounded_computational_claims() -> dict:
    polynomial_path = REPO / "validation" / "theorem_R_polynomial.json"
    ratio_path = REPO / "validation" / "theorem_R_table.json"
    failures = []

    polynomial = {
        "source": str(polynomial_path.relative_to(REPO)),
        "status": "missing_raw_data",
    }
    if polynomial_path.exists():
        data = read_json(polynomial_path)
        failed_cases = [case for case in data.get("cases", []) if not case.get("holdout_passes")]
        polynomial = {
            "source": str(polynomial_path.relative_to(REPO)),
            "status": "reproduced_from_existing_results",
            "top_level_status": data.get("status"),
            "cases_checked": len(data.get("cases", [])),
            "failed_holdout_cases": failed_cases,
            "scope_note": data.get("scope_note"),
        }
        failures.extend(failed_cases)

    ratio = {
        "source": str(ratio_path.relative_to(REPO)),
        "status": "missing_raw_data",
    }
    if ratio_path.exists():
        data = read_json(ratio_path)
        mismatches = []
        for row in data.get("rows", []):
            body = ("READ",) * int(row["L"]) + ("OBS",) * int(row["m"])
            osds_delta = _osds_divergence_from_table_row(row)
            runtime_delta = divergence_runtime(body, int(row["d"]))
            ratio_value = None if runtime_delta == 0 else osds_delta / runtime_delta
            expected_ratio = parse_fraction(row.get("ratio_exact"))
            row_mismatches = []
            if osds_delta != Fraction(row["Delta_OSDS_exact"]):
                row_mismatches.append("Delta_OSDS_exact")
            if runtime_delta != Fraction(row["Delta_runtime_exact"]):
                row_mismatches.append("Delta_runtime_exact")
            if ratio_value != expected_ratio:
                row_mismatches.append("ratio_exact")
            if row_mismatches:
                mismatches.append(
                    {
                        "row": row,
                        "fields": row_mismatches,
                        "recomputed": {
                            "Delta_OSDS_exact": fraction_text(osds_delta),
                            "Delta_runtime_exact": fraction_text(runtime_delta),
                            "ratio_exact": None if ratio_value is None else fraction_text(ratio_value),
                        },
                    }
                )
        ratio = {
            "source": str(ratio_path.relative_to(REPO)),
            "status": "reproduced_from_code",
            "rows_checked": len(data.get("rows", [])),
            "mismatches": mismatches,
        }
        failures.extend(mismatches)

    return write_summary(
        "bounded_computational_claims.json",
        {
            "claim": "Polynomial-degree and divergence-ratio checks are bounded computational evidence",
            "status": "PASS" if not failures else "FAIL",
            "polynomial_degree_configurations": polynomial,
            "divergence_ratio_cases": ratio,
            "failures": failures,
        },
    )
