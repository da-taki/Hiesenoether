# SCP Rewrite Results Brief

This brief is intended for manuscript drafting. It presents the evaluation as one coherent study and separates manuscript-ready results from claim-boundary constraints.

## 1. Manuscript-Ready Evaluation Summary

The evaluation includes a deterministic interpreter, an exact-rational OSDS replay model, bounded exhaustive enumeration, sampled mechanism sweeps, convergence checks for sampled extrema, and a Python syntactic screening study. Together, these components evaluate how access-sensitive reads, observation-induced mutation, and nonlinear composition produce semantic divergence in deterministic systems.

The central running example uses exact rational arithmetic to compare two operation orders with the same multiset: one observation and two reads. With base value `b = 10`, sequence A applies `OBS, READ, READ`, sequence B applies `READ, READ, OBS`, and both use the same compositional cap. Sequence A produces final output `7956/25`; sequence B produces `7596/25`; the exact divergence is `72/5`.

The mechanism sweep covers observation counts from 0 through 10, cap degrees from 1 through 8, body lengths 3, 5, 8, 10, 15, 20, 30, and 50, and three drift schedules: constant, linear decay, and exponential decay. Across 2,112 configurations and 622,416 evaluated order executions, all zero-observation configurations have zero divergence. Linear caps already show positive divergence in 240 configurations, showing that access-sensitive reads and observation mutation are sufficient for order-sensitive outputs. Nonlinear caps amplify range over the corresponding linear cap in 1,680 configurations, with no nonlinear amplification counterexamples in the sweep.

The exhaustive enumeration covers 240 configurations over body lengths 2 through 9, observation counts 0 through 5, and cap degrees 1 through 5. The original 112-configuration scope is preserved, and the enumeration extends coverage by 128 configurations. All 240 configurations are feasible under the safe permutation cutoff. Comparing sampled ranges with exhaustive ranges shows 15 sample-vs-exact range misses, demonstrating why sampled extrema must not be treated as exact.

The sampling-convergence study evaluates 160 rows across known-exhaustive configurations and sampling budgets from 8 through 1024. At budget 1024, the exact-extrema match rate is 0.85. Three max-budget extrema failures remain, showing that sampled extrema can miss exact extrema even at relatively high budgets.

The controlled analyzer benchmark contains 64 labeled classes, including 44 added controlled classes. The benchmark includes risky examples such as access-evolving properties, descriptors with latent mutation, observation methods that mutate later-read state, counter-based reads, reactive registration patterns, instrumentation hooks, invalidated caches, repeated-read composition, and hidden counters. It also includes benign near-misses such as stable properties, memoized properties, cached hashes, builder patterns, context-manager bookkeeping, logging side effects, independent metrics counters, stabilizing descriptors, dataclass-style properties, and fluent setters. On this 64-class benchmark, the syntactic screen obtains TP/FP/TN/FN = 40/9/15/0, precision 0.8163, recall 1.0, specificity 0.625, F1 0.8989, and exact-label accuracy 0.8594.

The Python screening study also includes a 20-class controlled benchmark and a PyPI corpus screen. On the 20-class benchmark, the analyzer obtains 0.9231 precision and 1.0 recall. The reviewed PyPI corpus covers 73 packages, 1,858 files, 4,437 classes, and 21,530 functions. Manual review of 278 MEDIUM/HIGH findings classifies 203 as likely true positives and 75 as likely false positives, giving reviewed precision 0.7302 over flagged findings. A cache-only expanded PyPI screen covers 116 packages, 3,275 files, 6,441 classes, and 49,523 functions, producing 5,874 SAFE, 0 LOW, 408 MEDIUM, and 0 HIGH labels. Its manual review queue contains 250 rows and supports future precision and limited false-negative estimation only after manual labeling.

## 2. Protected Numbers

### Core

