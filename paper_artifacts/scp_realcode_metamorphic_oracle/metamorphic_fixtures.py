from __future__ import annotations

import io
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SNAPSHOT = REPO / "paper_artifacts" / "scp_realworld_revision" / "source_snapshot"

FIXTURE_FAMILIES = [
    "string_text",
    "bytes",
    "io_bytes",
    "iterator",
    "list_or_dict",
    "tree_or_html",
    "yaml_or_repr",
    "logging_handler",
    "http_response",
    "parser_tokenizer",
    "buffer",
    "cache",
    "path_or_tempfile",
    "unknown",
]

class FixtureUnavailable(Exception):
    pass

@dataclass
class Fixture:

    family: str
    builder: Callable[[], Any]
    metadata: dict = field(default_factory=dict)
    cleanup: Optional[Callable[[], None]] = None
    snapshot: Optional[Callable[[Any], Any]] = None

_SNAPSHOT_ADDED = False

def add_snapshot_paths() -> list[str]:
    global _SNAPSHOT_ADDED
    added: list[str] = []
    if not SNAPSHOT.exists():
        return added
    paths: list[str] = []
    for dist in sorted(SNAPSHOT.iterdir()):
        if dist.is_dir():
            paths.append(str(dist))
            src = dist / "src"
            if src.exists():
                paths.append(str(src))
    for path in reversed(paths):
        if path not in sys.path:
            sys.path.insert(0, path)
            added.append(path)
    _SNAPSHOT_ADDED = True
    return added

