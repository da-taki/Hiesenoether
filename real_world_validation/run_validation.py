# run_validation.py

import argparse
import logging
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RWV = Path(__file__).parent
if str(RWV) not in sys.path:
    sys.path.insert(0, str(RWV))

import config

config.RESULTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
config.RESULTS_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
config.RESULTS_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
config.RESULTS_LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _setup_logging() -> logging.Logger:
    log_path = config.RESULTS_LOGS_DIR / "run.log"
    logger = logging.getLogger("validation")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def run_all(num_runs: int = config.NUM_RUNS) -> None:
    logger = _setup_logging()
    t_start = time.time()

    logger.info("=" * 60)
    logger.info("Ordered Chaos — Python Runtime Validation")
    logger.info(f"Python      : {sys.version.split()[0]}")
    logger.info(f"NUM_RUNS    : {num_runs:,}")
    logger.info(f"RANDOM_SEED : {config.RANDOM_SEED}")
    logger.info("=" * 60)

    random.seed(config.RANDOM_SEED)

    # ── Descriptor experiment ────────────────────────────────────────
    logger.info("Running descriptor experiment (A1 + A3 analogues)...")
    t0 = time.time()
    from experiments.exp_descriptor import run_experiment as run_descriptor
    descriptor_rows = run_descriptor(num_runs)
    logger.info(f"  Done in {time.time() - t0:.1f}s — {len(descriptor_rows)} config rows")

    # ── Cache invalidation ───────────────────────────────────────────
    logger.info("Running cache invalidation experiment...")
    t0 = time.time()
    from experiments.exp_cache_invalidation import run_experiment as run_cache
    cache_rows = run_cache()
    max_err = max(
        (float(r.get("cache_error_pct", 0)) for r in cache_rows
         if r.get("cache_error_pct") not in (None, "")),
        default=0.0,
    )
    logger.info(f"  Done in {time.time() - t0:.1f}s — max cache error: {max_err:.2f}%")

    # ── SLE fitting ──────────────────────────────────────────────────
    logger.info("Running SLE fitting experiment (A2 analogue)...")
    t0 = time.time()
    from experiments.exp_sle_fitting import run_experiment as run_sle
    sle_result = run_sle(num_runs)
    logger.info(
        f"  Done in {time.time() - t0:.1f}s — "
        f"SLE={sle_result['sle']:.4f}  R²={sle_result['r_squared']:.4f}  "
        f"95% CI=[{sle_result['ci_low']:.4f}, {sle_result['ci_high']:.4f}]"
    )

    # ── Real system case studies ─────────────────────────────────────
    logger.info("Running real system case studies (risk / ORM / ML)...")
    t0 = time.time()
    from experiments.exp_real_system_case import run_experiment as run_real_system
    real_system_rows = run_real_system(num_runs)
    if real_system_rows:
        cases = {}
        for r in real_system_rows:
            cases.setdefault(r["case"], []).append(r["flip_rate"])
        for case_name, flip_rates in cases.items():
            logger.info(
                f"  {case_name}: max flip_rate={max(flip_rates):.4f}  "
                f"monotonic={real_system_rows[[r['case'] for r in real_system_rows].index(case_name)]['monotonic_drift']}"
            )
    logger.info(
        f"  Done in {time.time() - t0:.1f}s — "
        f"{len(real_system_rows)} rows across "
        f"{len({r['case'] for r in real_system_rows})} case families"
    )

    # ── NumPy stub ───────────────────────────────────────────────────
    from experiments.exp_numpy_extension import run_experiment as run_numpy
    run_numpy()

    # ── Summarize ────────────────────────────────────────────────────
    logger.info("Writing summary CSVs and findings...")
    from analysis.summarize import summarize_all
    summary_data = summarize_all(
        descriptor_rows=descriptor_rows,
        sle_result_dict=sle_result,
        cache_rows=cache_rows,
    )

    # ── Plot ─────────────────────────────────────────────────────────
    logger.info("Generating figures...")
    from analysis.plot import plot_all
    plot_all(
        descriptor_rows=summary_data["descriptor_rows"],
        sle_rows=summary_data["sle_rows"],
        cache_rows=summary_data["cache_rows"],
        sweep_rows=sle_result.get("sweep_rows"),
    )

    # ── Final summary ────────────────────────────────────────────────
    elapsed = time.time() - t_start

    # Compute per-case max flip rates for summary line
    flip_summary = {}
    for r in real_system_rows:
        case = r["case"]
        fr = float(r.get("flip_rate", 0))
        if case not in flip_summary or fr > flip_summary[case]:
            flip_summary[case] = fr

    logger.info("=" * 60)
    logger.info("RESULTS SUMMARY")
    logger.info(f"  Python SLE              : {sle_result['sle']}")
    logger.info(f"  SLE R²                  : {sle_result['r_squared']}")
    logger.info(f"  SLE 95% CI              : [{sle_result['ci_low']}, {sle_result['ci_high']}]")
    logger.info(f"  Hiesenoether SLE (ref)  : 2.7891")
    logger.info(f"  Max cache error %%       : {max_err:.2f}")
    logger.info(f"  Real system rows        : {len(real_system_rows)}")
    for case_name, max_fr in flip_summary.items():
        logger.info(f"  Flip rate [{case_name:<20}]: {max_fr:.4f} ({max_fr*100:.2f}%)")
    logger.info(f"  Total runtime           : {elapsed:.1f}s")
    logger.info(f"  Summary CSVs            : {config.RESULTS_SUMMARY_DIR}")
    logger.info(f"  Figures                 : {config.RESULTS_FIGURES_DIR}")
    logger.info(f"  Run log                 : {config.RESULTS_LOGS_DIR / 'run.log'}")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ordered Chaos — Python Runtime Validation"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=config.NUM_RUNS,
        help=f"Number of shuffle iterations per config (default: {config.NUM_RUNS})",
    )
    args = parser.parse_args()
    run_all(num_runs=args.runs)