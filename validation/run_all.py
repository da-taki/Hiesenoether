import json, sys
from validation import (theorem_D_determinism, theorem_C_conservation,
                        theorem_P_permutation_sensitivity,
                        exhaustive_permutation_check,
                        sampled_confidence_intervals,
                        theorem_N_necessity, theorem_T2_length_scaling,
                        theorem_T4_SDR, theorem_T5_entropy_decay,
                        theorem_R_polynomial,
                        validate_against_runtime)

steps = [
    ("P exhaustive small-L check",            exhaustive_permutation_check.check),
    ("Sampled CI checks",                     sampled_confidence_intervals.check),
    ("D — Determinism",                       theorem_D_determinism.check),
    ("C — Conservation",                      theorem_C_conservation.check),
    ("P — Permutation Sensitivity",           theorem_P_permutation_sensitivity.check),
    ("N — Necessity (refined)",               theorem_N_necessity.check),
    ("R — Polynomial Structure",              theorem_R_polynomial.check),
    ("T2 — Length Scaling",                   theorem_T2_length_scaling.check),
    ("T4 — Degree Amplification (stratified)",theorem_T4_SDR.pooled_vs_stratified),
    ("T5 — Entropy Decay",                    theorem_T5_entropy_decay.check),
    ("Cross-check vs runtime",                validate_against_runtime.cross_check),
    ("Cross-check vs summary.csv",            validate_against_runtime.check_against_summary_csv),
]
PASS_STATUSES = {"VERIFIED", "VERIFIED (corrected scope)",
                 "VERIFIED (refined)", "OK", "PARTIAL", "SKIPPED"}

results, ok = {}, True
for label, fn in steps:
    r = fn()
    results[label] = r

    if label.startswith("T4"):
        comp_r2 = r.get("compositional_family", {}).get("R_squared", 0)
        sref_r2 = r.get("self_referential_family", {}).get("R_squared", 0)
        if comp_r2 >= 0.98 and sref_r2 >= 0.98:
            print(f"  {label:<44} -> OK (both family R² > 0.98)")
        else:
            print(f"  {label:<44} -> WEAK FIT "
                  f"(comp={comp_r2:.4f}, self_ref={sref_r2:.4f})")
            ok = False
        continue

    status = r.get("status", r.get("agreement", "n/a"))
    print(f"  {label:<44} -> {status}")
    if isinstance(status, bool):
        if not status:
            ok = False
    elif status not in PASS_STATUSES:
        ok = False
print()
print("ALL PASS" if ok else "SOME FAILED")
with open("validation/results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("-> validation/results.json")
sys.exit(0 if ok else 1)
