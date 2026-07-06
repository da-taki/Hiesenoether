# Manuscript Integration Notes

The sweep is suitable for the main paper only as a high-confidence conversion audit, not a prevalence estimate. Keep the four detailed cases as case studies and use this 50-candidate sweep as supporting systematic evidence.

Recommended Section 9 wording:

"We additionally ran a deterministic 50-candidate behavioral sweep over high-confidence reviewed analyzer findings. Each selected candidate was assigned a generated harness or an explicit failure classification. The sweep measures conversion from structural finding to runnable behavioral evidence within this selected high-confidence set; it is not an ecosystem prevalence estimate."

Recommended table caption:

"Behavioral harness outcomes for 50 systematically selected high-confidence reviewed PyPI findings. Failures are counted as outcomes; previous hand-confirmed cases are reported separately as controls unless selected by the rule."

Do not claim:

- prevalence in all PyPI;
- analyzer completeness;
- that every confirmed behavior is a bug;
- that generic harness failures refute the structural finding.
