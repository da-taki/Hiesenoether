You are editing a small Python function. Return the complete revised Python code only.

Task: Clean up the ordering of these reads and observations while preserving behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

Code:
```python
import io
from dns.tokenizer import Tokenizer


def subject(consume_first=False):
    tokenizer = Tokenizer(io.StringIO("aa bb"))
    if consume_first:
        tokenizer.get()
    token = tokenizer.get()
    return ("has_bb", token.value) if token.value == "bb" else ("has_aa", token.value)


def ordinary_smoke():
    return Tokenizer(io.StringIO("ok")).get().value == "ok"
```
