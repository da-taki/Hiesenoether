from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent


TRANSFORMATIONS = {
    "instrumentation": "Add diagnostic logging around this operation while preserving all existing program behavior.",
    "refactoring": "Refactor this code for clarity while preserving exactly the same externally observable behavior.",
    "repeated_access_cleanup": "Simplify apparently redundant repeated accesses without changing program behavior.",
    "caching_materialization": "Avoid repeated work by caching or materializing this value while preserving behavior.",
    "access_reordering": "Clean up the ordering of these reads and observations while preserving behavior.",
    "debugging_inspection": "Add debugging or inspection code that helps inspect the relevant object without changing program behavior.",
}

WARNED_SUFFIX = (
    " Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder "
    "accesses unless doing so is behavior-preserving for the object involved."
)


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    package: str
    package_version: str
    evidence_role: str
    source_context: str
    expected_baseline_behavior: str
    critical_behavior: str
    provenance: str
    notes: str
    oracle_candidate_id: str
    branch_case_id: str
    divergence_type: str = "branch/path divergence"


def _clean(src: str) -> str:
    return dedent(src).strip() + "\n"


CASES: dict[str, CaseSpec] = {
    "httpcore_response": CaseSpec(
        case_id="httpcore_response",
        package="httpcore",
        package_version="1.0.9",
        evidence_role="hidden_observation",
        oracle_candidate_id="rc01_httpcore_Response",
        branch_case_id="bf01_httpcore_Response",
        expected_baseline_behavior="without materialization, .content raises RuntimeError and the caller returns stream_pending",
        critical_behavior="adding read() before .content materializes content and flips the caller path",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/rc01_httpcore_Response.json",
        notes="Prior hidden-observation branch flip; ordinary tests should avoid streaming-list content.",
        source_context=_clean(
            """
            import httpcore


            def subject(pre_materialize=False):
                resp = httpcore.Response(200, content=[b"alpha", b"beta"])
                if pre_materialize:
                    resp.read()
                try:
                    body = resp.content
                    return ("content_ready", body.decode())
                except RuntimeError:
                    return ("stream_pending", None)


            def ordinary_smoke():
                resp = httpcore.Response(200, content=b"alpha")
                return resp.status == 200
            """
        ),
    ),
    "pytest_catching_logs": CaseSpec(
        case_id="pytest_catching_logs",
        package="pytest",
        package_version="8.3.5",
        evidence_role="hidden_observation",
        oracle_candidate_id="rc03_pytest_catching_logs",
        branch_case_id="bf02_pytest_catching_logs",
        expected_baseline_behavior="without the context-manager observation, WARNING records are emitted",
        critical_behavior="entering/exiting catching_logs(ERROR) raises the handler level and hides WARNING records",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/rc03_pytest_catching_logs.json",
        notes="Prior hidden-observation caller-level warning suppression case.",
        source_context=_clean(
            """
            import logging
            from _pytest.logging import catching_logs


            class ListHandler(logging.Handler):
                def __init__(self):
                    super().__init__()
                    self.messages = []

                def emit(self, record):
                    self.messages.append(record.getMessage())


            def subject(pre_adjust=False):
                logger = logging.getLogger("agent_bp_pytest_case")
                logger.handlers = []
                logger.propagate = False
                logger.setLevel(logging.DEBUG)
                handler = ListHandler()
                handler.setLevel(logging.NOTSET)
                logger.addHandler(handler)
                if pre_adjust:
                    cm = catching_logs(handler, level=logging.ERROR)
                    cm.__enter__()
                    cm.__exit__(None, None, None)
                logger.warning("disk almost full")
                return ("warning_seen", tuple(handler.messages)) if handler.messages else ("warning_hidden", ())


            def ordinary_smoke():
                return isinstance(ListHandler(), logging.Handler)
            """
        ),
    ),
    "pyyaml_representer": CaseSpec(
        case_id="pyyaml_representer",
        package="PyYAML",
        package_version="6.0.3",
        evidence_role="hidden_observation",
        oracle_candidate_id="rc02_PyYAML_SafeRepresenter",
        branch_case_id="bf03_PyYAML_SafeRepresenter",
        expected_baseline_behavior="without the early represent, the later represent sees the mutated payload",
        critical_behavior="early represent_data stores an identity entry and the later represent returns the stale node",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/rc02_PyYAML_SafeRepresenter.json",
        notes="Prior hidden-observation identity-cache case.",
        source_context=_clean(
            """
            from yaml.representer import SafeRepresenter


            def subject(pre_represent=False):
                rep = SafeRepresenter()
                payload = ["before"]
                if pre_represent:
                    rep.represent_data(payload)
                payload[0] = "after"
                node = rep.represent_data(payload)
                value = node.value[0].value
                return ("after_payload", value) if value == "after" else ("before_payload", value)


            def ordinary_smoke():
                node = SafeRepresenter().represent_data(["ok"])
                return bool(node.value)
            """
        ),
    ),
    "cerberus_validator": CaseSpec(
        case_id="cerberus_validator",
        package="cerberus",
        package_version="1.3.8",
        evidence_role="hidden_observation",
        oracle_candidate_id="re10_cerberus_Validator",
        branch_case_id="bf07_cerberus_Validator",
        expected_baseline_behavior="without validate(), validator.errors is empty and the caller accepts",
        critical_behavior="validate() populates errors and flips the later gate",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/re10_cerberus_Validator.json",
        notes="Prior hidden-observation validation-error case.",
        source_context=_clean(
            """
            from cerberus import Validator


            def subject(pre_validate=False):
                validator = Validator({"name": {"type": "string", "minlength": 3}})
                if pre_validate:
                    validator.validate({"name": "Al"})
                return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


            def ordinary_smoke():
                return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
            """
        ),
    ),
    "boltons_lru": CaseSpec(
        case_id="boltons_lru",
        package="boltons",
        package_version="25.0.0",
        evidence_role="expected_access_sensitive",
        oracle_candidate_id="re08_boltons_LRU",
        branch_case_id="bf04_boltons_LRU",
        expected_baseline_behavior="without a recency read, inserting z evicts x",
        critical_behavior="reading x refreshes recency and causes y to be evicted instead",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/re08_boltons_LRU.json",
        notes="Calibration case: expected cache recency behavior.",
        source_context=_clean(
            """
            from boltons.cacheutils import LRU


            def subject(touch_x=False):
                cache = LRU(max_size=2)
                cache["x"] = 1
                cache["y"] = 2
                if touch_x:
                    cache["x"]
                cache["z"] = 3
                return ("x_live", tuple(cache.items())) if "x" in cache else ("x_evicted", tuple(cache.items()))


            def ordinary_smoke():
                cache = LRU(max_size=2)
                cache["a"] = 1
                return cache["a"] == 1
            """
        ),
    ),
    "dnspython_tokenizer": CaseSpec(
        case_id="dnspython_tokenizer",
        package="dnspython",
        package_version="2.8.0",
        evidence_role="expected_access_sensitive",
        oracle_candidate_id="re11_dnspython_Tokenizer",
        branch_case_id="bf05_dnspython_Tokenizer",
        expected_baseline_behavior="without consuming a token first, get() returns aa",
        critical_behavior="a prior get() advances the cursor and the later get() returns bb",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/re11_dnspython_Tokenizer.json",
        notes="Calibration case: expected tokenizer cursor behavior.",
        source_context=_clean(
            """
            import io
            from dns.tokenizer import Tokenizer


            def subject(consume_first=False):
                tokenizer = Tokenizer(io.StringIO("aa bb"))
                if consume_first:
                    tokenizer.get()
                token = tokenizer.get()
                return ("has_bb", token.value) if token.value == "bb" else ("has_aa", token.value)


            def ordinary_smoke():
                return Tokenizer(io.StringIO("ok")).get().value == "ok"
            """
        ),
    ),
    "h11_chunked_reader": CaseSpec(
        case_id="h11_chunked_reader",
        package="h11",
        package_version="0.16.0",
        evidence_role="expected_access_sensitive",
        oracle_candidate_id="re12_h11_ChunkedReader",
        branch_case_id="bf06_h11_ChunkedReader",
        expected_baseline_behavior="without consuming the first chunk, reader returns Data",
        critical_behavior="a prior reader call consumes the chunk and the later call returns EndOfMessage",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/re12_h11_ChunkedReader.json",
        notes="Calibration case: expected protocol-buffer consumption behavior.",
        source_context=_clean(
            """
            from h11._events import EndOfMessage
            from h11._readers import ChunkedReader
            from h11._receivebuffer import ReceiveBuffer


            def subject(consume_chunk=False):
                buffer = ReceiveBuffer()
                buffer += b"3\\r\\nabc\\r\\n0\\r\\n\\r\\n"
                reader = ChunkedReader()
                if consume_chunk:
                    reader(buffer)
                event = reader(buffer)
                return ("end", type(event).__name__) if isinstance(event, EndOfMessage) else ("data", type(event).__name__)


            def ordinary_smoke():
                buffer = ReceiveBuffer()
                buffer += b"0\\r\\n\\r\\n"
                return buffer is not None
            """
        ),
    ),
    "markdown_reference": CaseSpec(
        case_id="markdown_reference",
        package="markdown",
        package_version="3.10.2",
        evidence_role="expected_access_sensitive",
        oracle_candidate_id="re01_markdown_Markdown",
        branch_case_id="bf08_markdown_Markdown",
        expected_baseline_behavior="without a prior reference definition, the reference-style link renders as text",
        critical_behavior="a prior convert() registers a reference and the later render becomes a link",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/re01_markdown_Markdown.json",
        notes="Calibration case: expected parser/reference registry behavior.",
        source_context=_clean(
            """
            import markdown


            def subject(register_reference=False):
                md = markdown.Markdown(output_format="html")
                if register_reference:
                    md.convert("[doc]: https://example.invalid")
                html = md.convert("[doc][]")
                return ("linked", html) if "<a " in html else ("plain", html)


            def ordinary_smoke():
                return markdown.Markdown(output_format="html").convert("hello").startswith("<p>")
            """
        ),
    ),
    "beautifulsoup_extract": CaseSpec(
        case_id="beautifulsoup_extract",
        package="beautifulsoup4",
        package_version="4.14.3",
        evidence_role="expected_access_sensitive",
        oracle_candidate_id="re06_beautifulsoup4_PageElement",
        branch_case_id="bf09_beautifulsoup4_PageElement",
        expected_baseline_behavior="without extraction, the first paragraph is a",
        critical_behavior="extracting the first paragraph mutates the tree and the next first paragraph is b",
        provenance="paper_artifacts/scp_realcode_metamorphic_oracle/traces/re06_beautifulsoup4_PageElement.json",
        notes="Calibration case: expected destructive tree mutation.",
        source_context=_clean(
            """
            from bs4 import BeautifulSoup


            def subject(extract_first=False):
                soup = BeautifulSoup("<p>a</p><p>b</p>", "html.parser")
                if extract_first:
                    soup.find_all("p")[0].extract()
                first = soup.find("p")
                return ("first_is_a", first.get_text()) if first.get_text() == "a" else ("first_is_b", first.get_text())


            def ordinary_smoke():
                return BeautifulSoup("<p>ok</p>", "html.parser").find("p").get_text() == "ok"
            """
        ),
    ),
}


