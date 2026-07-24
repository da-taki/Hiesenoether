# Formal Proof Appendix

This appendix states the proof core for the studied OSDS template. It is intended as artifact text, not as an experiment log.

## 1. Definitions

A semantic value is a tuple `(b, a, d)`. The base component `b` is the stable component of the value. The latent access count `a` records how many read transitions have occurred. The latent drift state `d` records hidden state that may be changed by reads or observations.

A store or configuration is `(x, y)`, where `x = (b, a, d)` is the semantic value and `y` is an accumulator. The initial configuration is fixed.

A read transition has the form

`read(b, a, d, y) = ((b, a + 1, r(a, d)), y + f(b, a, d))`,

where `f` is the exposed read value and `r` is the deterministic read-side latent-state update.

An observation transition has the form

`obs(b, a, d, y) = ((b, a, g(d)), y)`.

Observations expose no value to the additive body. They can affect later reads only through the latent update `g`.

An additive body update is the deterministic fold of read and observation transitions over an operation sequence. An operation sequence is a finite list over the alphabet `{READ, OBS}`. The body output is the final accumulator before the cap.

A cap or composition is a deterministic function `C` applied after body execution. The final output is `C(y)`, or more generally `C(y, x)` when the cap also reads the final latent value. Proposition 4 considers the linear cap `C(y) = alpha y + beta`.

For a fixed multiset of operations, divergence over a set of orderings is the difference between the maximum and minimum final outputs over those orderings, when the set is finite and exactly enumerated.

## 2. Assumptions

The propositions below assume exact arithmetic, deterministic transition functions, a fixed initial configuration, and a fixed operation multiset. The body contains read/add operations and observations. Observations expose no value.

Identity observation means `g(d) = d`. Access-insensitive read means `f(b, a, d) = h(b)`, so the exposed value ignores access count and latent drift. Caps are deterministic. Linear cap preservation assumes `C(y) = alpha y + beta` with `alpha != 0`.

The propositions apply to the studied straight-line template. They are not claims about arbitrary Python programs or about analyzer soundness.

## 3. Proposition 1: Fixed-Order Determinism

For a fixed initial configuration and a fixed operation sequence, body execution returns a unique final configuration and therefore a unique final output under a deterministic cap.

Proof. Proceed by induction on the length of the operation sequence.

Base case: the empty sequence performs no transition. The final configuration is the fixed initial configuration. Thus the result is unique.

Inductive step: assume every sequence of length `n` has a unique final configuration from the fixed initial configuration. Consider a sequence of length `n + 1`, written as `p ++ [op]`, where `p` has length `n`. By the induction hypothesis, executing `p` yields a unique configuration `(x, y)`. The final operation `op` is either `READ` or `OBS`. If `op = READ`, the read transition is a deterministic function, so it maps `(x, y)` to one unique next configuration. If `op = OBS`, the observation transition is also deterministic, so it maps `(x, y)` to one unique next configuration. Therefore the length `n + 1` sequence has a unique final configuration. A deterministic cap maps that final configuration to a unique output. By induction, fixed-order execution is deterministic.

## 4. Proposition 2: Identity-Observation Zero Divergence

Under the studied template assumptions, if observations are identity updates, then all permutations of a fixed multiset of identical read/add operations and inert observations produce the same body accumulator and the same final output under any deterministic cap that depends only on the resulting body accumulator and final latent state.

Proof. If `g(d) = d`, an observation transition leaves `(b, a, d)` unchanged and leaves `y` unchanged. Thus observations are semantically inert: inserting or moving an observation between reads does not change the latent state or accumulator.

After removing inert observations, every permutation of the same operation multiset has the same ordered list of read/add operations: a sequence of identical `READ` operations of the same length. The `k`-th read in this reduced sequence is reached after exactly `k` prior reads, with the same base component and the same latent drift as in every other permutation, because no observation has changed drift. Therefore the exposed read values are the same sequence in every permutation.

The body accumulator is the exact sum of that same read-value sequence. Exact addition is associative and deterministic, so the body accumulator is identical for all orderings. The final latent state is also identical because the same number of read updates and only identity observations occurred. A deterministic cap applied to identical body accumulator and identical final latent state gives identical final output. Hence the divergence over the set of such orderings is zero.

## 5. Proposition 3: Access-Insensitive-Read Zero Divergence

