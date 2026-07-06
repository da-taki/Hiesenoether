# Manuscript Decision

Observed case: Case A. New rescue output/branch divergences: 9.

Direct recommendation: Add the rescue sweep to main Section 9; keep the original four detailed cases; present the generic sweep as showing automatic conversion difficulty; present the manual rescue as showing package-specific construction recovers stronger evidence.

## Recommended Section 9.5 Wording If Case A Applies

A follow-up manual rescue pass selected 15 candidates from the failed or structurally weak generic sweep and supplied package-specific in-memory fixtures. Unlike the generic no-argument harness, the rescue pass recovered output-level divergences in several parser, iterator, cache, and stream objects. These results should be read as evidence that automatic harness construction is a limiting factor: many access-induced effects require domain-shaped objects and realistic input. The denominator remains the selected rescue set, not PyPI prevalence, and intentionally destructive cursor/stream examples are reported with boundary notes rather than treated as defects.

## Recommended Section 9.5 Wording If Case B Applies

The 50-candidate behavioral sweep is best treated as a limitations result. A generic no-argument harness converted few structural findings into consequential runtime evidence, and the manual rescue pass recovered at most one new output- or branch-level divergence. Accordingly, the main empirical evidence should remain the four detailed hand-built cases. The sweep can be summarized in a short limitations paragraph or artifact appendix as evidence that automatic conversion from static patterns to runnable behavior is difficult, not as a headline behavioral prevalence result.
