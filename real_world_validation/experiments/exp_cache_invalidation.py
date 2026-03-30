# exp_cache_invalidation.py

import csv
import functools
import math
from pathlib import Path

from core.unstable_object import UnstableObject

RAW_DIR = Path("real_world_validation/results/raw")

try:
    import config
    BASE_VALUE = config.BASE_VALUE
    RAW_DIR = config.RESULTS_RAW_DIR
except ImportError:
    BASE_VALUE = 10.0

STEPS_BETWEEN_SWEEP = [0, 1, 2, 3, 5, 10, 20]


def _make_fresh_obj_at_state(base: float, target_access: int, target_entropy: float) -> UnstableObject:
    """Reconstruct an UnstableObject with given access_count and entropy without calling read()."""
    from core.unstable_object import INITIAL_ENTROPY, ENTROPY_INCREMENT
    obj = UnstableObject(base=base, initial_entropy=target_entropy)
    obj.access_count = target_access
    return obj


def _compute_true_result(base: float, access_count_at_call: int, entropy_at_call: float,
                         multiplier: float) -> float:
    obj = _make_fresh_obj_at_state(base, access_count_at_call, entropy_at_call)
    return obj.read() * multiplier


def run_manual_dict_cache_case(steps_between: int) -> dict:
    multiplier = 2.0
    obj = UnstableObject(base=BASE_VALUE)

    first_val = obj.read() * multiplier
    cache = {"key": first_val}

    ac_after_first = obj.access_count
    ent_after_first = obj.entropy

    for _ in range(steps_between):
        obj.read()

    cache_hit_result = cache["key"]
    true_second_result = _compute_true_result(BASE_VALUE, ac_after_first,
                                              ent_after_first, multiplier)

    cache_error = abs(cache_hit_result - true_second_result)
    cache_error_pct = (100.0 * cache_error / abs(true_second_result)
                       if true_second_result != 0 else 0.0)

    return {
        "case_type": "manual_dict",
        "steps_between": steps_between,
        "observe_count": None,
        "cached_result": round(cache_hit_result, 6),
        "true_result": round(true_second_result, 6),
        "cache_error": round(cache_error, 6),
        "cache_error_pct": round(cache_error_pct, 4),
    }


def run_lru_cache_case(steps_between: int) -> dict:
    multiplier = 2.0
    call_log = []

    shared_obj = UnstableObject(base=BASE_VALUE)

    @functools.lru_cache(maxsize=128)
    def cached_compute(key: str, mult: float) -> float:
        val = shared_obj.read() * mult
        call_log.append(("computed", shared_obj.access_count, shared_obj.entropy, val))
        return val

    first_result = cached_compute("x", multiplier)
    ac_after_first = shared_obj.access_count
    ent_after_first = shared_obj.entropy

    for _ in range(steps_between):
        shared_obj.read()

    cache_hit_result = cached_compute("x", multiplier)
    true_second_result = _compute_true_result(BASE_VALUE, ac_after_first,
                                              ent_after_first, multiplier)

    cache_error = abs(cache_hit_result - true_second_result)
    cache_error_pct = (100.0 * cache_error / abs(true_second_result)
                       if true_second_result != 0 else 0.0)

    cached_compute.cache_clear()

    return {
        "case_type": "lru_cache",
        "steps_between": steps_between,
        "observe_count": None,
        "cached_result": round(cache_hit_result, 6),
        "true_result": round(true_second_result, 6),
        "cache_error": round(cache_error, 6),
        "cache_error_pct": round(cache_error_pct, 4),
    }


def run_observe_invalidation_case() -> dict:
    obj = UnstableObject(base=BASE_VALUE)
    first_val = obj.read()
    cache = {"key": first_val}

    ac_after_first = obj.access_count
    ent_after_first = obj.entropy

    obj.observe()

    cache_hit_result = cache["key"]
    true_second_result = _compute_true_result(BASE_VALUE, ac_after_first,
                                              obj.entropy, 1.0)

    cache_error = abs(cache_hit_result - true_second_result)
    cache_error_pct = (100.0 * cache_error / abs(true_second_result)
                       if true_second_result != 0 else 0.0)

    return {
        "case_type": "observe_invalidation",
        "steps_between": None,
        "observe_count": 1,
        "cached_result": round(cache_hit_result, 6),
        "true_result": round(true_second_result, 6),
        "cache_error": round(cache_error, 6),
        "cache_error_pct": round(cache_error_pct, 4),
    }


def run_invalidation_sweep() -> list:
    rows = []
    for steps in STEPS_BETWEEN_SWEEP:
        rows.append(run_manual_dict_cache_case(steps))
        rows.append(run_lru_cache_case(steps))
    return rows


def _write_csv(rows: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def run_experiment() -> list:
    rows = run_invalidation_sweep()
    rows.append(run_observe_invalidation_case())
    _write_csv(rows, RAW_DIR / "cache_invalidation_cases.csv")
    return rows