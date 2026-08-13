from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def wilson(passed: int, total: int, z: float = 1.96) -> str:
    if total == 0:
        return "n/a"
    phat = passed / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return f"{center - half:.1%}-{center + half:.1%}"


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    total = len(rows)
    attempted = sum(1 for r in rows if r.get("raw_response"))
    applied = sum(1 for r in rows if r.get("patch_applied"))
    executable = sum(1 for r in rows if r.get("execution_status") == "successful_execution")
    preserved = sum(1 for r in rows if r.get("behavior_preserved") is True)
    diverged = sum(1 for r in rows if r.get("behavior_preserved") is False and r.get("execution_status") == "successful_execution")
    ordinary_missed = sum(
        1
        for r in rows
        if r.get("ordinary_tests_pass") is True and r.get("metamorphic_tests_pass") is False
    )
    osds_caught = sum(1 for r in rows if r.get("metamorphic_tests_pass") is False and r.get("execution_status") == "successful_execution")
    claims = sum(
        1
        for r in rows
        if r.get("agent_claimed_preservation") is True
        and r.get("execution_status") == "successful_execution"
    )
    correct_claims = sum(
        1
        for r in rows
        if r.get("agent_claimed_preservation") is True
        and r.get("execution_status") == "successful_execution"
        and r.get("behavior_preserved") is True
    )
    false_claims = sum(
        1
        for r in rows
        if r.get("agent_claimed_preservation") is True
        and r.get("execution_status") == "successful_execution"
        and r.get("behavior_preserved") is False
    )
    by_divergence = Counter(str(r.get("divergence_type", "")) for r in rows)
    by_role = _group(rows, "evidence_role")
    by_family = _group(rows, "transformation_family")
    by_model = _group(rows, "model")
    return {
        "total_tasks": total,
        "generations_attempted": attempted,
        "generations_successfully_applied": applied,
        "executable_generations": executable,
        "preserved": preserved,
        "diverged": diverged,
        "behavior_preservation_rate": preserved / executable if executable else None,
        "behavior_preservation_rate_wilson_95": wilson(preserved, executable),
        "ordinary_tests_missed": ordinary_missed,
        "osds_caught": osds_caught,
        "ordinary_pass_metamorphic_fail": ordinary_missed,
        "claims_preserved": claims,
        "correct_preservation_claims": correct_claims,
        "false_preservation_claims": false_claims,
        "false_preservation_claim_rate": false_claims / claims if claims else None,
        "divergence_counts": dict(sorted(by_divergence.items())),
        "by_evidence_role": by_role,
        "by_transformation_family": by_family,
        "by_model": by_model,
    }


def _group(rows: list[dict[str, object]], key: str) -> dict[str, dict[str, int]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key, ""))].append(row)
    out = {}
    for name, group in sorted(groups.items()):
        executable = sum(1 for r in group if r.get("execution_status") == "successful_execution")
        preserved = sum(1 for r in group if r.get("behavior_preserved") is True)
        diverged = sum(1 for r in group if r.get("behavior_preserved") is False and r.get("execution_status") == "successful_execution")
        out[name] = {"tasks": len(group), "executable": executable, "preserved": preserved, "diverged": diverged}
    return out

