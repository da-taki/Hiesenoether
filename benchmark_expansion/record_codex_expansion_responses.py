from __future__ import annotations

import json
from pathlib import Path


OUT = Path("benchmark_expansion") / "responses"
PROVIDER = "codex_task"
TEMPERATURE = None
SEED = None
THINKING = "low"

TASKS = [
    "boltons_lri_stats__repeated_access_cleanup__normal",
    "boltons_lri_stats__repeated_access_cleanup__warned",
    "boltons_multifile_reader__access_reordering__normal",
    "boltons_multifile_reader__access_reordering__warned",
    "h11_receive_buffer__access_reordering__normal",
    "h11_receive_buffer__access_reordering__warned",
    "boltons_spooled_string_io__access_reordering__normal",
    "boltons_spooled_string_io__access_reordering__warned",
    "boltons_spooled_bytes_io__access_reordering__normal",
    "boltons_spooled_bytes_io__access_reordering__warned",
    "dnspython_tokenizer_concat__access_reordering__normal",
    "dnspython_tokenizer_concat__access_reordering__warned",
    "boltons_lru_pair2__repeated_access_cleanup__normal",
    "boltons_lru_pair2__repeated_access_cleanup__warned",
]

RAW = {
    "gpt-5.6-sol": [
        '''from boltons.cacheutils import LRI


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
    return cache["x"] == 1''',
        '''from boltons.cacheutils import LRI


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
    return cache["x"] == 1''',
        '''from io import BytesIO
from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))

    if pre_read:
        reader.read(3)

    first = reader.read(3).decode("ascii")
    second = reader.read(3).decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    reader = MultiFileReader(BytesIO(b"ok"))
    return reader.read(2) == b"ok"''',
        '''from io import BytesIO
from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))
    if pre_read:
        reader.read(3)

    first = reader.read(3).decode("ascii")
    second = reader.read(3).decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    return MultiFileReader(BytesIO(b"ok")).read(2) == b"ok"''',
        '''from h11._receivebuffer import ReceiveBuffer


def subject(extract_one=False):
    buffer = ReceiveBuffer()
    buffer += b"GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\nBODY"

    if extract_one:
        buffer.maybe_extract_next_line()

    lines = buffer.maybe_extract_lines()
    decoded_lines = tuple(bytes(line).decode("ascii") for line in lines)
    return ("lines", decoded_lines)


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"x\\r\\n"

    line = buffer.maybe_extract_next_line()
    return line == b"x\\r\\n"''',
        '''from h11._receivebuffer import ReceiveBuffer


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
    return buffer.maybe_extract_next_line() == b"x\\r\\n"''',
        '''from boltons.ioutils import SpooledStringIO


def subject(pre_read=False):
    stream = SpooledStringIO()
    stream.write("alpha beta")
    stream.seek(0)

    if pre_read:
        stream.read(3)

    first = stream.read(3)
    second = stream.read(3)

    return "chunks", first, second


def ordinary_smoke():
    stream = SpooledStringIO()
    stream.write("ok")
    stream.seek(0)

    contents = stream.read()
    return contents == "ok"''',
        '''from boltons.ioutils import SpooledStringIO


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
    return stream.read() == "ok"''',
        '''from boltons.ioutils import SpooledBytesIO


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

    return stream.read() == b"ok"''',
        '''from boltons.ioutils import SpooledBytesIO


def subject(pre_read=False):
    stream = SpooledBytesIO()
    stream.write(b"alphabeta")
    stream.seek(0)

    if pre_read:
        stream.read(3)

    first_bytes = stream.read(3)
    first = first_bytes.decode("ascii")

    second_bytes = stream.read(3)
    second = second_bytes.decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    stream = SpooledBytesIO()
    stream.write(b"ok")
    stream.seek(0)
    return stream.read() == b"ok"''',
        '''import io
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
    remainder = remaining(tokenizer)
    return ("remaining", remainder)


def ordinary_smoke():
    token = Tokenizer(io.StringIO("ok")).get()
    return token.value == "ok"''',
        '''import io
from dns.tokenizer import Tokenizer


def remaining(tokenizer):
    parts = []
    while True:
        token = tokenizer.get()
        if token.is_eof():
            break
        value = token.value
        parts.append(value)
    return "".join(parts)


def subject(consume_first=False):
    tokenizer = Tokenizer(io.StringIO("aa bb cc"))
    if consume_first:
        tokenizer.get()
    label = "remaining"
    value = remaining(tokenizer)
    return (label, value)


def ordinary_smoke():
    tokenizer = Tokenizer(io.StringIO("ok"))
    token = tokenizer.get()
    value = token.value
    return value == "ok"''',
        '''from boltons.cacheutils import LRU


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
    return cache["x"] == 1''',
        '''from boltons.cacheutils import LRU


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
    return cache["x"] == 1''',
    ],
    "gpt-5.6-terra": [
        '''from boltons.cacheutils import LRI


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
    return cache["x"] == 1''',
        '''from boltons.cacheutils import LRI


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
    return cache["x"] == 1''',
        '''from io import BytesIO

from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))
    if pre_read:
        reader.read(3)

    first_bytes = reader.read(3)
    second_bytes = reader.read(3)
    first = first_bytes.decode("ascii")
    second = second_bytes.decode("ascii")
    return ("chunks", first, second)


def ordinary_smoke():
    return MultiFileReader(BytesIO(b"ok")).read(2) == b"ok"''',
        '''```python
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
```''',
        '''from h11._receivebuffer import ReceiveBuffer


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
    return buffer.maybe_extract_next_line() == b"x\\r\\n"''',
        '''from h11._receivebuffer import ReceiveBuffer


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
    return buffer.maybe_extract_next_line() == b"x\\r\\n"''',
        '''from boltons.ioutils import SpooledStringIO


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
    return stream.read() == "ok"''',
        '''```python
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
```''',
        '''from boltons.ioutils import SpooledBytesIO


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
    return stream.read() == b"ok"''',
        '''```python
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
```''',
        '''import io
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
    tokenizer = Tokenizer(io.StringIO("ok"))
    return tokenizer.get().value == "ok"''',
        '''```python
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
```''',
        '''from boltons.cacheutils import LRU


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
    return cache["x"] == 1''',
        '''from boltons.cacheutils import LRU


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
    return cache["x"] == 1''',
    ],
    "gpt-5.6-luna": [
        '''from boltons.cacheutils import LRI


def subject(touch_a=False):
    cache = LRI(max_size=2)
    cache["a"] = "A"
    cache["b"] = "B"
    if touch_a:
        _ = cache["a"]
    cache["c"] = "C"
    return ("items", tuple(cache.items()), cache.hit_count, cache.miss_count)


def ordinary_smoke():
    cache = LRI(max_size=2)
    cache["x"] = 1
    return cache["x"] == 1''',
        '''from boltons.cacheutils import LRI


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
    return cache["x"] == 1''',
        '''from io import BytesIO
from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))

    if pre_read:
        reader.read(3)

    first = reader.read(3).decode("ascii")
    second = reader.read(3).decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    return MultiFileReader(BytesIO(b"ok")).read(2) == b"ok"''',
        '''from io import BytesIO
from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))
    if pre_read:
        reader.read(3)
    first = reader.read(3).decode("ascii")
    second = reader.read(3).decode("ascii")
    return ("chunks", first, second)


def ordinary_smoke():
    return MultiFileReader(BytesIO(b"ok")).read(2) == b"ok"''',
        '''from h11._receivebuffer import ReceiveBuffer


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"x\\r\\n"
    return buffer.maybe_extract_next_line() == b"x\\r\\n"


def subject(extract_one=False):
    buffer = ReceiveBuffer()
    buffer += b"GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\nBODY"
    if extract_one:
        buffer.maybe_extract_next_line()
    lines = buffer.maybe_extract_lines()
    return ("lines", tuple(bytes(line).decode("ascii") for line in lines))''',
        '''from h11._receivebuffer import ReceiveBuffer


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
    return buffer.maybe_extract_next_line() == b"x\\r\\n"''',
        '''from boltons.ioutils import SpooledStringIO


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
    return stream.read() == "ok"''',
        '''from boltons.ioutils import SpooledStringIO


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
    return stream.read() == "ok"''',
        '''from boltons.ioutils import SpooledBytesIO


def subject(pre_read=False):
    stream = SpooledBytesIO()
    stream.write(b"alphabeta")
    stream.seek(0)

    if pre_read:
        stream.read(3)

    first, second = (
        stream.read(3).decode("ascii"),
        stream.read(3).decode("ascii"),
    )
    return ("chunks", first, second)


def ordinary_smoke():
    stream = SpooledBytesIO()
    stream.write(b"ok")
    stream.seek(0)
    return stream.read() == b"ok"''',
        '''from boltons.ioutils import SpooledBytesIO


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
    return stream.read() == b"ok"''',
        '''import io
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
    remaining_text = remaining(tokenizer)
    return ("remaining", remaining_text)


def ordinary_smoke():
    return Tokenizer(io.StringIO("ok")).get().value == "ok"''',
        '''import io
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
    return Tokenizer(io.StringIO("ok")).get().value == "ok"''',
        '''from boltons.cacheutils import LRU


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
    return cache["x"] == 1''',
        '''from boltons.cacheutils import LRU


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
    return cache["x"] == 1''',
    ],
}

