import io
from dns.tokenizer import Tokenizer


def subject(consume_first=False):
    tokenizer = Tokenizer(io.StringIO("aa bb"))
    if consume_first:
        tokenizer.get()

    value = tokenizer.get().value
    return ("has_bb", value) if value == "bb" else ("has_aa", value)


def ordinary_smoke():
    return Tokenizer(io.StringIO("ok")).get().value == "ok"