Under the studied template assumptions, if `f(b, a, d) = h(b)`, then all permutations of a fixed multiset of identical read/add operations and observations produce the same body accumulator. If the cap is deterministic and does not introduce order dependence beyond the final read count and observation count, the final output is also permutation-invariant.

Proof. Since `f(b, a, d) = h(b)`, every read exposes the same value for the fixed base component `b`, regardless of access count `a` or latent drift `d`. Observations may update `d`, and reads may update `a` and `d`, but none of those changes can alter exposed body read values.

For any ordering with `L` read/add operations, the body accumulator is therefore

`h(b) + h(b) + ... + h(b)` with `L` summands.

This sum depends only on `L`, not on the positions of observations. Since all compared orderings use the same operation multiset, they have the same `L`, so their body accumulators are equal. In the studied template, all such orderings also have the same final read count and observation count. A deterministic cap that depends only on the accumulator and those final counts gives the same output for all orderings. Thus divergence is zero.

## 6. Proposition 4: Linear Cap Preserves Body-Level Divergence

Let `C(y) = alpha y + beta` with `alpha != 0`. If two body accumulators `y1` and `y2` differ, then their capped outputs differ.

Proof. Suppose `y1 != y2`. Then `y1 - y2 != 0`. The capped difference is

`C(y1) - C(y2) = (alpha y1 + beta) - (alpha y2 + beta) = alpha (y1 - y2)`.

Since `alpha != 0` and `y1 - y2 != 0`, exact arithmetic gives `alpha (y1 - y2) != 0`. Therefore `C(y1) != C(y2)`. A nonzero-slope linear cap is injective and preserves unequal body accumulators.

## 7. Empirical and Bounded Computational Boundary

Nonlinear amplification is not proved generally. The sweep result that nonlinear caps amplify over the corresponding linear cap in the tested region is empirical over that region.

Degree relationships are bounded computational findings unless a separate proof is supplied. Divergence-ratio relationships are bounded computational findings unless a separate proof is supplied.

Sampled extrema are lower-bound estimates unless exhaustive enumeration is used. The sampling-convergence study shows that sampled extrema can miss exact extrema.

The analyzer is a syntactic screening tool. Controlled benchmark precision and recall, reviewed PyPI precision, and expanded PyPI screening scale are empirical or source-inspection results. They do not establish analyzer soundness and they do not establish production prevalence.

## 8. Claim-to-Evidence Table

| Paper claim | Evidence level | Proof or artifact | Scope | Non-claim |
| --- | --- | --- | --- | --- |
| Fixed-order determinism | Formal proof | Proposition 1 in this appendix | Deterministic studied template | Not a claim about nondeterministic hosts |
| Identity-observation zero divergence | Formal proof | Proposition 2 in this appendix | Identity observation, identical read/add multiset | Not a claim about mutating observations |
| Access-insensitive-read zero divergence | Formal proof | Proposition 3 in this appendix | Reads ignoring access count and drift | Not a claim about access-sensitive reads |
| Linear cap preserves body-level divergence | Formal proof | Proposition 4 in this appendix | Nonzero-slope linear cap | Not nonlinear amplification |
| Running example divergence | Exact rational replay | `results/proof_support/running_example_derivation.md` | Two specified operation orders | Not a prevalence claim |
| Nonlinear cap amplification | Empirical sweep | `results/review_experiments/expanded_mechanism_sweep_summary.json` | Tested region only | Not universally proved |
| Degree relationships | Exact bounded enumeration | `validation/theorem_R_polynomial.py` and related outputs | Bounded validation grid | Not a theorem for all programs |
| Divergence-ratio relationships | Exact bounded enumeration | `validation/rho_infinity_investigation.py` and validation outputs | Bounded validation grid | Not a universal law |
| Sampled extrema | Empirical sweep | `results/review_experiments/sampling_convergence_summary.json` | Sampled budgets tested | Not exact unless exhaustive |
| Analyzer benchmark metrics | Source-inspection evaluation | `results/review_experiments/extended_controlled_benchmark_summary.json` | Labeled benchmark classes | Not analyzer soundness |
| PyPI screening counts | Screening-scale evidence | `results/review_experiments/pypi_expanded_screen_summary.json` | Cache-only corpus analyzed | Not production prevalence |
