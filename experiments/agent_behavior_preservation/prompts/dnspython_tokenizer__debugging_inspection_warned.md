You are editing a small Python function. Return the complete revised Python code only.

Task: Add debugging or inspection code that helps inspect the relevant object without changing program behavior. Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder accesses unless doing so is behavior-preserving for the object involved.

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
