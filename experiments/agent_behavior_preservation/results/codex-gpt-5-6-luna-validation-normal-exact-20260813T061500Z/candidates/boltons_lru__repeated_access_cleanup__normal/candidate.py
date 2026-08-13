from boltons.cacheutils import LRU


def subject(touch_x=False):
    cache = LRU(max_size=2)
    cache["x"] = 1
    cache["y"] = 2
    if touch_x:
        cache["x"]
    cache["z"] = 3
    items = tuple(cache.items())
    return ("x_live", items) if "x" in cache else ("x_evicted", items)


def ordinary_smoke():
    cache = LRU(max_size=2)
    cache["a"] = 1
    return cache["a"] == 1
