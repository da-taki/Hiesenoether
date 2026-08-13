# Prospective Task Compliance Audit

This audit classifies the 42 frozen prospective expansion outputs without modifying any model response. Task compliance is separate from ordinary correctness and OSDS preservation.

| Model | Outputs | Task-compliant transformations | Unchanged outputs | Other noncompliant outputs | Ordinary pass | Verified OSDS divergences |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | 14 | 8 | 6 | 0 | 14 | 0 |
| `gpt-5.6-terra` | 14 | 8 | 6 | 0 | 14 | 0 |
| `gpt-5.6-luna` | 14 | 7 | 7 | 0 | 14 | 0 |

Overall: 42 outputs audited; 23 task-compliant transformations; 19 unchanged outputs; 0 other noncompliant outputs; 0 verified prospective OSDS divergences.
Task-compliant and OSDS-preserving outputs: 23/23.
All 42 prospective outputs avoided verified OSDS divergence, but unchanged outputs are not counted as task-compliant transformations.