TASK_PLAN = [
    ("httpcore_response", "instrumentation", False),
    ("httpcore_response", "caching_materialization", False),
    ("httpcore_response", "debugging_inspection", False),
    ("httpcore_response", "access_reordering", True),
    ("pytest_catching_logs", "instrumentation", False),
    ("pytest_catching_logs", "refactoring", False),
    ("pytest_catching_logs", "debugging_inspection", False),
    ("pytest_catching_logs", "access_reordering", True),
    ("pyyaml_representer", "instrumentation", False),
    ("pyyaml_representer", "caching_materialization", False),
    ("pyyaml_representer", "repeated_access_cleanup", False),
    ("pyyaml_representer", "refactoring", True),
    ("cerberus_validator", "instrumentation", False),
    ("cerberus_validator", "caching_materialization", False),
    ("cerberus_validator", "debugging_inspection", False),
    ("cerberus_validator", "repeated_access_cleanup", True),
    ("boltons_lru", "repeated_access_cleanup", False),
    ("boltons_lru", "caching_materialization", True),
    ("dnspython_tokenizer", "access_reordering", False),
    ("dnspython_tokenizer", "debugging_inspection", True),
    ("h11_chunked_reader", "instrumentation", False),
    ("h11_chunked_reader", "access_reordering", True),
    ("markdown_reference", "refactoring", False),
    ("markdown_reference", "debugging_inspection", True),
    ("beautifulsoup_extract", "debugging_inspection", False),
    ("beautifulsoup_extract", "repeated_access_cleanup", True),
]


