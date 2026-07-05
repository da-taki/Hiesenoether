# Soundness Boundary

This repository supports formal and empirical reasoning about observation-sensitive deterministic systems (OSDS), but it does not make every result a theorem.

## Formal Core

The OSDS transition rules in `validation/exact_semantics.py` use exact rational arithmetic. They are suitable for formal reasoning because each transition is functional: a state and operation determine one next state and one output.

Fixed-order determinism is provable from those functional transitions. For a fixed template, fixed permutation, fixed parameters, and fixed initial state, repeated evaluation must produce the same final state and final output.

Identity-observation zero-divergence is provable only under the stated template assumptions: the compared executions use the same multiset of operations, templates contain only reads and observations over the modeled value, and the observation transition is the identity `g(d) = d`.

Access-insensitive-read zero-divergence is provable only under the stated template assumptions: reads return a value independent of access count and drift, and the compared executions use the same operation multiset.

## Empirical and Bounded Claims

Composition amplification is empirical unless separately proved symbolically. The repository checks exact-rational configurations showing that linear caps already diverge when access-sensitive reads and observation mutation are present, and that nonlinear caps increase the measured range in the tested configurations.

Polynomial-degree and divergence-ratio relationships are bounded computational findings in this repository. The checked JSON files and evidence tests record the exact cases covered. They should not be stated as unbounded theorems unless the manuscript includes a separate symbolic proof.

## Static Analyzer Boundary

The Python analyzer is not sound or complete. It is a syntactic screen for access-sensitive reads, observation-induced mutation, and nonlinear composition patterns.

`SAFE` means no evidence was found by this syntactic screen. It does not mean absence of the pattern, absence of semantic divergence, or production safety.

The PyPI scan estimates precision over reviewed MEDIUM/HIGH findings. It does not estimate production prevalence, and it does not establish recall over PyPI.
