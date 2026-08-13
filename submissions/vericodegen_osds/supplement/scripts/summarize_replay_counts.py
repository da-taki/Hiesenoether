from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "experiments" / "agent_behavior_preservation" / "results"
EXPANSION_ANALYSIS = ROOT / "analysis" / "prospective_task_compliance.csv"
CAUSAL = ROOT / "analysis" / "model_failure_causal_controls.csv"

PRIMARY_RUNS = {
    "gpt-5.6-sol normal": "codex-gpt-5-6-sol-full-normal-exact-20260813T1415Z",
    "gpt-5.6-sol warned": "codex-gpt-5-6-sol-full-warned-exact-20260813T1430Z",
    "gpt-5.6-terra": "codex-gpt-5-6-terra-full-exact-20260813T1730Z",
    "gpt-5.6-luna": "codex-gpt-5-6-luna-full-exact-20260813T1730Z",
}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def main() -> int:
    print("# Frozen replay count summary")
    print("\n## Primary replay results")
    for label, run_id in PRIMARY_RUNS.items():
        rows = list(read_jsonl(PRIMARY / run_id / "results.jsonl"))
        status = Counter(row.get("execution_status") for row in rows)
        osds = sum(row.get("metamorphic_tests_pass") is False and row.get("ordinary_tests_pass") is True for row in rows)
        print(f"- {label}: rows={len(rows)} execution={dict(status)} silent_osds_candidates={osds}")
    print("\n## Prospective task compliance")
    rows = list(csv.DictReader(EXPANSION_ANALYSIS.open(encoding="utf-8")))
    print(f"- total={len(rows)}")
    print(f"- task_compliance={dict(Counter(row['task_compliance'] for row in rows))}")
    print(f"- osds_preservation={dict(Counter(row['osds_preservation'] for row in rows))}")
    print("\n## Causal controls")
    rows = list(csv.DictReader(CAUSAL.open(encoding="utf-8")))
    print(f"- total={len(rows)}")
    print(f"- causal_status={dict(Counter(row['causal_status'] for row in rows))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
