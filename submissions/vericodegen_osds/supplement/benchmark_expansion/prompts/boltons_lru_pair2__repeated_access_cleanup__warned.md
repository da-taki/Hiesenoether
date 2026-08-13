You are editing a small Python function. Return the complete revised Python code only.

Task: Simplify apparently redundant repeated accesses without changing program behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

Code:
```python
from boltons.cacheutils import LRU


def subject(touch_x=False):
    cache = LRU(max_size=2)
    cache["x"] = 1
    cache["y"] = 2
    first = tuple(cache.items())
    if touch_x:
        cache["x"]
    cache["z"] = 3
    second = tuple(cache.items())
    return ("items", first, second)


def ordinary_smoke():
    cache = LRU(max_size=2)
    cache["x"] = 1
    return cache["x"] == 1
```
