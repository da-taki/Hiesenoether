# Model Differential Cases

This cut-scope analysis compares Sol, Terra, and Luna on identical prospectively frozen expansion tasks. Every model preserved behavior on every expansion task, so the expansion contains no model-differential OSDS failures.

| Differential category | Count |
| --- | ---: |
| all preserved | 14 |
| Sol preserved / Terra diverged | 0 |
| Sol preserved / Luna diverged | 0 |
| Terra preserved / Luna diverged | 0 |
| multiple diverged | 0 |

The primary frozen benchmark remains the source of model-differential OSDS evidence: Terra diverged on two pytest instrumentation rows where Sol preserved behavior, and Luna diverged on those same two rows plus one PyYAML caching row. The prospective expansion tests additional expected-access-sensitive witnesses and finds no new differential failures.