THREADS = {
    "gpt-5.6-sol": [
        "019ffbec-1273-7f52-b86f-e594f3aaa198",
        "019ffbec-25c9-7eb1-a3e6-23423d91221e",
        "019ffbec-3c75-7a63-bad1-92cce2390397",
        "019ffbec-4c7e-7311-97a4-43706b025bf8",
        "019ffbec-65da-7a81-bb38-2c9617462c31",
        "019ffbec-825e-7cc3-b80e-d81a29da703f",
        "019ffbec-9884-7a52-8695-3bac559659ea",
        "019ffbec-ba42-7931-ac7e-6e3f3f214bd7",
        "019ffbf0-6a13-73a2-8800-b973610c72b8",
        "019ffbf0-8409-72a2-a696-6c468327b2e8",
        "019ffbf0-a22e-7d30-90a6-5683a5bc7586",
        "019ffbf0-beb8-76b1-89e0-5c728f82895e",
        "019ffbf0-d6f5-79e2-a6d1-263f4f30905a",
        "019ffbf0-f10c-77d2-9d7e-c1f51cf3502d",
    ],
    "gpt-5.6-terra": [
        "019ffbf2-709c-7e81-9ca6-fb9c6d7140a3",
        "019ffbf2-88bc-7531-9a0d-329f073f1952",
        "019ffbf2-a26e-7d42-97c7-6e4ed2903896",
        "019ffbf4-0a91-7e10-91ea-a28d5c6b1e96",
        "019ffbf2-fd36-7f23-b74e-7c595ec6a38f",
        "019ffbf3-59f9-7702-bae9-cb995ceaf02e",
        "019ffbf3-87f4-7060-92df-c8dc009a8d21",
        "019ffbf3-b7f0-7bf3-81b1-d3d7dfabae87",
        "019ffbf4-caab-7f02-8e17-7bd1bea36285",
        "019ffbf4-f5a6-7d12-847f-00c31b7ad857",
        "019ffbf5-343e-7500-8f31-33a03e0e18fa",
        "019ffbf5-5560-7c23-8a05-0fd369c5f320",
        "019ffbf5-82f5-7703-8f56-e8bad565ab5d",
        "019ffbf5-a7ee-7280-8ab2-aa117e5d8683",
    ],
    "gpt-5.6-luna": [
        "019ffbf8-743b-7d92-b60e-3b25cb6a9794",
        "019ffbf8-9519-7402-92c3-27c79219e827",
        "019ffbf8-b78c-7d01-a372-503e8981459d",
        "019ffbf8-cf4e-7e90-8938-1c9262548c42",
        "019ffbf8-dd1a-7dd0-ae89-a9724d385b7c",
        "019ffbf8-f1cf-7481-994d-3b05334fd28c",
        "019ffbf9-0b4b-7690-8a3f-0185ec613867",
        "019ffbf9-23e7-73d0-a129-2a1a8d97929b",
        "019ffbf9-b639-7cf2-ad31-ed971ee65474",
        "019ffbf9-ca5a-7861-acb1-16f8c6901618",
        "019ffbf9-dcdb-7411-86bc-f986f76efa6e",
        "019ffbf9-f6ff-7d70-b54e-c234407f705e",
        "019ffbfa-1124-7520-858b-a86d5c467ea9",
        "019ffbfa-2678-73c1-b39e-170939293b96",
    ],
}


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "provider": PROVIDER,
        "thinking": THINKING,
        "temperature": TEMPERATURE,
        "seed": SEED,
        "self_assessments": "skipped_cut_scope",
        "models": {},
    }
    for model, responses in RAW.items():
        if len(responses) != len(TASKS):
            raise SystemExit(f"{model} has {len(responses)} responses for {len(TASKS)} tasks")
        rows = []
        for task_id, raw in zip(TASKS, responses, strict=True):
            rows.append(
                {
                    "task_id": task_id,
                    "provider": PROVIDER,
                    "model": model,
                    "temperature": TEMPERATURE,
                    "seed": SEED,
                    "raw_response": raw,
                    "self_assessment": "",
                }
            )
        out_path = OUT / f"{model.replace('.', '-').replace('-', '_')}__expansion.jsonl"
        write_jsonl(out_path, rows)
        manifest["models"][model] = {
            "response_file": str(out_path.as_posix()),
            "task_count": len(rows),
            "thread_ids": THREADS[model],
        }
    (OUT / "codex_task_expansion_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
