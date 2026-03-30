# exp_numpy_extension.py

try:
    import config
    ENABLE_NUMPY_EXP = config.ENABLE_NUMPY_EXP
except ImportError:
    ENABLE_NUMPY_EXP = False


def _run_numpy_sle_sweep():
    raise NotImplementedError(
        "NumPy extension not yet implemented. "
        "See real_world_validation/README.md — Future Work section."
    )


def run_experiment() -> list:
    if not ENABLE_NUMPY_EXP:
        print("[numpy_extension] Skipped (ENABLE_NUMPY_EXP=False in config.py)")
        return []

    try:
        import numpy  # noqa: F401
    except ImportError:
        print("[numpy_extension] Skipped (numpy not installed)")
        return []

    _run_numpy_sle_sweep()
    return []