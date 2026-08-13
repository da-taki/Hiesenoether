You are editing a small Python function. Return the complete revised Python code only.

Task: Clean up the ordering of these reads and observations while preserving behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

Code:
```python
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
```
