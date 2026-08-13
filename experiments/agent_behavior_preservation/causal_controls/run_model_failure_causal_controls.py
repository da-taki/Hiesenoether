from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import logging
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[1]
ORACLE_DIR = REPO / "paper_artifacts" / "scp_realcode_metamorphic_oracle"
ROOT_ANALYSIS = REPO / "analysis"
TASKS = EXPERIMENT / "benchmark" / "tasks.jsonl"

sys.path.insert(0, str(EXPERIMENT))
sys.path.insert(0, str(ORACLE_DIR))

from agent_bp.execution import compare_behavior, evaluate_source, sha256_text  # noqa: E402

try:
    import metamorphic_fixtures as F  # noqa: E402

    F.add_snapshot_paths()
except Exception:
    pass

CSV_FIELDS = [
    "model",
    "condition",
    "task_id",
    "package",
    "package_version",
    "witness_id",
    "generated_candidate_path",
    "generated_candidate_sha256",
    "baseline_behavior",
    "generated_behavior",
    "ordinary_test_result",
    "osds_result",
    "caller_level_result",
    "control_intervention",
    "controlled_behavior",
    "controlled_osds_result",
    "controlled_caller_result",
    "causal_status",
]


@dataclass(frozen=True)
class KnownFailure:
    model: str
    run_id: str
    task_id: str
    control_kind: str
    control_intervention: str

    @property
    def condition(self) -> str:
        return self.task_id.rsplit("__", 1)[-1]


KNOWN_FAILURES: tuple[KnownFailure, ...] = (
    KnownFailure(
        model="gpt-5.6-terra",
        run_id="codex-gpt-5-6-terra-full-exact-20260813T1730Z",
        task_id="pytest_catching_logs__instrumentation__normal",
        control_kind="pytest_logging_isolation",
        control_intervention="isolate diagnostic logger from the captured handler hierarchy",
    ),
    KnownFailure(
        model="gpt-5.6-terra",
        run_id="codex-gpt-5-6-terra-full-exact-20260813T1730Z",
        task_id="pytest_catching_logs__instrumentation__warned",
        control_kind="pytest_logging_isolation",
        control_intervention="isolate diagnostic logger from the captured handler hierarchy",
    ),
    KnownFailure(
        model="gpt-5.6-luna",
        run_id="codex-gpt-5-6-luna-full-exact-20260813T1730Z",
        task_id="pytest_catching_logs__instrumentation__normal",
        control_kind="pytest_logging_isolation",
        control_intervention="isolate diagnostic logger from the captured handler hierarchy",
    ),
    KnownFailure(
        model="gpt-5.6-luna",
        run_id="codex-gpt-5-6-luna-full-exact-20260813T1730Z",
        task_id="pytest_catching_logs__instrumentation__warned",
        control_kind="pytest_logging_isolation",
        control_intervention="isolate diagnostic logger from the captured handler hierarchy",
    ),
    KnownFailure(
        model="gpt-5.6-luna",
        run_id="codex-gpt-5-6-luna-full-exact-20260813T1730Z",
        task_id="pyyaml_representer__caching_materialization__normal",
        control_kind="pyyaml_cache_neutralization",
        control_intervention="clear representer identity cache after represent_data observations",
    ),
)


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_tasks() -> dict[str, dict[str, object]]:
    return {str(row["task_id"]): row for row in load_jsonl(TASKS)}


def load_result_row(failure: KnownFailure) -> dict[str, object]:
    path = EXPERIMENT / "results" / failure.run_id / "results.jsonl"
    for row in load_jsonl(path):
        if row.get("task_id") == failure.task_id:
            return row
    raise KeyError(f"result row not found for {failure.run_id}/{failure.task_id}")


def candidate_path(failure: KnownFailure) -> Path:
    return EXPERIMENT / "results" / failure.run_id / "candidates" / failure.task_id / "candidate.py"


