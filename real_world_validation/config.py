from pathlib import Path

RANDOM_SEED: int = 42
NUM_RUNS: int = 100_000
BASE_VALUE: float = 10.0
INITIAL_ENTROPY: float = 1.0
ENTROPY_INCREMENT: float = 0.1
OBSERVE_ENTROPY_BUMP: float = 1.0

NONLINEARITY_LEVELS: list = ["linear", "quadratic", "cubic", "extreme"]
OBSERVE_COUNTS: list = [0, 1, 2, 3, 4, 5]
STEP_COUNTS: list = [3, 6, 9, 12, 15, 20]
DEFAULT_STEPS: int = 6
DEFAULT_OBSERVES: int = 1

BOOTSTRAP_RESAMPLES: int = 1000
SLE_CI_LEVEL: float = 0.95

ENABLE_NUMPY_EXP: bool = False

_BASE = Path(__file__).parent

RESULTS_RAW_DIR     = _BASE / "results" / "raw"
RESULTS_SUMMARY_DIR = _BASE / "results" / "summary"
RESULTS_FIGURES_DIR = _BASE / "results" / "figures"
RESULTS_LOGS_DIR    = _BASE / "results" / "logs"

for _d in (RESULTS_RAW_DIR, RESULTS_SUMMARY_DIR, RESULTS_FIGURES_DIR, RESULTS_LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

FIGURE_NAMES: dict = {
    "a1_observation":    "python_a1_observation",
    "sle_fit":           "python_sle_fit",
    "cache_invalidation":"python_cache_invalidation",
    "a3_length_scaling": "python_a3_length_scaling",
}
