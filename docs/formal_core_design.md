# Formal Core Design

This note defines the proof core used by the review artifact. It is deliberately smaller than the full Hiesenoether implementation, but it preserves the semantic structure needed for the paper's formal claims: deterministic read transitions, deterministic observation transitions, additive body execution, and deterministic caps over the body accumulator.

## Scope of the Formalization

The core formalizes the straight-line OSDS template used by the running example, paper evidence tests, exact enumeration, and expanded mechanism sweeps. A configuration contains:

- a base component `b`;
- a latent access count `a`;
- a latent drift or entropy state `d`;
- an accumulator `y`;
- a fixed operation list containing read/add operations and observation operations.

A read exposes a value `f(b, a, d)`, increments the access count, and may update drift. An observation exposes no value and updates only the latent drift through a deterministic function `g`. Body execution folds the deterministic step function over an operation list. A cap is a deterministic function applied after the body.

The implementation points are:

- `validation/exact_semantics.py`: `do_read`, `do_obs`, `do_cap`, `evaluate`, and `trace`.
- `examples/running_example.py`: exact replay of the central two-read, one-observation example.
- `scripts/review_experiments/common.py`: exact-rational order enumeration, sampled order evaluation, read/observation transitions, and cap evaluation for expanded sweeps.
- `analyzer/abstract_interpreter.py`: bounded abstract summaries for the straight-line positive-parameter fragment.
- `tests/paper_evidence` and `results/paper_evidence`: proof-oriented replay checks.
- `results/running_example.json`: replay output for the running example.

## Simplifications

The proof core does not model arbitrary Python programs, object aliasing, control-flow joins, exceptions, mutation through reflection, or the syntactic analyzer. It models a single OSDS value, a single additive accumulator, deterministic operations, exact arithmetic, and deterministic caps.

The core also separates proof claims from computational claims. Nonlinear caps are included as deterministic caps, but no universal nonlinear amplification theorem is claimed. Degree and ratio relationships are left as bounded computational findings. Analyzer results are left as empirical screening results.

## Why the Simplifications Preserve the Needed Structure

The artifact's formal propositions concern order sensitivity in the studied template, not all Python behavior. The simplified core preserves the properties needed for those propositions:

- fixed operation lists are executed by a deterministic fold;
- observations expose no additive value;
- identity observations leave the latent drift unchanged;
- access-insensitive reads expose the same value for a fixed base component;
- exact addition makes identical multisets of read exposures permutation-invariant;
- injective linear caps preserve unequal body accumulators.

These are precisely the semantic facts used by the running example, exact enumeration, and evidence tests. The simplifications remove engineering details that are irrelevant to those facts while keeping the read/observe/body/cap structure intact.

## Claims Proved

The proof appendix gives paper-level proofs for:

- fixed-order determinism;
- identity-observation zero divergence under the studied template assumptions;
- access-insensitive-read zero divergence under the studied template assumptions;
- preservation of body-level divergence by a nonzero-slope linear cap.

## Claims Not Proved

The formal core does not prove:

- universal nonlinear amplification;
- general degree laws for all OSDS programs;
- general divergence-ratio laws;
- exactness of sampled extrema;
- analyzer soundness;
- production prevalence of OSDS patterns.

## Empirical and Bounded Computational Claims

The following remain outside the proof core:

- nonlinear cap amplification over the tested region;
- degree and divergence-ratio relationships reported by bounded validation scripts;
- sampled extrema and their convergence behavior;
- controlled benchmark precision and recall;
- reviewed PyPI precision;
- expanded PyPI screening counts.

Those claims should be written as exact bounded enumeration, exact rational replay, empirical sweep, source-inspection evaluation, or screening-scale evidence, depending on the artifact named in the claim manifest.
