from __future__ import annotations
from itertools import permutations
from fractions import Fraction
from validation.exact_semantics import evaluate, Params

def check(L_max: int = 4, m_max: int = 3,
          degrees=(1, 2, 3, 4), trials: int = 5) -> dict:
    p = Params()
    checked = 0
    for L in range(1, L_max + 1):
        for m in range(0, m_max + 1):
            for d in degrees:
                body = ("READ",) * L + ("OBS",) * m
                for perm in set(permutations(body)):
                    vals = {evaluate(perm, d, p) for _ in range(trials)}
                    if len(vals) != 1:
                        return {"theorem": "D", "status": "REFUTED",
                                "counterexample": (perm, d), "values": list(vals)}
                    checked += 1
    return {"theorem": "D", "status": "VERIFIED",
            "configurations_checked": checked,
            "scope": f"L<={L_max}, m<={m_max}, d in {degrees}, trials={trials}"}

if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
