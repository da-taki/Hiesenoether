# Agent Behavior Preservation: Current Phase Report

## Status

The benchmark and environment are ready for real model execution, but no authenticated external coding-model provider was discovered. Per protocol, the experiment stops before real-model claims.

## Environment Reconstruction

All 9 required top-level packages were exactly reproduced in the repository-local venv:

- httpcore 1.0.9
- pytest 8.3.5
- PyYAML 6.0.3
- h11 0.16.0
- cerberus 1.3.8
- boltons 25.0.0
- dnspython 2.8.0
- markdown 3.10.2
- beautifulsoup4 4.14.3

See `environment/reconstruction.json` and `environment/reconstruction.md`.

## Baseline Eligibility

`validation/baseline_validation.jsonl` records 26/26 tasks eligible for primary analysis:

- fixture/source executes: 26/26
- ordinary baseline pass: 26/26
- metamorphic witness reproduced: 26/26
- caller wrapper reproduced: 26/26
- controls reproduced where applicable: 26/26

Existing inherited validation now reproduces 9/9 caller branch wrappers and 19/19 controls.

## Benchmark Balance

- Tasks: 26
- Paired base tasks: 13
- Unique witnesses: 9
- Packages: 9
- Hidden-observation tasks: 16
- Expected access-sensitive calibration tasks: 10

Multiple tasks derived from the same witness/package are correlated and must not be treated as independent semantic phenomena.

## Prompt Leakage

The leakage audit found 0 forbidden-term leaks in normal prompts and 0 pair consistency errors.

## Provider Discovery

No usable external coding-model provider was discovered. No secret values were printed or stored.

## Pipeline Controls

No-op control:

- 26 attempted
- 26 executable
- 26 preserved
- 0 diverged

Semantics-blind control:

- 26 attempted
- 26 executable
- 0 preserved
- 26 diverged
- 26 ordinary-pass / OSDS-fail cases

These remain pipeline controls only, not real coding-model results.

## Real-Model Readiness

Ready inputs for real-model execution are in `prompts/` and `benchmark/tasks.jsonl`. The JSONL replay provider can import externally collected model responses with raw responses and optional self-assessment text.

## Blocker

Real-model evaluation requires authenticated provider access or a JSONL file of externally collected model responses. Until then, there are no real-model normal-prompt, warned-prompt, paired, self-assessment, or workshop-result claims.
