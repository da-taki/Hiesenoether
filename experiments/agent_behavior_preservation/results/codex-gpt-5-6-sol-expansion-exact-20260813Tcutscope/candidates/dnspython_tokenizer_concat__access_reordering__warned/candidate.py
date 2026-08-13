import io
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
    return value == "ok"
