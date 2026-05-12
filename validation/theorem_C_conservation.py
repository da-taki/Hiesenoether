"""Theorem C (Conservation): n, e are monotone non-decreasing along every trace."""
from __future__ import annotations
from itertools import permutations
from validation.exact_semantics import trace, Params


def check(L_max: int = 4, m_max: int = 3, degrees=(1, 2, 3, 4)) -> dict:
    p = Params()
    checked = 0
    for L in range(1, L_max + 1):
        for m in range(0, m_max + 1):
            for d in degrees:
                body = ("READ",) * L + ("OBS",) * m
                for perm in set(permutations(body)):
                    h = trace(perm, d, p)
                    prev_n, prev_e = 0, h[0][2].e
                    for _, _, x in h:
                        if x.n < prev_n or x.e < prev_e:
                            return {"theorem": "C", "status": "REFUTED",
                                    "counterexample": (perm, d)}
                        prev_n, prev_e = x.n, x.e
                    checked += 1
    return {"theorem": "C", "status": "VERIFIED",
            "configurations_checked": checked,
            "scope": f"L<={L_max}, m<={m_max}, d in {degrees}"}


if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))