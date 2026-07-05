# SCP Evidence Memo

This memo maps the old SCP rejection points to repository evidence that can support a stronger resubmission. It is not a manuscript rewrite.

## Criticism 1: Results Were Not Detailed Enough

Response:

- `scripts/generate_paper_results_report.py` collects the experiment, analyzer, PyPI, and exhaustive-enumeration evidence into `results/paper_results_summary.json` and `results/paper_results_tables.md`.
- `examples/running_example.py` and `results/running_example.json` give an exact replayable running example with intermediate rational states.
- `scripts/generate_exhaustive_enumeration_report.py` checks the bounded 112-configuration sweep and records exact denominators, sampled ranges, exhaustive ranges, and mismatches.
- `analysis/oc_static_benchmark.py` reproduces the controlled benchmark metrics.
- `results/pypi_reviewed_findings.csv` records the reviewed MEDIUM/HIGH PyPI findings in a compact table.

## Criticism 2: Proofs Were Sketches

Response:

- Formal propositions should be limited to claims derived from functional OSDS transitions, especially fixed-order determinism.
- Identity-observation zero-divergence and access-insensitive-read zero-divergence are formal only under the stated template assumptions in `docs/soundness_boundary.md`.
- Composition amplification should be presented as exact-rational empirical evidence unless the paper adds a symbolic proof.
- Polynomial-degree and divergence-ratio relationships should be presented as bounded computational findings unless the paper adds a complete proof.
- `tests/paper_evidence/` records which checks support each claim and writes summaries under `results/paper_evidence/`.

## Criticism 3: Insufficient Running Examples

Response:

- The new central example compares `OBS, READ, READ` against `READ, READ, OBS`.
- Both sequences use the same operation multiset, the same base value, exact rational arithmetic, and the same final cap.
- Observation before reads changes the later drift, so the two deterministic executions produce different final outputs.
- This example can be carried through the paper from the introduction into the formal model, exact replay, and experimental design sections.

## Criticism 4: Weak Presentation

Recommended manuscript structure:

1. Introduction
2. Running Example
3. Related Work
4. OSDS Formal Model
5. Formal Properties and Soundness Boundary
6. Hiesenoether Implementation
7. Experimental Design
8. Results
9. Python Screening Study
10. Discussion
11. Threats to Validity
12. Conclusion
