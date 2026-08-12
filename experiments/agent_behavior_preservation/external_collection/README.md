# External Model Collection

These files are for collecting real coding-model responses outside this repository-local
runner when no authenticated provider is available locally.

Use one fresh model context per JSONL row. Do not show prior results, oracle outcomes,
hidden labels, or normal-condition outputs to warned-condition generations.

For each collected generation, store the exact raw model response in a replay JSONL row
with `task_id`, `provider`, `model`, `temperature`, `seed`, `raw_response`, and
`self_assessment`. Then evaluate it with:

```powershell
experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe experiments\agent_behavior_preservation\runners\run_benchmark.py --provider jsonl --replay-path <responses.jsonl> --task-ids-from-replay --run-id <unique-run-id>
```

Run the small validation subset first, then all normal prompts, then all warned prompts.
Never overwrite completed response files or benchmark run directories.

