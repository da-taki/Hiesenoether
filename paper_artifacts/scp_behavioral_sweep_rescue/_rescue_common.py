from __future__ import annotations

import io
import json
import sys
import warnings
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SNAPSHOT = REPO / "paper_artifacts" / "scp_realworld_revision" / "source_snapshot"
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
