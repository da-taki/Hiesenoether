from __future__ import annotations

import json
from pathlib import Path

from agent_bp.cases import build_tasks, render_prompt
from agent_bp.schema import validate_tasks


BASE = Path(__file__).resolve().parent
BENCHMARK = BASE / "benchmark"
PROMPTS = BASE / "prompts"


def main() -> int:
    tasks = build_tasks()
    validate_tasks(tasks)
    BENCHMARK.mkdir(parents=True, exist_ok=True)
    PROMPTS.mkdir(parents=True, exist_ok=True)
    for stale_prompt in PROMPTS.glob("*.md"):
        stale_prompt.unlink()
    task_path = BENCHMARK / "tasks.jsonl"
    with task_path.open("w", encoding="utf-8") as handle:
        for task in tasks:
            handle.write(json.dumps(task, sort_keys=True) + "\n")
            (PROMPTS / f"{task['task_id']}.md").write_text(render_prompt(task), encoding="utf-8")
    print(f"wrote {task_path} ({len(tasks)} tasks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

