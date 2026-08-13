from __future__ import annotations

import io
import warnings

class CouldNotConstruct(Exception):
    pass

class NotRelevant(Exception):
    pass

class UnsafeToExecute(Exception):
    pass

def h_httpcore_response(F):
    import httpcore

    fx = F.fixture_http_response()
    return {
        "builder": fx.builder,
        "observation": lambda r: r.read(),
        "target": lambda r: r.content.decode(),
        "state": fx.snapshot,
        "obs_label": "response.read()",
        "read_label": "response.content",
    }

def h_pyyaml_representer(F):
    import yaml
    from yaml.representer import SafeRepresenter

    def custom():
        rep_a = SafeRepresenter()
        payload = ["before"]
        payload[0] = "after"
        node_a = rep_a.represent_data(payload)
        state_a = {"represented_objects": len(rep_a.represented_objects),
                   "object_keeper": len(rep_a.object_keeper)}
        rep_b = SafeRepresenter()
        payload_b = ["before"]
        first = rep_b.represent_data(payload_b)
        payload_b[0] = "after"
        node_b = rep_b.represent_data(payload_b)
        same = node_b is first
        state_b = {"represented_objects": len(rep_b.represented_objects),
                   "object_keeper": len(rep_b.object_keeper), "same_node_returned": same}
        order_A = {
            "steps": ["SafeRepresenter()", "payload[0]='after'", "represent_data(payload)"],
            "output": _node_payload(node_a),
            "exception": None,
            "state": state_a,
        }
        order_B = {
            "steps": ["SafeRepresenter()", "represent_data(payload)", "payload[0]='after'",
                      "represent_data(payload)"],
            "output": _node_payload(node_b),
            "exception": None,
            "state": state_b,
        }
        return {"order_A": order_A, "order_B": order_B}

    return {"custom": custom}

def _node_payload(node):
    try:
        return str([(getattr(v, "tag", None), getattr(v, "value", None)) for v in node.value])
    except Exception:
        return repr(node)

def h_pytest_catching_logs(F):
    import logging
    from _pytest.logging import catching_logs

    class ListHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record.getMessage())

    def emit_and_capture(observe):
        logger = logging.getLogger("scp_meta_pytest_case")
        logger.handlers = []
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        handler = ListHandler()
        handler.setLevel(logging.NOTSET)
        logger.addHandler(handler)
        if observe:
            cm = catching_logs(handler, level=logging.ERROR)
            cm.__enter__()
            cm.__exit__(None, None, None)
        logger.warning("warning-visible")
        messages = list(handler.messages)
        return {"messages": messages, "handler_level": handler.level, "observed": observe}

    def custom():
        a = emit_and_capture(False)
        b = emit_and_capture(True)
        return {
            "order_A": {"steps": ["fresh handler", "emit WARNING", "read messages"],
                        "output": a["messages"], "exception": None,
                        "state": {"handler_level": a["handler_level"]}},
            "order_B": {"steps": ["fresh handler", "enter/exit catching_logs(level=ERROR)",
                                  "emit WARNING", "read messages"],
                        "output": b["messages"], "exception": None,
                        "state": {"handler_level": b["handler_level"]}},
        }

    return {"custom": custom}

def h_rich_richhandler(F):
    import rich
    from rich.logging import RichHandler

    def spec_builder():
        return RichHandler()

    return {
        "builder": spec_builder,
        "observation": lambda h: h.render_message.__self__ and None,
        "target": lambda h: getattr(h.highlighter, "highlights", None),
        "state": lambda h: {"keywords": getattr(h, "keywords", None)},
        "obs_label": "render_message()",
        "read_label": "handler.keywords",
    }

def h_markdown(F):
    import markdown

    return {
        "builder": lambda: markdown.Markdown(output_format="html"),
        "observation": lambda m: m.convert("[alpha]: https://example.invalid"),
        "target": lambda m: m.convert("[alpha][]"),
        "state": lambda m: {"references": dict(m.references)},
        "obs_label": "convert('[alpha]: https://example.invalid')",
        "read_label": "convert('[alpha][]')",
    }

def h_more_itertools_seekable(F):
    from more_itertools import seekable

    return {
        "pair_type": "pair3",
        "builder": lambda: seekable(iter(["a", "b", "c"])),
        "observation": lambda it: next(it),
        "target": lambda it: next(it),
        "state": lambda it: {"elements": list(it.elements())},
        "obs_label": "next(it)",
        "read_label": "next(it)",
    }

def h_pygments_escape(F):
    from pygments.formatters.terminal256 import EscapeSequence

    return {
        "builder": lambda: EscapeSequence(fg="ansired"),
        "observation": lambda e: e.color_string(),
        "target": lambda e: e.reset_string(),
        "state": lambda e: dict(e.__dict__),
        "obs_label": "color_string()",
        "read_label": "reset_string()",
    }

def h_docutils_transformer(F):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from docutils.frontend import OptionParser
    from docutils.transforms import Transform, Transformer
    from docutils.utils import new_document

    class T10(Transform):
        default_priority = 10

        def apply(self):
            pass

    class T5(Transform):
        default_priority = 5

        def apply(self):
            pass

    def make():
        settings = OptionParser(components=()).get_default_values()
        document = new_document("<meta>", settings=settings)
        tr = Transformer(document)
        tr.add_transform(T10)
        tr.add_transform(T5)
        return tr

    return {
        "builder": make,
        "observation": lambda tr: tr.get_priority_string(10),
        "target": lambda tr: [t[0] for t in tr.transforms],
        "state": lambda tr: {"serialno": tr.serialno, "sorted": tr.sorted},
        "obs_label": "get_priority_string(10)",
        "read_label": "inspect transform priority queue",
    }

