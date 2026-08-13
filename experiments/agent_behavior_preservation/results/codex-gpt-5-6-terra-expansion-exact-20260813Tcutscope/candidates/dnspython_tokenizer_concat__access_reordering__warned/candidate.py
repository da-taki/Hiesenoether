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
