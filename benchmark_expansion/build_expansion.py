from __future__ import annotations

import csv
import importlib.metadata as metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
EXPANSION = ROOT / "benchmark_expansion"
AGENT_BP = ROOT / "experiments" / "agent_behavior_preservation"
sys.path.insert(0, str(AGENT_BP))

from agent_bp.cases import TRANSFORMATIONS, WARNED_SUFFIX, render_prompt
from agent_bp.execution import evaluate_source
from agent_bp.schema import FORBIDDEN_NORMAL_PROMPT_TERMS, validate_tasks

CANDIDATE_FIELDS = [
    "package", "version", "witness", "classification",
    "hidden_observation_or_expected_access_sensitive", "current_primary_benchmark_member",
    "eligible", "exclusion_reason", "caller_wrapper_available", "control_available",
    "candidate_transformation_families", "boundary_note",
]

CANDIDATES = [
    ("httpcore", "1.0.9", "rc01_httpcore_Response", "confirmed_branch_divergence", "hidden_observation", True, False, "already in frozen primary benchmark", True, True, "", "read() materializes _content; content flips RuntimeError->value"),
    ("PyYAML", "6.0.3", "rc02_PyYAML_SafeRepresenter", "confirmed_output_divergence", "hidden_observation", True, False, "already in frozen primary benchmark", True, True, "", "identity cache returns stale node for mutated object"),
    ("pytest", "8.3.5", "rc03_pytest_catching_logs", "confirmed_output_divergence", "hidden_observation", True, False, "already in frozen primary benchmark", True, True, "", "handler level mutation filters later WARNING"),
    ("markdown", "3.10.2", "re01_markdown_Markdown", "confirmed_output_divergence", "expected_access_sensitive", True, False, "already in frozen primary benchmark", True, True, "", "reference registry from prior convert changes later render"),
    ("more-itertools", "11.0.2", "re02_more_itertools_seekable", "confirmed_output_divergence", "expected_access_sensitive", False, False, "more-itertools 11.0.2 is not importable in the current experiment venv or source snapshot", False, False, "", "cursor advance changes later next()"),
    ("docutils", "0.22.4", "re04_docutils_Transformer", "confirmed_state_only_divergence", "hidden_observation", False, False, "docutils 0.22.4 is not importable in the current experiment venv or source snapshot; witness is state-only", False, False, "", "serial bookkeeping advances on priority string"),
    ("beautifulsoup4", "4.14.3", "re06_beautifulsoup4_PageElement", "confirmed_output_divergence", "expected_access_sensitive", True, False, "already in frozen primary benchmark", True, False, "", "extract() destructively mutates tree"),
    ("boltons", "25.0.0", "re07_boltons_LRI", "confirmed_state_only_divergence", "expected_access_sensitive", False, True, "", False, False, "repeated_access_cleanup", "access affects stats but not eviction order"),
    ("boltons", "25.0.0", "re08_boltons_LRU", "confirmed_output_divergence", "expected_access_sensitive", True, False, "already in frozen primary benchmark", True, True, "", "access reorders recency -> changes eviction"),
    ("boltons", "25.0.0", "re09_boltons_MultiFileReader", "confirmed_output_divergence", "expected_access_sensitive", False, True, "", False, False, "access_reordering", "stream cursor advances"),
    ("cerberus", "1.3.8", "re10_cerberus_Validator", "confirmed_output_divergence", "hidden_observation", True, False, "already in frozen primary benchmark", True, True, "", "validate populates errors read later"),
    ("dnspython", "2.8.0", "re11_dnspython_Tokenizer", "confirmed_output_divergence", "expected_access_sensitive", True, False, "already in frozen primary benchmark", True, True, "", "token consumption advances cursor"),
    ("h11", "0.16.0", "re12_h11_ChunkedReader", "confirmed_output_divergence", "expected_access_sensitive", True, False, "already in frozen primary benchmark", True, True, "", "Data vs EndOfMessage after consuming chunk"),
    ("h11", "0.16.0", "re13_h11_ReceiveBuffer", "confirmed_output_divergence", "expected_access_sensitive", False, True, "", False, False, "access_reordering", "line extraction is destructive"),
    ("anyio", "4.13.0", "bs09_anyio_BlockingPortalProvider", "confirmed_output_divergence", "hidden_observation", False, False, "anyio 4.13.0 is not importable in the current experiment venv or source snapshot", False, False, "", "enter mutates lease counter"),
    ("boltons", "25.0.0", "bs15_boltons_SpooledStringIO", "confirmed_output_divergence", "expected_access_sensitive", False, True, "", False, False, "access_reordering", "text cursor advances"),
    ("docutils", "0.22.4", "bs23_docutils_Publisher", "confirmed_output_divergence", "hidden_observation", False, False, "docutils 0.22.4 is not importable in the current experiment venv or source snapshot", False, False, "", "get_settings caches settings"),
    ("boltons", "25.0.0", "ext02_boltons_SpooledBytesIO", "confirmed_output_divergence", "expected_access_sensitive", False, True, "", False, False, "access_reordering", "byte cursor advances"),
    ("dnspython", "2.8.0", "ext07_dnspython_Tokenizer_concat", "confirmed_output_divergence", "expected_access_sensitive", False, True, "", False, False, "access_reordering", "consuming tokens changes remaining concatenation"),
    ("boltons", "25.0.0", "ext08_boltons_LRU_pair2", "confirmed_output_divergence", "expected_access_sensitive", False, True, "", False, False, "repeated_access_cleanup", "access between reads changes eviction victim"),
]

