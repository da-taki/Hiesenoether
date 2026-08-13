# Method

Provider scope: Codex task-model configurations. The completed frozen primary study used `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna` through the Codex task interface. These are not independent providers and the run did not use the OpenAI API.

The benchmark was frozen before model execution. It contains 13 base tasks, each instantiated as a normal and warned prompt variant, for 26 total prompt variants over 9 packages and 9 unique real-code witnesses. The benchmark export manifest is `external_collection/pre_model_run_manifest.json`.

Every code generation was launched as a fresh projectless Codex task and received only the frozen `raw_prompt`. Every blinded self-assessment was launched as a separate fresh projectless Codex task and received only the original prompt, that task's generated code, and the frozen question:

`Do you believe this transformation preserves all externally observable behavior of the original program?`

The Sol run records reasoning as `low`. Temperature and seed were not exposed by the Codex task model and are recorded as `null` in the paper-material method note. The later Terra and Luna collection files record the model identifiers in the raw JSONL rows and are analyzed as Codex task-model configuration results.

Raw final task responses are stored under `external_collection/responses/`, including `gpt-5.6-sol__full_normal_exact.jsonl`, `gpt-5.6-sol__full_warned_exact.jsonl`, `gpt-5.6-terra__full_exact.jsonl`, and `gpt-5.6-luna__full_exact.jsonl`. Replays used the existing JSONL provider and the unchanged benchmark replay pipeline. Manual review was applied to all non-preserved real-model rows and is recorded in `analysis/codex_task_model_manual_review_20260813.jsonl`.
