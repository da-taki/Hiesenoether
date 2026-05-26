# Access-Counter-Indexed Abstract Domain

This prototype is a parallel artifact to the existing syntactic analyzer in
`analysis/oc_static.py`. It does not parse arbitrary Python and it does not
replace the heuristic class scanner. It analyzes the straight-line OSDS fragment
with `L` additive reads of `x`, `m` inspections of `x`, and a compositional cap
of degree `d`.

## Domain

An unstable value is represented as:

```text
AbstractUnstable = (B, N, E)
```

where `B`, `N`, and `E` are closed intervals over exact
`fractions.Fraction` values. `B` abstracts the base value, `N` abstracts the
access count, and `E` abstracts the entropy parameter. Stable values and the
accumulator `y` are represented as a single interval.

## Transitions

- Read:

```text
exposed = B + N * E
N' = N + [1, 1]
E' = E + [delta, delta]
```

- Inspect:

```text
E' = E + [eta, eta]
```

- Additive update:

```text
y <- y + read(x)
```

- Compositional cap:

```text
y <- y * read(x)^(d - 1)
```

The primitive interval operations are implemented in
`analyzer/abstract_domain.py`. The straight-line order summary is implemented in
`analyzer/abstract_interpreter.py`.

## Order Summary

The prototype avoids general control-flow joins by summarizing orderings with
the counts `(k, j)`, where `k` is the number of additive reads already performed
and `j` is the number of inspections already performed. For positive default
parameters, the largest body accumulator occurs when inspections precede reads,
and the smallest occurs when inspections follow reads. This gives:

```text
body_spread = eta * m * L * (L - 1) / 2
```

After the body, the cap state of `x` is order-independent in this OSDS fragment:
`x` has been read `L` times and inspected `m` times. The compositional cap
therefore multiplies the body spread by the product of the final `d - 1` reads
of `x`.

The returned divergence interval is `[0, B]`, where:

```text
B = body_spread * cap_factor
```

For this restricted fragment and the default positive parameters, this matches
the exhaustive concrete OSDS range. The implementation keeps the wording local
to this fragment; it is not a sound analyzer for arbitrary Python programs.

## Test Results

Run:

```powershell
py analyzer\test_abstract.py
```

Observed results:

| case | L | m | d | B | concrete divergence | B / actual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| no divergence expected | 1 | 0 | 1 | 0 | 0 | undefined |
| small divergence expected | 3 | 1 | 1 | 3 | 3 | 1 |
| large divergence expected | 3 | 2 | 2 | 597/5 | 597/5 | 1 |

The large case is `119.4` in decimal notation. The code prints the exact
rational value `597/5`.

## Where The Abstraction Loses Precision

The interval domain does not record which body reads occurred after which
inspections. If the primitive transitions alone are joined after each possible
ordering, the entropy interval `E` forgets the read/inspection correlation and
can pair a high entropy with reads that could not have seen it concretely.

This prototype compensates with the `(k, j)` straight-line summary and the
closed-form body-spread bound. That is precise for the tested positive-parameter
fragment, but it is not a general solution to join points, loops, aliasing,
multiple unstable sources, dynamic dispatch, or arbitrary Python control flow.

## Extended validation

Run:

```powershell
py analyzer\test_abstract_extended.py
```

All configurations below were checked by exhaustive enumeration; none required
the sampled fallback because every case has `L + m <= 8`.

| Config | Abstract bound B | Concrete divergence | Precision ratio | Abstract time (ms) | Concrete time (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| L=4, m=2, d=3 | 7788 | 7788 | 1 | 0.283 | 0.616 |
| L=5, m=3, d=2 | 975 | 975 | 1 | 0.142 | 1.918 |
| L=6, m=2, d=4 | 34373532/25 | 34373532/25 | 1 | 0.213 | 1.327 |
| L=3, m=2, cap=y^2 * read(x) | 43581/5 | 43581/5 | 1 | 0.103 | 0.389 |
| L=4, m=2, cap=y^3 * read(x) | 304110072/125 | 304110072/125 | 1 | 0.110 | 0.474 |
| L=2, m=0, d=2 | 0 | 0 | 1 | 0.083 | 0.028 |
| L=1, m=5, d=3 | 0 | 0 | 1 | 0.102 | 0.165 |

### Where the abstraction stays tight

- `L=4, m=2, d=3`, `L=5, m=3, d=2`, and `L=6, m=2, d=4` stay tight because the compositional cap's final `x` state is order-independent after the body; the only order-dependent quantity is the body accumulator spread, and the access-counter-indexed summary captures its extremal range exactly for positive parameters.
- `L=3, m=2, cap=y^2 * read(x)` and `L=4, m=2, cap=y^3 * read(x)` stay tight because the body accumulator interval has exact positive lower and upper endpoints, so interval exponentiation over `[y_min, y_max]` is exact for these monotone self-referential caps.
- `L=2, m=0, d=2` and `L=1, m=5, d=3` stay tight at zero: with no inspections there is no order-sensitive entropy injection, and with only one additive read the body has no read-read ordering freedom for inspections to amplify.

### Where the abstraction loses precision

No precision-loss case was observed in this stress set. This is a useful negative result, but it is narrow: these programs are still single-source, straight-line, positive-parameter cases where the final `x` cap state is order-independent and the body accumulator is monotone in the number of preceding inspections.

The expected precision loss has not been exercised yet. It should appear once the program shape forces the analysis to join states that differ in correlations, for example when multiple unstable values are interleaved, when a cap expression mixes independently widened intervals, or when a control-flow join merges states where high entropy and high access count are not simultaneously feasible.

### Implications for refinement

A tighter next domain should record relational facts between access count,
entropy, and accumulator contribution, not just independent intervals. A
path-sensitive analysis could keep separate states per ordering-equivalence
class for small `L + m`, then fall back to the interval bound when enumeration
becomes too expensive. A bounded hybrid would be especially useful here:
enumerate exact straight-line schedules up to a configured threshold and use the
abstract count-indexed bound beyond that threshold.