def snapshot(value: Any, _depth: int = 0) -> Any:
    if _depth > 6:
        return repr(value)
    if isinstance(value, (bytes, bytearray)):
        return repr(bytes(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): snapshot(v, _depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [snapshot(v, _depth + 1) for v in value]
    if isinstance(value, set):
        return sorted(repr(v) for v in value)
    return repr(value)

def fixture_string_text(text: str = "alpha beta gamma") -> Fixture:
    return Fixture(
        family="string_text",
        builder=lambda: str(text),
        metadata={"seed": text},
        snapshot=lambda o: snapshot(o),
    )

def fixture_bytes(data: bytes = b"alphabeta") -> Fixture:
    return Fixture(
        family="bytes",
        builder=lambda: bytes(data),
        metadata={"seed": repr(data)},
        snapshot=lambda o: snapshot(o),
    )

def fixture_io_bytes(data: bytes = b"alphabeta") -> Fixture:
    return Fixture(
        family="io_bytes",
        builder=lambda: io.BytesIO(bytes(data)),
        metadata={"seed": repr(data)},
        snapshot=lambda o: {"tell": o.tell(), "closed": o.closed},
    )

def fixture_io_string(text: str = "alpha beta\n") -> Fixture:
    return Fixture(
        family="io_bytes",
        builder=lambda: io.StringIO(str(text)),
        metadata={"seed": text},
        snapshot=lambda o: {"tell": o.tell(), "closed": o.closed},
    )

def fixture_iterator(seq=("a", "b", "c")) -> Fixture:
    items = list(seq)
    return Fixture(
        family="iterator",
        builder=lambda: iter(list(items)),
        metadata={"seed": items},
        snapshot=lambda o: repr(o),
    )

def fixture_list_or_dict(template=None) -> Fixture:
    template = template if template is not None else {"a": 1, "b": [2, 3], "c": {"d": 4}}
    import copy

    return Fixture(
        family="list_or_dict",
        builder=lambda: copy.deepcopy(template),
        metadata={"seed": snapshot(template)},
        snapshot=lambda o: snapshot(o),
    )

def fixture_tree_or_html(html: str = "<div><p class='a'>x</p><p>y</p></div>") -> Fixture:
    try:
        from bs4 import BeautifulSoup
    except Exception as exc:
        raise FixtureUnavailable(f"bs4 unavailable: {exc}") from exc

    return Fixture(
        family="tree_or_html",
        builder=lambda: BeautifulSoup(html, "html.parser"),
        metadata={"seed": html, "parser": "html.parser"},
        snapshot=lambda o: {"p_count": len(o.find_all("p")), "text": o.get_text()},
    )

def fixture_yaml_or_repr(payload=None) -> Fixture:
    payload = payload if payload is not None else ["before"]
    import copy

    return Fixture(
        family="yaml_or_repr",
        builder=lambda: copy.deepcopy(payload),
        metadata={"seed": snapshot(payload)},
        snapshot=lambda o: snapshot(o),
    )

def fixture_logging_handler() -> Fixture:
    import logging

    def build():
        handler = logging.Handler()
        handler.setLevel(logging.NOTSET)
        return handler

    return Fixture(
        family="logging_handler",
        builder=build,
        metadata={"seed": "logging.Handler()"},
        snapshot=lambda o: {"level": o.level},
    )

def fixture_http_response(chunks=(b"alpha", b"beta")) -> Fixture:
    try:
        import httpcore
    except Exception as exc:
        raise FixtureUnavailable(f"httpcore unavailable: {exc}") from exc

    chunk_list = [bytes(c) for c in chunks]
    return Fixture(
        family="http_response",
        builder=lambda: httpcore.Response(200, content=list(chunk_list)),
        metadata={"seed": [repr(c) for c in chunk_list], "version": httpcore.__version__},
        snapshot=lambda o: {
            "has__content": hasattr(o, "_content"),
            "stream_consumed": getattr(o, "_stream_consumed", None),
        },
    )

def fixture_parser_tokenizer(text: str = "alpha beta\n") -> Fixture:
    try:
        from dns.tokenizer import Tokenizer
    except Exception as exc:
        raise FixtureUnavailable(f"dnspython unavailable: {exc}") from exc
    from dns.tokenizer import Tokenizer

    return Fixture(
        family="parser_tokenizer",
        builder=lambda: Tokenizer(io.StringIO(str(text))),
        metadata={"seed": text},
        snapshot=lambda o: {"eof": o.eof, "where": list(o.where())},
    )

def fixture_buffer(data: bytes = b"GET / HTTP/1.1\r\nHost: x\r\n\r\nBODY") -> Fixture:
    try:
        from h11._receivebuffer import ReceiveBuffer
    except Exception as exc:
        raise FixtureUnavailable(f"h11 unavailable: {exc}") from exc

    def build():
        buf = ReceiveBuffer()
        buf += bytes(data)
        return buf

    return Fixture(
        family="buffer",
        builder=build,
        metadata={"seed": repr(data)},
        snapshot=lambda o: {"len": len(bytes(o))},
    )

def fixture_cache(kind: str = "LRU", max_size: int = 2, seed=(("a", "A"), ("b", "B"))) -> Fixture:
    try:
        from boltons import cacheutils
    except Exception as exc:
        raise FixtureUnavailable(f"boltons unavailable: {exc}") from exc

    cls = getattr(cacheutils, kind)
    pairs = list(seed)

    def build():
        cache = cls(max_size=max_size)
        for k, v in pairs:
            cache[k] = v
        return cache

    return Fixture(
        family="cache",
        builder=build,
        metadata={"kind": kind, "max_size": max_size, "seed": pairs},
        snapshot=lambda o: {"items": [list(t) for t in o.items()]},
    )

def fixture_path_or_tempfile(data: bytes = b"line1\nline2\n") -> Fixture:
    import tempfile

    holder: dict[str, Any] = {}

    def build():
        fd, name = tempfile.mkstemp(prefix="scp_meta_", suffix=".txt")
        with io.open(fd, "wb") as fh:
            fh.write(bytes(data))
        holder.setdefault("paths", []).append(name)
        return open(name, "rb")

    def cleanup():
        import os

        for name in holder.get("paths", []):
            try:
                os.unlink(name)
            except OSError:
                pass

    return Fixture(
        family="path_or_tempfile",
        builder=build,
        metadata={"seed": repr(data)},
        cleanup=cleanup,
        snapshot=lambda o: {"tell": o.tell(), "closed": o.closed},
    )

FAMILY_FACTORIES: dict[str, Callable[..., Fixture]] = {
    "string_text": fixture_string_text,
    "bytes": fixture_bytes,
    "io_bytes": fixture_io_bytes,
    "iterator": fixture_iterator,
    "list_or_dict": fixture_list_or_dict,
    "tree_or_html": fixture_tree_or_html,
    "yaml_or_repr": fixture_yaml_or_repr,
    "logging_handler": fixture_logging_handler,
    "http_response": fixture_http_response,
    "parser_tokenizer": fixture_parser_tokenizer,
    "buffer": fixture_buffer,
    "cache": fixture_cache,
    "path_or_tempfile": fixture_path_or_tempfile,
}

def make_fixture(family: str, **kwargs) -> Fixture:
    factory = FAMILY_FACTORIES.get(family)
    if factory is None:
        raise FixtureUnavailable(f"no factory for family {family!r}")
    return factory(**kwargs)

if __name__ == "__main__":
    add_snapshot_paths()
    report = {}
    for fam in FIXTURE_FAMILIES:
        if fam == "unknown":
            continue
        try:
            fx = make_fixture(fam)
            obj = fx.builder()
            report[fam] = {"ok": True, "type": type(obj).__name__}
            if fx.cleanup:
                fx.cleanup()
        except FixtureUnavailable as exc:
            report[fam] = {"ok": False, "reason": str(exc)}
        except Exception as exc:
            report[fam] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    import json

    print(json.dumps(report, indent=2))
