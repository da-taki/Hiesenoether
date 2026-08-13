from boltons.cacheutils import LRI


def subject(touch_a=False):
    cache = LRI(max_size=2)
    cache["a"] = "A"
    cache["b"] = "B"
    if touch_a:
        _ = cache["a"]
    cache["c"] = "C"
    return ("items", tuple(cache.items()), cache.hit_count, cache.miss_count)


def ordinary_smoke():
    cache = LRI(max_size=2)
    cache["x"] = 1
    return cache["x"] == 1