def h_soupsieve_cssmatch(F):
    import soupsieve as sv
    from bs4 import BeautifulSoup
    from soupsieve.css_match import CSSMatch

    def make():
        soup = BeautifulSoup("<div><p class='a'>x</p><p>y</p></div>", "html.parser")
        selectors = sv.compile("p.a").selectors
        return CSSMatch(selectors, soup, None, 0)

    return {
        "builder": make,
        "observation": lambda m: m.match(m.tag.find("p")),
        "target": lambda m: [str(t) for t in m.select()],
        "state": lambda m: {"cached_meta_lang": m.cached_meta_lang},
        "obs_label": "match(first p)",
        "read_label": "list(select())",
    }

def h_bs4_pageelement(F):
    from bs4 import BeautifulSoup

    return {
        "builder": lambda: BeautifulSoup("<p>a</p><p>b</p>", "html.parser"),
        "observation": lambda s: str(s.find_all("p")[0].extract()),
        "target": lambda s: str(s),
        "state": lambda s: {"p_count": len(s.find_all("p"))},
        "obs_label": "first <p>.extract()",
        "read_label": "str(soup)",
    }

def h_boltons_lri(F):
    fx = F.fixture_cache(kind="LRI")

    def make():
        return fx.builder()

    return {
        "builder": make,
        "observation": lambda c: c["a"],
        "target": lambda c: (_cache_insert(c, "c", "C"), list(c.items()))[1],
        "state": lambda c: {"hit_count": c.hit_count, "miss_count": c.miss_count},
        "obs_label": "__getitem__('a')",
        "read_label": "insert c; then items()",
    }

def h_boltons_lru(F):
    fx = F.fixture_cache(kind="LRU")

    return {
        "builder": fx.builder,
        "observation": lambda c: c["a"],
        "target": lambda c: (_cache_insert(c, "c", "C"), list(c.items()))[1],
        "state": lambda c: {"hit_count": c.hit_count, "miss_count": c.miss_count},
        "obs_label": "__getitem__('a')",
        "read_label": "insert c; then items()",
    }

def _cache_insert(cache, k, v):
    cache[k] = v
    return None

def h_boltons_multifilereader(F):
    from boltons.ioutils import MultiFileReader

    return {
        "pair_type": "pair3",
        "builder": lambda: MultiFileReader(io.BytesIO(b"ab"), io.BytesIO(b"cd"), io.BytesIO(b"e")),
        "observation": lambda r: r.read(3),
        "target": lambda r: r.read(3),
        "state": lambda r: {"index": r._index},
        "obs_label": "read(3)",
        "read_label": "read(3)",
    }

def h_boltons_spooledstringio(F):
    from boltons.ioutils import SpooledStringIO

    def make():
        s = SpooledStringIO()
        s.write("alpha beta")
        s.seek(0)
        return s

    return {
        "pair_type": "pair3",
        "builder": make,
        "observation": lambda s: s.read(3),
        "target": lambda s: s.read(3),
        "state": lambda s: {"tell": s.tell()},
        "obs_label": "read(3)",
        "read_label": "read(3)",
    }

def h_boltons_spooledbytesio(F):
    from boltons.ioutils import SpooledBytesIO

    def make():
        s = SpooledBytesIO()
        s.write(b"alphabeta")
        s.seek(0)
        return s

    return {
        "pair_type": "pair3",
        "builder": make,
        "observation": lambda s: s.read(3),
        "target": lambda s: s.read(3),
        "state": lambda s: {"tell": s.tell()},
        "obs_label": "read(3)",
        "read_label": "read(3)",
    }

def h_cerberus_validator(F):
    from cerberus import Validator

    schema = {"name": {"type": "string", "minlength": 3}}
    return {
        "builder": lambda: Validator(schema),
        "observation": lambda v: v.validate({"name": "Al"}),
        "target": lambda v: dict(v.errors),
        "state": lambda v: {"document": v.document},
        "obs_label": "validate({'name': 'Al'})",
        "read_label": "validator.errors",
    }

def h_dnspython_tokenizer(F):
    from dns.tokenizer import Tokenizer

    return {
        "builder": lambda: Tokenizer(io.StringIO("alpha beta\n")),
        "observation": lambda t: t.get().value,
        "target": lambda t: t.get_string(),
        "state": lambda t: {"eof": t.eof},
        "obs_label": "get()",
        "read_label": "get_string()",
    }

def h_dnspython_btree(F):
    from dns.btree import BTree, KV

    def make():
        tree = BTree()
        tree.insert_element(KV("a", "A"))
        tree.insert_element(KV("b", "B"))
        return tree

    return {
        "builder": make,
        "observation": lambda t: t.get_element("a"),
        "target": lambda t: t.get_element("b"),
        "state": lambda t: {"size": t.size, "cursors": len(t.cursors)},
        "obs_label": "get_element('a')",
        "read_label": "get_element('b')",
    }

def h_h11_chunkedreader(F):
    from h11._receivebuffer import ReceiveBuffer
    from h11._readers import ChunkedReader

    def make():
        buf = ReceiveBuffer()
        buf += b"3\r\nabc\r\n0\r\n\r\n"
        return {"buf": buf, "reader": ChunkedReader()}

    return {
        "pair_type": "pair3",
        "builder": make,
        "observation": lambda d: repr(d["reader"](d["buf"])),
        "target": lambda d: repr(d["reader"](d["buf"])),
        "state": lambda d: {"buffer": bytes(d["buf"])},
        "obs_label": "ChunkedReader()(buffer)",
        "read_label": "ChunkedReader()(buffer)",
    }

def h_h11_receivebuffer(F):
    from h11._receivebuffer import ReceiveBuffer

    def make():
        buf = ReceiveBuffer()
        buf += b"GET / HTTP/1.1\r\nHost: x\r\n\r\nBODY"
        return buf

    def obs(buf):
        line = buf.maybe_extract_next_line()
        return bytes(line) if line else None

    def target(buf):
        lines = buf.maybe_extract_lines()
        return [bytes(x) for x in lines] if lines is not None else None

    return {
        "builder": make,
        "observation": obs,
        "target": target,
        "state": lambda b: {"buffer": bytes(b)},
        "obs_label": "maybe_extract_next_line()",
        "read_label": "maybe_extract_lines()",
    }

