# Method

Provider: Codex task model. Model: `gpt-5.6-sol`. Reasoning setting: `low`. Temperature and seed were not exposed by the Codex task model and are recorded as `null`.

The run used 13 frozen normal prompts and 13 frozen warned prompts. Every code generation was launched as a fresh projectless Codex task and received only the frozen `raw_prompt`. Every blinded self-assessment was launched as a separate fresh projectless Codex task and received only the original prompt, that task's generated code, and the frozen YES/NO preservation question.

Raw final task responses were stored in `external_collection/responses/gpt-5.6-sol__full_normal_exact.jsonl` and `external_collection/responses/gpt-5.6-sol__full_warned_exact.jsonl`. Replays used `--task-ids-from-replay` and selected exactly 13 rows for each condition. Manual review was applied to all replay non-preserved rows.
