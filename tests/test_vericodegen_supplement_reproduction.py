from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPLEMENT = ROOT / "submissions" / "vericodegen_osds" / "supplement"


def _build_zip(target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SUPPLEMENT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(SUPPLEMENT).as_posix())


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = ""
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, timeout=90)


def test_vericodegen_supplement_clean_extraction_reproduces_core_artifacts(tmp_path: Path):
    package = tmp_path / "vericodegen_osds_supplement.zip"
    extract = tmp_path / "extract"
    _build_zip(package)
    with zipfile.ZipFile(package) as archive:
        archive.extractall(extract)

    required = [
        "REPRODUCE.md",
        "SUPPLEMENT_DEPENDENCY_AUDIT.md",
        "experiments/agent_behavior_preservation/agent_bp/cases.py",
        "experiments/agent_behavior_preservation/agent_bp/execution.py",
        "experiments/agent_behavior_preservation/agent_bp/patching.py",
        "experiments/agent_behavior_preservation/agent_bp/providers.py",
        "experiments/agent_behavior_preservation/agent_bp/schema.py",
        "paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py",
        "paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_candidates.py",
        "experiments/agent_behavior_preservation/causal_controls/frozen_candidates/terra_pytest_normal.py",
        "experiments/agent_behavior_preservation/causal_controls/frozen_candidates/luna_pyyaml_normal.py",
    ]
    for rel in required:
        assert (extract / rel).exists(), rel

    audit = (extract / "SUPPLEMENT_DEPENDENCY_AUDIT.md").read_text(encoding="utf-8")
    assert "Unresolved repository-local imports for documented reproduction commands: 0" in audit

    import_check = _run([
        sys.executable,
        "-c",
        "import sys; sys.path.insert(0, 'experiments/agent_behavior_preservation'); sys.path.insert(0, 'paper_artifacts/scp_realcode_metamorphic_oracle'); import agent_bp.cases, agent_bp.execution, agent_bp.patching, agent_bp.providers, agent_bp.schema, metamorphic_fixtures, metamorphic_candidates; print('imports ok')",
    ], extract)
    assert import_check.returncode == 0, import_check.stderr + import_check.stdout

    primary = _run([
        sys.executable,
        "experiments/agent_behavior_preservation/runners/run_benchmark.py",
        "--provider", "jsonl",
        "--replay-path", "experiments/agent_behavior_preservation/external_collection/responses/gpt-5.6-terra__full_exact.jsonl",
        "--task-id", "pytest_catching_logs__instrumentation__normal",
        "--run-id", "clean-test-primary",
        "--timeout-s", "8",
    ], extract)
    assert primary.returncode == 0, primary.stderr + primary.stdout
    primary_payload = json.loads(primary.stdout)
    assert primary_payload["tasks"] == 1
    assert (extract / "experiments/agent_behavior_preservation/results/clean-test-primary/results.jsonl").exists()
    assert (extract / "experiments/agent_behavior_preservation/results/clean-test-primary/candidates/pytest_catching_logs__instrumentation__normal/candidate.py").exists()

    prospective = _run([
        sys.executable,
        "experiments/agent_behavior_preservation/runners/run_benchmark.py",
        "--tasks", "benchmark_expansion/tasks.jsonl",
        "--provider", "jsonl",
        "--replay-path", "benchmark_expansion/responses/gpt_5_6_luna__expansion.jsonl",
        "--task-id", "h11_receive_buffer__access_reordering__normal",
        "--run-id", "clean-test-prospective",
        "--timeout-s", "8",
    ], extract)
    assert prospective.returncode == 0, prospective.stderr + prospective.stdout
    prospective_payload = json.loads(prospective.stdout)
    assert prospective_payload["tasks"] == 1
    assert (extract / "experiments/agent_behavior_preservation/results/clean-test-prospective/results.jsonl").exists()

    causal = _run([
        sys.executable,
        "experiments/agent_behavior_preservation/causal_controls/run_model_failure_causal_controls.py",
        "--no-write",
    ], extract)
    assert causal.returncode == 0, causal.stderr + causal.stdout
    causal_payload = json.loads(causal.stdout)
    assert causal_payload == {
        "causal_status_counts": {"mechanism_neutralized_divergence_disappeared": 5},
        "records": 5,
    }