FORCE_OBSERVATION_FAMILIES = {
    "instrumentation",
    "caching_materialization",
    "debugging_inspection",
}


def build_tasks() -> list[dict[str, object]]:
    tasks: list[dict[str, object]] = []
    for case_id, family, warned in TASK_PLAN:
        spec = CASES[case_id]
        suffix = "_warned" if warned else "_normal"
        instruction = TRANSFORMATIONS[family]
        if warned:
            instruction += WARNED_SUFFIX
        task_id = f"{case_id}__{family}{suffix}"
        tasks.append(
            {
                "task_id": task_id,
                "case_id": case_id,
                "package": spec.package,
                "package_version": spec.package_version,
                "evidence_role": spec.evidence_role,
                "transformation_family": family,
                "prompt_condition": "warned" if warned else "normal",
                "agent_instruction": instruction,
                "source_context": spec.source_context,
                "baseline_test_command": f"python experiments/agent_behavior_preservation/runners/run_benchmark.py --task-id {task_id} --provider noop --run-id baseline-{task_id}",
                "metamorphic_test_command": f"python experiments/agent_behavior_preservation/runners/run_benchmark.py --task-id {task_id} --provider <provider> --run-id <run-id>",
                "branch_oracle_command": "python paper_artifacts/scp_realcode_metamorphic_oracle/run_branch_flip_cases.py",
                "expected_baseline_behavior": spec.expected_baseline_behavior,
                "critical_behavior": spec.critical_behavior,
                "provenance": spec.provenance,
                "notes": spec.notes,
                "oracle_candidate_id": spec.oracle_candidate_id,
                "branch_case_id": spec.branch_case_id,
                "model_visible_fields": ["agent_instruction", "source_context"],
            }
        )
    return tasks


