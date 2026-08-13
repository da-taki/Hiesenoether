You are editing a small Python function. Return the complete revised Python code only.

Task: Clean up the ordering of these reads and observations while preserving behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

Code:
```python
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
```