SOURCES = {
"re07_boltons_LRI": ("boltons_lri_stats", "repeated_access_cleanup", "boltons", "boltons", "25.0.0", "expected_access_sensitive", "touching a changes hit_count even though item order is unchanged", "without touching a first, hit_count is zero", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/re07_boltons_LRI.json", "Prospective unused cache-stat witness.", '''
from boltons.cacheutils import LRI


def subject(touch_a=False):
    cache = LRI(max_size=2)
    cache["a"] = "A"
    cache["b"] = "B"
    if touch_a:
        cache["a"]
    cache["c"] = "C"
    return ("items", tuple(cache.items()), cache.hit_count, cache.miss_count)


def ordinary_smoke():
    cache = LRI(max_size=2)
    cache["x"] = 1
    return cache["x"] == 1
'''),
"re09_boltons_MultiFileReader": ("boltons_multifile_reader", "access_reordering", "boltons", "boltons", "25.0.0", "expected_access_sensitive", "a preliminary read advances the multi-file cursor", "without a preliminary read, chunks are abc and de", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/re09_boltons_MultiFileReader.json", "Prospective unused stream-cursor witness.", '''
from io import BytesIO
from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))
    if pre_read:
        reader.read(3)
    first = reader.read(3).decode("ascii")
    second = reader.read(3).decode("ascii")
    return ("chunks", first, second)


def ordinary_smoke():
    return MultiFileReader(BytesIO(b"ok")).read(2) == b"ok"
'''),
"re13_h11_ReceiveBuffer": ("h11_receive_buffer", "access_reordering", "h11", "h11", "0.16.0", "expected_access_sensitive", "extracting one line consumes it before later header extraction", "without extracting first, request and host lines remain", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/re13_h11_ReceiveBuffer.json", "Prospective unused destructive-buffer witness.", '''
from h11._receivebuffer import ReceiveBuffer


def subject(extract_one=False):
    buffer = ReceiveBuffer()
    buffer += b"GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\nBODY"
    if extract_one:
        buffer.maybe_extract_next_line()
    lines = buffer.maybe_extract_lines()
    return ("lines", tuple(bytes(line).decode("ascii") for line in lines))


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"x\\r\\n"
    return buffer.maybe_extract_next_line() == b"x\\r\\n"
'''),
"bs15_boltons_SpooledStringIO": ("boltons_spooled_string_io", "access_reordering", "boltons", "boltons", "25.0.0", "expected_access_sensitive", "a preliminary read advances the text stream cursor", "without a preliminary read, chunks are alp and ha ", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/bs15_boltons_SpooledStringIO.json", "Prospective unused text-spool witness.", '''
from boltons.ioutils import SpooledStringIO


def subject(pre_read=False):
    stream = SpooledStringIO()
    stream.write("alpha beta")
    stream.seek(0)
    if pre_read:
        stream.read(3)
    first = stream.read(3)
    second = stream.read(3)
    return ("chunks", first, second)


def ordinary_smoke():
    stream = SpooledStringIO()
    stream.write("ok")
    stream.seek(0)
    return stream.read() == "ok"
'''),
"ext02_boltons_SpooledBytesIO": ("boltons_spooled_bytes_io", "access_reordering", "boltons", "boltons", "25.0.0", "expected_access_sensitive", "a preliminary read advances the byte stream cursor", "without a preliminary read, chunks are alp and hab", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/ext02_boltons_SpooledBytesIO.json", "Prospective unused byte-spool witness.", '''
from boltons.ioutils import SpooledBytesIO