def h_click_optgroup(F):
    import click
    from click.testing import CliRunner
    from click_option_group import optgroup

    def build(observe):
        def callback(**kwargs):
            click.echo(str(kwargs))

        group = optgroup.group("Group")
        if observe:
            _ = repr(group(callback))
        command = click.command()(optgroup.option("--foo")(group(callback)))
        inv = CliRunner().invoke(command, ["--foo", "x"])
        return {"params": [p.name for p in command.params], "exit_code": inv.exit_code,
                "output": inv.output.strip()}

    def custom():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            a = build(False)
            b = build(True)
        return {
            "order_A": {"steps": ["build grouped command", "invoke --foo x"], "output": a,
                        "exception": None, "state": {}},
            "order_B": {"steps": ["call group decorator (observe)", "build command",
                                  "invoke --foo x"], "output": b, "exception": None, "state": {}},
        }

    return {"custom": custom}

def h_more_itertools_peekable(F):
    from more_itertools import peekable

    return {
        "builder": lambda: peekable(iter(["x", "y", "z"])),
        "observation": lambda it: it.peek(),
        "target": lambda it: next(it),
        "state": lambda it: {"has_cache": bool(getattr(it, "_cache", None))},
        "obs_label": "peek()",
        "read_label": "next(it)",
    }

def h_anyio_blockingportalprovider(F):
    from anyio.from_thread import BlockingPortalProvider

    def make():
        return BlockingPortalProvider()

    return {
        "builder": make,
        "observation": lambda p: p.__enter__() and None,
        "target": lambda p: {"leases": getattr(p, "_leases", None)},
        "state": lambda p: {"leases": getattr(p, "_leases", None)},
        "obs_label": "__enter__()",
        "read_label": "read _leases",
    }

def h_anyio_cancelscope(F):
    from anyio import CancelScope

    return {
        "builder": lambda: CancelScope(),
        "observation": lambda s: None,
        "target": lambda s: {"cancel_called": s.cancel_called},
        "state": lambda s: {"cancel_called": s.cancel_called},
        "obs_label": "no-op observation",
        "read_label": "read cancel_called",
    }

def h_docutils_publisher(F):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from docutils.core import Publisher

    return {
        "builder": lambda: Publisher(),
        "observation": lambda p: p.get_settings(),
        "target": lambda p: {"has_settings": p.settings is not None},
        "state": lambda p: {"has_settings": p.settings is not None},
        "obs_label": "get_settings()",
        "read_label": "read .settings",
    }

def h_docutils_viewlist(F):
    from docutils.statemachine import ViewList

    return {
        "builder": lambda: ViewList(["a", "b"], source="<meta>"),
        "observation": lambda v: len(v),
        "target": lambda v: list(v),
        "state": lambda v: {"len": len(v)},
        "obs_label": "len(view)",
        "read_label": "list(view)",
    }

def h_docutils_reader(F):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from docutils.readers import Reader

    return {
        "builder": lambda: Reader(),
        "observation": lambda r: None,
        "target": lambda r: {"has_parser": getattr(r, "parser", None) is not None},
        "state": lambda r: {"has_parser": getattr(r, "parser", None) is not None},
        "obs_label": "no-op observation",
        "read_label": "read .parser",
    }

def h_tomlkit_parser(F):
    import tomlkit

    return {
        "builder": lambda: tomlkit.parse("a = 1\nb = 2\n"),
        "observation": lambda d: d["a"],
        "target": lambda d: dict(d),
        "state": lambda d: {"keys": list(d.keys())},
        "obs_label": "doc['a']",
        "read_label": "dict(doc)",
    }

def h_marshmallow_schema(F):
    from marshmallow import Schema, fields

    class S(Schema):
        name = fields.String(required=True)

    return {
        "builder": lambda: S(),
        "observation": lambda s: s.load({"name": "ok"}),
        "target": lambda s: s.dump({"name": "again"}),
        "state": lambda s: {"declared": sorted(s.fields.keys())},
        "obs_label": "load({'name':'ok'})",
        "read_label": "dump({'name':'again'})",
    }

def h_mistune_markdown(F):
    import mistune

    def custom():
        md_a = mistune.create_markdown()
        out_a = md_a("[a][]")
        md_b = mistune.create_markdown()
        _obs = md_b("[a]: https://example.invalid\n")
        out_b = md_b("[a][]")
        return {
            "order_A": {"steps": ["create_markdown()", "render('[a][]')"],
                        "output": out_a.strip(), "exception": None, "state": {}},
            "order_B": {"steps": ["create_markdown()", "render ref-def", "render('[a][]')"],
                        "output": out_b.strip(), "exception": None, "state": {}},
        }

    return {"custom": custom}

def h_more_itertools_spy(F):
    from more_itertools import spy

    def custom():
        it_a = iter(["p", "q", "r"])
        head_a, rest_a = spy(it_a, 2)
        out_a = list(rest_a)
        it_b = iter(["p", "q", "r"])
        head_b, rest_b = spy(it_b, 2)
        _obs = list(head_b)
        out_b = list(rest_b)
        return {
            "order_A": {"steps": ["spy(it,2)", "list(rest)"], "output": out_a,
                        "exception": None, "state": {"head": list(head_a)}},
            "order_B": {"steps": ["spy(it,2)", "list(head) [observe]", "list(rest)"],
                        "output": out_b, "exception": None, "state": {"head": list(head_b)}},
        }

    return {"custom": custom}

def h_dnspython_tokenizer_concat(F):
    from dns.tokenizer import Tokenizer

    def custom():
        tok_a = Tokenizer(io.StringIO("aa bb cc"))
        out_a = tok_a.concatenate_remaining_identifiers()
        tok_b = Tokenizer(io.StringIO("aa bb cc"))
        _obs = tok_b.get().value
        out_b = tok_b.concatenate_remaining_identifiers()
        return {
            "order_A": {"steps": ["Tokenizer('aa bb cc')", "concatenate_remaining_identifiers()"],
                        "output": str(out_a), "exception": None, "state": {"eof": tok_a.eof}},
            "order_B": {"steps": ["Tokenizer('aa bb cc')", "get() [observe]",
                                  "concatenate_remaining_identifiers()"],
                        "output": str(out_b), "exception": None, "state": {"eof": tok_b.eof}},
        }

    return {"custom": custom}

