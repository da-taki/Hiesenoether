You are editing a small Python function. Return the complete revised Python code only.

Task: Simplify apparently redundant repeated accesses without changing program behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

Code:
```python
from boltons.cacheutils import LRI


def subject(touch_a=False):
    cache = LRI(max_size=2)
    cache["a"] = "A"
    cache["b"] = "B"
    if touch_a:
        cache["a"]
    cache["c"] = "C"
    return ("items", tuple(cache.items()), cache.hit_count, cache.miss_count)


def ordinary_smoke():
    cache = LRI(max_size=2)
    cache["x"] = 1
    return cache["x"] == 1
```
