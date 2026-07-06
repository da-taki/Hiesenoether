# SCP Revision Results

## Executive Summary

The revised validation produced a clean theorem-backed upgrade for the compositional polynomial-degree finding, but only after correcting the theorem shape. The old preferred `d*q` form is not supported by the repository's current cap semantics. The corrected restricted statement is degree `2d`, validated on 20 exact-rational checked configurations with 0 failures.

The requested reviewed-corpus recall estimate could not be computed from this checkout because the unflagged reviewed PyPI source files are missing. The script records the reviewed denominators (4437 corpus classes, 278 flagged findings, 4159 unflagged classes) and emits a missing-data fallback rather than inventing recall.

The named real-world hazard was reproduced locally for CPython issue #132385: traceback/name-suggestion handling invoked `__getattr__`, and the hook produced a visible side effect.

## Theorem Upgrade Result

Candidate theorem: for the current compositional OSDS cap with fixed positive rational parameters, fixed observation count `m`, and cap degree `d`, if OBS-first is the max branch and OBS-last is the min branch, then the output range over `L` reads is a polynomial of degree `2d` with leading coefficient `eta*m*delta^(d-1)/2`.

| family | configs_checked | cap_degree | accumulator_degree_q | predicted_range_degree | observed_range_degree | stable_extrema | leading_terms_cancel | status |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| compositional OSDS | 20/20 rows; m=1..4, d=1..5, L=2..15 | 1..5 | 3 | 2d | 2d | 20/20 | 20/20 | pass_corrected_2d |

Bounded Computational Finding 1 can be partially replaced: use the restricted theorem above, plus exact bounded validation for the extrema side condition. Bounded Computational Finding 2, the divergence-ratio relationship, should remain bounded computational evidence unless the external generalized runtime model is promoted into the formal statement.

## Recall Audit Result

| Corpus classes | Flagged reviewed | Likely flagged matches | Unflagged classes | Unflagged sample | Likely missed matches | Uncertain | Estimated recall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4437 | 278/278 | 203/278 | 4159 | 100 fallback rows | 0 | 100 | not computed: reviewed source missing |

Formula intended when source is available:

`recall_hat = TP / (TP + estimated_FN)`.

This run cannot supply `estimated_FN` for the reviewed corpus. The available fallback rows come from `results/scp_new_experiments/pypi_expanded_manual_review_queue.csv`, not from a fresh 200-class reviewed-corpus source audit. They are all labeled `uncertain`.

## Real Named Case

| case | reproduced locally | read-shaped operation | observation path | latent state | amplification |
| --- | --- | --- | --- | --- | --- |
| CPython issue #132385 | yes | `__getattr__("foo")` | traceback/name suggestion after `NameError` | `A.touched` counter | none reproduced |

Recommended manuscript wording:

"CPython issue #132385 provides a named hazard case: instance-attribute error suggestion logic can invoke user-defined `__getattr__` during diagnostic handling. Our local harness on Python 3.12.13 reproduced the observer-side-effect mechanism: the diagnostic path called `__getattr__("foo")` and changed a class counter. We use this as motivation for OSDS-style observer effects, not as prevalence evidence and not as evidence of composition amplification."

## Manuscript Edits Needed

| Location | Recommended change |
| --- | --- |
| Abstract | Say one bounded polynomial claim is now theorem-backed under a restricted compositional OSDS condition; do not claim general analyzer recall. |
| Section 2.4 | Add the CPython diagnostic-side-effect hazard as motivation. |
| Section 5 | Replace broad `d*q` language with corrected restricted `2d` theorem and side conditions. |
| Table 2 | Add theorem validation row: 20/20 exact-rational corrected-2d cases. |
| Section 8.5 | State reviewed PyPI precision remains 203/278; recall audit is blocked by missing reviewed source. |
| Section 9 | Mention CPython #132385 as a named observer-path hazard, not prevalence evidence. |
| Threats to validity | Add missing-source limitation for unflagged recall and bounded extrema validation. |
| Cover letter | Say the revision adds exact theorem-backed validation, a reproducible named hazard, and an explicit non-result for recall due missing data. |

## Paper-Ready Tables

### Table A: Theorem Validation

| Cases | Cap degrees | m values | Arithmetic | Predicted degree | Observed degree | Failures |
| ---: | --- | --- | --- | --- | --- | ---: |
| 20/20 | 1..5 | 1..4 | exact rational | 2d | 2d | 0/20 |

### Table B: Unflagged Recall Audit Summary

| Corpus classes | Flagged reviewed | Likely flagged matches | Unflagged classes | Requested sample | Available fallback sample | Likely missed | Uncertain | Recall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4437 | 278/278 | 203/278 | 4159 | 200 | 100 | 0 | 100 | not computed |

### Table C: Likely Missed/Uncertain Unflagged Cases

See `paper_artifacts/unflagged_audit_report.md`. All 100 fallback rows are `uncertain`; there are 0 likely missed matches in the fallback sample, but this is not a recall estimate.

### Table D: Real Named Case Mapping

| Case | Source | Local status | OSDS boundary |
| --- | --- | --- | --- |
| CPython issue #132385 | https://github.com/python/cpython/issues/132385 | reproduced observer-side-effect mechanism | partial OSDS instance; no composition/threshold amplification |

## Exact Command Log

Successful commands:

- bundled Python `run_tests.py`: 28/28 passed.
- bundled Python `-m pytest tests -q`: 44/44 passed.
- bundled Python `-m validation.run_all`: `ALL PASS`.
- bundled Python `-m validation.rho_infinity_investigation`: 34 checked, 0 failures.
- bundled Python `paper_artifacts\validate_polynomial_degree_theorem.py`: 20 checked, 0 corrected-2d failures.
- bundled Python `paper_artifacts\sample_unflagged_recall_audit.py`: wrote missing-data fallback audit.
- bundled Python `paper_artifacts\real_named_case_reproduction.py`: reproduced local diagnostic-side-effect mechanism.

Failed or bounded commands:

- `python --version`, `python -m pip list`, `py --version`, and `py -m pip list` failed because system Python/launcher is unavailable.
- bundled Python `-m validation.polynomial_degree_extended` timed out at 120 seconds.
- reviewed PyPI source reacquisition for the recall audit timed out after 5 minutes and again after 15 minutes with escalation.

Generated files:

- `paper_artifacts/REPO_AUDIT.md`
- `paper_artifacts/validate_polynomial_degree_theorem.py`
- `paper_artifacts/polynomial_degree_theorem_validation.csv`
- `paper_artifacts/polynomial_degree_theorem_validation.md`
- `paper_artifacts/polynomial_degree_theorem_notes.md`
- `paper_artifacts/THEOREM_UPGRADE_DRAFT.md`
- `paper_artifacts/sample_unflagged_recall_audit.py`
- `paper_artifacts/unflagged_audit_sample.csv`
- `paper_artifacts/unflagged_audit_summary.csv`
- `paper_artifacts/unflagged_audit_report.md`
- `paper_artifacts/real_named_case_reproduction.py`
- `paper_artifacts/real_named_case_reproduction_output.json`
- `paper_artifacts/REAL_CASE_REPORT.md`
- `paper_artifacts/SCP_REVISION_RESULTS.md`
- `REPRODUCIBILITY.md`