def h_boltons_lru_pair2(F):
    from boltons.cacheutils import LRU

    def custom():
        a = LRU(max_size=2)
        a["x"], a["y"] = 1, 2
        first_a = list(a.items())
        a["z"] = 3
        second_a = list(a.items())
        b = LRU(max_size=2)
        b["x"], b["y"] = 1, 2
        first_b = list(b.items())
        _obs = b["x"]
        b["z"] = 3
        second_b = list(b.items())
        return {
            "order_A": {"steps": ["LRU x,y", "items()", "insert z", "items()"],
                        "output": [list(t) for t in second_a], "exception": None,
                        "state": {"first": [list(t) for t in first_a]}},
            "order_B": {"steps": ["LRU x,y", "items()", "get('x') [observe]", "insert z",
                                  "items()"],
                        "output": [list(t) for t in second_b], "exception": None,
                        "state": {"first": [list(t) for t in first_b]}},
        }

    return {"custom": custom}

def make_directive_attempt(module_path, cls_name):
    def h(F):
        mod = __import__(module_path, fromlist=[cls_name])
        cls = getattr(mod, cls_name)

        def custom():
            try:
                obj = cls()
                return {"order_A": {"steps": [f"{cls_name}()"], "output": repr(obj),
                                    "exception": None, "state": {}},
                        "order_B": {"steps": [f"{cls_name}()"], "output": repr(obj),
                                    "exception": None, "state": {}}}
            except TypeError as exc:
                raise CouldNotConstruct(
                    f"{cls_name} requires state-machine constructor args: {exc}") from exc

        return {"custom": custom}

    return h

def make_generic_attempt(module_path, cls_name, ctor_args=(), ctor_kwargs=None,
                         obs_method=None, read_method=None, read_args=()):
    ctor_kwargs = ctor_kwargs or {}

    def h(F):
        mod = __import__(module_path, fromlist=[cls_name])
        cls = getattr(mod, cls_name)

        def builder():
            try:
                return cls(*ctor_args, **ctor_kwargs)
            except TypeError as exc:
                raise CouldNotConstruct(
                    f"{cls_name} construction requires args: {exc}") from exc

        def observation(obj):
            if obs_method and hasattr(obj, obs_method):
                return getattr(obj, obs_method)()
            return None

        def target(obj):
            if read_method and hasattr(obj, read_method):
                return F.snapshot(getattr(obj, read_method)(*read_args))
            return repr(type(obj).__name__)

        return {
            "builder": builder,
            "observation": observation,
            "target": target,
            "state": lambda o: {"repr": repr(type(o).__name__)},
            "obs_label": obs_method or "(no-op)",
            "read_label": read_method or "repr(class)",
        }

    return h

def h_docutils_stringoutput_unsafe(F):
    def custom():
        raise UnsafeToExecute(
            "StringOutput.write() performs output side effects; excluded from execution "
            "per safety policy (matches behavioral sweep 'unsafe_to_execute').")

    return {"custom": custom}

def h_dnspython_message_notrelevant(F):
    def custom():
        raise NotRelevant(
            "dns.message.Message fresh instances are not order-comparable (random id / "
            "distinct object identity); no observation/read boundary to test.")

    return {"custom": custom}

def h_dnspython_entropypool_notrelevant(F):
    def custom():
        raise NotRelevant(
            "EntropyPool methods are intentionally nondeterministic (randomness); an "
            "order-dependence oracle does not apply.")

    return {"custom": custom}

def _c(**kw):
    kw.setdefault("pair_type", "pair1")
    kw.setdefault("selected_for_harness", "yes")
    kw.setdefault("harness", None)
    return kw

_DIRECTIVE_FAMILY = [
    ("Body", "docutils.parsers.rst.states"),
    ("BulletList", "docutils.parsers.rst.states"),
    ("Definition", "docutils.parsers.rst.states"),
    ("EnumeratedList", "docutils.parsers.rst.states"),
    ("Explicit", "docutils.parsers.rst.states"),
    ("FieldList", "docutils.parsers.rst.states"),
    ("Line", "docutils.parsers.rst.states"),
    ("LineBlock", "docutils.parsers.rst.states"),
    ("OptionList", "docutils.parsers.rst.states"),
    ("RFC2822Body", "docutils.parsers.rst.states"),
    ("RFC2822List", "docutils.parsers.rst.states"),
    ("Text", "docutils.parsers.rst.states"),
    ("Include", "docutils.parsers.rst.directives.misc"),
]

