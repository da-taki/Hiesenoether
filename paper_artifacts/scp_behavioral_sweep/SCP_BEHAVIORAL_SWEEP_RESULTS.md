# SCP Behavioral Sweep Results

## Executive Summary

Selected candidates: 50. Runnable harnesses attempted: 50. Branch/output confirmed: 0. State-only confirmed: 4.

This sweep strengthens the artifact trail by counting systematic harness attempts over high-confidence reviewed findings. The low conversion rate should be reported as part of the result, because generic no-arg harnesses often cannot construct framework/cache/parser objects.

## Selection Rule And Denominators

See `CANDIDATE_SELECTION_RULE.md`. The sweep selected exactly 50 likely-true-positive reviewed findings with available rebuilt source, ordered by the deterministic score and tie-breaks.

- reviewed findings: 278
- likely true positives: 203
- likely true positives with source available: 202
- selected candidates: 50
- previous four confirmed cases selected by this rule: none

## Aggregate Results

- confirmed_branch_flip: 0
- confirmed_output_divergence: 0
- confirmed_state_divergence_only: 4
- structural_only_no_runtime_difference: 21
- could_not_construct: 17
- import_failed: 3
- unsafe_to_execute: 2
- requires_external_service_or_complex_fixture: 0
- not_applicable_after_inspection: 3
- output/branch per selected: 0/50
- output/branch per runnable attempted: 0/50
- visible divergence per selected: 4/50
- visible divergence per runnable attempted: 4/50

| Selected | Runnable attempted | Branch/output confirmed | State-only confirmed | Structural only | Could not construct | Import failed | Fixture required | Unsafe |
| -------: | -----------------: | ----------------------: | -------------------: | --------------: | ------------------: | ------------: | ---------------: | -----: |
| 50 | 50 | 0 | 4 | 21 | 17 | 3 | 0 | 2 |

## Confirmed Cases

| Rank | Package | Class | Classification | Notes |
| ---: | --- | --- | --- | --- |
| 9 | anyio | BlockingPortalProvider | confirmed_state_divergence_only | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
| 15 | boltons | SpooledStringIO | confirmed_state_divergence_only | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
| 22 | dnspython | Tokenizer | confirmed_state_divergence_only | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
| 23 | docutils | Publisher | confirmed_state_divergence_only | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |

## Failed/Structural-Only Cases

Failures are mostly construction/import limitations of a generated no-argument harness. They do not refute the structural findings.

Common outcomes:

- 21 structural-only cases: the operation ran but did not produce a visible difference under the generic repeated-operation harness.
- 17 could-not-construct cases: class construction required arguments or raised during no-argument construction.
- 3 import failures: module/class import failed from the rebuilt snapshot.
- 3 not-applicable cases: the parsed operation was nondeterministic or not read/observer-shaped after inspection.
- 2 unsafe cases: method names matched the sweep's unsafe-operation guard.

## Controls

Previous confirmed controls passed: 4/4.

## Threats

- Harness construction bias: the generic repeated-operation harness favors no-arg constructors and no-arg methods.
- High-confidence selection bias: this is not a PyPI prevalence estimate.
- Package import/context limitations: many classes require framework state, parser state, or callbacks.
- Internal API cases should be framed as behavioral instances, not bugs.

## Manuscript Recommendation

Use this sweep in an appendix or artifact-evaluation section, and keep the four detailed hand-built cases in the main text. Mention the systematic conversion rate only with the failure categories.

## Exact Command Log

- `prepare_behavioral_sweep.py` generated candidates, harnesses, packet, and integration notes.
- `run_behavioral_sweep.py` executed 50 harnesses and reran 4 controls.
- Quality gate commands are recorded in `QUALITY_GATE_REPORT.md`.
