from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from agent_bp.cases import render_prompt
from agent_bp.schema import validate_tasks


TASKS = BASE / "benchmark" / "tasks.jsonl"
DEFAULT_OUT = BASE / "external_collection"
REPO = BASE.parents[1]
SELF_ASSESSMENT_PROMPT = (
    "Do you believe your transformation preserves all externally observable\n"
    "behavior of the original program?\n\n"
    "Answer YES or NO first, then briefly explain why.\n"
)


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def load_tasks(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    validate_tasks(rows)
    return rows


def load_exact_requirements(path: Path) -> dict[str, str]:
    versions: dict[str, str] = {}
    with path.open(encoding="utf-8-sig") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "==" not in line:
                continue
            package, version = line.split("==", 1)
            versions[package.strip()] = version.strip()
    return versions


def load_provider_discovery(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8-sig")).get("providers", [])


def normal_base_tasks(tasks: list[dict[str, object]]) -> list[dict[str, object]]:
    return [task for task in tasks if task["prompt_condition"] == "normal"]


def select_validation_subset(tasks: list[dict[str, object]]) -> list[dict[str, object]]:
    normal = normal_base_tasks(tasks)
    hidden = [task for task in normal if task["evidence_role"] == "hidden_observation"]
    calibration = [task for task in normal if task["evidence_role"] == "expected_access_sensitive"]
    return hidden[:4] + calibration[:2]


def prompt_row(task: dict[str, object]) -> dict[str, object]:
    return {
        "task_id": task["task_id"],
        "pair_id": task["pair_id"],
        "witness_id": task["witness_id"],
        "package": task["package"],
        "package_version": task["package_version"],
        "evidence_role": task["evidence_role"],
        "transformation_family": task["transformation_family"],
        "prompt_condition": task["prompt_condition"],
        "raw_prompt": render_prompt(task),
    }


def replay_template_row(task: dict[str, object]) -> dict[str, object]:
    return {
        "task_id": task["task_id"],
        "provider": "<provider-name>",
        "model": "<provider-returned-model-id>",
        "temperature": 0,
        "seed": None,
        "raw_response": "<paste exact model response here>",
        "self_assessment": "<paste fresh-context self-assessment here>",
    }


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def collection_readme() -> str:
    return """# External Model Collection

These files are for collecting real coding-model responses outside this repository-local
runner when no authenticated provider is available locally.

Use one fresh model context per JSONL row. Do not show prior results, oracle outcomes,
hidden labels, or normal-condition outputs to warned-condition generations.

For each collected generation, store the exact raw model response in a replay JSONL row
with `task_id`, `provider`, `model`, `temperature`, `seed`, `raw_response`, and
`self_assessment`. Then evaluate it with:

```powershell
experiments\\agent_behavior_preservation\\environment\\.venv\\Scripts\\python.exe experiments\\agent_behavior_preservation\\runners\\run_benchmark.py --provider jsonl --replay-path <responses.jsonl> --run-id <unique-run-id>
```

Run the small validation subset first, then all normal prompts, then all warned prompts.
Never overwrite completed response files or benchmark run directories.
"""


def build_manifest(
    *,
    tasks: list[dict[str, object]],
    benchmark_commit: str,
    provider_discovery: list[dict[str, object]],
) -> dict[str, object]:
    witness_count = len({task["witness_id"] for task in tasks})
    packages = sorted({task["package"] for task in tasks})
    prompt_counts = Counter(str(task["prompt_condition"]) for task in tasks)
    evidence_counts = Counter(str(task["evidence_role"]) for task in tasks)
    family_counts = Counter(str(task["transformation_family"]) for task in tasks)
    usable_providers = [
        provider
        for provider in provider_discovery
        if provider.get("authentication_usable") is True
    ]
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "branch": git_value("branch", "--show-current"),
        "benchmark_commit": benchmark_commit,
        "support_commit_at_export": git_value("rev-parse", "HEAD"),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "operating_system": platform.platform(),
        "package_versions": load_exact_requirements(BASE / "environment" / "requirements-exact.txt"),
        "benchmark_task_count": len(tasks),
        "base_task_count": len(normal_base_tasks(tasks)),
        "witness_count": witness_count,
        "packages": packages,
        "prompt_condition_counts": dict(sorted(prompt_counts.items())),
        "evidence_role_counts": dict(sorted(evidence_counts.items())),
        "transformation_family_counts": dict(sorted(family_counts.items())),
        "provider_discovery": provider_discovery,
        "provider_model_configuration": {
            "usable_provider_count": len(usable_providers),
            "models_selected_for_local_execution": [],
            "fallback": "jsonl_replay_external_collection",
            "generation_parameters": {"temperature": 0},
        },
    }


def export_collection(tasks: list[dict[str, object]], out_dir: Path, benchmark_commit: str) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    normal = [task for task in tasks if task["prompt_condition"] == "normal"]
    warned = [task for task in tasks if task["prompt_condition"] == "warned"]
    validation = select_validation_subset(tasks)
    provider_discovery = load_provider_discovery(BASE / "environment" / "provider_discovery.json")

    write_jsonl(out_dir / "small_validation_normal_prompts.jsonl", [prompt_row(task) for task in validation])
    write_jsonl(out_dir / "full_normal_prompts.jsonl", [prompt_row(task) for task in normal])
    write_jsonl(out_dir / "full_warned_prompts.jsonl", [prompt_row(task) for task in warned])
    write_jsonl(out_dir / "replay_response_template.jsonl", [replay_template_row(task) for task in tasks])
    write_text(out_dir / "self_assessment_prompt.txt", SELF_ASSESSMENT_PROMPT)
    write_text(out_dir / "README.md", collection_readme())

    manifest = build_manifest(
        tasks=tasks,
        benchmark_commit=benchmark_commit,
        provider_discovery=provider_discovery,
    )
    manifest["files"] = {
        "small_validation_normal_prompts": "small_validation_normal_prompts.jsonl",
        "full_normal_prompts": "full_normal_prompts.jsonl",
        "full_warned_prompts": "full_warned_prompts.jsonl",
        "replay_response_template": "replay_response_template.jsonl",
        "self_assessment_prompt": "self_assessment_prompt.txt",
    }
    write_text(out_dir / "pre_model_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default=str(TASKS))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--benchmark-commit", default=git_value("rev-parse", "HEAD"))
    args = parser.parse_args()

    tasks = load_tasks(Path(args.tasks))
    manifest = export_collection(tasks, Path(args.out_dir), args.benchmark_commit)
    print(json.dumps({
        "out_dir": args.out_dir,
        "benchmark_commit": manifest["benchmark_commit"],
        "base_task_count": manifest["base_task_count"],
        "task_count": manifest["benchmark_task_count"],
        "usable_provider_count": manifest["provider_model_configuration"]["usable_provider_count"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
