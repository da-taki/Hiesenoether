from __future__ import annotations

from collections import defaultdict


REQUIRED_TASK_FIELDS = {
    "task_id",
    "pair_id",
    "case_id",
    "witness_id",
    "package_id",
    "package",
    "package_version",
    "evidence_role",
    "transformation_family",
    "prompt_condition",
    "agent_instruction",
    "source_context",
    "baseline_test_command",
    "metamorphic_test_command",
    "branch_oracle_command",
    "expected_baseline_behavior",
    "critical_behavior",
    "provenance",
    "notes",
    "oracle_candidate_id",
    "branch_case_id",
}

VALID_EVIDENCE_ROLES = {"hidden_observation", "expected_access_sensitive"}
VALID_PROMPT_CONDITIONS = {"normal", "warned"}
FORBIDDEN_NORMAL_PROMPT_TERMS = {
    "osds",
    "hiesenoether",
    "access-induced semantic divergence",
    "hidden observation",
    "metamorphic oracle",
    "branch flip",
    "expected divergence",
    "critical ordering",
    "known bug",
}


class SchemaError(ValueError):
    pass


def validate_task(task: dict[str, object]) -> None:
    missing = sorted(REQUIRED_TASK_FIELDS - set(task))
    if missing:
        raise SchemaError(f"{task.get('task_id', '<unknown>')}: missing fields {missing}")
    if task["evidence_role"] not in VALID_EVIDENCE_ROLES:
        raise SchemaError(f"{task['task_id']}: invalid evidence_role {task['evidence_role']!r}")
    if task["prompt_condition"] not in VALID_PROMPT_CONDITIONS:
        raise SchemaError(f"{task['task_id']}: invalid prompt_condition {task['prompt_condition']!r}")
    if not str(task["package_version"]).strip():
        raise SchemaError(f"{task['task_id']}: package_version is required")
    if not str(task["witness_id"]).strip():
        raise SchemaError(f"{task['task_id']}: witness_id is required")
    if not str(task["package_id"]).strip():
        raise SchemaError(f"{task['task_id']}: package_id is required")
    if task["prompt_condition"] == "normal":
        visible = (str(task["agent_instruction"]) + "\n" + str(task["source_context"])).lower()
        leaks = sorted(term for term in FORBIDDEN_NORMAL_PROMPT_TERMS if term in visible)
        if leaks:
            raise SchemaError(f"{task['task_id']}: normal prompt leaks forbidden terms {leaks}")


def validate_tasks(tasks: list[dict[str, object]]) -> None:
    seen: set[str] = set()
    pairs: dict[str, list[dict[str, object]]] = defaultdict(list)
    for task in tasks:
        validate_task(task)
        task_id = str(task["task_id"])
        if task_id in seen:
            raise SchemaError(f"duplicate task_id {task_id}")
        seen.add(task_id)
        pairs[str(task["pair_id"])].append(task)
    for pair_id, pair in pairs.items():
        conditions = sorted(str(task["prompt_condition"]) for task in pair)
        if conditions != ["normal", "warned"]:
            raise SchemaError(f"{pair_id}: expected one normal and one warned task, saw {conditions}")
        normal, warned = sorted(pair, key=lambda task: str(task["prompt_condition"]))
        equivalent_fields = [
            "case_id",
            "witness_id",
            "package_id",
            "package",
            "package_version",
            "evidence_role",
            "transformation_family",
            "source_context",
            "oracle_candidate_id",
            "branch_case_id",
        ]
        for field in equivalent_fields:
            if normal[field] != warned[field]:
                raise SchemaError(f"{pair_id}: paired tasks differ in {field}")
        base_instruction = str(normal["agent_instruction"])
        warned_instruction = str(warned["agent_instruction"])
        if not warned_instruction.startswith(base_instruction):
            raise SchemaError(f"{pair_id}: warned prompt does not preserve normal instruction prefix")
