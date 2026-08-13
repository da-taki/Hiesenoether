# Reproducing the OSDS VeriCodeGen Results

This supplement is anonymized and uses paths relative to the supplement root.

## Environment

Supported Python: Python 3.11 or newer. Install the project dependencies used by the repository, including pytest, PyYAML, pytest, h11, boltons, dnspython, httpcore, markdown, more-itertools, docutils, beautifulsoup4, cerberus, and anyio at the exact package versions recorded in the included manifests and witness metadata.

## Primary Benchmark Replay

From the repository root, use the included runner:

```text
py experiments/agent_behavior_preservation/runners/run_benchmark.py --provider jsonl --task-ids-from-replay
```

Expected primary summary: Sol has 26 executable and 0 verified OSDS; Terra has 24 executable and 2 verified OSDS; Luna has 24 executable and 3 verified OSDS.

## Prospective Benchmark Replay

Use `benchmark_expansion/tasks.jsonl`, `benchmark_expansion/prompts/`, and the raw expansion response JSONLs in `benchmark_expansion/responses/`. The exact replay result JSONLs are included under `experiments/agent_behavior_preservation/results/*expansion-exact-20260813Tcutscope/`.

Expected prospective summary: 42 outputs audited, 23 task-compliant transformations, 19 unchanged outputs, 0 other noncompliant outputs, 42 ordinary-pass outputs, and 0 verified OSDS divergences.

## Causal-Control Replay

Run:

```text
py experiments/agent_behavior_preservation/causal_controls/run_model_failure_causal_controls.py
```

Expected output: all five original failures reproduce under the original witness and all five pass the mechanism-neutralizing controls. The included result files are `analysis/model_failure_causal_controls.csv` and `.md`.

## Paper Tables

Paper numbers are mapped in `ARTIFACT_INDEX.md`. The table inputs are the cross-model analysis JSON/MD, manual-review JSONL, prospective task-compliance CSV/MD, causal-control CSV/MD, and real-code oracle CSV/MD files included in this supplement.