- 2,200,000 executions
- 112 original exhaustive configurations
- 20-class original controlled benchmark
- 0.9231 precision and 1.0 recall on the 20-class benchmark
- 73 PyPI packages
- 1,858 files
- 4,437 classes
- 21,530 functions
- 278 reviewed MEDIUM/HIGH findings
- 203 likely true positives
- 75 likely false positives
- 0.7302 reviewed precision

### Expanded

- 712,216 evaluated order executions
- expanded mechanism sweep: 2,112 configurations and 622,416 executions
- zero-observation configurations: all zero divergence
- linear cap positive divergence configurations: 240
- nonlinear cap amplified over linear configurations: 1,680
- nonlinear amplification counterexamples: 0
- extended exhaustive enumeration: 240 configurations
- original 112 scope preserved
- extension by 128 configurations
- sample-vs-exact range misses: 15
- sampling convergence rows: 160
- budget 1024 extrema match rate: 0.85
- remaining max-budget extrema failures: 3
- expanded controlled benchmark: 64 classes
- added controlled classes: 44
- TP/FP/TN/FN: 40/9/15/0
- precision: 0.8163
- recall: 1.0
- specificity: 0.625
- F1: 0.8989
- exact-label accuracy: 0.8594
- expanded PyPI cache-only packages: 116
- expanded PyPI files/classes/functions: 3,275 / 6,441 / 49,523
- expanded PyPI SAFE/LOW/MEDIUM/HIGH: 5,874 / 0 / 408 / 0
- manual review queue rows: 250

## 3. Claim Boundaries

- Formal propositions are only the deterministic and zero-divergence statements under stated assumptions.
- Composition amplification is empirical unless separately proved.
- Degree and ratio relationships are bounded computational findings, not theorems.
- Sampled extrema are not exact.
- Sampling convergence shows sampled extrema can miss exact extrema.
- The analyzer is a syntactic screening tool, not a sound verifier.
- SAFE means no evidence found by this screen, not absence of the pattern.
- Expanded PyPI results are screening counts only.
- Expanded PyPI precision and recall cannot be claimed until manual labels are completed.
- Production prevalence is not claimed.

## 4. Recommended SCP Paper Structure

Title

Author information

Abstract

Keywords

1. Introduction
2. Running Example
3. Background and Related Work
4. Observation-Sensitive Deterministic Systems
5. Formal Properties and Soundness Boundary
6. Hiesenoether Implementation
7. Experimental Design
8. Results
9. Python Screening Study
10. Discussion
11. Threats to Validity
12. Conclusion

Declarations

References

## 5. Tables To Include

- Running example trace table
- Formal claims and evidence level table
- Mechanism sweep summary
- Extended exhaustive enumeration summary
- Sampling convergence summary
- Controlled benchmark comparison
- PyPI screening summary
- Case-study examples

## 6. Case Studies

The case-study section should include three controlled true-positive-style examples, three benign near-misses, and three PyPI flagged examples pending manual review.

Controlled true-positive-style examples should illustrate access-evolving or observation-sensitive behavior using short excerpts from labeled benchmark classes. Good candidates are classes where the analyzer and benchmark label agree on MEDIUM or HIGH behavior, such as an access-evolving property, an observer-mutated later-read cell, and a descriptor with latent state mutation.

Benign near-misses should show why syntactic screening can over-approximate. Good candidates include harmless memoization, cached hash computation, context-manager bookkeeping, metrics counters independent of returned values, stabilizing descriptors, and fluent setters returning `self`.

PyPI flagged examples should be presented as pending manual review. They can demonstrate realistic syntactic patterns found by the screen, but they should not be described as confirmed true positives until reviewed. Keep code excerpts short and focus on the analyzer evidence, the suspected latent state, and the later read or value path.

## 7. Data and Materials Availability

The interpreter, validation suite, static analyzer, experiment scripts, benchmark outputs, and result summaries are available at https://github.com/da-taki/Hiesenoether.
