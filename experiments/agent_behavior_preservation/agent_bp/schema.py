from __future__ import annotations


REQUIRED_TASK_FIELDS = {
    "task_id",
    "case_id",
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
    if "hidden_observation" in str(task["agent_instruction"]):
        raise SchemaError(f"{task['task_id']}: model-visible prompt leaks evidence role")


def validate_tasks(tasks: list[dict[str, object]]) -> None:
    seen: set[str] = set()
    for task in tasks:
        validate_task(task)
        task_id = str(task["task_id"])
        if task_id in seen:
            raise SchemaError(f"duplicate task_id {task_id}")
        seen.add(task_id)
