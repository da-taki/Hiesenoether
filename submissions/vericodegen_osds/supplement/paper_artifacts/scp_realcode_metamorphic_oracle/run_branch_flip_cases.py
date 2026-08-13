from __future__ import annotations

import csv
import io
import json
import logging
import sys
import warnings
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import metamorphic_fixtures as F

RESULTS_JSON = BASE / "branch_flip_results.json"
RESULTS_CSV = BASE / "branch_flip_results.csv"

FIELDS = [
    "branch_case_id", "package_name", "package_version", "underlying_candidate_id",
    "order_A_steps", "order_B_steps", "order_A_branch", "order_B_branch",
    "order_A_consequence", "order_B_consequence", "branch_changed", "consequence_changed",
    "output_changed", "exception_changed", "classification", "code_snippet", "boundary_note",
]

def _classify(a_branch, b_branch, a_cons, b_cons):
    branch_changed = a_branch != b_branch
    consequence_changed = a_cons != b_cons
    if branch_changed:
        return branch_changed, consequence_changed, "confirmed_branch_flip"
    if consequence_changed:
        return branch_changed, consequence_changed, "confirmed_consequence_change"
    return branch_changed, consequence_changed, "no_branch_flip"

def bc_httpcore():
    import httpcore

    snippet = (
        "def handle(resp, observe):\n"
        "    if observe: resp.read()          # real httpcore op\n"
        "    try:\n"
        "        body = resp.content           # real httpcore op\n"
        "        return 'content_ready', 'cache_response'\n"
        "    except RuntimeError:\n"
        "        return 'stream_pending', 'stream_response_or_error'")

    def handle(observe):
        resp = httpcore.Response(200, content=[b"alpha", b"beta"])
        steps = ["construct Response(streaming)"]
        if observe:
            resp.read()
            steps.append("resp.read()")
        try:
            _ = resp.content
            steps.append("resp.content")
            return "content_ready", "cache_response", steps, None
        except RuntimeError as exc:
            steps.append("resp.content -> RuntimeError")
            return "stream_pending", "stream_response_or_error", steps, type(exc).__name__

    a = handle(False)
    b = handle(True)
    return _pack("bf01_httpcore_Response", "httpcore", httpcore.__version__,
                 "rc01_httpcore_Response", a, b, snippet,
                 "read() materializes _content; .content flips RuntimeError->value")

def bc_pytest():
    from _pytest.logging import catching_logs

    snippet = (
        "def alert(observe):\n"
        "    handler = ListHandler(); logger.addHandler(handler)\n"
        "    if observe:\n"
        "        cm = catching_logs(handler, level=ERROR); cm.__enter__(); cm.__exit__(...)\n"
        "    logger.warning('disk almost full')   # real emit\n"
        "    if handler.messages: return 'warning_seen', 'emit_alert'\n"
        "    return 'warning_hidden', 'suppress_alert'")

    class ListHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record.getMessage())

    def alert(observe):
        logger = logging.getLogger("scp_meta_branch_pytest")
        logger.handlers = []
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        handler = ListHandler()
        handler.setLevel(logging.NOTSET)
        logger.addHandler(handler)
        steps = ["fresh handler"]
        if observe:
            cm = catching_logs(handler, level=logging.ERROR)
            cm.__enter__()
            cm.__exit__(None, None, None)
            steps.append("catching_logs(handler, ERROR) enter/exit")
        logger.warning("disk almost full")
        steps.append("logger.warning('disk almost full')")
        if handler.messages:
            return "warning_seen", "emit_alert", steps, None
        return "warning_hidden", "suppress_alert", steps, None

    a = alert(False)
    b = alert(True)
    return _pack("bf02_pytest_catching_logs", "pytest", _ver("pytest"),
                 "rc03_pytest_catching_logs", a, b, snippet,
                 "catching_logs raises the handler level and does not restore it")

def bc_pyyaml():
    from yaml.representer import SafeRepresenter

    snippet = (
        "def route(observe):\n"
        "    rep = SafeRepresenter(); payload = ['before']\n"
        "    if observe: rep.represent_data(payload)   # caches identity\n"
        "    payload[0] = 'after'\n"
        "    node = rep.represent_data(payload)        # real represent\n"
        "    val = node.value[0].value\n"
        "    return ('after_payload','use_after_payload') if val=='after' \\\n"
        "           else ('before_payload','use_before_payload')")

    def route(observe):
        rep = SafeRepresenter()
        payload = ["before"]
        steps = ["SafeRepresenter()", "payload=['before']"]
        if observe:
            rep.represent_data(payload)
            steps.append("represent_data(payload) [observe -> caches identity]")
        payload[0] = "after"
        steps.append("payload[0]='after'")
        node = rep.represent_data(payload)
        steps.append("represent_data(payload)")
        val = node.value[0].value
        if val == "after":
            return "after_payload", "use_after_payload", steps, None
        return "before_payload", "use_before_payload", steps, None

    a = route(False)
    b = route(True)
    return _pack("bf03_PyYAML_SafeRepresenter", "PyYAML", _ver("PyYAML"),
                 "rc02_PyYAML_SafeRepresenter", a, b, snippet,
                 "identity cache returns the stale node for a mutated object")

