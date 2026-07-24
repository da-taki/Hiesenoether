# Real-World Package Study Results

## Executive Summary

This revision closes much of the "why does this matter in real code?" gap. Four runnable real-code/library harnesses were added. Three show output or branch divergence, and one shows visible state divergence only. The strongest cases are `httpcore.Response`, `_pytest.logging.catching_logs`, and `PyYAML.SafeRepresenter`.

The reviewed PyPI source snapshot was rebuilt successfully: 73/73 exact package versions were reacquired under `source_snapshot/`. The rebuilt snapshot has 4383 analyzable classes, while the original published benchmark reported 4437 classes. Recall-v2 is therefore a rebuilt-snapshot audit, not a byte-identical replay. On a deterministic sample of 200 unflagged rebuilt-snapshot classes, the audit found 0 likely missed matches, 200 likely nonmatches, and 0 uncertain cases. Under the stated estimator, `estimated_FN = 0/1` and `estimated_recall = 1/1`; this should be reported with the rebuilt-snapshot limitation.

The adjacent-swap proof attempt succeeded for the current compositional OSDS family under explicit positivity assumptions. OBS-first/OBS-last extrema can be theorem-backed rather than assumed for that restricted family.

## Real Cases

### Confirmed Cases

| case | package | version | class | classification | output_diff | branch_flip | state_diff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| case_1_httpcore_Response | httpcore | 1.0.9 | Response | confirmed_branch_flip | true | true | true |
| case_2_pytest_catching_logs | pytest | 8.3.5 | catching_logs | confirmed_branch_flip | true | true | true |
| case_3_pyyaml_SafeRepresenter | PyYAML | 6.0.3 | SafeRepresenter | confirmed_output_divergence | true | false | false |
| case_4_rich_RichHandler | rich | 15.0.0 | RichHandler | confirmed_state_divergence_only | false | false | true |

### Structural-Only Or Failed Cases

No attempted harness failed in this run. The candidate table still contains lower-ranked structural candidates that were not attempted.

### Mechanism Notes

`httpcore.Response`: without prior `read()`, later `response.content` raises a runtime error. If `read()` occurs first, it materializes `_content`, consumes the stream, and the same later `response.content` returns bytes. This is a real public API branch/output difference.

`_pytest.logging.catching_logs`: entering/exiting the logging context mutates the handler level. In the harness, the later identical `WARNING` message is emitted without the prior observation-like context operation and filtered after it. This uses an internal pytest utility and should be framed as a behavioral instance, not an upstream bug.

`PyYAML.SafeRepresenter`: low-level `represent_data()` caches a representation for object identity. If the list is represented before mutation, a later representation of the same object returns the cached earlier node. If mutation occurs first, the later representation reflects the new value. The full dumper resets state after `represent()`, so this is a low-level representer boundary case.

`rich.RichHandler`: `render_message()` initializes `handler.keywords`. This is visible state divergence in a logging/rendering path, but no output divergence was reproduced.

## Recall Audit

### Source Snapshot Status

| packages | exact versions reacquired | missing | analyzable classes |
| ---: | ---: | ---: | ---: |
| 73 | 73 | 0 | 4383 |

Original benchmark denominator: 4437 classes. Rebuilt snapshot denominator: 4383 classes.

### Recall Summary

| total_corpus_classes | flagged_classes_or_findings | likely_flagged_matches | likely_flagged_false_positives | unflagged_classes | sampled_unflagged_classes | likely_missed_matches | likely_nonmatches | uncertain_cases | estimated_FN | estimated_recall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4383 | 278 | 203 | 75 | 4093 | 200 | 0 | 200 | 0 | 0/1 | 1/1 |

Estimator:

`estimated_FN = likely_missed_matches / sampled_unflagged_classes * unflagged_classes`

`recall_hat = TP / (TP + estimated_FN)`

### Sensitivity

| Treat uncertain as | Estimated FN | Estimated recall |
| --- | ---: | ---: |
| nonmatch | 0/1 | 1/1 |
| half missed | 0/1 | 1/1 |
| missed | 0/1 | 1/1 |

Limitations: the audit is static/manual-style AST evidence over the rebuilt wheel/source snapshot. It should not be described as proof of completeness. The class denominator differs from the original benchmark by 54 classes.

## Theorem/Extrema

The adjacent-swap theorem attempt succeeded for the current compositional family.

Lemma: with `eta >= 0`, `delta >= 0`, nonnegative access count `n`, and positive final cap multiplier, swapping adjacent `READ, OBS` to `OBS, READ` weakly increases the body accumulator and final output.

