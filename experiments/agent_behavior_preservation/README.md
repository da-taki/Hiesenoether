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

## Exact Environment Reconstruction

The current benchmark should be run from the repository-local venv:

```powershell
py -m venv experiments\agent_behavior_preservation\environment\.venv
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe -m pip install -r experiments\agent_behavior_preservation\environment\requirements-exact.txt
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\environment\reconstruct_environment.py
```

Then regenerate and validate:

```powershell
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\build_benchmark.py
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\analysis\audit_benchmark_balance.py
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\analysis\audit_prompt_leakage.py
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\runners\validate_baselines.py
```

## Provider Gate

Run provider discovery before real model calls:

```powershell
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\environment\discover_providers.py
```

If no authenticated provider is available, stop after environment/baseline validation and use the JSONL replay provider for externally collected responses. Do not treat `noop-preserving` or `static-semantics-blind-transformer` as real coding models.

## External Model Collection Fallback

When provider discovery reports no authenticated real-model access, export the exact collection package:

```powershell
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\runners\export_external_collection.py --benchmark-commit 7d85b076b7203300c10eda308649e785bd4cd615
```

The exporter writes `external_collection/` with a pre-model run manifest, a six-task normal-only validation subset, full normal prompts, full warned prompts, a replay response template, and the self-assessment prompt. Collect each generation in a fresh external model context and evaluate the filled response JSONL with the existing `--provider jsonl` runner. Keep local controls separate from real-model results.
