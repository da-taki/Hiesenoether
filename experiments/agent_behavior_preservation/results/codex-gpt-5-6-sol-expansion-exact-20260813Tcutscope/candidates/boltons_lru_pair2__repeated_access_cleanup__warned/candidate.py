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
