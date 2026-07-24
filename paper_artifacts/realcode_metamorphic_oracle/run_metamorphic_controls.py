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

CONTROLS_CSV = BASE / "metamorphic_controls.csv"
FIELDS = ["candidate_id", "control_type", "expected_result", "observed_result",
          "divergence_removed", "notes"]

rows: list[dict] = []

def add(candidate_id, control_type, expected, observed, removed, notes):
    rows.append({
        "candidate_id": candidate_id, "control_type": control_type,
        "expected_result": expected, "observed_result": observed,
        "divergence_removed": removed, "notes": notes,
    })

def controls_httpcore():
    import httpcore
    cid = "rc01_httpcore_Response"

    def mk():
        return httpcore.Response(200, content=[b"alpha", b"beta"])

    def observe_then_read():
        r = mk(); r.read(); return r.content.decode()
    d1, d2 = observe_then_read(), observe_then_read()
    add(cid, "determinism", "identical", f"{d1!r}=={d2!r}", d1 == d2,
        "read()->content is deterministic across repeats")

    r1 = mk(); r1.read()
    r2 = mk()
    try:
        r2.content
        obs = "value"
    except RuntimeError:
        obs = "RuntimeError"
    add(cid, "fresh_object", "RuntimeError (baseline)", obs, obs == "RuntimeError",
        "materializing one response does not affect a fresh response")

    r3 = mk(); _ = list(r3.headers)
    try:
        r3.content
        obs = "value"
    except RuntimeError:
        obs = "RuntimeError"
    add(cid, "pure_observation", "RuntimeError (baseline)", obs, obs == "RuntimeError",
        "reading headers does not materialize content")

def controls_markdown():
    import markdown
    cid = "re01_markdown_Markdown"

    def render_after_refdef(reset):
        md = markdown.Markdown(output_format="html")
        md.convert("[alpha]: https://example.invalid")
        if reset:
            md.reset()
        return md.convert("[alpha][]")

    base = markdown.Markdown(output_format="html").convert("[alpha][]")

    r1 = render_after_refdef(False)
    r2 = render_after_refdef(False)
    add(cid, "determinism", "identical", f"eq={r1==r2}", r1 == r2,
        "reference-carrying render is deterministic")

    r_reset = render_after_refdef(True)
    add(cid, "reset_between", f"baseline {base!r}", r_reset, r_reset == base,
        "reset() restores the no-reference baseline")

    md1 = markdown.Markdown(output_format="html")
    md1.convert("[alpha]: https://example.invalid")
    fresh = markdown.Markdown(output_format="html").convert("[alpha][]")
    add(cid, "fresh_object", f"baseline {base!r}", fresh, fresh == base,
        "a fresh Markdown instance has no references")

def controls_boltons_lru():
    from boltons.cacheutils import LRU
    cid = "re08_boltons_LRU"

    def evict(observe_x, pure):
        c = LRU(max_size=2); c["x"], c["y"] = 1, 2
        if observe_x:
            _ = c["x"]
        if pure:
            _ = len(c)
        c["z"] = 3
        return "x" in c

    d1, d2 = evict(True, False), evict(True, False)
    add(cid, "determinism", "identical", f"{d1}=={d2}", d1 == d2, "eviction deterministic")

    x_live = evict(False, True)
    add(cid, "pure_observation", "x evicted (baseline)", f"x_in_cache={x_live}", x_live is False,
        "len() does not refresh recency; x still evicted")

    c1 = LRU(max_size=2); c1["x"], c1["y"] = 1, 2; _ = c1["x"]
    c2 = LRU(max_size=2); c2["x"], c2["y"] = 1, 2; c2["z"] = 3
    add(cid, "fresh_object", "x evicted (baseline)", f"x_in_cache={'x' in c2}", "x" not in c2,
        "touching one cache does not affect a fresh cache")

def controls_dnspython_tokenizer():
    from dns.tokenizer import Tokenizer
    cid = "re11_dnspython_Tokenizer"

    def read_second(observe):
        t = Tokenizer(io.StringIO("aa bb"))
        if observe:
            t.get()
        return t.get().value

    d1, d2 = read_second(True), read_second(True)
    add(cid, "determinism", "identical", f"{d1!r}=={d2!r}", d1 == d2, "tokenizer deterministic")

    t1 = Tokenizer(io.StringIO("aa bb")); t1.get()
    fresh = Tokenizer(io.StringIO("aa bb")).get().value
    add(cid, "fresh_object", "aa (baseline)", fresh, fresh == "aa",
        "a fresh tokenizer starts at the first token")

