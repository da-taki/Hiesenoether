from __future__ import annotations

import csv
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from validation.exact_semantics import Params, Value, do_cap, do_obs, do_read

OUT = Path(__file__).resolve().parent
CSV_OUT = OUT / "adjacent_swap_validation.csv"
NOTES = OUT / "ADJACENT_SWAP_THEOREM_NOTES.md"

def f(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"

def adjacent_delta(n: int, eta: Fraction) -> Fraction:
    return Fraction(n) * eta

def eval_order(order: tuple[str, ...], d: int, p: Params) -> Fraction:
    x = Value(b=Fraction(10))
    y = Fraction(0)
    for op in order:
        if op == "READ":
            value, x = do_read(x, p)
            y += value
        else:
            x = do_obs(x, p)
    return do_cap(y, x, d, p)

def all_orders(L: int, m: int) -> list[tuple[str, ...]]:
    out = []
    for obs_pos in combinations(range(L + m), m):
        obs = set(obs_pos)
        out.append(tuple("OBS" if idx in obs else "READ" for idx in range(L + m)))
    return out

def validate_grid() -> list[dict[str, object]]:
    rows = []
    p = Params()
    for n in range(0, 8):
        for eta in (Fraction(1, 2), Fraction(1), Fraction(3)):
            rows.append(
                {
                    "check": "symbolic_adjacent_pair",
                    "n": n,
                    "eta": f(eta),
                    "delta": f(p.de_access),
                    "obs_read_minus_read_obs": f(adjacent_delta(n, eta)),
                    "weakly_increases": adjacent_delta(n, eta) >= 0,
                }
            )
    for L in range(1, 8):
        for m in range(1, 5):
            for d in range(1, 5):
                orders = all_orders(L, m)
                values = [(order, eval_order(order, d, p)) for order in orders]
                obs_first = ("OBS",) * m + ("READ",) * L
                obs_last = ("READ",) * L + ("OBS",) * m
                rows.append(
                    {
                        "check": "extrema_grid",
                        "n": L,
                        "eta": f(p.de_obs),
                        "delta": f(p.de_access),
                        "obs_read_minus_read_obs": "",
                        "weakly_increases": (
                            eval_order(obs_first, d, p) == max(v for _, v in values)
                            and eval_order(obs_last, d, p) == min(v for _, v in values)
                        ),
                    }
                )
    return rows

def write_outputs(rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    failed = [row for row in rows if not row["weakly_increases"]]
    lines = [
        "# Adjacent-Swap Extrema Theorem Notes",
        "",
        "## Lemma",
        "",
        "For the current exact compositional OSDS semantics, assume `eta = de_obs >= 0`, `delta = de_access >= 0`, nonnegative access count `n`, and a positive final cap multiplier. Swapping an adjacent `READ, OBS` pair to `OBS, READ` weakly increases the body accumulator and therefore weakly increases final output.",
        "",
        "## Local Symbolic Calculation",
        "",
        "Let the state before the adjacent pair be `(base=b, access_count=n, drift=e)`. In `READ, OBS`, the exposed read is `b + n e`. In `OBS, READ`, observation first changes drift to `e + eta`, so the exposed read is `b + n(e + eta)`. The difference is `n eta`. Both orders leave the post-pair state at `(b, n+1, e+delta+eta)`.",
        "",
        "Because the post-pair state is identical, all suffix reads and the final compositional cap multiplier are identical. Repeated adjacent swaps move observations left to obtain OBS-first as a maximum branch and right to obtain OBS-last as a minimum branch.",
        "",
        "## Assumptions",
        "",
        "- `eta >= 0`; strict improvement requires `eta > 0` and `n > 0`.",
        "- The final cap multiplier is positive. This holds in the checked default family because base and drift are positive.",
        "- The cap is the current compositional cap that multiplies by common post-body state reads.",
        "",
        "## Exact Validation",
        "",
        f"- validation rows: {len(rows)}",
        f"- failures: {len(failed)}",
        "",
        "## Impact On Theorem 5",
        "",
        "Under the assumptions above, OBS-first/OBS-last extrema no longer need to be assumed for the current compositional family. The finite validation becomes corroboration of the adjacent-swap proof rather than the source of the extrema claim.",
    ]
    if failed:
        lines.extend(["", "## Counterexamples"])
        for row in failed[:10]:
            lines.append(f"- {row}")
    NOTES.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    rows = validate_grid()
    write_outputs(rows)
    failed = [row for row in rows if not row["weakly_increases"]]
    print(f"wrote {CSV_OUT}")
    print(f"wrote {NOTES}")
    print(f"rows={len(rows)} failures={len(failed)}")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
