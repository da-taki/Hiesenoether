# Extended Polynomial Degree Verification

## Scope

- cap family: compositional OSDS caps
- m range: 1..4
- d range: 1..5
- L interpolation range: 2..14
- holdout L: 15
- arithmetic: exact `fractions.Fraction` rational arithmetic

## Method

For each `(m,d)`, the script computes an exact extremal-order range formula and checks that formula against exhaustive permutation enumeration for small L values. It then performs finite-difference degree detection and rational Lagrange interpolation on the exact extremal-order values, followed by exact holdout prediction.

The exhaustive checks are finite-grid checks over L=2..8. The larger-L interpolation evidence is exact extremal-order verification, not full exhaustive verification. It is not a formal proof for all L.

## d+2 Result

- cases checked: 20
- cases passing detected degree = d+2: 4
- cases failing detected degree = d+2: 16
- cases matching detected degree = 2d: 20
- holdout failures: 0
- extremal-vs-exhaustive failures: 0

Cases passing d+2:
- m=1, d=2, degree=4
- m=2, d=2, degree=4
- m=3, d=2, degree=4
- m=4, d=2, degree=4

Cases failing d+2:
- m=1, d=1: detected degree 2; expected d+2=3; reason: detected degree 2, not expected d+2=3
- m=1, d=3: detected degree 6; expected d+2=5; reason: detected degree 6, not expected d+2=5
- m=1, d=4: detected degree 8; expected d+2=6; reason: detected degree 8, not expected d+2=6
- m=1, d=5: detected degree 10; expected d+2=7; reason: detected degree 10, not expected d+2=7
- m=2, d=1: detected degree 2; expected d+2=3; reason: detected degree 2, not expected d+2=3
- m=2, d=3: detected degree 6; expected d+2=5; reason: detected degree 6, not expected d+2=5
- m=2, d=4: detected degree 8; expected d+2=6; reason: detected degree 8, not expected d+2=6
- m=2, d=5: detected degree 10; expected d+2=7; reason: detected degree 10, not expected d+2=7
- m=3, d=1: detected degree 2; expected d+2=3; reason: detected degree 2, not expected d+2=3
- m=3, d=3: detected degree 6; expected d+2=5; reason: detected degree 6, not expected d+2=5
- m=3, d=4: detected degree 8; expected d+2=6; reason: detected degree 8, not expected d+2=6
- m=3, d=5: detected degree 10; expected d+2=7; reason: detected degree 10, not expected d+2=7
- m=4, d=1: detected degree 2; expected d+2=3; reason: detected degree 2, not expected d+2=3
- m=4, d=3: detected degree 6; expected d+2=5; reason: detected degree 6, not expected d+2=5
- m=4, d=4: detected degree 8; expected d+2=6; reason: detected degree 8, not expected d+2=6
- m=4, d=5: detected degree 10; expected d+2=7; reason: detected degree 10, not expected d+2=7

## Skipped Or Timed Out

No cases were skipped or timed out.

## Mechanized Support Beyond d <= 2

The script expands exact checked evidence beyond d <= 2 by evaluating d=3, d=4, and d=5 for m=1..4. The expanded evidence does not support the unqualified d+2 degree claim for the current compositional-degree parameterization; it instead detects degree 2d for every checked d=1..5 case.
