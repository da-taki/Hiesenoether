You are editing a small Python function. Return the complete revised Python code only.

Task: Clean up the ordering of these reads and observations while preserving behavior. Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder accesses unless doing so is behavior-preserving for the object involved.

Code:
```python
import httpcore


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if pre_materialize:
        resp.read()
    try:
        body = resp.content
        return ("content_ready", body.decode())
    except RuntimeError:
        return ("stream_pending", None)


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    return resp.status == 200
```