def subject(pre_read=False):
    stream = SpooledBytesIO()
    stream.write(b"alphabeta")
    stream.seek(0)
    if pre_read:
        stream.read(3)
    first = stream.read(3).decode("ascii")
    second = stream.read(3).decode("ascii")
    return ("chunks", first, second)


def ordinary_smoke():
    stream = SpooledBytesIO()
    stream.write(b"ok")
    stream.seek(0)
    return stream.read() == b"ok"
'''),
"ext07_dnspython_Tokenizer_concat": ("dnspython_tokenizer_concat", "access_reordering", "dnspython", "dnspython", "2.8.0", "expected_access_sensitive", "a preliminary token read removes aa from later concatenation", "without consuming first, remaining identifiers concatenate to aabbcc", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/ext07_dnspython_Tokenizer_concat.json", "Prospective unused tokenizer-concat witness.", '''
import io
from dns.tokenizer import Tokenizer


def remaining(tokenizer):
    parts = []
    while True:
        token = tokenizer.get()
        if token.is_eof():
            break
        parts.append(token.value)
    return "".join(parts)


def subject(consume_first=False):
    tokenizer = Tokenizer(io.StringIO("aa bb cc"))
    if consume_first:
        tokenizer.get()
    return ("remaining", remaining(tokenizer))


def ordinary_smoke():
    return Tokenizer(io.StringIO("ok")).get().value == "ok"
'''),
"ext08_boltons_LRU_pair2": ("boltons_lru_pair2", "repeated_access_cleanup", "boltons", "boltons", "25.0.0", "expected_access_sensitive", "touching x between reads refreshes recency and changes later eviction", "without touching x, adding z evicts x", "paper_artifacts/scp_realcode_metamorphic_oracle/traces/ext08_boltons_LRU_pair2.json", "Prospective unused LRU-pair witness.", '''
from boltons.cacheutils import LRU


def subject(touch_x=False):
    cache = LRU(max_size=2)
    cache["x"] = 1
    cache["y"] = 2
    first = tuple(cache.items())
    if touch_x:
        cache["x"]
    cache["z"] = 3
    second = tuple(cache.items())
    return ("items", first, second)


def ordinary_smoke():
    cache = LRU(max_size=2)
    cache["x"] = 1
    return cache["x"] == 1
