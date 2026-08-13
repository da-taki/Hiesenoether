import io
from dns.tokenizer import Tokenizer


def subject(consume_first=False):
    tokenizer = Tokenizer(io.StringIO("aa bb"))
    if consume_first:
        tokenizer.get()

    token = tokenizer.get()
    observed_value = token.value
    if observed_value == "bb":
        return ("has_bb", token.value)
    return ("has_aa", token.value)


def ordinary_smoke():
    return Tokenizer(io.StringIO("ok")).get().value == "ok"