CANDIDATES = [
    _c(candidate_id="rc01_httpcore_Response", source_artifact="real_case_results.csv",
       package_name="httpcore", package_version="1.0.9", module_path="httpcore/_models.py",
       class_name="Response", observation_operation="response.read()",
       target_read_operation="response.content", state_fields_suspected="_content;_stream_consumed",
       construction_hint="httpcore.Response(200, content=[b'alpha', b'beta'])",
       fixture_family="http_response",
       expected_boundary="read() materializes _content; content flips RuntimeError->value",
       priority="1", harness=h_httpcore_response),
    _c(candidate_id="rc02_PyYAML_SafeRepresenter", source_artifact="real_case_results.csv",
       package_name="PyYAML", package_version="6.0.3", module_path="yaml/representer.py",
       class_name="SafeRepresenter", observation_operation="represent_data(list) first",
       target_read_operation="represent_data(list)", state_fields_suspected="represented_objects;object_keeper",
       construction_hint="SafeRepresenter(); mutable list payload",
       fixture_family="yaml_or_repr",
       expected_boundary="identity cache returns stale node for mutated object",
       priority="1", harness=h_pyyaml_representer),
    _c(candidate_id="rc03_pytest_catching_logs", source_artifact="real_case_results.csv",
       package_name="pytest", package_version="8.3.5", module_path="_pytest/logging.py",
       class_name="catching_logs", observation_operation="enter/exit catching_logs(level=ERROR)",
       target_read_operation="emit WARNING; read messages", state_fields_suspected="handler.level",
       construction_hint="LogCaptureHandler + logging.getLogger",
       fixture_family="logging_handler",
       expected_boundary="handler level mutation filters later WARNING",
       priority="1", harness=h_pytest_catching_logs),
    _c(candidate_id="rc04_rich_RichHandler", source_artifact="real_case_results.csv",
       package_name="rich", package_version="15.0.0", module_path="rich/logging.py",
       class_name="RichHandler", observation_operation="render_message()",
       target_read_operation="handler.keywords", state_fields_suspected="keywords",
       construction_hint="RichHandler() (rich NOT available -> import_failed)",
       fixture_family="logging_handler",
       expected_boundary="first render initializes keyword highlighter",
       priority="1", harness=h_rich_richhandler),

    _c(candidate_id="re01_markdown_Markdown", source_artifact="rescue_results.csv",
       package_name="markdown", package_version="3.10.2", module_path="markdown/core.py",
       class_name="Markdown", observation_operation="convert link-def first",
       target_read_operation="convert('[alpha][]')", state_fields_suspected="references",
       construction_hint="Markdown(output_format='html')", fixture_family="string_text",
       expected_boundary="reference registry from prior convert changes later render",
       priority="1", harness=h_markdown),
    _c(candidate_id="re02_more_itertools_seekable", source_artifact="rescue_results.csv",
       package_name="more-itertools", package_version="11.0.2", module_path="more_itertools/more.py",
       class_name="seekable", observation_operation="next(it)", target_read_operation="next(it)",
       state_fields_suspected="_index;_cache", construction_hint="seekable(iter(['a','b','c']))",
       fixture_family="iterator", expected_boundary="cursor advance changes later next()",
       priority="1", harness=h_more_itertools_seekable),
    _c(candidate_id="re03_pygments_EscapeSequence", source_artifact="rescue_results.csv",
       package_name="pygments", package_version="2.20.0",
       module_path="pygments/formatters/terminal256.py", class_name="EscapeSequence",
       observation_operation="color_string()", target_read_operation="reset_string()",
       state_fields_suspected="fg;bg;bold", construction_hint="EscapeSequence(fg='ansired')",
       fixture_family="yaml_or_repr", expected_boundary="suspected bold mutation (not triggered)",
       priority="2", harness=h_pygments_escape),
    _c(candidate_id="re04_docutils_Transformer", source_artifact="rescue_results.csv",
       package_name="docutils", package_version="0.22.4",
       module_path="docutils/transforms/__init__.py", class_name="Transformer",
       observation_operation="get_priority_string(10)",
       target_read_operation="inspect transform priority queue",
       state_fields_suspected="serialno;sorted", construction_hint="new_document + 2 Transforms",
       fixture_family="unknown", expected_boundary="serial bookkeeping advances on priority string",
       priority="2", harness=h_docutils_transformer),
    _c(candidate_id="re05_soupsieve_CSSMatch", source_artifact="rescue_results.csv",
       package_name="soupsieve", package_version="2.8.3", module_path="soupsieve/css_match.py",
       class_name="CSSMatch", observation_operation="match(first p)",
       target_read_operation="list(select())", state_fields_suspected="cached_meta_lang",
       construction_hint="bs4 tree + compiled 'p.a'", fixture_family="tree_or_html",
       expected_boundary="selector caches (not triggered by simple selector)",
       priority="2", harness=h_soupsieve_cssmatch),
    _c(candidate_id="re06_beautifulsoup4_PageElement", source_artifact="rescue_results.csv",
       package_name="beautifulsoup4", package_version="4.14.3", module_path="bs4/element.py",
       class_name="PageElement", observation_operation="first <p>.extract()",
       target_read_operation="str(soup)", state_fields_suspected="tree children",
       construction_hint="BeautifulSoup('<p>a</p><p>b</p>')", fixture_family="tree_or_html",
       expected_boundary="extract() destructively mutates tree",
       priority="1", harness=h_bs4_pageelement),
    _c(candidate_id="re07_boltons_LRI", source_artifact="rescue_results.csv",
       package_name="boltons", package_version="25.0.0", module_path="boltons/cacheutils.py",
       class_name="LRI", observation_operation="__getitem__('a')",
       target_read_operation="insert c; then items()", state_fields_suspected="hit_count;miss_count",
       construction_hint="LRI(max_size=2)", fixture_family="cache",
       expected_boundary="access affects stats but not eviction order",
       priority="2", harness=h_boltons_lri),
    _c(candidate_id="re08_boltons_LRU", source_artifact="rescue_results.csv",
       package_name="boltons", package_version="25.0.0", module_path="boltons/cacheutils.py",
       class_name="LRU", observation_operation="__getitem__('a')",
       target_read_operation="insert c; then items()", state_fields_suspected="recency order",
       construction_hint="LRU(max_size=2)", fixture_family="cache",
       expected_boundary="access reorders recency -> changes eviction",
       priority="1", harness=h_boltons_lru),
    _c(candidate_id="re09_boltons_MultiFileReader", source_artifact="rescue_results.csv",
       package_name="boltons", package_version="25.0.0", module_path="boltons/ioutils.py",
       class_name="MultiFileReader", observation_operation="read(3)", target_read_operation="read(3)",
       state_fields_suspected="_index", construction_hint="MultiFileReader(BytesIO x3)",
       fixture_family="io_bytes", expected_boundary="stream cursor advances",
       priority="1", harness=h_boltons_multifilereader),
    _c(candidate_id="re10_cerberus_Validator", source_artifact="rescue_results.csv",
       package_name="cerberus", package_version="1.3.8", module_path="cerberus/validator.py",
       class_name="BareValidator", observation_operation="validate({'name':'Al'})",
       target_read_operation="validator.errors", state_fields_suspected="document;_errors",
       construction_hint="Validator(schema)", fixture_family="list_or_dict",
       expected_boundary="validate populates errors read later",
       priority="1", harness=h_cerberus_validator),
    _c(candidate_id="re11_dnspython_Tokenizer", source_artifact="rescue_results.csv",
       package_name="dnspython", package_version="2.8.0", module_path="dns/tokenizer.py",
       class_name="Tokenizer", observation_operation="get()", target_read_operation="get_string()",
       state_fields_suspected="current;eof", construction_hint="Tokenizer(StringIO('alpha beta'))",
       fixture_family="parser_tokenizer", expected_boundary="token consumption advances cursor",
       priority="1", harness=h_dnspython_tokenizer),
    _c(candidate_id="re12_h11_ChunkedReader", source_artifact="rescue_results.csv",
       package_name="h11", package_version="0.16.0", module_path="h11/_readers.py",
       class_name="ChunkedReader", observation_operation="ChunkedReader()(buffer)",
       target_read_operation="ChunkedReader()(buffer)", state_fields_suspected="buffer;bytes_to_discard",
       construction_hint="ReceiveBuffer chunked body", fixture_family="buffer",
       expected_boundary="Data vs EndOfMessage after consuming chunk",
       priority="1", harness=h_h11_chunkedreader),
    _c(candidate_id="re13_h11_ReceiveBuffer", source_artifact="rescue_results.csv",
       package_name="h11", package_version="0.16.0", module_path="h11/_receivebuffer.py",
       class_name="ReceiveBuffer", observation_operation="maybe_extract_next_line()",
       target_read_operation="maybe_extract_lines()", state_fields_suspected="data;next_line_search",
       construction_hint="ReceiveBuffer(header bytes)", fixture_family="buffer",
       expected_boundary="line extraction is destructive",
       priority="1", harness=h_h11_receivebuffer),
    _c(candidate_id="re14_dnspython_BTree", source_artifact="rescue_results.csv",
       package_name="dnspython", package_version="2.8.0", module_path="dns/btree.py",
       class_name="BTree", observation_operation="get_element('a')",
       target_read_operation="get_element('b')", state_fields_suspected="cursors;size",
       construction_hint="BTree + KV a,b", fixture_family="unknown",
       expected_boundary="lookup stable under minimal fixture", priority="3", harness=h_dnspython_btree),
    _c(candidate_id="re15_click_option_group_OptGroup", source_artifact="rescue_results.csv",
       package_name="click-option-group", package_version="0.5.9",
       module_path="src/click_option_group/_decorators.py", class_name="_OptGroup",
       observation_operation="call group decorator", target_read_operation="build+invoke command",
       state_fields_suspected="decorators registry", construction_hint="optgroup + CliRunner",
       fixture_family="unknown", expected_boundary="in-process decorator, no runtime divergence",
       priority="3", harness=h_click_optgroup),

    _c(candidate_id="bs09_anyio_BlockingPortalProvider", source_artifact="behavioral_sweep_results.csv",
       package_name="anyio", package_version="4.13.0", module_path="anyio/from_thread.py",
       class_name="BlockingPortalProvider", observation_operation="__enter__()",
       target_read_operation="read _leases", state_fields_suspected="_leases;_portal",
       construction_hint="BlockingPortalProvider()", fixture_family="unknown",
       expected_boundary="enter mutates lease counter (state-only)", priority="2",
       harness=h_anyio_blockingportalprovider),
    _c(candidate_id="bs06_anyio_CancelScope", source_artifact="behavioral_sweep_results.csv",
       package_name="anyio", package_version="4.13.0", module_path="anyio/_core/_tasks.py",
       class_name="CancelScope", observation_operation="no-op observation",
       target_read_operation="read cancel_called", state_fields_suspected="cancel_called",
       construction_hint="CancelScope()", fixture_family="unknown",
       expected_boundary="no observation boundary at construction", priority="3",
       harness=h_anyio_cancelscope),
    _c(candidate_id="bs15_boltons_SpooledStringIO", source_artifact="behavioral_sweep_results.csv",
       package_name="boltons", package_version="25.0.0", module_path="boltons/ioutils.py",
       class_name="SpooledStringIO", observation_operation="read(3)", target_read_operation="read(3)",
       state_fields_suspected="buffer position", construction_hint="SpooledStringIO()+write",
       fixture_family="io_bytes", expected_boundary="text cursor advances", priority="2",
       harness=h_boltons_spooledstringio),
    _c(candidate_id="bs23_docutils_Publisher", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/core.py",
       class_name="Publisher", observation_operation="get_settings()",
       target_read_operation="read .settings", state_fields_suspected="settings",
       construction_hint="Publisher()", fixture_family="unknown",
       expected_boundary="get_settings caches settings (state-only)", priority="2",
       harness=h_docutils_publisher),
    _c(candidate_id="bs44_docutils_ViewList", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/statemachine.py",
       class_name="ViewList", observation_operation="len(view)", target_read_operation="list(view)",
       state_fields_suspected="data;items", construction_hint="ViewList(['a','b'])",
       fixture_family="list_or_dict", expected_boundary="pure read, no divergence expected",
       priority="3", harness=h_docutils_viewlist),
    _c(candidate_id="bs43_docutils_Reader", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/readers/__init__.py",
       class_name="Reader", observation_operation="no-op observation",
       target_read_operation="read .parser", state_fields_suspected="parser;source",
       construction_hint="Reader()", fixture_family="unknown",
       expected_boundary="no construction-time boundary", priority="3", harness=h_docutils_reader),
    _c(candidate_id="bs26_docutils_StringOutput", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/io.py",
       class_name="StringOutput", observation_operation="(excluded)",
       target_read_operation="write()", state_fields_suspected="destination",
       construction_hint="write() has output side effects", fixture_family="unknown",
       expected_boundary="unsafe to execute (output side effect)", priority="3",
       harness=h_docutils_stringoutput_unsafe),
    _c(candidate_id="bs20_dnspython_Message", source_artifact="behavioral_sweep_results.csv",
       package_name="dnspython", package_version="2.8.0", module_path="dns/message.py",
       class_name="Message", observation_operation="(n/a)", target_read_operation="(n/a)",
       state_fields_suspected="id", construction_hint="fresh instances not comparable",
       fixture_family="unknown", expected_boundary="random id -> not order-comparable",
       priority="3", harness=h_dnspython_message_notrelevant),
    _c(candidate_id="bs19_dnspython_EntropyPool", source_artifact="behavioral_sweep_results.csv",
       package_name="dnspython", package_version="2.8.0", module_path="dns/entropy.py",
       class_name="EntropyPool", observation_operation="(n/a)", target_read_operation="(n/a)",
       state_fields_suspected="pool", construction_hint="intentionally nondeterministic",
       fixture_family="unknown", expected_boundary="randomness -> oracle N/A",
       priority="3", harness=h_dnspython_entropypool_notrelevant),

    _c(candidate_id="ext01_more_itertools_peekable", source_artifact="source_snapshot",
       package_name="more-itertools", package_version="11.0.2", module_path="more_itertools/more.py",
       class_name="peekable", observation_operation="peek()", target_read_operation="next(it)",
       state_fields_suspected="_cache", construction_hint="peekable(iter(['x','y','z']))",
       fixture_family="iterator", expected_boundary="peek caches but next still consumes head",
       priority="2", harness=h_more_itertools_peekable),
    _c(candidate_id="ext02_boltons_SpooledBytesIO", source_artifact="source_snapshot",
       package_name="boltons", package_version="25.0.0", module_path="boltons/ioutils.py",
       class_name="SpooledBytesIO", observation_operation="read(3)", target_read_operation="read(3)",
       state_fields_suspected="buffer position", construction_hint="SpooledBytesIO()+write",
       fixture_family="io_bytes", expected_boundary="byte cursor advances", priority="2",
       harness=h_boltons_spooledbytesio),
    _c(candidate_id="ext03_tomlkit_TOMLDocument", source_artifact="source_snapshot",
       package_name="tomlkit", package_version="0.15.0", module_path="tomlkit/container.py",
       class_name="TOMLDocument", observation_operation="doc['a']", target_read_operation="dict(doc)",
       state_fields_suspected="_body", construction_hint="tomlkit.parse('a=1 b=2')",
       fixture_family="list_or_dict", expected_boundary="pure read, no divergence expected",
       priority="3", harness=h_tomlkit_parser),
    _c(candidate_id="ext04_marshmallow_Schema", source_artifact="source_snapshot",
       package_name="marshmallow", package_version="4.3.0", module_path="marshmallow/schema.py",
       class_name="Schema", observation_operation="load({'name':'ok'})",
       target_read_operation="dump({'name':'again'})", state_fields_suspected="fields cache",
       construction_hint="Schema subclass with String field", fixture_family="list_or_dict",
       expected_boundary="load/dump share no order-dependent state", priority="3",
       harness=h_marshmallow_schema),

    _c(candidate_id="bs07_anyio_Runner", source_artifact="behavioral_sweep_results.csv",
       package_name="anyio", package_version="4.13.0", module_path="anyio/_backends/_asyncio.py",
       class_name="Runner", observation_operation="run", target_read_operation="repr(class)",
       state_fields_suspected="_loop;_task", construction_hint="Runner() (may require args)",
       fixture_family="unknown", expected_boundary="event-loop runner; construction likely fails",
       priority="3", harness=make_generic_attempt("anyio._backends._asyncio", "Runner")),
    _c(candidate_id="bs08_anyio_ContextManagerMixin", source_artifact="behavioral_sweep_results.csv",
       package_name="anyio", package_version="4.13.0",
       module_path="anyio/_core/_contextmanagers.py", class_name="ContextManagerMixin",
       observation_operation="__enter__", target_read_operation="repr(class)",
       state_fields_suspected="_cm", construction_hint="abstract mixin", fixture_family="unknown",
       expected_boundary="abstract mixin; construction likely fails", priority="3",
       harness=make_generic_attempt("anyio._core._contextmanagers", "ContextManagerMixin")),
    _c(candidate_id="bs10_beautifulsoup4_HTML5TreeBuilder",
       source_artifact="behavioral_sweep_results.csv", package_name="beautifulsoup4",
       package_version="4.14.3", module_path="bs4/builder/_html5lib.py",
       class_name="HTML5TreeBuilder", observation_operation="create_treebuilder",
       target_read_operation="repr(class)", state_fields_suspected="soup",
       construction_hint="requires html5lib (not available)", fixture_family="tree_or_html",
       expected_boundary="html5lib missing -> import_failed", priority="3",
       harness=make_generic_attempt("bs4.builder._html5lib", "HTML5TreeBuilder")),
    _c(candidate_id="bs21_dnspython_Buffer", source_artifact="behavioral_sweep_results.csv",
       package_name="dnspython", package_version="2.8.0", module_path="dns/quic/_common.py",
       class_name="Buffer", observation_operation="get", target_read_operation="repr(class)",
       state_fields_suspected="_buffer;_seen_end", construction_hint="Buffer()",
       fixture_family="buffer", expected_boundary="quic buffer; may not construct plainly",
       priority="3", harness=make_generic_attempt("dns.quic._common", "Buffer")),
    _c(candidate_id="bs24_docutils_OptionParser", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/frontend.py",
       class_name="OptionParser", observation_operation="get_config_file_settings",
       target_read_operation="repr(class)", state_fields_suspected="config_files",
       construction_hint="OptionParser(components=())", fixture_family="unknown",
       expected_boundary="config settings read; no order dependence expected", priority="3",
       harness=make_generic_attempt("docutils.frontend", "OptionParser",
                                    ctor_kwargs={"components": ()})),
    _c(candidate_id="bs25_docutils_Input", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/io.py",
       class_name="Input", observation_operation="decode", target_read_operation="repr(class)",
       state_fields_suspected="source;encoding", construction_hint="Input() (needs source)",
       fixture_family="unknown", expected_boundary="base Input needs a source",
       priority="3", harness=make_generic_attempt("docutils.io", "Input")),
    _c(candidate_id="bs36_docutils_Inliner", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4",
       module_path="docutils/parsers/rst/states.py", class_name="Inliner",
       observation_operation="parse", target_read_operation="repr(class)",
       state_fields_suspected="patterns", construction_hint="Inliner()", fixture_family="unknown",
       expected_boundary="constructs but parse needs document context", priority="3",
       harness=make_generic_attempt("docutils.parsers.rst.states", "Inliner")),
    _c(candidate_id="bs45_docutils_MathElement", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4",
       module_path="docutils/utils/math/mathml_elements.py", class_name="MathElement",
       observation_operation="close", target_read_operation="repr(class)",
       state_fields_suspected="children", construction_hint="MathElement()",
       fixture_family="unknown", expected_boundary="mathml node; append/close bookkeeping",
       priority="3", harness=make_generic_attempt("docutils.utils.math.mathml_elements",
                                                  "MathElement")),
    _c(candidate_id="bs46_docutils_MathSchema", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4",
       module_path="docutils/utils/math/mathml_elements.py", class_name="MathSchema",
       observation_operation="append", target_read_operation="repr(class)",
       state_fields_suspected="children", construction_hint="MathSchema()",
       fixture_family="unknown", expected_boundary="mathml schema node bookkeeping",
       priority="3", harness=make_generic_attempt("docutils.utils.math.mathml_elements",
                                                  "MathSchema")),
    _c(candidate_id="bs47_docutils_Writer", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4", module_path="docutils/writers/__init__.py",
       class_name="Writer", observation_operation="(excluded)", target_read_operation="write()",
       state_fields_suspected="output", construction_hint="write() has output side effects",
       fixture_family="unknown", expected_boundary="unsafe to execute (output side effect)",
       priority="3", harness=h_docutils_stringoutput_unsafe),
    _c(candidate_id="bs48_docutils_pep_html_Writer", source_artifact="behavioral_sweep_results.csv",
       package_name="docutils", package_version="0.22.4",
       module_path="docutils/writers/pep_html/__init__.py", class_name="Writer",
       observation_operation="interpolation_dict", target_read_operation="repr(class)",
       state_fields_suspected="settings", construction_hint="Writer()", fixture_family="unknown",
       expected_boundary="interpolation dict read; no order dependence expected", priority="3",
       harness=make_generic_attempt("docutils.writers.pep_html", "Writer")),

    _c(candidate_id="ext05_mistune_Markdown", source_artifact="source_snapshot",
       package_name="mistune", package_version="3.2.1", module_path="mistune/markdown.py",
       class_name="Markdown", observation_operation="parse ref-def first",
       target_read_operation="render '[a][]'", state_fields_suspected="block state",
       construction_hint="mistune.create_markdown()", fixture_family="string_text",
       expected_boundary="reference-style link resolution across calls", priority="2",
       harness=h_mistune_markdown),
    _c(candidate_id="ext06_more_itertools_spy", source_artifact="source_snapshot",
       package_name="more-itertools", package_version="11.0.2",
       module_path="more_itertools/more.py", class_name="spy", observation_operation="spy head",
       target_read_operation="list(iterable)", state_fields_suspected="cached head",
       construction_hint="spy(iter([...]))", fixture_family="iterator",
       expected_boundary="spy returns head without consuming", priority="2",
       harness=h_more_itertools_spy),
    _c(candidate_id="ext07_dnspython_Tokenizer_concat", source_artifact="source_snapshot",
       package_name="dnspython", package_version="2.8.0", module_path="dns/tokenizer.py",
       class_name="Tokenizer", observation_operation="get() twice",
       target_read_operation="concatenate_remaining_identifiers", state_fields_suspected="cursor",
       construction_hint="Tokenizer(StringIO('a b c'))", fixture_family="parser_tokenizer",
       expected_boundary="consuming tokens changes remaining concatenation", priority="2",
       harness=h_dnspython_tokenizer_concat),
    _c(candidate_id="ext08_boltons_LRU_pair2", source_artifact="source_snapshot",
       package_name="boltons", package_version="25.0.0", module_path="boltons/cacheutils.py",
       class_name="LRU", observation_operation="get('a') between two reads",
       target_read_operation="popitem-order after insert", state_fields_suspected="recency",
       construction_hint="LRU(max_size=2) pair2", fixture_family="cache",
       expected_boundary="access between reads changes eviction victim", priority="2",
       harness=h_boltons_lru_pair2),
]

for _cls, _mod in _DIRECTIVE_FAMILY:
    CANDIDATES.append(_c(
        candidate_id="dir_docutils_" + _cls, source_artifact="behavioral_sweep_results.csv",
        package_name="docutils", package_version="0.22.4",
        module_path=_mod.replace(".", "/") + ".py", class_name=_cls,
        observation_operation="(construction attempt)",
        target_read_operation="(construction attempt)",
        state_fields_suspected="state machine bookkeeping",
        construction_hint=_cls + "() requires (state_machine, debug) args",
        fixture_family="unknown",
        expected_boundary="RST state class needs state machine -> could_not_construct",
        priority="3", harness=make_directive_attempt(_mod, _cls)))

CANDIDATES_BY_ID = {c["candidate_id"]: c for c in CANDIDATES}
POOL_FIELDS = [
    "candidate_id", "source_artifact", "package_name", "package_version", "module_path",
    "class_name", "observation_operation", "target_read_operation", "state_fields_suspected",
    "construction_hint", "fixture_family", "expected_boundary", "priority", "selected_for_harness",
]
