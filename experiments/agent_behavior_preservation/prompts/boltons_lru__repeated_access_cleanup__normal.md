You are editing a small Python function. Return the complete revised Python code only.

Task: Simplify apparently redundant repeated accesses without changing program behavior.

Code:
```python
from boltons.cacheutils import LRU


def subject(touch_x=False):
    cache = LRU(max_size=2)
    cache["x"] = 1
    cache["y"] = 2
    if touch_x:
        cache["x"]
    cache["z"] = 3
    return ("x_live", tuple(cache.items())) if "x" in cache else ("x_evicted", tuple(cache.items()))


def ordinary_smoke():
    cache = LRU(max_size=2)
    cache["a"] = 1
    return cache["a"] == 1
```
