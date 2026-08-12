You are editing a small Python function. Return the complete revised Python code only.

Task: Avoid repeated work by caching or materializing this value while preserving behavior. Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder accesses unless doing so is behavior-preserving for the object involved.

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
