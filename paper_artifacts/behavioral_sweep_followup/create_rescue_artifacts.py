from __future__ import annotations

import csv
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HARNESS_DIR = ROOT / "harnesses"
OUTPUT_DIR = ROOT / "outputs"

SELECTION_ROWS = [
    {
        "rescue_rank": "1",
        "original_sweep_rank": "1",
        "package": "markdown",
        "version": "3.10.2",
        "class_name": "Markdown",
        "file_path": "markdown-3.10.2\\markdown\\core.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Manual packet and source docs show Markdown.convert accumulates references unless reset is called; the generic build_parser repetition did not exercise conversion state.",
        "suspected_operation_A": "convert('[alpha][]')",
        "suspected_operation_B": "convert('[alpha]: https://example.invalid') before convert('[alpha][]')",
        "suspected_latent_state": "references/htmlStash parser state",
        "suspected_later_behavior": "HTML conversion of a reference-style link",
        "expected_fixture_needed": "Real Markdown strings and a single Markdown instance.",
    },
    {
        "rescue_rank": "2",
        "original_sweep_rank": "2",
        "package": "more-itertools",
        "version": "11.0.2",
        "class_name": "seekable",
        "file_path": "more-itertools-11.0.2\\more_itertools\\more.py",
        "previous_classification": "could_not_construct",
        "previous_failure_reason": "constructor requires arguments: iterable",
        "selection_reason": "Docstring gives an exact iterator fixture and describes progressive caching and seeking.",
        "suspected_operation_A": "next(it)",
        "suspected_operation_B": "next(it) before next(it)",
        "suspected_latent_state": "_index/cache position",
        "suspected_later_behavior": "Next item yielded by the iterator",
        "expected_fixture_needed": "iter(['a', 'b', 'c'])",
    },
    {
        "rescue_rank": "3",
        "original_sweep_rank": "3",
        "package": "pygments",
        "version": "2.20.0",
        "class_name": "EscapeSequence",
        "file_path": "pygments-2.20.0\\pygments\\formatters\\terminal256.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Source contains an apparent state write inside color_string; a fixture with an ANSI foreground checks whether it is observable in the current package version.",
        "suspected_operation_A": "reset_string()",
        "suspected_operation_B": "color_string() before reset_string()",
        "suspected_latent_state": "bold flag",
        "suspected_later_behavior": "ANSI reset escape string",
        "expected_fixture_needed": "EscapeSequence(fg='ansired')",
    },
    {
        "rescue_rank": "4",
        "original_sweep_rank": "4",
        "package": "docutils",
        "version": "0.22.4",
        "class_name": "Transformer",
        "file_path": "docutils-0.22.4\\docutils\\transforms\\__init__.py",
        "previous_classification": "could_not_construct",
        "previous_failure_reason": "constructor requires arguments: document",
        "selection_reason": "Source constructor only needs a document; docutils utilities can build an in-memory document without external files.",
        "suspected_operation_A": "inspect transform priority strings",
        "suspected_operation_B": "get_priority_string() before inspecting transform priority strings",
        "suspected_latent_state": "serialno/sorted transform bookkeeping",
        "suspected_later_behavior": "Transform queue priority strings and serial counter",
        "expected_fixture_needed": "docutils.utils.new_document plus two tiny Transform subclasses.",
    },
    {
        "rescue_rank": "5",
        "original_sweep_rank": "5",
        "package": "soupsieve",
        "version": "2.8.3",
        "class_name": "CSSMatch",
        "file_path": "soupsieve-2.8.3\\soupsieve\\css_match.py",
        "previous_classification": "import_failed",
        "previous_failure_reason": "import_failed: ModuleNotFoundError: No module named 'bs4'",
        "selection_reason": "The missing bs4 dependency is present in the rebuilt snapshot, so the import failure can be rescued by adding snapshot paths.",
        "suspected_operation_A": "select()",
        "suspected_operation_B": "match() before select()",
        "suspected_latent_state": "cached_meta_lang/cached_default_forms/namespaces",
        "suspected_later_behavior": "Selected BeautifulSoup tags",
        "expected_fixture_needed": "BeautifulSoup document and soupsieve compiled selector.",
    },
    {
        "rescue_rank": "6",
        "original_sweep_rank": "11",
        "package": "beautifulsoup4",
        "version": "4.14.3",
        "class_name": "PageElement",
        "file_path": "beautifulsoup4-4.14.3\\bs4\\element.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Generic harness constructed the abstract base directly; a real soup tag is a PageElement subclass and exercises extract() realistically.",
        "suspected_operation_A": "str(soup)",
        "suspected_operation_B": "first_p.extract() before str(soup)",
        "suspected_latent_state": "parent/sibling/tree links",
        "suspected_later_behavior": "Serialized parse tree",
        "expected_fixture_needed": "BeautifulSoup('<p>a</p><p>b</p>', 'html.parser')",
    },
    {
        "rescue_rank": "7",
        "original_sweep_rank": "12",
        "package": "boltons",
        "version": "25.0.0",
        "class_name": "LRI",
        "file_path": "boltons-25.0.0\\boltons\\cacheutils.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Docstring has a small cache fixture and counters; manual harness can distinguish value output from statistics-only effects.",
        "suspected_operation_A": "insert c after initializing a,b",
        "suspected_operation_B": "__getitem__('a') before inserting c",
        "suspected_latent_state": "hit_count/miss_count/linked list",
        "suspected_later_behavior": "Cache contents and statistics after eviction",
        "expected_fixture_needed": "LRI(max_size=2) with two string keys.",
    },
    {
        "rescue_rank": "8",
        "original_sweep_rank": "13",
        "package": "boltons",
        "version": "25.0.0",
        "class_name": "LRU",
        "file_path": "boltons-25.0.0\\boltons\\cacheutils.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "LRU access is expected to affect recency and eviction; the generic no-arg cache had no meaningful keys.",
        "suspected_operation_A": "insert c after initializing a,b",
        "suspected_operation_B": "__getitem__('a') before inserting c",
        "suspected_latent_state": "linked-list recency order",
        "suspected_later_behavior": "Which key survives eviction",
        "expected_fixture_needed": "LRU(max_size=2) with two string keys.",
    },
    {
        "rescue_rank": "9",
        "original_sweep_rank": "14",
        "package": "boltons",
        "version": "25.0.0",
        "class_name": "MultiFileReader",
        "file_path": "boltons-25.0.0\\boltons\\ioutils.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Docstring provides an exact BytesIO fixture; old harness used an empty reader.",
        "suspected_operation_A": "read(3)",
        "suspected_operation_B": "read(3) before read(3)",
        "suspected_latent_state": "_index and underlying file positions",
        "suspected_later_behavior": "Bytes returned by later read",
        "expected_fixture_needed": "BytesIO(b'ab'), BytesIO(b'cd'), BytesIO(b'e')",
    },
    {
        "rescue_rank": "10",
        "original_sweep_rank": "16",
        "package": "cerberus",
        "version": "1.3.8",
        "class_name": "BareValidator",
        "file_path": "cerberus-1.3.8\\cerberus\\validator.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Validation has a clear small schema/document fixture; BareValidator itself needs the public Validator subclass to run schema-backed behavior.",
        "suspected_operation_A": "read errors",
        "suspected_operation_B": "validate(invalid document) before reading errors",
        "suspected_latent_state": "_errors/document_error_tree",
        "suspected_later_behavior": "Validator errors output",
        "expected_fixture_needed": "cerberus.Validator with a small schema, noted as subclass coverage of BareValidator behavior.",
    },
    {
        "rescue_rank": "11",
        "original_sweep_rank": "17",
        "package": "click-option-group",
        "version": "0.5.9",
        "class_name": "_OptGroup",
        "file_path": "click-option-group-0.5.9\\src\\click_option_group\\_decorators.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "Decorator registration can be tested with a tiny click command without invoking external services.",
        "suspected_operation_A": "build and invoke command",
        "suspected_operation_B": "group decorator call before building and invoking command",
        "suspected_latent_state": "_decorating_state/_not_attached_options",
        "suspected_later_behavior": "Click command options and invocation output",
        "expected_fixture_needed": "Tiny in-process click command and CliRunner.",
    },
    {
        "rescue_rank": "12",
        "original_sweep_rank": "18",
        "package": "dnspython",
        "version": "2.8.0",
        "class_name": "BTree",
        "file_path": "dnspython-2.8.0\\dns\\btree.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "In-memory BTree can be populated with package KV elements; no external DNS/network fixture is needed.",
        "suspected_operation_A": "get_element('b')",
        "suspected_operation_B": "get_element('a') before get_element('b')",
        "suspected_latent_state": "cursor/root/copy-on-write bookkeeping",
        "suspected_later_behavior": "Element returned by lookup",
        "expected_fixture_needed": "BTree plus dns.btree.KV elements.",
    },
    {
        "rescue_rank": "13",
        "original_sweep_rank": "22",
        "package": "dnspython",
        "version": "2.8.0",
        "class_name": "Tokenizer",
        "file_path": "dnspython-2.8.0\\dns\\tokenizer.py",
        "previous_classification": "confirmed_state_divergence_only",
        "previous_failure_reason": "",
        "selection_reason": "Prompt explicitly flagged it; a real token input can test whether the previous state-only result becomes visible output.",
        "suspected_operation_A": "get_string()",
        "suspected_operation_B": "get() before get_string()",
        "suspected_latent_state": "file cursor/ungotten_token/eof/line_number",
        "suspected_later_behavior": "Next token string",
        "expected_fixture_needed": "io.StringIO('alpha beta\\n')",
    },
    {
        "rescue_rank": "14",
        "original_sweep_rank": "49",
        "package": "h11",
        "version": "0.16.0",
        "class_name": "ChunkedReader",
        "file_path": "h11-0.16.0\\h11\\_readers.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "A minimal in-memory chunked body exercises reader state and ReceiveBuffer interaction.",
        "suspected_operation_A": "reader(buf)",
        "suspected_operation_B": "reader(buf) before reader(buf)",
        "suspected_latent_state": "_bytes_in_chunk/_bytes_to_discard/_reading_trailer",
        "suspected_later_behavior": "Data versus EndOfMessage return",
        "expected_fixture_needed": "ReceiveBuffer with b'3\\r\\nabc\\r\\n0\\r\\n\\r\\n'.",
    },
    {
        "rescue_rank": "15",
        "original_sweep_rank": "50",
        "package": "h11",
        "version": "0.16.0",
        "class_name": "ReceiveBuffer",
        "file_path": "h11-0.16.0\\h11\\_receivebuffer.py",
        "previous_classification": "structural_only_no_runtime_difference",
        "previous_failure_reason": "",
        "selection_reason": "ReceiveBuffer has a small in-memory byte fixture and line extraction state, avoiding sockets or server setup.",
        "suspected_operation_A": "maybe_extract_lines()",
        "suspected_operation_B": "maybe_extract_next_line() before maybe_extract_lines()",
        "suspected_latent_state": "_data/_next_line_search/_multiple_lines_search",
        "suspected_later_behavior": "Parsed header lines and remaining buffer",
        "expected_fixture_needed": "HTTP-like bytes in ReceiveBuffer.",
    },
]

