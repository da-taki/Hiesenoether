# Agent Behavior Preservation Pilot

This directory contains a pilot benchmark for testing whether ordinary coding-agent
transformations preserve behavior around access-sensitive and observation-sensitive real
package witnesses.

The benchmark reuses the existing Hiesenoether artifacts:

- real-code metamorphic candidates from `paper_artifacts/scp_realcode_metamorphic_oracle/`;
- caller-level branch wrappers from `run_branch_flip_cases.py`;
- negative controls from `run_metamorphic_controls.py`;
- pinned package versions and source-snapshot import setup from `metamorphic_fixtures.py`.

The model-visible prompt contains only a developer-style instruction and a small code
snippet. The answer key fields, evidence role, provenance, and oracle identifiers are kept
in `benchmark/tasks.jsonl`.

## Layout

- `agent_bp/`: benchmark, provider, extraction, execution, and summarization helpers.
- `benchmark/tasks.jsonl`: generated machine-readable task metadata.
- `prompts/`: generated model-visible prompts.
- `runners/run_benchmark.py`: provider-neutral execution runner.
- `analysis/summarize_results.py`: Markdown and JSON summary generator.
- `results/<run-id>/`: timestamped raw run outputs.
- `tests/`: infrastructure tests.

## Reproduce

```powershell
python experiments/agent_behavior_preservation/build_benchmark.py
python experiments/agent_behavior_preservation/runners/run_benchmark.py --provider static --run-id <run-id>
python experiments/agent_behavior_preservation/analysis/summarize_results.py --run-dir experiments/agent_behavior_preservation/results/<run-id>
```

`--provider static` is a deterministic local control provider used to validate the
pipeline. It is not a paid external model and should not be used as evidence about a named
coding model. To evaluate stored external model responses, write JSONL rows containing
`task_id`, `provider`, `model`, `raw_response`, and optional self-assessment fields, then
run with `--provider jsonl --replay-path <responses.jsonl>`.
