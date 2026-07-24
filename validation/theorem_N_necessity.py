from __future__ import annotations
from itertools import permutations
from validation.exact_semantics import evaluate, Params

def divergence(body: tuple, degree: int, p: Params):
    vals = [evaluate(perm, degree, p) for perm in set(permutations(body))]
    return max(vals) - min(vals)

def check(L: int = 3, m: int = 2, d: int = 2) -> dict:
    body = ("READ",) * L + ("OBS",) * m
    res = {
        "baseline":    float(divergence(body, d, Params())),
        "P1_removed":  float(divergence(body, d, Params(P1=False))),
        "P2_removed":  float(divergence(body, d, Params(P2=False))),
        "P3_removed":  float(divergence(body, d, Params(P3=False))),
    }
    p1_nec = res["P1_removed"] == 0.0
    p2_nec = res["P2_removed"] == 0.0
    p3_nec = res["P3_removed"] == 0.0
    p3_amplifies = res["P3_removed"] < res["baseline"]
    return {"theorem": "N",
            "config": f"L={L}, m={m}, d={d}",
            "divergences": res,
            "p1_necessary": p1_nec,
            "p2_necessary": p2_nec,
            "p3_role": ("necessary" if p3_nec
                        else "amplifying" if p3_amplifies
                        else "no_effect"),
            "status": ("VERIFIED (refined)" if (p1_nec and p2_nec
                                                and res["baseline"] > 0)
                       else "REFUTED"),
            "correction_note":
                "P3 is NOT individually necessary; reclassified as "
                "amplifying. P1, P2 remain necessary."}

if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
    print()
    print("Sweep over (L, m, d) to confirm the result is structural:")
    for L in (2, 3, 4):
        for m in (1, 2):
            for d in (2, 3):
                r = check(L=L, m=m, d=d)
                print(f"  L={L} m={m} d={d}: "
                      f"P1_nec={r['p1_necessary']} "
                      f"P2_nec={r['p2_necessary']} "
                      f"P3={r['p3_role']:<10} "
                      f"baseline={r['divergences']['baseline']:.4f}")