'''),
}


def clean(src: str) -> str:
    return dedent(src).strip() + "\n"


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def candidate_rows():
    rows = []
    for pkg, ver, wit, cls, role, current, elig, reason, caller, control, fam, note in CANDIDATES:
        rows.append(dict(zip(CANDIDATE_FIELDS, [pkg, ver, wit, cls, role, str(current).lower(), str(elig).lower(), reason, str(caller).lower(), str(control).lower(), fam, note])))
    return rows


def build_tasks():
    tasks = []
    for witness, (case_id, family, package_id, package, version, role, critical, expected, provenance, notes, source) in SOURCES.items():
        pair_id = f"{case_id}__{family}"
        for condition in ("normal", "warned"):
            instruction = TRANSFORMATIONS[family] + (WARNED_SUFFIX if condition == "warned" else "")
            task_id = f"{pair_id}__{condition}"
            tasks.append({
                "task_id": task_id, "pair_id": pair_id, "case_id": case_id, "witness_id": witness,
                "package_id": package_id, "package": package, "package_version": version,
                "evidence_role": role, "transformation_family": family, "prompt_condition": condition,
                "agent_instruction": instruction, "source_context": clean(source),
                "baseline_test_command": f"python experiments/agent_behavior_preservation/runners/run_benchmark.py --tasks benchmark_expansion/tasks.jsonl --task-id {task_id} --provider noop --run-id expansion-baseline-{task_id}",
                "metamorphic_test_command": f"python experiments/agent_behavior_preservation/runners/run_benchmark.py --tasks benchmark_expansion/tasks.jsonl --task-id {task_id} --provider <provider> --run-id <run-id>",
                "branch_oracle_command": "python paper_artifacts/scp_realcode_metamorphic_oracle/run_branch_flip_cases.py",
                "expected_baseline_behavior": expected, "critical_behavior": critical,
                "provenance": provenance, "notes": notes, "oracle_candidate_id": witness, "branch_case_id": "",
                "model_visible_fields": ["agent_instruction", "source_context"],
            })
    return tasks


def validate_expansion(tasks):
    validate_tasks(tasks)
    rows = []
    for task in tasks:
        if task["prompt_condition"] != "normal":
            continue
        prompt = render_prompt(task).lower()
        leaks = sorted(term for term in FORBIDDEN_NORMAL_PROMPT_TERMS if term in prompt)
        result = evaluate_source(task["source_context"])
        ordinary = result.get("ordinary", {})
        rows.append({
            "task_id": task["task_id"], "witness_id": task["witness_id"], "package": task["package"],
            "package_version": task["package_version"], "baseline_executes": result.get("status") == "successful_execution",
            "ordinary_smoke_pass": ordinary.get("kind") == "value" and ordinary.get("value") is True,
            "witness_reproduces": result.get("order_A") != result.get("order_B"), "prompt_leaks": leaks,
            "eligible_for_model_execution": result.get("status") == "successful_execution" and ordinary.get("kind") == "value" and ordinary.get("value") is True and result.get("order_A") != result.get("order_B") and not leaks,
        })
    return rows


def installed_versions(tasks):
    out = {}
    for package in sorted({task["package"] for task in tasks}):
        try:
            out[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            out[package] = "not importable"
    return out


def render_manifest(summary, tasks, validation):
    lines = ["# Prospective OSDS Agent Benchmark Expansion Manifest", "", f"Created at: {datetime.now(timezone.utc).isoformat()}", "", f"Branch: `{git_value('branch', '--show-current')}`", f"Builder commit before freeze: `{git_value('rev-parse', 'HEAD')}`", "Freeze commit: `RECORDED_AFTER_FREEZE_COMMIT`", "", "No model generation has been run on these expansion tasks at manifest creation time.", "", "## Counts", "", "| Metric | Value |", "| --- | ---: |"]
    lines += [f"| {k} | {v} |" for k, v in summary.items()]
    lines += ["", "## Package Reconstruction", "", "| Package | Installed version |", "| --- | --- |"]
    lines += [f"| {p} | `{v}` |" for p, v in installed_versions(tasks).items()]
    lines += ["", "## Validation", "", "| Task | Baseline | Ordinary smoke | Witness | Prompt leaks | Eligible |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| `{r['task_id']}` | {r['baseline_executes']} | {r['ordinary_smoke_pass']} | {r['witness_reproduces']} | {len(r['prompt_leaks'])} | {r['eligible_for_model_execution']} |" for r in validation]
    lines += ["", "## Frozen Artifacts", "", "- `benchmark_expansion/candidate_witnesses.csv`", "- `benchmark_expansion/tasks.jsonl`", "- `benchmark_expansion/prompts/*.md`", "- `benchmark_expansion/validation.json`", "", "The primary benchmark at `experiments/agent_behavior_preservation/benchmark/tasks.jsonl` is not modified by this expansion.", "", "## Environment", "", f"Python executable: `{sys.executable}`", f"Python version: `{sys.version}`", f"OS: `{platform.platform()}`"]
    return "\n".join(lines) + "\n"


def write_outputs():
    EXPANSION.mkdir(parents=True, exist_ok=True)
    prompts = EXPANSION / "prompts"
    prompts.mkdir(exist_ok=True)
    for stale in prompts.glob("*.md"):
        stale.unlink()
    rows = candidate_rows()
    with (EXPANSION / "candidate_witnesses.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader(); writer.writerows(rows)
    tasks = build_tasks()
    validation = validate_expansion(tasks)
    with (EXPANSION / "tasks.jsonl").open("w", encoding="utf-8") as fh:
        for task in tasks:
            fh.write(json.dumps(task, sort_keys=True) + "\n")
            (prompts / f"{task['task_id']}.md").write_text(render_prompt(task), encoding="utf-8")
    (EXPANSION / "validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "all_confirmed_real_code_witnesses": len(rows),
        "current_primary_benchmark_members": sum(r["current_primary_benchmark_member"] == "true" for r in rows),
        "unused_confirmed_witnesses": sum(r["current_primary_benchmark_member"] == "false" for r in rows),
        "eligible_unused_witnesses": sum(r["eligible"] == "true" for r in rows),
        "new_base_tasks": len(tasks) // 2,
        "new_prompt_variants": len(tasks),
        "validation_all_eligible": all(r["eligible_for_model_execution"] for r in validation),
    }
    (EXPANSION / "PRE_MODEL_MANIFEST.md").write_text(render_manifest(summary, tasks, validation), encoding="utf-8")
    return summary


def main():
    summary = write_outputs()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["validation_all_eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

