from __future__ import annotations

from .evidence_checks import (
    check_access_insensitive_reads_zero_divergence,
    check_bounded_computational_claims,
    check_composition_amplification,
    check_fixed_order_determinism,
    check_identity_observation_zero_divergence,
)

def test_fixed_order_determinism():
    summary = check_fixed_order_determinism()
    assert summary["status"] == "PASS"
    assert summary["mismatches"] == []

def test_identity_observation_gives_zero_divergence():
    summary = check_identity_observation_zero_divergence()
    assert summary["status"] == "PASS"
    assert summary["counterexamples"] == []

def test_access_insensitive_reads_give_zero_divergence():
    summary = check_access_insensitive_reads_zero_divergence()
    assert summary["status"] == "PASS"
    assert summary["counterexamples"] == []

def test_composition_amplification_empirical_evidence():
    summary = check_composition_amplification()
    assert summary["status"] == "PASS"
    assert summary["failures"] == []

def test_bounded_computational_claims_match_checked_data():
    summary = check_bounded_computational_claims()
    assert summary["status"] == "PASS"
    assert summary["failures"] == []