def bc_boltons_lru():
    from boltons.cacheutils import LRU

    snippet = (
        "def serve(observe):\n"
        "    cache = LRU(max_size=2); cache['x']=1; cache['y']=2\n"
        "    if observe: cache['x']            # real access -> refresh recency\n"
        "    cache['z'] = 3                     # eviction\n"
        "    return ('x_live','serve_x_from_cache') if 'x' in cache \\\n"
        "           else ('x_evicted','recompute_x')")

    def serve(observe):
        cache = LRU(max_size=2)
        cache["x"], cache["y"] = 1, 2
        steps = ["LRU(max_size=2) x,y"]
        if observe:
            _ = cache["x"]
            steps.append("cache['x'] [observe]")
        cache["z"] = 3
        steps.append("cache['z']=3 (eviction)")
        if "x" in cache:
            return "x_live", "serve_x_from_cache", steps, None
        return "x_evicted", "recompute_x", steps, None

    a = serve(False)
    b = serve(True)
    return _pack("bf04_boltons_LRU", "boltons", "25.0.0", "re08_boltons_LRU", a, b, snippet,
                 "read refreshes recency so a different key is evicted")

def bc_dnspython_tokenizer():
    from dns.tokenizer import Tokenizer

    snippet = (
        "def parse(observe):\n"
        "    tok = Tokenizer(StringIO('aa bb'))\n"
        "    if observe: tok.get()             # consume one token\n"
        "    t = tok.get()                     # real tokenizer read\n"
        "    return ('has_bb','continue_parse') if t.value=='bb' \\\n"
        "           else ('has_aa','handle_first_field')")

    def parse(observe):
        tok = Tokenizer(io.StringIO("aa bb"))
        steps = ["Tokenizer('aa bb')"]
        if observe:
            tok.get()
            steps.append("tok.get() [observe]")
        t = tok.get()
        steps.append("tok.get()")
        if t.value == "bb":
            return "has_bb", "continue_parse", steps, None
        return "has_aa", "handle_first_field", steps, None

    a = parse(False)
    b = parse(True)
    return _pack("bf05_dnspython_Tokenizer", "dnspython", "2.8.0", "re11_dnspython_Tokenizer",
                 a, b, snippet, "cursor advance changes which token the caller reads")

def bc_h11_chunkedreader():
    from h11._receivebuffer import ReceiveBuffer
    from h11._readers import ChunkedReader
    from h11._events import EndOfMessage

    snippet = (
        "def pump(observe):\n"
        "    buf = ReceiveBuffer(); buf += b'3\\r\\nabc\\r\\n0\\r\\n\\r\\n'\n"
        "    reader = ChunkedReader()\n"
        "    if observe: reader(buf)           # consume first chunk\n"
        "    ev = reader(buf)                  # real reader read\n"
        "    return ('end','finish_response') if isinstance(ev, EndOfMessage) \\\n"
        "           else ('data','continue_parse')")

    def pump(observe):
        buf = ReceiveBuffer()
        buf += b"3\r\nabc\r\n0\r\n\r\n"
        reader = ChunkedReader()
        steps = ["ReceiveBuffer(chunked body)", "ChunkedReader()"]
        if observe:
            reader(buf)
            steps.append("reader(buf) [observe]")
        ev = reader(buf)
        steps.append("reader(buf)")
        if isinstance(ev, EndOfMessage):
            return "end", "finish_response", steps, None
        return "data", "continue_parse", steps, None

    a = pump(False)
    b = pump(True)
    return _pack("bf06_h11_ChunkedReader", "h11", _ver("h11"), "re12_h11_ChunkedReader",
                 a, b, snippet, "consuming a chunk flips Data vs EndOfMessage")

def bc_cerberus():
    from cerberus import Validator

    snippet = (
        "def gate(observe):\n"
        "    v = Validator({'name': {'type':'string','minlength':3}})\n"
        "    if observe: v.validate({'name':'Al'})   # real validate (fails)\n"
        "    return ('has_errors','reject_request') if v.errors \\\n"
        "           else ('clean','accept_request')")

    def gate(observe):
        v = Validator({"name": {"type": "string", "minlength": 3}})
        steps = ["Validator(schema)"]
        if observe:
            v.validate({"name": "Al"})
            steps.append("v.validate({'name':'Al'}) [observe]")
        if v.errors:
            return "has_errors", "reject_request", steps, None
        return "clean", "accept_request", steps, None

    a = gate(False)
    b = gate(True)
    return _pack("bf07_cerberus_Validator", "cerberus", "1.3.8", "re10_cerberus_Validator",
                 a, b, snippet, "validate() populates the errors read on the next line")

