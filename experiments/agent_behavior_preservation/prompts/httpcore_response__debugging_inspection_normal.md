You are editing a small Python function. Return the complete revised Python code only.

Task: Add debugging or inspection code that helps inspect the relevant object without changing program behavior.

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
