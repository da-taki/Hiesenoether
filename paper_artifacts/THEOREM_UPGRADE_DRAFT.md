# Theorem Upgrade Draft

## Proposed Theorem Statement

Restricted compositional OSDS degree theorem. Fix positive rational parameters eta=de_obs and delta=de_access, a fixed observation count m>=1, and a compositional cap degree d>=1. For executions containing L READ operations and m OBS operations, assume the OBS-first permutation realizes the maximum output and the OBS-last permutation realizes the minimum output. Then the output range is a polynomial in L of degree 2d. Its leading coefficient is eta*m*delta^(d-1)/2.

## Assumptions

- The cap is the repository's current compositional cap: the body accumulator is multiplied by d-1 final reads of the same evolving state.
- Parameters eta and delta are positive rationals.
- m and d are fixed while L varies.
- The extrema branches are OBS-first for max and OBS-last for min.

## Proof Sketch

The body accumulator for each fixed branch is polynomial in L. The max and min branch accumulators have the same degree-3 leading term from ordinary access drift, so their accumulator difference cancels to degree 2 with leading coefficient eta*m/2. After the body, the x state is order-independent for fixed L and m. Each final cap read contributes a quadratic-in-L factor with leading coefficient delta. The common cap multiplier therefore has degree 2(d-1) and leading coefficient delta^(d-1). Multiplying the degree-2 accumulator range by this common factor gives degree 2+2(d-1)=2d and leading coefficient eta*m*delta^(d-1)/2.

## Repo Validation Support

- Exact rational cases checked: 20.
- Corrected theorem pass status: all checked cases pass.
- Grid: m=1..4, d=1..5, L=2..15.
- Exact holdout interpolation checks passed for every generated row.
- Extrema stability was checked by exhaustive unique-order enumeration on the stated finite grid.

## What Remains Bounded Computational Evidence

- Extrema stability is checked on L=2..15, not proved for all L.
- The older preferred d*q theorem is not supported by the current compositional cap family.
- The divergence-ratio result remains bounded computational evidence unless the external runtime model is promoted to an explicit formal object.

## Manuscript-Ready Table Text

The corrected compositional OSDS degree validation checked 20 exact-rational configurations (m=1..4, d=1..5) and all 20 matched the restricted 2d range-degree theorem on L=2..15. The previously suggested d*q form failed on the smallest checked case (m=1,d=1), because branch leading terms cancel before the range is formed.
