from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO / "results" / "proof_support"
JSON_PATH = RESULTS_DIR / "claim_manifest.json"
MD_PATH = RESULTS_DIR / "claim_manifest.md"

CLAIMS: list[dict] = [
    {"claim": "fixed-order determinism", "classification": "proved in paper", "evidence_level": "Formal proof", "artifact": "docs/formal_proof_appendix.md#3-proposition-1-fixed-order-determinism", "scope": "fixed initial configuration, fixed operation sequence, deterministic transitions", "non_claim": "not a claim about nondeterministic hosts or arbitrary Python effects"},
    {"claim": "identity-observation zero divergence", "classification": "proved in paper", "evidence_level": "Formal proof", "artifact": "docs/formal_proof_appendix.md#4-proposition-2-identity-observation-zero-divergence", "scope": "studied template with g(d) = d and identical read/add operation multiset", "non_claim": "not a claim about observations that mutate latent state"},
    {"claim": "access-insensitive-read zero divergence", "classification": "proved in paper", "evidence_level": "Formal proof", "artifact": "docs/formal_proof_appendix.md#5-proposition-3-access-insensitive-read-zero-divergence", "scope": "studied template with f(b, a, d) = h(b)", "non_claim": "not a claim about access-sensitive or drift-sensitive reads"},
    {"claim": "linear cap preserves body-level divergence", "classification": "proved in paper", "evidence_level": "Formal proof", "artifact": "docs/formal_proof_appendix.md#6-proposition-4-linear-cap-preserves-body-level-divergence", "scope": "linear cap alpha*x + beta with alpha != 0", "non_claim": "not a nonlinear amplification theorem"},
    {"claim": "nonlinear cap amplification", "classification": "empirical finding", "evidence_level": "Empirical sweep", "artifact": "results/review_experiments/expanded_mechanism_sweep_summary.json", "scope": "tested region of expanded mechanism sweep", "non_claim": "not universally proved"},
    {"claim": "degree relationship", "classification": "bounded exact computational finding", "evidence_level": "Exact bounded enumeration", "artifact": "validation/theorem_R_polynomial.py; validation/theorem_T4_SDR.py", "scope": "bounded validation grids and reported exact-rational checks", "non_claim": "not a theorem for all OSDS programs"},
    {"claim": "divergence-ratio relationship", "classification": "bounded exact computational finding", "evidence_level": "Exact bounded enumeration", "artifact": "validation/rho_infinity_investigation.py; validation/results.json", "scope": "bounded validation grids", "non_claim": "not a universal asymptotic law"},
    {"claim": "zero-observation configurations have zero divergence in the sweep", "classification": "bounded exact computational finding", "evidence_level": "Exact rational replay", "artifact": "results/review_experiments/expanded_mechanism_sweep_summary.json", "scope": "2,112-configuration sweep subset with observation_count = 0", "non_claim": "not a claim about every possible program shape"},
    {"claim": "linear cap positive divergence in 240 configs", "classification": "bounded exact computational finding", "evidence_level": "Exact rational replay", "artifact": "results/review_experiments/expanded_mechanism_sweep_summary.json", "scope": "expanded mechanism sweep configurations", "non_claim": "not a universal lower bound"},
    {"claim": "nonlinear cap amplified in 1,680 configs", "classification": "empirical finding", "evidence_level": "Empirical sweep", "artifact": "results/review_experiments/expanded_mechanism_sweep_summary.json", "scope": "tested positive-observation nonlinear cap configurations", "non_claim": "not universally proved"},
    {"claim": "no nonlinear amplification counterexamples in tested region", "classification": "empirical finding", "evidence_level": "Empirical sweep", "artifact": "results/review_experiments/expanded_mechanism_sweep_summary.json", "scope": "tested region only", "non_claim": "not absence of counterexamples outside the tested region"},
    {"claim": "240 exhaustive configurations", "classification": "bounded exact computational finding", "evidence_level": "Exact bounded enumeration", "artifact": "results/review_experiments/extended_exhaustive_enumeration_summary.json", "scope": "body lengths 2 through 9, observation counts 0 through 5, cap degrees 1 through 5 under cutoff", "non_claim": "not exhaustive over all body sizes"},
    {"claim": "sample-vs-exact range misses", "classification": "bounded exact computational finding", "evidence_level": "Exact bounded enumeration", "artifact": "results/review_experiments/extended_exhaustive_enumeration_summary.json", "scope": "cases where exact and sampled ranges are both available", "non_claim": "not a statement about every sampling policy"},
    {"claim": "sampling convergence at budget 1024", "classification": "empirical finding", "evidence_level": "Empirical sweep", "artifact": "results/review_experiments/sampling_convergence_summary.json", "scope": "sampled budgets and seeds in the convergence study", "non_claim": "not exact extrema unless exhaustive enumeration is used"},
    {"claim": "analyzer controlled benchmark recall", "classification": "empirical finding", "evidence_level": "Source-inspection evaluation", "artifact": "results/review_experiments/extended_controlled_benchmark_summary.json", "scope": "64 labeled controlled classes", "non_claim": "not analyzer soundness"},
    {"claim": "analyzer controlled benchmark precision", "classification": "empirical finding", "evidence_level": "Source-inspection evaluation", "artifact": "results/review_experiments/extended_controlled_benchmark_summary.json", "scope": "64 labeled controlled classes", "non_claim": "not analyzer soundness"},
    {"claim": "reviewed PyPI precision", "classification": "empirical finding", "evidence_level": "Source-inspection evaluation", "artifact": "results/pypi_reviewed_findings.csv", "scope": "manual review of 278 MEDIUM/HIGH findings", "non_claim": "not production prevalence and not analyzer soundness"},
    {"claim": "expanded PyPI screening scale", "classification": "analyzer screening result", "evidence_level": "Screening-scale evidence", "artifact": "results/review_experiments/pypi_expanded_screen_summary.json", "scope": "cache-only screen of 116 packages", "non_claim": "not precision or recall until manual labels are completed"},
    {"claim": "production prevalence", "classification": "unsupported / should not be claimed", "evidence_level": "Screening-scale evidence", "artifact": "none", "scope": "no production-prevalence design is present", "non_claim": "should not be claimed"},
]

def write_markdown(payload: dict) -> None:
    lines = [
        "# Claim Manifest",
        "",
        "This manifest classifies paper claims by evidence level so artifact drafting does not turn bounded or empirical findings into theorems.",
        "",
        "| Claim | Classification | Evidence level | Artifact | Scope | Non-claim |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for claim in payload["claims"]:
        lines.append(
            "| {claim} | {classification} | {evidence_level} | `{artifact}` | {scope} | {non_claim} |".format(
                **claim
            )
        )
    lines.append("")
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")

def build_manifest() -> dict:
    return {
        "schema_version": 1,
        "machine_checked": False,
        "machine_checked_reason": "Lean version/build commands timed out locally; no compiled theorem is claimed.",
        "claims": CLAIMS,
    }

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_manifest()
    JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"wrote {JSON_PATH}")
    print(f"wrote {MD_PATH}")
    print(f"claims={len(payload['claims'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
