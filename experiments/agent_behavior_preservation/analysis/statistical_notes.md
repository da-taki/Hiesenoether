# Statistical notes

This GPT-5.6 Sol run contains 26 frozen prompt variants: 13 normal and 13 warned. Variants are paired and several derive from the same witness, so the 26 rows should not be treated as 26 independent real-world discoveries.

Manual review found 0 verified semantic divergences, 0 silent semantic divergences, and 3 ordinary programming bugs caught by ordinary tests. With zero verified semantic divergences, the estimated observed silent semantic divergence rate is 0/26 for this benchmark run.

The normal and warned conditions both had 0 false preservation claims under the study definition: model says YES and manual review confirms semantic divergence. Conservative NO behavior was common: 9/13 normal rows and 7/13 warned rows were behavior-preserved in replay but self-assessed as NO.

Pipeline controls remain separate from the real-model result: noop-preserving was 26/26 preserved, and static-semantics-blind-transformer was 26/26 divergent with ordinary-pass / OSDS-fail behavior in the frozen control run.
