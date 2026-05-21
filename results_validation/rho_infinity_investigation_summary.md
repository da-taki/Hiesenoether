# Rho Infinity Investigation

## Scope

- default grid: m=1..5, d=1..5
- default parameters: eta=1, delta=1/10, base=10
- variant sweeps: selected eta, delta, and base changes
- arithmetic: exact `fractions.Fraction` rational arithmetic
- runtime model: generalized compositional runtime formula external to core interpreter semantics

## Default Cases

- default cases checked: 25
- default cases where rho_infinity = 5: 25
- default cases where rho_infinity != 5: 0
- interpolation holdout failures: 0

Representative leading coefficients:

| m | d | OSDS lead | runtime lead | rho_infinity |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 1/2 | 1/10 | 5/1 |
| 1 | 2 | 1/20 | 1/100 | 5/1 |
| 3 | 4 | 3/2000 | 3/10000 | 5/1 |
| 5 | 5 | 1/4000 | 1/20000 | 5/1 |

## Parameter Variants

The checked data match the simple pattern `rho_infinity = eta / (2 * delta)` for every default and variant case. Changing base did not affect the leading-coefficient ratio in the checked cases; changing eta or delta changed rho according to that expression.

- variant cases checked: 9
- cases not matching eta/(2delta): 0

## Supported Conjecture

For the external generalized compositional runtime model and the OSDS extremal-order formula, the data support the conjecture that the leading cap factors cancel and `rho_infinity = eta / (2 * delta)` for positive delta. Under the default parameters eta=1 and delta=1/10, this gives rho_infinity=5.

This is not a formal proof for the manuscript unless the algebraic derivation is completed and reviewed; it is exact computational evidence plus a proof sketch target.

Default non-5 cases: none
