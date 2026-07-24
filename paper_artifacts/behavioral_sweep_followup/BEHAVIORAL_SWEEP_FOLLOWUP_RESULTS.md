# Behavioral Sweep Follow-up Results

## 1. Executive Summary

Selected rescue candidates: 15. Manual harnesses attempted: 15. New output/branch divergences: 9. New state-only divergences: 2. Structural-only or failed manual attempts: 4.

## 2. Why The Rescue Pass Was Needed

The prior 50-candidate generic sweep found 0 output/branch divergences and 4 state-only divergences. Many failures were caused by no-argument construction or empty fixtures for package objects that require iterables, parser documents, buffers, cache entries, or framework-shaped objects.

## 3. Candidate Selection

The rescue pass selected 15 candidates from the previous sweep, favoring construction failures, structural-only generic runs, and import failures whose dependencies were present in the rebuilt snapshot. Unsafe, nondeterministic, network, database, credential, browser, server, destructive filesystem, and subprocess-heavy cases were excluded.

## 4. Aggregate Results

| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |
| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |
| 15 | 15 | 9 | 2 | 4 | 0 | 0 | 0 | 0 |

## 5. Confirmed Output/Branch Cases

- Rescue 1: markdown `Markdown` -> `confirmed_output_divergence`. The Python-Markdown docs explicitly say reset() should be called between convert() calls; count this as stateful reuse behavior, not a package bug.
- Rescue 2: more-itertools `seekable` -> `confirmed_output_divergence`. Iterator consumption is expected behavior; the rescue shows the generic no-arg harness missed a real cursor effect.
- Rescue 6: beautifulsoup4 `PageElement` -> `confirmed_output_divergence`. BeautifulSoup extraction is intentionally destructive; use only as a tree-mutation/access-order example.
- Rescue 8: boltons `LRU` -> `confirmed_output_divergence`. LRU access affects eviction order as designed; it is evidence of consequential access state, not a defect.
- Rescue 9: boltons `MultiFileReader` -> `confirmed_output_divergence`. MultiFileReader is a stream-like cursor; output divergence is expected after a prior read.
- Rescue 10: cerberus `BareValidator` -> `confirmed_output_divergence`. BareValidator itself rejects schema-backed validation; the runnable fixture uses the public Validator subclass to exercise inherited BareValidator state.
- Rescue 13: dnspython `Tokenizer` -> `confirmed_output_divergence`. Tokenizer is a cursor over token input; output divergence is expected after consuming a token.
- Rescue 14: h11 `ChunkedReader` -> `confirmed_output_divergence`. ChunkedReader consumes a ReceiveBuffer; Data versus EndOfMessage is expected stream-reader state.
- Rescue 15: h11 `ReceiveBuffer` -> `confirmed_output_divergence`. ReceiveBuffer line extraction is destructive by design; it is a cursor semantics example.

## 6. Confirmed State-Only Cases

- Rescue 4: docutils `Transformer` -> `confirmed_state_divergence_only`. The manual fixture tests Transformer serial bookkeeping, not transform application output.
- Rescue 7: boltons `LRI` -> `confirmed_state_divergence_only`. LRI access affects statistics but not eviction order in this fixture.

## 7. Failed Or Still Structural Cases

- Rescue 3: pygments `EscapeSequence` -> `structural_only_no_runtime_difference`. In this Pygments version the ANSI fixture did not trigger the suspected bold mutation; the case remains structural-only.
- Rescue 5: soupsieve `CSSMatch` -> `structural_only_no_runtime_difference`. The rescue only fixes sys.path/import construction; simple selector matching remained output-equivalent.
- Rescue 11: click-option-group `_OptGroup` -> `structural_only_no_runtime_difference`. The decorator fixture is tiny and in-process; it did not produce a meaningful runtime divergence.
- Rescue 12: dnspython `BTree` -> `structural_only_no_runtime_difference`. BTree lookup is stable under this minimal fixture; cursor/copy-on-write behavior was not forced.

## 8. Interpretation

The rescue pass shows that the generic harness limitation was real: several candidates needed package-specific fixtures before output-level behavior appeared. The positive cases are mostly stateful parsers, iterators, caches, tree nodes, and stream readers, so they should be framed as access-order-sensitive behavior rather than defects. The selected rescue denominator is not a PyPI prevalence claim.

## 9. Artifact Recommendation

Case A: add the rescue sweep to main Section 9 with strong boundary language; keep the original four detailed cases.

## 10. Exact Command Log

- `Get-Content <redacted-local-tool-cache>/pasted-text.txt`
- `Import-Csv paper_artifacts\behavioral_sweep\behavioral_sweep_results.csv`
- `Get-Content paper_artifacts\behavioral_sweep\MANUAL_REVIEW_PACKET.md`
- `Get-Content paper_artifacts\behavioral_sweep\OSDS_BEHAVIORAL_SWEEP_RESULTS.md`
- Source inspection with `Select-String` over selected files in `paper_artifacts\realworld_package_study\source_snapshot\`.
- Exploratory harness probes with `python -`.
- `python paper_artifacts\behavioral_sweep_followup\create_rescue_artifacts.py`
- `python paper_artifacts\behavioral_sweep_followup\run_rescue_harnesses.py`
- `python run_tests.py`
- `python -m pytest` (collection failed in third-party source snapshot tests; see `QUALITY_GATE_REPORT.md`)
- `python -m pytest tests`
- `python paper_artifacts\realworld_package_study\run_real_case_harnesses.py`
- `python paper_artifacts\behavioral_sweep_followup\run_rescue_harnesses.py`