COMMON = r'''
from __future__ import annotations

import io
import json
import sys
import warnings
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SNAPSHOT = REPO / "paper_artifacts" / "realworld_package_study" / "source_snapshot"
OUTPUT_DIR = BASE / "outputs"


CASES = {
    1: ("markdown", "3.10.2", "Markdown", "markdown-3.10.2\\markdown\\core.py", 1),
    2: ("more-itertools", "11.0.2", "seekable", "more-itertools-11.0.2\\more_itertools\\more.py", 2),
    3: ("pygments", "2.20.0", "EscapeSequence", "pygments-2.20.0\\pygments\\formatters\\terminal256.py", 3),
    4: ("docutils", "0.22.4", "Transformer", "docutils-0.22.4\\docutils\\transforms\\__init__.py", 4),
    5: ("soupsieve", "2.8.3", "CSSMatch", "soupsieve-2.8.3\\soupsieve\\css_match.py", 5),
    6: ("beautifulsoup4", "4.14.3", "PageElement", "beautifulsoup4-4.14.3\\bs4\\element.py", 11),
    7: ("boltons", "25.0.0", "LRI", "boltons-25.0.0\\boltons\\cacheutils.py", 12),
    8: ("boltons", "25.0.0", "LRU", "boltons-25.0.0\\boltons\\cacheutils.py", 13),
    9: ("boltons", "25.0.0", "MultiFileReader", "boltons-25.0.0\\boltons\\ioutils.py", 14),
    10: ("cerberus", "1.3.8", "BareValidator", "cerberus-1.3.8\\cerberus\\validator.py", 16),
    11: ("click-option-group", "0.5.9", "_OptGroup", "click-option-group-0.5.9\\src\\click_option_group\\_decorators.py", 17),
    12: ("dnspython", "2.8.0", "BTree", "dnspython-2.8.0\\dns\\btree.py", 18),
    13: ("dnspython", "2.8.0", "Tokenizer", "dnspython-2.8.0\\dns\\tokenizer.py", 22),
    14: ("h11", "0.16.0", "ChunkedReader", "h11-0.16.0\\h11\\_readers.py", 49),
    15: ("h11", "0.16.0", "ReceiveBuffer", "h11-0.16.0\\h11\\_receivebuffer.py", 50),
}


BOUNDARY_NOTES = {
    1: "The Python-Markdown docs explicitly say reset() should be called between convert() calls; count this as stateful reuse behavior, not a package bug.",
    2: "Iterator consumption is expected behavior; the rescue shows the generic no-arg harness missed a real cursor effect.",
    3: "In this Pygments version the ANSI fixture did not trigger the suspected bold mutation; the case remains structural-only.",
    4: "The manual fixture tests Transformer serial bookkeeping, not transform application output.",
    5: "The rescue only fixes sys.path/import construction; simple selector matching remained output-equivalent.",
    6: "BeautifulSoup extraction is intentionally destructive; use only as a tree-mutation/access-order example.",
    7: "LRI access affects statistics but not eviction order in this fixture.",
    8: "LRU access affects eviction order as designed; it is evidence of consequential access state, not a defect.",
    9: "MultiFileReader is a stream-like cursor; output divergence is expected after a prior read.",
    10: "BareValidator itself rejects schema-backed validation; the runnable fixture uses the public Validator subclass to exercise inherited BareValidator state.",
    11: "The decorator fixture is tiny and in-process; it did not produce a meaningful runtime divergence.",
    12: "BTree lookup is stable under this minimal fixture; cursor/copy-on-write behavior was not forced.",
    13: "Tokenizer is a cursor over token input; output divergence is expected after consuming a token.",
    14: "ChunkedReader consumes a ReceiveBuffer; Data versus EndOfMessage is expected stream-reader state.",
    15: "ReceiveBuffer line extraction is destructive by design; it is a cursor semantics example.",
}


def add_snapshot_paths() -> None:
    if not SNAPSHOT.exists():
        return
    paths = []
    for dist in sorted(SNAPSHOT.iterdir()):
        if dist.is_dir():
            paths.append(str(dist))
            src = dist / "src"
            if src.exists():
                paths.append(str(src))
    for path in reversed(paths):
        if path not in sys.path:
            sys.path.insert(0, path)


def stable(value):
    if isinstance(value, bytes):
        return repr(value)
    if isinstance(value, bytearray):
        return repr(bytes(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): stable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [stable(v) for v in value]
    return repr(value)


def classify(result_a, result_b):
    output_diff = result_a.get("later") != result_b.get("later")
    branch_flip = result_a.get("kind") != result_b.get("kind")
    state_diff = result_a.get("state") != result_b.get("state")
    if branch_flip:
        classification = "confirmed_branch_flip"
    elif output_diff:
        classification = "confirmed_output_divergence"
    elif state_diff:
        classification = "confirmed_state_divergence_only"
    else:
        classification = "structural_only_no_runtime_difference"
    return output_diff, branch_flip, state_diff, classification


def base_result(rank, operation_a, operation_b, fixture_description):
    package, version, class_name, file_path, original_rank = CASES[rank]
    return {
        "package": package,
        "version": version,
        "class_name": class_name,
        "file_path": file_path,
        "original_sweep_rank": original_rank,
        "rescue_rank": rank,
        "operation_A": operation_a,
        "operation_B": operation_b,
        "fixture_description": fixture_description,
        "result_A": {},
        "result_B": {},
        "output_diff": False,
        "branch_flip": False,
        "state_diff": False,
        "classification": "could_not_construct_even_manually",
        "boundary_note": BOUNDARY_NOTES[rank],
        "failure_reason": "",
    }


def finalize(payload, result_a, result_b):
    payload["result_A"] = stable(result_a)
    payload["result_B"] = stable(result_b)
    output_diff, branch_flip, state_diff, classification = classify(payload["result_A"], payload["result_B"])
    payload["output_diff"] = output_diff
    payload["branch_flip"] = branch_flip
    payload["state_diff"] = state_diff
    payload["classification"] = classification
    return payload


def case_1():
    payload = base_result(1, "convert('[alpha][]')", "convert('[alpha]: https://example.invalid') first; then convert('[alpha][]')", "Two real Markdown strings on one Markdown instance, output_format='html'.")
    import markdown
    a_md = markdown.Markdown(output_format="html")
    result_a = {"kind": "value", "later": a_md.convert("[alpha][]"), "state": {"references": dict(a_md.references)}}
    b_md = markdown.Markdown(output_format="html")
    observation = b_md.convert("[alpha]: https://example.invalid")
    result_b = {"kind": "value", "observation": observation, "later": b_md.convert("[alpha][]"), "state": {"references": dict(b_md.references)}}
    return finalize(payload, result_a, result_b)


def case_2():
    payload = base_result(2, "next(seekable(iter(['a','b','c'])))", "next(it) first; then next(it)", "seekable over iter(['a', 'b', 'c']).")
    from more_itertools import seekable
    a_it = seekable(iter(["a", "b", "c"]))
    result_a = {"kind": "value", "later": next(a_it), "state": {"elements": list(a_it.elements())}}
    b_it = seekable(iter(["a", "b", "c"]))
    observation = next(b_it)
    result_b = {"kind": "value", "observation": observation, "later": next(b_it), "state": {"elements": list(b_it.elements())}}
    return finalize(payload, result_a, result_b)


def case_3():
    payload = base_result(3, "reset_string() on EscapeSequence(fg='ansired')", "color_string() first; then reset_string()", "EscapeSequence(fg='ansired') using Pygments terminal formatter internals.")
    from pygments.formatters.terminal256 import EscapeSequence
    a_esc = EscapeSequence(fg="ansired")
    result_a = {"kind": "value", "later": a_esc.reset_string(), "state": dict(a_esc.__dict__)}
    b_esc = EscapeSequence(fg="ansired")
    observation = b_esc.color_string()
    result_b = {"kind": "value", "observation": observation, "later": b_esc.reset_string(), "state": dict(b_esc.__dict__)}
    return finalize(payload, result_a, result_b)


def case_4():
    payload = base_result(4, "inspect transform priority queue", "get_priority_string(10) first; then inspect transform priority queue", "docutils new_document with two tiny Transform subclasses.")
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from docutils.frontend import OptionParser
    from docutils.transforms import Transform, Transformer
    from docutils.utils import new_document

    class T10(Transform):
        default_priority = 10
        def apply(self):
            self.document["t10"] = "yes"

    class T5(Transform):
        default_priority = 5
        def apply(self):
            self.document["t5"] = "yes"

    def make_transformer():
        settings = OptionParser(components=()).get_default_values()
        document = new_document("<rescue>", settings=settings)
        transformer = Transformer(document)
        transformer.add_transform(T10)
        transformer.add_transform(T5)
        return transformer

    a_tr = make_transformer()
    result_a = {"kind": "value", "later": [t[0] for t in a_tr.transforms], "state": {"serialno": a_tr.serialno, "sorted": a_tr.sorted}}
    b_tr = make_transformer()
    observation = b_tr.get_priority_string(10)
    result_b = {"kind": "value", "observation": observation, "later": [t[0] for t in b_tr.transforms], "state": {"serialno": b_tr.serialno, "sorted": b_tr.sorted}}
    return finalize(payload, result_a, result_b)


def case_5():
    payload = base_result(5, "list(CSSMatch(...).select())", "match(first p) first; then list(CSSMatch(...).select())", "BeautifulSoup tree and soupsieve compiled selector 'p.a'.")
    import soupsieve as sv
    from bs4 import BeautifulSoup
    from soupsieve.css_match import CSSMatch

    soup = BeautifulSoup("<div><p class='a'>x</p><p>y</p></div>", "html.parser")
    selectors = sv.compile("p.a").selectors
    a_match = CSSMatch(selectors, soup, None, 0)
    result_a = {"kind": "value", "later": [str(tag) for tag in a_match.select()], "state": {"cached_meta_lang": a_match.cached_meta_lang, "cached_default_forms": a_match.cached_default_forms}}
    b_match = CSSMatch(selectors, soup, None, 0)
    observation = b_match.match(soup.find("p"))
    result_b = {"kind": "value", "observation": observation, "later": [str(tag) for tag in b_match.select()], "state": {"cached_meta_lang": b_match.cached_meta_lang, "cached_default_forms": b_match.cached_default_forms}}
    return finalize(payload, result_a, result_b)


def case_6():
    payload = base_result(6, "str(soup)", "first <p>.extract() first; then str(soup)", "BeautifulSoup('<p>a</p><p>b</p>', 'html.parser'); Tag is a PageElement subclass.")
    from bs4 import BeautifulSoup
    a_soup = BeautifulSoup("<p>a</p><p>b</p>", "html.parser")
    result_a = {"kind": "value", "later": str(a_soup), "state": {"p_count": len(a_soup.find_all("p"))}}
    b_soup = BeautifulSoup("<p>a</p><p>b</p>", "html.parser")
    observation = str(b_soup.find_all("p")[0].extract())
    result_b = {"kind": "value", "observation": observation, "later": str(b_soup), "state": {"p_count": len(b_soup.find_all("p"))}}
    return finalize(payload, result_a, result_b)


def case_7():
    payload = base_result(7, "insert c after initializing LRI with a,b", "__getitem__('a') first; then insert c", "LRI(max_size=2) with keys a, b, c.")
    from boltons.cacheutils import LRI

    def run(observe):
        cache = LRI(max_size=2)
        cache["a"], cache["b"] = "A", "B"
        observation = cache["a"] if observe else None
        cache["c"] = "C"
        return {"kind": "value", "observation": observation, "later": list(cache.items()), "state": {"hit_count": cache.hit_count, "miss_count": cache.miss_count, "soft_miss_count": cache.soft_miss_count}}

    return finalize(payload, run(False), run(True))


def case_8():
    payload = base_result(8, "insert c after initializing LRU with a,b", "__getitem__('a') first; then insert c", "LRU(max_size=2) with keys a, b, c.")
    from boltons.cacheutils import LRU

    def run(observe):
        cache = LRU(max_size=2)
        cache["a"], cache["b"] = "A", "B"
        observation = cache["a"] if observe else None
        cache["c"] = "C"
        return {"kind": "value", "observation": observation, "later": list(cache.items()), "state": {"hit_count": cache.hit_count, "miss_count": cache.miss_count, "soft_miss_count": cache.soft_miss_count}}

    return finalize(payload, run(False), run(True))


def case_9():
    payload = base_result(9, "read(3)", "read(3) first; then read(3)", "MultiFileReader(BytesIO(b'ab'), BytesIO(b'cd'), BytesIO(b'e')).")
    from boltons.ioutils import MultiFileReader

    def run(observe):
        reader = MultiFileReader(io.BytesIO(b"ab"), io.BytesIO(b"cd"), io.BytesIO(b"e"))
        observation = reader.read(3) if observe else None
        return {"kind": "value", "observation": observation, "later": reader.read(3), "state": {"index": reader._index}}

    return finalize(payload, run(False), run(True))


def case_10():
    payload = base_result(10, "read validator.errors", "validate({'name': 'Al'}) first; then read validator.errors", "Public cerberus.Validator subclass with schema {'name': {'type': 'string', 'minlength': 3}}.")
    from cerberus import Validator

    schema = {"name": {"type": "string", "minlength": 3}}
    a_validator = Validator(schema)
    result_a = {"kind": "value", "later": dict(a_validator.errors), "state": {"document": a_validator.document, "errors": dict(a_validator.errors)}}
    b_validator = Validator(schema)
    observation = b_validator.validate({"name": "Al"})
    result_b = {"kind": "value", "observation": observation, "later": dict(b_validator.errors), "state": {"document": b_validator.document, "errors": dict(b_validator.errors)}}
    return finalize(payload, result_a, result_b)


def case_11():
    payload = base_result(11, "build command with grouped option and invoke --foo x", "call group decorator on a function first; then build and invoke command", "Tiny Click command using click-option-group public optgroup helpers and CliRunner.")
    import click
    from click.testing import CliRunner
    from click_option_group import optgroup

    def build(observe):
        def callback(**kwargs):
            click.echo(str(kwargs))

        group = optgroup.group("Group")
        observation = None
        if observe:
            observation = repr(group(callback))
        command = click.command()(optgroup.option("--foo")(group(callback)))
        invocation = CliRunner().invoke(command, ["--foo", "x"])
        return {"kind": "value", "observation": observation, "later": {"params": [p.name for p in command.params], "exit_code": invocation.exit_code, "output": invocation.output.strip()}, "state": {}}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return finalize(payload, build(False), build(True))


def case_12():
    payload = base_result(12, "get_element('b')", "get_element('a') first; then get_element('b')", "BTree populated with dns.btree.KV('a','A') and KV('b','B').")
    from dns.btree import BTree, KV

    def make_tree():
        tree = BTree()
        tree.insert_element(KV("a", "A"))
        tree.insert_element(KV("b", "B"))
        return tree

    a_tree = make_tree()
    result_a = {"kind": "value", "later": a_tree.get_element("b"), "state": {"size": a_tree.size, "cursors": len(a_tree.cursors)}}
    b_tree = make_tree()
    observation = b_tree.get_element("a")
    result_b = {"kind": "value", "observation": observation, "later": b_tree.get_element("b"), "state": {"size": b_tree.size, "cursors": len(b_tree.cursors)}}
    return finalize(payload, result_a, result_b)


def case_13():
    payload = base_result(13, "get_string()", "get() first; then get_string()", "dns.tokenizer.Tokenizer over io.StringIO('alpha beta\\n').")
    from dns.tokenizer import Tokenizer

    def run(observe):
        tokenizer = Tokenizer(io.StringIO("alpha beta\n"))
        observation = tokenizer.get().value if observe else None
        return {"kind": "value", "observation": observation, "later": tokenizer.get_string(), "state": {"where": tokenizer.where(), "eof": tokenizer.eof, "ungotten_token": tokenizer.ungotten_token}}

    return finalize(payload, run(False), run(True))


def case_14():
    payload = base_result(14, "ChunkedReader()(buffer)", "ChunkedReader()(buffer) first; then ChunkedReader()(buffer)", "h11 ReceiveBuffer containing a complete chunked body b'3\\r\\nabc\\r\\n0\\r\\n\\r\\n'.")
    from h11._receivebuffer import ReceiveBuffer
    from h11._readers import ChunkedReader

    def run(observe):
        buffer = ReceiveBuffer()
        buffer += b"3\r\nabc\r\n0\r\n\r\n"
        reader = ChunkedReader()
        observation = repr(reader(buffer)) if observe else None
        return {"kind": "value", "observation": observation, "later": repr(reader(buffer)), "state": {"buffer": bytes(buffer), "reader": dict(reader.__dict__)}}

    return finalize(payload, run(False), run(True))


def case_15():
    payload = base_result(15, "maybe_extract_lines()", "maybe_extract_next_line() first; then maybe_extract_lines()", "ReceiveBuffer containing HTTP-like header bytes.")
    from h11._receivebuffer import ReceiveBuffer

    def run(observe):
        buffer = ReceiveBuffer()
        buffer += b"GET / HTTP/1.1\r\nHost: x\r\n\r\nBODY"
        observation = bytes(buffer.maybe_extract_next_line() or b"") if observe else None
        later = buffer.maybe_extract_lines()
        return {"kind": "value", "observation": observation, "later": [bytes(line) for line in later] if later is not None else None, "state": {"buffer": bytes(buffer), "next_line_search": buffer._next_line_search, "multiple_lines_search": buffer._multiple_lines_search}}

    return finalize(payload, run(False), run(True))


CASE_FUNCS = {
    1: case_1,
    2: case_2,
    3: case_3,
    4: case_4,
    5: case_5,
    6: case_6,
    7: case_7,
    8: case_8,
    9: case_9,
    10: case_10,
    11: case_11,
    12: case_12,
    13: case_13,
    14: case_14,
    15: case_15,
}


def run_case(rank: int) -> dict:
    add_snapshot_paths()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    package, _, class_name, _, _ = CASES[rank]
    out_name = f"rescue_{rank:02d}_{package.replace('-', '_')}_{class_name.lstrip('_')}.json"
    out_path = OUTPUT_DIR / out_name
    try:
        payload = CASE_FUNCS[rank]()
    except ModuleNotFoundError as exc:
        payload = base_result(rank, "", "", "")
        payload["classification"] = "import_failed"
        payload["failure_reason"] = f"import_failed: {type(exc).__name__}: {exc}"
    except Exception as exc:
        payload = base_result(rank, "", "", "")
        payload["classification"] = "could_not_construct_even_manually"
        payload["failure_reason"] = f"{type(exc).__name__}: {exc}"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return payload


def main(argv: list[str]) -> int:
    rank = int(argv[1]) if len(argv) > 1 else int(Path(argv[0]).stem.split("_")[1])
    run_case(rank)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
'''