Symbolic difference:

`OBS_READ - READ_OBS = n * eta`

Both orders leave the same post-pair state, so suffix reads and final cap factors are identical. Repeated swaps establish OBS-first as maximum and OBS-last as minimum under the stated assumptions.

Validation: 136 exact validation rows, 0 failures.

Impact: Theorem 5 can remove the OBS-first/OBS-last extrema assumption for the restricted positive compositional OSDS family and cite the adjacent-swap proof sketch.

## Named Public Hazards

| case | source | reproduced | boundary |
| --- | --- | --- | --- |
| CPython issue #132385 | https://github.com/python/cpython/issues/132385 | yes | named diagnostic-side-effect hazard; partial OSDS instance |
| Duktape GH-303 candidate | not verified | no | external verification required |

## Artifact Edits Needed

| Location | Revision |
| --- | --- |
| Abstract | Lead with real-code behavioral cases plus theorem-backed extrema; keep recall claim bounded to rebuilt snapshot. |
| Introduction | Add the `httpcore`, `pytest`, and `PyYAML` examples as motivating evidence. |
| Section 2.4 | Use CPython #132385 and the harness cases to explain non-inert observation/read paths. |
| Section 5 | Replace assumed extrema with adjacent-swap theorem under positivity assumptions. |
| Section 8.5 | Report precision as before and add rebuilt-snapshot recall audit with denominator caveat. |
| Section 9 | Present real cases as behavioral instances, not bugs or prevalence evidence. |
| Discussion | Emphasize mechanism-first contribution over execution volume. |
| Threats | Add rebuilt wheel-vs-original-source denominator mismatch and static audit limitations. |
| Conclusion | Claim exact replay, theorem-backed calibration, and real-code behavioral cases. |
| Cover letter | Highlight 4 runnable cases, rebuilt source snapshot, recall-v2 audit, and adjacent-swap proof. |

## Paper-Ready Tables

### Table A: Confirmed Real-Code Behavioral Cases

| Package | Class | Operation A | Operation B | Classification |
| --- | --- | --- | --- | --- |
| httpcore | Response | `content` before `read()` | `read(); content` | branch/output divergence |
| pytest | catching_logs | emit warning | enter/exit logging context; emit warning | branch/output divergence |
| PyYAML | SafeRepresenter | mutate; represent | represent; mutate; represent | output divergence |
| rich | RichHandler | no render | render message | state divergence only |

### Table B: Recall Audit Summary

| Classes | Unflagged | Sample | Misses | Uncertain | Recall |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4383 | 4093 | 200 | 0 | 0 | 1/1 |

### Table C: Recall Sensitivity

| Treat uncertain as | Estimated FN | Estimated recall |
| --- | ---: | ---: |
| nonmatch | 0/1 | 1/1 |
| half missed | 0/1 | 1/1 |
| missed | 0/1 | 1/1 |

### Table D: Adjacent-Swap/Extrema Status

| Claim | Status | Evidence |
| --- | --- | --- |
| OBS-first max / OBS-last min for positive compositional OSDS | theorem-backed under stated assumptions | symbolic adjacent-swap difference `n*eta`; 136 exact validation rows, 0 failures |

### Table E: Named Public Hazard Mapping

| Case | Observation path | Side effect | Later behavior |
| --- | --- | --- | --- |
| CPython #132385 | traceback/name suggestion | `__getattr__` invoked and counter changed | visible state at process exit |

## Exact Command Log

Successful commands:

- `build_source_snapshot.py --download --timeout 45`: 73/73 exact versions reacquired; runtime about 195 seconds.
- `mine_real_case_candidates.py`: 207 candidates written.
- `run_real_case_harnesses.py`: 4 confirmed / 4 attempted.
- `sample_unflagged_recall_audit_v2.py`: sample 200; 0 likely missed; 0 uncertain.
- `adjacent_swap_extrema_analysis.py`: 136 rows; 0 failures.
- `run_tests.py`: 28/28 passed.
- `python -m pytest tests -q`: 44/44 passed.

Failed or constrained commands:

- sandboxed `pip download`: blocked by `WinError 10013`.
- Duktape GH-303 web/source search: no verifiable source found in this run.
- system `python` and `py`: unavailable.

## Final Recommendation

Revise more before review release, but the paper is materially stronger. The real-code gap is now addressed by runnable harnesses and a rebuilt source snapshot. The main remaining caution is wording: do not claim corpus-wide completeness, do not imply bugs, and do not hide that the recall denominator is a rebuilt exact-version snapshot with 4383 analyzable classes rather than the original 4437.

