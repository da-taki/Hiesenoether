# Polynomial Degree Theorem Notes

## What Was Checked

- Family: current compositional OSDS exact semantics.
- Grid: m=1..4, cap degree d=1..5, L=2..15.
- Arithmetic: `fractions.Fraction` exact rational arithmetic.
- Enumeration: unique OBS-position combinations, not duplicate tuple permutations.
- Denominators: all leading coefficients in CSV are serialized as numerator/denominator.

## Result

- Cases checked: 20.
- Corrected 2d degree passes: 20/20.
- Preferred d*q degree matches observed degree: 0/20.

The preferred theorem shape does not fit this repository's current compositional cap semantics. In the checked family, each branch accumulator is a degree-3 polynomial in L, but the degree-3 leading coefficient is common to the max and min branches. The cap then multiplies both branches by the same post-body state-read factor. The leading output terms cancel in the range, leaving degree 2d rather than d*q.

## Corrected Restricted Theorem

For positive eta and delta in the compositional OSDS family, with m fixed and d>=1, if all OBS operations precede all READ operations for the maximum branch and follow all READ operations for the minimum branch, then the output range over L READ operations is a polynomial in L of degree 2d with leading coefficient eta*m*delta^(d-1)/2.

## Counterexample To Preferred d*q Form

For m=1 and d=1, both extrema accumulators have degree q=3, so d*q=3. The exact output range has degree 2 and leading coefficient 1/2. This is the smallest checked counterexample.

## Divergence-Ratio Corollary Status

The existing `validation/rho_infinity_investigation.py` data support a leading-coefficient cancellation formula, rho_infinity = eta/(2*delta), for the external generalized compositional runtime model. This can be presented as a corollary only if the runtime model and extrema assumptions are stated explicitly; otherwise it remains exact bounded computational evidence plus a derivation target.