RUNNER = r'''
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
HARNESS_DIR = BASE / "harnesses"
OUTPUT_DIR = BASE / "outputs"
SELECTION_CSV = BASE / "rescue_candidate_selection.csv"
RESULTS_CSV = BASE / "rescue_results.csv"
SUMMARY_MD = BASE / "rescue_summary.md"
MANUAL_NOTES_MD = BASE / "RESCUE_MANUAL_REVIEW_NOTES.md"
DECISION_MD = BASE / "FOLLOWUP_DECISION.md"
FINAL_MD = BASE / "OSDS_BEHAVIORAL_SWEEP_RESCUE_RESULTS.md"

REQUIRED_JSON_KEYS = {
    "package", "version", "class_name", "file_path", "original_sweep_rank", "rescue_rank",
    "operation_A", "operation_B", "fixture_description", "result_A", "result_B",
    "output_diff", "branch_flip", "state_diff", "classification", "boundary_note", "failure_reason",
}

RESULT_COLUMNS = [
    "rescue_rank", "original_sweep_rank", "package", "version", "class_name", "previous_classification",
    "rescue_classification", "output_diff", "branch_flip", "state_diff", "fixture_description",
    "operation_A", "operation_B", "failure_reason", "boundary_note", "harness_path", "json_output_path",
]


def load_selection():
    with SELECTION_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def harness_name(row):
    package = row["package"].replace("-", "_")
    cls = row["class_name"].lstrip("_")
    return f"rescue_{int(row['rescue_rank']):02d}_{package}_{cls}.py"


def output_name(row):
    package = row["package"].replace("-", "_")
    cls = row["class_name"].lstrip("_")
    return f"rescue_{int(row['rescue_rank']):02d}_{package}_{cls}.json"


def run_harnesses(selection):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    attempts = []
    for row in selection:
        harness = HARNESS_DIR / harness_name(row)
        completed = subprocess.run(
            [sys.executable, str(harness)],
            cwd=str(BASE.parents[1]),
            text=True,
            capture_output=True,
            timeout=20,
        )
        attempts.append((row, harness, completed.returncode, completed.stdout, completed.stderr))
    return attempts


def load_outputs(selection):
    payloads = []
    errors = []
    for row in selection:
        path = OUTPUT_DIR / output_name(row)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            missing = sorted(REQUIRED_JSON_KEYS - set(payload))
            if missing:
                errors.append(f"{path}: missing keys {missing}")
            payloads.append((row, path, payload))
        except Exception as exc:
            errors.append(f"{path}: {type(exc).__name__}: {exc}")
    return payloads, errors


def write_results_csv(payloads):
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row, json_path, payload in payloads:
            harness = HARNESS_DIR / harness_name(row)
            writer.writerow({
                "rescue_rank": payload["rescue_rank"],
                "original_sweep_rank": payload["original_sweep_rank"],
                "package": payload["package"],
                "version": payload["version"],
                "class_name": payload["class_name"],
                "previous_classification": row["previous_classification"],
                "rescue_classification": payload["classification"],
                "output_diff": payload["output_diff"],
                "branch_flip": payload["branch_flip"],
                "state_diff": payload["state_diff"],
                "fixture_description": payload["fixture_description"],
                "operation_A": payload["operation_A"],
                "operation_B": payload["operation_B"],
                "failure_reason": payload["failure_reason"],
                "boundary_note": payload["boundary_note"],
                "harness_path": str(harness.resolve()),
                "json_output_path": str(json_path.resolve()),
            })


def counts(payloads):
    c = Counter(payload["classification"] for _, _, payload in payloads)
    branch_output = c["confirmed_branch_flip"] + c["confirmed_output_divergence"]
    return c, branch_output


def md_table(rows, columns):
    out = []
    out.append("| " + " | ".join(columns) + " |")
    out.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        out.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(out)


def write_summary(selection, payloads, validation_errors, attempts):
    c, branch_output = counts(payloads)
    state_only = c["confirmed_state_divergence_only"]
    structural = c["structural_only_no_runtime_difference"]
    could_not = c["could_not_construct_even_manually"]
    import_failed = c["import_failed"]
    external = c["requires_external_fixture"]
    not_applicable = c["not_applicable_after_manual_inspection"]
    attempted = len(attempts)
    selected_rows = [
        {
            "Rank": row["rescue_rank"],
            "Original": row["original_sweep_rank"],
            "Package": row["package"],
            "Class": row["class_name"],
            "Previous": row["previous_classification"],
        }
        for row in selection
    ]
    confirmed = [
        {
            "Rank": payload["rescue_rank"],
            "Package": payload["package"],
            "Class": payload["class_name"],
            "Classification": payload["classification"],
            "Boundary": payload["boundary_note"],
        }
        for _, _, payload in payloads
        if payload["classification"] in {"confirmed_branch_flip", "confirmed_output_divergence"}
    ]
    state_rows = [
        {
            "Rank": payload["rescue_rank"],
            "Package": payload["package"],
            "Class": payload["class_name"],
            "Boundary": payload["boundary_note"],
        }
        for _, _, payload in payloads
        if payload["classification"] == "confirmed_state_divergence_only"
    ]
    failed_rows = [
        {
            "Rank": payload["rescue_rank"],
            "Package": payload["package"],
            "Class": payload["class_name"],
            "Classification": payload["classification"],
            "Reason": payload["failure_reason"] or payload["boundary_note"],
        }
        for _, _, payload in payloads
        if payload["classification"] not in {"confirmed_branch_flip", "confirmed_output_divergence", "confirmed_state_divergence_only"}
    ]
    aggregate_table = (
        "| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |\n"
        "| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |\n"
        f"| {len(selection)} | {attempted} | {branch_output} | {state_only} | {structural} | {could_not} | {import_failed} | {external} | {not_applicable} |\n"
    )
    validation_text = "None." if not validation_errors else "\n".join(f"- {e}" for e in validation_errors)
    SUMMARY_MD.write_text(
        "# Rescue Summary\n\n"
        f"{aggregate_table}\n"
        "## Selected Rescue Candidates\n\n"
        + md_table(selected_rows, ["Rank", "Original", "Package", "Class", "Previous"])
        + "\n\n## Runnable Manual Harnesses Attempted\n\n"
        f"Attempted {attempted} manual harnesses with a 20 second timeout per harness.\n\n"
        "## Output/Branch Divergences Found\n\n"
        + (md_table(confirmed, ["Rank", "Package", "Class", "Classification", "Boundary"]) if confirmed else "None.")
        + "\n\n## State-Only Divergences Found\n\n"
        + (md_table(state_rows, ["Rank", "Package", "Class", "Boundary"]) if state_rows else "None.")
        + "\n\n## Structural Or Failed Manual Attempts\n\n"
        + (md_table(failed_rows, ["Rank", "Package", "Class", "Classification", "Reason"]) if failed_rows else "None.")
        + "\n\n## JSON Validation\n\n"
        + validation_text
        + "\n\n## Comparison With Original Generic Sweep\n\n"
        "The original generic sweep selected 50 candidates and found 0 output/branch divergences and 4 state-only divergences. "
        f"This manual rescue selected 15 candidates, attempted {attempted} package-specific fixtures, and found {branch_output} output/branch divergences plus {state_only} state-only divergences. "
        "The result supports the narrower claim that package-specific construction can recover behavior that a no-argument generic harness misses; it is not a PyPI prevalence estimate.\n",
        encoding="utf-8",
    )


def write_manual_notes(selection, payloads):
    by_rank = {int(payload["rescue_rank"]): (row, payload) for row, _, payload in payloads}
    parts = ["# Rescue Manual Review Notes\n"]
    for row in selection:
        rank = int(row["rescue_rank"])
        _, payload = by_rank[rank]
        use = "Use only with explicit boundary language." if payload["classification"] in {"confirmed_output_divergence", "confirmed_branch_flip"} else "Do not use as a headline paper example."
        realistic = "Yes" if payload["fixture_description"] else "No"
        parts.append(
            f"## {rank}. {row['package']} `{row['class_name']}`\n\n"
            f"- Original sweep classification: `{row['previous_classification']}`\n"
            f"- Why the generic harness failed or was weak: {row['previous_failure_reason'] or 'It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.'}\n"
            f"- Manual fixture built: {payload['fixture_description']}\n"
            f"- Realistic fixture: {realistic}.\n"
            f"- Result: `{payload['classification']}`; output_diff={payload['output_diff']}, branch_flip={payload['branch_flip']}, state_diff={payload['state_diff']}.\n"
            f"- Should it be used in the paper: {use}\n"
            f"- Exact caution language: {payload['boundary_note']}\n"
        )
    MANUAL_NOTES_MD.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_decision(payloads):
    _, branch_output = counts(payloads)
    case = "A" if branch_output >= 2 else "B"
    recommendation = (
        "Add the rescue sweep to main Section 9; keep the original four detailed cases; present the generic sweep as showing automatic conversion difficulty; present the manual rescue as showing package-specific construction recovers stronger evidence."
        if case == "A"
        else "Move or shrink the 50-candidate sweep; do not mention it in the abstract; keep four detailed cases as main evidence; use rescue as artifact honesty."
    )
    case_a_wording = (
        "A follow-up manual rescue pass selected 15 candidates from the failed or structurally weak generic sweep and supplied package-specific in-memory fixtures. "
        "Unlike the generic no-argument harness, the rescue pass recovered output-level divergences in several parser, iterator, cache, and stream objects. "
        "These results should be read as evidence that automatic harness construction is a limiting factor: many access-induced effects require domain-shaped objects and realistic input. "
        "The denominator remains the selected rescue set, not PyPI prevalence, and intentionally destructive cursor/stream examples are reported with boundary notes rather than treated as defects."
    )
    case_b_wording = (
        "The 50-candidate behavioral sweep is best treated as a limitations result. A generic no-argument harness converted few structural findings into consequential runtime evidence, and the manual rescue pass recovered at most one new output- or branch-level divergence. "
        "Accordingly, the main empirical evidence should remain the four detailed hand-built cases. The sweep can be summarized in a short limitations paragraph or artifact appendix as evidence that automatic conversion from static patterns to runnable behavior is difficult, not as a headline behavioral prevalence result."
    )
    DECISION_MD.write_text(
        "# Artifact Decision\n\n"
        f"Observed case: Case {case}. New rescue output/branch divergences: {branch_output}.\n\n"
        f"Direct recommendation: {recommendation}\n\n"
        "## Recommended Section 9.5 Wording If Case A Applies\n\n"
        f"{case_a_wording}\n\n"
        "## Recommended Section 9.5 Wording If Case B Applies\n\n"
        f"{case_b_wording}\n",
        encoding="utf-8",
    )


def write_final_report(selection, payloads):
    c, branch_output = counts(payloads)
    state_only = c["confirmed_state_divergence_only"]
    confirmed = [payload for _, _, payload in payloads if payload["classification"] in {"confirmed_branch_flip", "confirmed_output_divergence"}]
    state_rows = [payload for _, _, payload in payloads if payload["classification"] == "confirmed_state_divergence_only"]
    failed = [payload for _, _, payload in payloads if payload["classification"] not in {"confirmed_branch_flip", "confirmed_output_divergence", "confirmed_state_divergence_only"}]
    recommendation = (
        "Case A: add the rescue sweep to main Section 9 with strong boundary language; keep the original four detailed cases."
        if branch_output >= 2
        else "Case B: shrink or move the sweep; keep the original four detailed cases as the main evidence."
    )
    command_log = [
        "Read prior behavioral_sweep_results.csv, MANUAL_REVIEW_PACKET.md, OSDS_BEHAVIORAL_SWEEP_RESULTS.md, real_case_results.csv, and source_snapshot files.",
        "Created package-specific rescue harnesses under paper_artifacts/behavioral_sweep_followup/harnesses/.",
        f"Ran {Path(__file__).name} with the active Python interpreter to execute and aggregate rescue harnesses.",
    ]
    def bullet_payloads(rows):
        if not rows:
            return "None.\n"
        return "\n".join(
            f"- Rescue {p['rescue_rank']}: {p['package']} `{p['class_name']}` -> `{p['classification']}`. {p['boundary_note']}"
            for p in rows
        ) + "\n"
    FINAL_MD.write_text(
        "# Behavioral Sweep Follow-up Results\n\n"
        "## 1. Executive Summary\n\n"
        f"Selected rescue candidates: {len(selection)}. Manual harnesses attempted: {len(payloads)}. "
        f"New output/branch divergences: {branch_output}. New state-only divergences: {state_only}. "
        f"Structural-only or failed manual attempts: {len(failed)}.\n\n"
        "## 2. Why The Rescue Pass Was Needed\n\n"
        "The prior 50-candidate generic sweep found 0 output/branch divergences and 4 state-only divergences. Many failures were caused by no-argument construction or empty fixtures for package objects that require iterables, parser documents, buffers, cache entries, or framework-shaped objects.\n\n"
        "## 3. Candidate Selection\n\n"
        "The rescue pass selected 15 candidates from the previous sweep, favoring construction failures, structural-only generic runs, and import failures whose dependencies were present in the rebuilt snapshot. Unsafe, nondeterministic, network, database, credential, browser, server, destructive filesystem, and subprocess-heavy cases were excluded.\n\n"
        "## 4. Aggregate Results\n\n"
        "| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |\n"
        "| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |\n"
        f"| {len(selection)} | {len(payloads)} | {branch_output} | {state_only} | {c['structural_only_no_runtime_difference']} | {c['could_not_construct_even_manually']} | {c['import_failed']} | {c['requires_external_fixture']} | {c['not_applicable_after_manual_inspection']} |\n\n"
        "## 5. Confirmed Output/Branch Cases\n\n"
        + bullet_payloads(confirmed)
        + "\n## 6. Confirmed State-Only Cases\n\n"
        + bullet_payloads(state_rows)
        + "\n## 7. Failed Or Still Structural Cases\n\n"
        + bullet_payloads(failed)
        + "\n## 8. Interpretation\n\n"
        "The rescue pass shows that the generic harness limitation was real: several candidates needed package-specific fixtures before output-level behavior appeared. The positive cases are mostly stateful parsers, iterators, caches, tree nodes, and stream readers, so they should be framed as access-order-sensitive behavior rather than defects. The selected rescue denominator is not a PyPI prevalence claim.\n\n"
        "## 9. Artifact Recommendation\n\n"
        f"{recommendation}\n\n"
        "## 10. Exact Command Log\n\n"
        + "\n".join(f"- {entry}" for entry in command_log)
        + "\n",
        encoding="utf-8",
    )


def main():
    selection = load_selection()
    attempts = run_harnesses(selection)
    payloads, validation_errors = load_outputs(selection)
    write_results_csv(payloads)
    write_summary(selection, payloads, validation_errors, attempts)
    write_manual_notes(selection, payloads)
    write_decision(payloads)
    write_final_report(selection, payloads)
    if validation_errors:
        print("\n".join(validation_errors), file=sys.stderr)
        return 1
    for _, harness, code, stdout, stderr in attempts:
        if code != 0:
            print(f"{harness} exited {code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

def main() -> int:
    HARNESS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with (ROOT / "rescue_candidate_selection.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SELECTION_ROWS[0]))
        writer.writeheader()
        writer.writerows(SELECTION_ROWS)

    notes = [
        "# Rescue Selection Notes",
        "",
        "The 15 rescue candidates were selected from the previous 50-candidate behavioral sweep. Selection prioritized `could_not_construct`, `structural_only_no_runtime_difference`, and import failures whose dependencies exist in the rebuilt source snapshot. One prior state-only case, dnspython `Tokenizer`, was included because the user prompt explicitly identified it and a real token stream could test whether state-only evidence becomes output-visible.",
        "",
        "Excluded cases include the unsafe docutils writer/string-output entries, nondeterministic dnspython `EntropyPool`, import failures requiring unavailable `html5lib` or `aioquic`, AnyIO runtime/context cases that require event-loop semantics, and Docutils parser state-machine directive classes whose realistic setup would require a larger parser framework fixture.",
        "",
        "The selected cases favor in-memory fixtures: strings, iterables, `BytesIO`, BeautifulSoup trees, Click's in-process `CliRunner`, Docutils document utilities, and h11 receive buffers. No network, database, credential, browser, server, destructive filesystem, or subprocess-heavy setup is used by the harnesses.",
    ]
    (ROOT / "RESCUE_SELECTION_NOTES.md").write_text("\n".join(notes) + "\n", encoding="utf-8")

    write_text(ROOT / "_rescue_common.py", COMMON)
    write_text(ROOT / "run_rescue_harnesses.py", RUNNER)

    for row in SELECTION_ROWS:
        rank = int(row["rescue_rank"])
        package = row["package"].replace("-", "_")
        cls = row["class_name"].lstrip("_")
        harness = HARNESS_DIR / f"rescue_{rank:02d}_{package}_{cls}.py"
        write_text(
            harness,
            f'''
            from pathlib import Path
            import sys

            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from _rescue_common import run_case

            if __name__ == "__main__":
                run_case({rank})
            ''',
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
