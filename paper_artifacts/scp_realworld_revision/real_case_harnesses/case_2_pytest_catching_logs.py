from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from _pytest.logging import catching_logs


OUT = Path(__file__).resolve().parents[1] / "real_case_outputs" / "case_2_pytest_catching_logs.json"


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def run_sequence(observe_first: bool) -> dict[str, object]:
    logger = logging.getLogger("scp_realworld_revision.pytest_case")
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    handler = ListHandler()
    handler.setLevel(logging.NOTSET)
    logger.addHandler(handler)
    before = {"handler_level": handler.level, "messages": list(handler.messages)}
    if observe_first:
        cm = catching_logs(handler, level=logging.ERROR)
        cm.__enter__()
        cm.__exit__(None, None, None)
    after_observation = {"handler_level": handler.level, "messages": list(handler.messages)}
    logger.warning("warning-visible")
    after_later = {"handler_level": handler.level, "messages": list(handler.messages)}
    return {"before": before, "after_observation": after_observation, "after_later": after_later}


def main() -> int:
    a = run_sequence(False)
    b = run_sequence(True)
    output_diff = a["after_later"]["messages"] != b["after_later"]["messages"]
    state_diff = a["after_later"]["handler_level"] != b["after_later"]["handler_level"]
    data = {
        "case_id": "case_2_pytest_catching_logs",
        "package": "pytest",
        "version": pytest.__version__,
        "class_name": "catching_logs",
        "file_path": "_pytest/logging.py",
        "operation_A": "emit WARNING with fresh handler",
        "result_A": a,
        "operation_B": "enter/exit catching_logs(level=ERROR); then emit same WARNING",
        "result_B": b,
        "branch_flip": output_diff,
        "output_diff": output_diff,
        "state_diff": state_diff,
        "classification": "confirmed_branch_flip" if output_diff else "structural_only_no_runtime_difference",
        "read_or_observer_operation": "catching_logs.__enter__()/__exit__()",
        "latent_state": "handler.level",
        "later_read_or_behavior": "logging handler filters WARNING after level mutation",
        "notes": "Uses pytest internal logging utility. It is a behavioral instance, not an upstream bug claim.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