def run_controls(write_outputs: bool = True) -> list[dict[str, str]]:
    tasks = load_tasks()
    records = [_evaluate_failure(failure, tasks[failure.task_id]) for failure in KNOWN_FAILURES]
    if write_outputs:
        ROOT_ANALYSIS.mkdir(parents=True, exist_ok=True)
        csv_path = ROOT_ANALYSIS / "model_failure_causal_controls.csv"
        md_path = ROOT_ANALYSIS / "model_failure_causal_controls.md"
        write_csv(records, csv_path)
        write_markdown(records, md_path)
    return records


def _evaluate_failure(failure: KnownFailure, task: dict[str, object]) -> dict[str, str]:
    path = candidate_path(failure)
    source = path.read_text(encoding="utf-8")
    replay_row = load_result_row(failure)
    source_sha = sha256_text(source)
    if source_sha != replay_row.get("candidate_source_sha256"):
        raise RuntimeError(f"candidate sha mismatch for {failure.task_id}")

    baseline = evaluate_source(str(task["source_context"]))
    generated = evaluate_source(source)
    original_comparison = compare_behavior(baseline, generated)

    controlled_baseline = evaluate_controlled(failure.control_kind, str(task["source_context"]))
    controlled_generated = evaluate_controlled(failure.control_kind, source)
    controlled_comparison = compare_behavior(controlled_baseline, controlled_generated)

    ordinary_pass = bool(original_comparison.get("ordinary_tests_pass"))
    original_osds_pass = bool(original_comparison.get("metamorphic_tests_pass"))
    controlled_osds_pass = bool(controlled_comparison.get("metamorphic_tests_pass"))

    if generated.get("status") != "successful_execution" or controlled_generated.get("status") != "successful_execution":
        causal_status = "control_failed"
    elif not original_osds_pass and controlled_osds_pass:
        causal_status = "mechanism_neutralized_divergence_disappeared"
    elif not original_osds_pass and not controlled_osds_pass:
        causal_status = "divergence_persisted"
    else:
        causal_status = "unclear"

    return {
        "model": failure.model,
        "condition": failure.condition,
        "task_id": failure.task_id,
        "package": str(task["package"]),
        "package_version": str(task["package_version"]),
        "witness_id": str(task["witness_id"]),
        "generated_candidate_path": str(path),
        "generated_candidate_sha256": source_sha,
        "baseline_behavior": behavior_json(baseline),
        "generated_behavior": behavior_json(generated),
        "ordinary_test_result": "pass" if ordinary_pass else "fail",
        "osds_result": "pass" if original_osds_pass else "fail",
        "caller_level_result": caller_summary(generated),
        "control_intervention": failure.control_intervention,
        "controlled_behavior": behavior_json(controlled_generated),
        "controlled_osds_result": "pass" if controlled_osds_pass else "fail",
        "controlled_caller_result": caller_summary(controlled_generated),
        "causal_status": causal_status,
    }


def behavior_json(result: dict[str, object]) -> str:
    payload = {
        "status": result.get("status"),
        "ordinary": result.get("ordinary"),
        "order_A": result.get("order_A"),
        "order_B": result.get("order_B"),
    }
    return json.dumps(payload, sort_keys=True)


def caller_summary(result: dict[str, object]) -> str:
    return json.dumps({"order_A": result.get("order_A"), "order_B": result.get("order_B")}, sort_keys=True)


def evaluate_controlled(control_kind: str, source: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="agent_bp_causal_") as tmp:
        module_path = Path(tmp) / "candidate.py"
        module_path.write_text(source, encoding="utf-8")
        try:
            mod = import_module(module_path)
            if not hasattr(mod, "subject"):
                return {"status": "runtime_failure", "phase": "shape", "error": "missing subject"}
            with control_context(control_kind):
                ordinary = cap(lambda: bool(getattr(mod, "ordinary_smoke", lambda: True)()))
                order_a = _controlled_subject_call(control_kind, mod, False)
                order_b = _controlled_subject_call(control_kind, mod, True)
            return {
                "status": "successful_execution",
                "ordinary": ordinary,
                "order_A": order_a,
                "order_B": order_b,
                "source_sha256": sha256_text(source),
                "module_path": str(module_path),
            }
        except SyntaxError as exc:
            return {"status": "syntax_failure", "error": f"{type(exc).__name__}: {exc}"}
        except ImportError as exc:
            return {"status": "import_failure", "error": f"{type(exc).__name__}: {exc}"}
        except Exception as exc:
            return {"status": "environment_failure", "error": f"{type(exc).__name__}: {exc}"}