def bc_markdown():
    import markdown

    snippet = (
        "def render(observe):\n"
        "    md = markdown.Markdown(output_format='html')\n"
        "    if observe: md.convert('[doc]: https://x')   # registers reference\n"
        "    html = md.convert('[doc][]')                 # real convert\n"
        "    return ('linked','render_hyperlink') if '<a ' in html \\\n"
        "           else ('plain','render_plain_text')")

    def render(observe):
        md = markdown.Markdown(output_format="html")
        steps = ["Markdown(output_format='html')"]
        if observe:
            md.convert("[doc]: https://example.invalid")
            steps.append("convert(ref-def) [observe]")
        html = md.convert("[doc][]")
        steps.append("convert('[doc][]')")
        if "<a " in html:
            return "linked", "render_hyperlink", steps, None
        return "plain", "render_plain_text", steps, None

    a = render(False)
    b = render(True)
    return _pack("bf08_markdown_Markdown", "markdown", "3.10.2", "re01_markdown_Markdown",
                 a, b, snippet, "reference registry from a prior convert() changes rendering")

def bc_bs4():
    from bs4 import BeautifulSoup

    snippet = (
        "def pick(observe):\n"
        "    soup = BeautifulSoup('<p>a</p><p>b</p>', 'html.parser')\n"
        "    if observe: soup.find_all('p')[0].extract()   # destructive access\n"
        "    first = soup.find('p')                        # real read\n"
        "    return ('first_is_a','process_a') if first.get_text()=='a' \\\n"
        "           else ('first_is_b','process_b')")

    def pick(observe):
        soup = BeautifulSoup("<p>a</p><p>b</p>", "html.parser")
        steps = ["BeautifulSoup('<p>a</p><p>b</p>')"]
        if observe:
            soup.find_all("p")[0].extract()
            steps.append("first <p>.extract() [observe]")
        first = soup.find("p")
        steps.append("soup.find('p')")
        if first.get_text() == "a":
            return "first_is_a", "process_a", steps, None
        return "first_is_b", "process_b", steps, None

    a = pick(False)
    b = pick(True)
    return _pack("bf09_beautifulsoup4_PageElement", "beautifulsoup4", "4.14.3",
                 "re06_beautifulsoup4_PageElement", a, b, snippet,
                 "extract() destructively removes the node the caller then reads")

def _ver(dist):
    try:
        import importlib.metadata as m
        return m.version(dist)
    except Exception:
        return "snapshot"

def _pack(case_id, pkg, ver, underlying, a, b, snippet, boundary):
    a_branch, a_cons, a_steps, a_exc = a
    b_branch, b_cons, b_steps, b_exc = b
    branch_changed, consequence_changed, classification = _classify(a_branch, b_branch, a_cons, b_cons)
    return {
        "branch_case_id": case_id,
        "package_name": pkg,
        "package_version": ver,
        "underlying_candidate_id": underlying,
        "order_A_steps": " | ".join(a_steps),
        "order_B_steps": " | ".join(b_steps),
        "order_A_branch": a_branch,
        "order_B_branch": b_branch,
        "order_A_consequence": a_cons,
        "order_B_consequence": b_cons,
        "branch_changed": branch_changed,
        "consequence_changed": consequence_changed,
        "output_changed": a_branch != b_branch,
        "exception_changed": (a_exc or "") != (b_exc or ""),
        "classification": classification,
        "code_snippet": snippet,
        "boundary_note": boundary,
    }

CASES = [bc_httpcore, bc_pytest, bc_pyyaml, bc_boltons_lru, bc_dnspython_tokenizer,
         bc_h11_chunkedreader, bc_cerberus, bc_markdown, bc_bs4]

def main() -> int:
    F.add_snapshot_paths()
    warnings.simplefilter("ignore")
    results = []
    for case in CASES:
        try:
            results.append(case())
        except Exception as exc:
            results.append({
                "branch_case_id": case.__name__, "package_name": "", "package_version": "",
                "underlying_candidate_id": "", "order_A_steps": "", "order_B_steps": "",
                "order_A_branch": "", "order_B_branch": "", "order_A_consequence": "",
                "order_B_consequence": "", "branch_changed": False, "consequence_changed": False,
                "output_changed": False, "exception_changed": False,
                "classification": "could_not_construct", "code_snippet": "",
                "boundary_note": f"{type(exc).__name__}: {exc}",
            })

    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    from collections import Counter
    counts = Counter(r["classification"] for r in results)
    summary = {
        "branch_cases": len(results),
        "confirmed_branch_flip": counts.get("confirmed_branch_flip", 0),
        "confirmed_consequence_change": counts.get("confirmed_consequence_change", 0),
        "no_branch_flip": counts.get("no_branch_flip", 0),
        "could_not_construct": counts.get("could_not_construct", 0),
        "classification_counts": dict(sorted(counts.items())),
    }
    RESULTS_JSON.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