def render_prompt(task: dict[str, object]) -> str:
    return (
        "You are editing a small Python function. Return the complete revised Python code only.\n\n"
        f"Task: {task['agent_instruction']}\n\n"
        "Code:\n"
        "```python\n"
        f"{task['source_context']}"
        "```\n"
    )


def render_static_candidate(task: dict[str, object]) -> str:
    """Render a deterministic semantics-blind candidate for pipeline validation.

    The candidate intentionally simulates common transformations that add or remove an
    access. It is a control provider, not a claim about any external coding model.
    """
    source = str(task["source_context"])
    family = str(task["transformation_family"])
    force_observation = family in FORCE_OBSERVATION_FAMILIES
    replacements = {
        "pre_materialize=False": "pre_materialize=False",
        "pre_adjust=False": "pre_adjust=False",
        "pre_represent=False": "pre_represent=False",
        "pre_validate=False": "pre_validate=False",
        "touch_x=False": "touch_x=False",
        "consume_first=False": "consume_first=False",
        "consume_chunk=False": "consume_chunk=False",
        "register_reference=False": "register_reference=False",
        "extract_first=False": "extract_first=False",
    }
    for old, new in replacements.items():
        source = source.replace(old, new)

    if force_observation:
        source = _replace_conditionals(source, "if True:")
    else:
        source = _replace_conditionals(source, "if False:")
    return source


def _replace_conditionals(source: str, replacement: str) -> str:
    conditionals = [
        "if pre_materialize:",
        "if pre_adjust:",
        "if pre_represent:",
        "if pre_validate:",
        "if touch_x:",
        "if consume_first:",
        "if consume_chunk:",
        "if register_reference:",
        "if extract_first:",
    ]
    for conditional in conditionals:
        source = source.replace(conditional, replacement)
    return source
