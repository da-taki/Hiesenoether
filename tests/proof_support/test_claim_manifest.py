from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "proof_support" / "generate_claim_manifest.py"
RESULT = REPO / "results" / "proof_support" / "claim_manifest.json"

REQUIRED_CLAIMS = {
    "fixed-order determinism",
    "identity-observation zero divergence",
    "access-insensitive-read zero divergence",
    "linear cap preserves body-level divergence",
    "nonlinear cap amplification",
    "degree relationship",
    "divergence-ratio relationship",
    "zero-observation configurations have zero divergence in the sweep",
    "linear cap positive divergence in 240 configs",
    "nonlinear cap amplified in 1,680 configs",
    "no nonlinear amplification counterexamples in tested region",
    "240 exhaustive configurations",
    "sample-vs-exact range misses",
    "sampling convergence at budget 1024",
    "analyzer controlled benchmark recall",
    "analyzer controlled benchmark precision",
    "reviewed PyPI precision",
    "expanded PyPI screening scale",
    "production prevalence",
}

def load_manifest() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=REPO, check=True)
    assert RESULT.exists()
    return json.loads(RESULT.read_text(encoding="utf-8"))

def by_claim(manifest: dict) -> dict[str, dict]:
    return {row["claim"]: row for row in manifest["claims"]}

def test_manifest_exists_and_has_required_claims() -> None:
    manifest = load_manifest()
    claims = by_claim(manifest)
    assert REQUIRED_CLAIMS <= set(claims)

def test_unsupported_claim_is_not_proved() -> None:
    claims = by_claim(load_manifest())
    production = claims["production prevalence"]
    assert production["classification"] == "unsupported / should not be claimed"
    assert production["evidence_level"] != "Formal proof"

def test_empirical_and_bounded_claims_are_not_theorems() -> None:
    claims = by_claim(load_manifest())
    assert claims["nonlinear cap amplification"]["evidence_level"] != "Formal proof"
    assert claims["nonlinear cap amplification"]["classification"] == "empirical finding"
    assert claims["degree relationship"]["classification"] == "bounded exact computational finding"
    assert claims["divergence-ratio relationship"]["classification"] == "bounded exact computational finding"

def test_analyzer_is_not_marked_sound() -> None:
    claims = by_claim(load_manifest())
    analyzer_claims = [
        claims["analyzer controlled benchmark recall"],
        claims["analyzer controlled benchmark precision"],
        claims["reviewed PyPI precision"],
        claims["expanded PyPI screening scale"],
    ]
    for claim in analyzer_claims:
        text = " ".join(str(value).lower() for value in claim.values())
        assert "not analyzer soundness" in text or "not precision or recall" in text
        assert claim["evidence_level"] != "Formal proof"