def controls_cerberus():
    from cerberus import Validator
    cid = "re10_cerberus_Validator"

    def errors_after(observe):
        v = Validator({"name": {"type": "string", "minlength": 3}})
        if observe:
            v.validate({"name": "Al"})
        return bool(v.errors)

    d1, d2 = errors_after(True), errors_after(True)
    add(cid, "determinism", "identical", f"{d1}=={d2}", d1 == d2, "validation deterministic")

    v1 = Validator({"name": {"type": "string", "minlength": 3}}); v1.validate({"name": "Al"})
    fresh_errors = bool(Validator({"name": {"type": "string", "minlength": 3}}).errors)
    add(cid, "fresh_object", "no errors (baseline)", f"errors={fresh_errors}", fresh_errors is False,
        "a fresh validator has no errors")

def controls_pytest():
    from _pytest.logging import catching_logs
    cid = "rc03_pytest_catching_logs"

    class LH(logging.Handler):
        def __init__(self):
            super().__init__(); self.messages = []

        def emit(self, record):
            self.messages.append(record.getMessage())

    def emit(observe, fresh_emit_handler=False):
        logger = logging.getLogger("review_meta_control_pytest")
        logger.handlers = []; logger.propagate = False; logger.setLevel(logging.DEBUG)
        handler = LH(); handler.setLevel(logging.NOTSET); logger.addHandler(handler)
        if observe:
            cm = catching_logs(handler, level=logging.ERROR); cm.__enter__(); cm.__exit__(None, None, None)
        target_handler = handler
        if fresh_emit_handler:
            logger.handlers = []; target_handler = LH(); target_handler.setLevel(logging.NOTSET)
            logger.addHandler(target_handler)
        logger.warning("warning-visible")
        return bool(target_handler.messages)

    d1, d2 = emit(True), emit(True)
    add(cid, "determinism", "identical", f"{d1}=={d2}", d1 == d2, "suppression deterministic")

    fresh_seen = emit(True, fresh_emit_handler=True)
    add(cid, "fresh_object", "warning visible (baseline)", f"seen={fresh_seen}", fresh_seen is True,
        "a fresh handler is not level-mutated; warning is visible")

def controls_pyyaml():
    from yaml.representer import SafeRepresenter
    cid = "rc02_PyYAML_SafeRepresenter"

    def represent(observe):
        rep = SafeRepresenter(); payload = ["before"]
        if observe:
            rep.represent_data(payload)
        payload[0] = "after"
        return rep.represent_data(payload).value[0].value

    d1, d2 = represent(True), represent(True)
    add(cid, "determinism", "identical", f"{d1!r}=={d2!r}", d1 == d2, "representer deterministic")

    rep1 = SafeRepresenter(); p = ["before"]; rep1.represent_data(p)
    rep2 = SafeRepresenter(); p[0] = "after"
    fresh_val = rep2.represent_data(p).value[0].value
    add(cid, "fresh_object", "after (baseline)", fresh_val, fresh_val == "after",
        "a fresh representer has no identity cache; sees the mutated value")

def controls_h11():
    from h11._receivebuffer import ReceiveBuffer
    from h11._readers import ChunkedReader
    from h11._events import EndOfMessage
    cid = "re12_h11_ChunkedReader"

    def mk():
        buf = ReceiveBuffer(); buf += b"3\r\nabc\r\n0\r\n\r\n"; return buf, ChunkedReader()

    def second_event(observe):
        buf, reader = mk()
        if observe:
            reader(buf)
        return type(reader(buf)).__name__

    d1, d2 = second_event(True), second_event(True)
    add(cid, "determinism", "identical", f"{d1}=={d2}", d1 == d2, "chunk reader deterministic")

    buf1, r1 = mk(); r1(buf1)
    buf2, r2 = mk()
    first = type(r2(buf2)).__name__
    add(cid, "fresh_object", "Data (baseline)", first, first != "EndOfMessage",
        "a fresh buffer yields the first Data event")

def main() -> int:
    F.add_snapshot_paths()
    warnings.simplefilter("ignore")
    for fn in (controls_httpcore, controls_markdown, controls_boltons_lru,
               controls_dnspython_tokenizer, controls_cerberus, controls_pytest,
               controls_pyyaml, controls_h11):
        try:
            fn()
        except Exception as exc:
            add(fn.__name__, "error", "n/a", f"{type(exc).__name__}: {exc}", False,
                "control raised unexpectedly")
    with CONTROLS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    removed = sum(1 for r in rows if r["divergence_removed"] is True)
    print(json.dumps({"controls": len(rows), "divergence_removed_true": removed,
                      "divergence_removed_false": len(rows) - removed}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