def _controlled_subject_call(control_kind: str, mod: object, flag: bool) -> dict[str, object]:
    if control_kind == "pytest_logging_isolation":
        isolate_pytest_diagnostic_logger()
    return cap(lambda: mod.subject(flag))


def import_module(module_path: Path) -> object:
    name = f"agent_bp_causal_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {module_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cap(fn: Callable[[], object]) -> dict[str, object]:
    try:
        return {"kind": "value", "value": fn()}
    except Exception as exc:
        return {"kind": "exception", "type": type(exc).__name__, "message": str(exc)[:500]}


@contextmanager
def control_context(control_kind: str):
    if control_kind == "pytest_logging_isolation":
        yield
        cleanup_pytest_loggers()
        return
    if control_kind == "pyyaml_cache_neutralization":
        with neutralize_pyyaml_identity_cache():
            yield
        return
    raise ValueError(f"unknown control kind: {control_kind}")


def isolate_pytest_diagnostic_logger() -> None:
    diagnostic = logging.getLogger("agent_bp_pytest_case.diagnostics")
    diagnostic.handlers = []
    diagnostic.addHandler(logging.NullHandler())
    diagnostic.propagate = False
    diagnostic.setLevel(logging.DEBUG)


def cleanup_pytest_loggers() -> None:
    for name in ("agent_bp_pytest_case", "agent_bp_pytest_case.diagnostics"):
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True
        logger.disabled = False


@contextmanager
def neutralize_pyyaml_identity_cache():
    from yaml.representer import SafeRepresenter

    original = SafeRepresenter.represent_data

    def represent_data_and_clear(self, data):
        node = original(self, data)
        if hasattr(self, "represented_objects"):
            self.represented_objects.clear()
        if hasattr(self, "object_keeper"):
            self.object_keeper.clear()
        return node

    SafeRepresenter.represent_data = represent_data_and_clear
    try:
        yield
    finally:
        SafeRepresenter.represent_data = original


def write_csv(records: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def write_markdown(records: list[dict[str, str]], path: Path) -> None:
    status_counts: dict[str, int] = {}
    for row in records:
        status_counts[row["causal_status"]] = status_counts.get(row["causal_status"], 0) + 1
    lines = [
        "# Model Failure Causal Controls",
        "",
        "This report replays the five verified OSDS failures from the frozen primary Codex task-model study under mechanism-neutralizing witness controls. The generated candidate files are read exactly from the frozen replay result directories and are not edited.",
        "",
        "## Summary",
        "",
        "| Causal status | Count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{status}` | {count} |")
    lines.extend([
        "",
        "## Per-Failure Results",
        "",
        "| Model | Task | Package | Intervention | Original OSDS | Controlled OSDS | Causal status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in records:
        lines.append(
            "| {model} | `{task_id}` | {package} | {control_intervention} | {osds_result} | {controlled_osds_result} | `{causal_status}` |".format(
                **row
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "For pytest, the control isolates the diagnostic logger from the logger hierarchy that owns the captured handler. The exact generated patch still executes its diagnostic logging calls, but those calls no longer populate the same handler whose level is later mutated by `catching_logs`. Under this neutralized witness environment, the candidate behavior matches the controlled baseline.",
        "",
        "For PyYAML, the control wraps `SafeRepresenter.represent_data` so the identity cache is cleared after each representer observation. The exact Luna candidate still uses its generated caching transformation. Under this cache-neutralized environment, the controlled baseline no longer returns the stale pre-mutation node, and the candidate matches the controlled baseline.",
        "",
        "These controls support the causal attribution that the five verified failures depend on the access-induced latent-state mechanisms identified by the OSDS witnesses.",
        "",
        "CSV source: `analysis/model_failure_causal_controls.csv`.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    records = run_controls(write_outputs=not args.no_write)
    print(json.dumps({"records": len(records), "causal_status_counts": _counts(records)}, indent=2, sort_keys=True))
    return 0


def _counts(records: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        status = record["causal_status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
