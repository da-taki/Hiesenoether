# Adjacent-Swap Extrema Theorem Notes

## Lemma

For the current exact compositional OSDS semantics, assume `eta = de_obs >= 0`, `delta = de_access >= 0`, nonnegative access count `n`, and a positive final cap multiplier. Swapping an adjacent `READ, OBS` pair to `OBS, READ` weakly increases the body accumulator and therefore weakly increases final output.

## Local Symbolic Calculation

Let the state before the adjacent pair be `(base=b, access_count=n, drift=e)`. In `READ, OBS`, the exposed read is `b + n e`. In `OBS, READ`, observation first changes drift to `e + eta`, so the exposed read is `b + n(e + eta)`. The difference is `n eta`. Both orders leave the post-pair state at `(b, n+1, e+delta+eta)`.

Because the post-pair state is identical, all suffix reads and the final compositional cap multiplier are identical. Repeated adjacent swaps move observations left to obtain OBS-first as a maximum branch and right to obtain OBS-last as a minimum branch.

## Assumptions

- `eta >= 0`; strict improvement requires `eta > 0` and `n > 0`.
- The final cap multiplier is positive. This holds in the checked default family because base and drift are positive.
- The cap is the current compositional cap that multiplies by common post-body state reads.

## Exact Validation

- validation rows: 136
- failures: 0

## Impact On Theorem 5

Under the assumptions above, OBS-first/OBS-last extrema no longer need to be assumed for the current compositional family. The finite validation becomes corroboration of the adjacent-swap proof rather than the source of the extrema claim.
