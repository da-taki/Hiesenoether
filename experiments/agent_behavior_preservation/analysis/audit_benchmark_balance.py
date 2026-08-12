from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from runners.run_benchmark import load_tasks

OUT_JSON = BASE / "analysis" / "benchmark_balance.json"
OUT_MD = BASE / "analysis" / "benchmark_balance.md"
TASKS = BASE / "benchmark" / "tasks.jsonl"


def main() -> int:
    tasks = load_tasks(TASKS)
    package_rows = []
    by_package: dict[str, list[dict[str, object]]] = defaultdict(list)
    for task in tasks:
        by_package[str(task["package"])].append(task)
    for package, group in sorted(by_package.items()):
        witnesses = sorted({str(task["witness_id"]) for task in group})
        normal = sum(1 for task in group if task["prompt_condition"] == "normal")
        warned = sum(1 for task in group if task["prompt_condition"] == "warned")
        families = sorted({str(task["transformation_family"]) for task in group})
        package_rows.append(
            {
                "package": package,
                "witnesses": witnesses,
                "normal_tasks": normal,
                "warned_tasks": warned,
                "transformation_families": families,
                "tasks": len(group),
            }
        )
    summary = {
        "tasks": len(tasks),
        "pairs": len({task["pair_id"] for task in tasks}),
        "unique_witnesses": len({task["witness_id"] for task in tasks}),
        "packages": len(by_package),
        "by_evidence_role": dict(Counter(str(task["evidence_role"]) for task in tasks)),
        "by_prompt_condition": dict(Counter(str(task["prompt_condition"]) for task in tasks)),
        "by_transformation_family": dict(Counter(str(task["transformation_family"]) for task in tasks)),
        "packages_detail": package_rows,
        "correlation_note": "Multiple tasks derived from the same witness/package are correlated and should not be described as independent semantic phenomena.",
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Benchmark Balance Audit",
        "",
        summary["correlation_note"],
        "",
        "| Package | Underlying witnesses | Normal tasks | Warned tasks | Transformation families |",
        "|---|---|---:|---:|---|",
    ]
    for row in package_rows:
        lines.append(
            f"| {row['package']} | {', '.join(row['witnesses'])} | {row['normal_tasks']} | {row['warned_tasks']} | {', '.join(row['transformation_families'])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("tasks", "pairs", "unique_witnesses", "packages")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
