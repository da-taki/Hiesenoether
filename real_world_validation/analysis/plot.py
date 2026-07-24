import math
from pathlib import Path

FIGURES_DIR = Path("real_world_validation/results/figures")

try:
    import config
    FIGURES_DIR = config.RESULTS_FIGURES_DIR
except ImportError:
    pass

COLORS = ["#2C7BB6", "#D7191C", "#1A9641", "#FDAE61"]
_MPL_CONFIGURED = False

def _configure_mpl():
    global _MPL_CONFIGURED
    if _MPL_CONFIGURED:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.size": 11,
        "figure.dpi": 150,
        "figure.autolayout": True,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    _MPL_CONFIGURED = True

def _save(fig, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png = FIGURES_DIR / f"{name}.png"
    pdf = FIGURES_DIR / f"{name}.pdf"
    fig.savefig(png, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    print(f"  -> {png} written")

def plot_a1_analogue(rows: list) -> None:
    _configure_mpl()
    import matplotlib.pyplot as plt

    shuffled = sorted(
        [r for r in rows if r.get("axis") == "A1_py" and r.get("access_mode") == "shuffled"],
        key=lambda r: int(r.get("observes", 0)),
    )
    cached = sorted(
        [r for r in rows if r.get("axis") == "A1_py" and r.get("access_mode") == "cached"],
        key=lambda r: int(r.get("observes", 0)),
    )
    if not shuffled:
        print("  [plot] No A1 descriptor data — skipping plot_a1_analogue")
        return

    obs_counts = [int(r["observes"]) for r in shuffled]
    stds_shuffled = [float(r["std"]) for r in shuffled]
    stds_cached = [float(r["std"]) for r in cached] if cached else []
    ranges_shuffled = [float(r["range"]) for r in shuffled]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.bar([o - 0.2 for o in obs_counts], stds_shuffled, width=0.35,
            color=COLORS[0], label="Shuffled", alpha=0.85)
    if stds_cached:
        ax1.bar([o + 0.2 for o in obs_counts], stds_cached, width=0.35,
                color=COLORS[1], label="Cached (stale)", alpha=0.85)
    ax1.set_xlabel("Observation count")
    ax1.set_ylabel("Standard deviation")
    ax1.set_title("(a) Std vs observation count")
    ax1.set_xticks(obs_counts)
    ax1.legend(fontsize=9)

    ax2.plot(obs_counts, ranges_shuffled, marker="o", color=COLORS[0],
             linewidth=1.8, label="Shuffled range")
    ax2.set_xlabel("Observation count")
    ax2.set_ylabel("Output range")
    ax2.set_title("(b) Range vs observation count")
    ax2.set_xticks(obs_counts)
    ax2.legend(fontsize=9)

    _save(fig, "python_a1_observation")
    plt.close(fig)

def plot_sle(sle_rows: list) -> None:
    _configure_mpl()
    import matplotlib.pyplot as plt

    rows = sorted(
        [r for r in sle_rows if r.get("log_range") and float(r["log_range"]) > 0],
        key=lambda r: int(r.get("degree", 0)),
    )
    if len(rows) < 2:
        print("  [plot] Insufficient SLE data — skipping plot_sle")
        return

    degrees = [int(r["degree"]) for r in rows]
    log_ranges = [float(r["log_range"]) for r in rows]
    labels = [r["nonlinearity"] for r in rows]
    ranges = [float(r["range"]) for r in rows]

    sle = float(rows[0].get("sle", 0))
    r2 = float(rows[0].get("r_squared", 0))
    n = len(degrees)
    x_mean = sum(degrees) / n
    y_mean = sum(log_ranges) / n
    intercept = y_mean - sle * x_mean
    fitted = [intercept + sle * d for d in degrees]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.scatter(degrees, log_ranges, color=COLORS[0], s=70, zorder=3,
                label="Measured log(range)")
    ax1.plot(degrees, fitted, color=COLORS[1], linewidth=1.8, linestyle="--",
             label=f"SLE fit (slope={sle:.4f}, R²={r2:.4f})")
    for d, lr, lbl in zip(degrees, log_ranges, labels):
        ax1.annotate(lbl, (d, lr), textcoords="offset points",
                     xytext=(4, 4), fontsize=8)
    ax1.set_xlabel("Nonlinearity degree")
    ax1.set_ylabel("log(Range)")
    ax1.set_title("(a) SLE: log(range) vs nonlinearity degree")
    ax1.legend(fontsize=9)

    ax2.bar(labels, ranges, color=COLORS[2], alpha=0.85)
    ax2.set_yscale("log")
    ax2.set_xlabel("Nonlinearity level")
    ax2.set_ylabel("Output range (log scale)")
    ax2.set_title("(b) Raw range by nonlinearity")

    _save(fig, "python_sle_fit")
    plt.close(fig)

def plot_cache_invalidation(cache_rows: list) -> None:
    _configure_mpl()
    import matplotlib.pyplot as plt

    sweep = [r for r in cache_rows
             if r.get("case_type") in ("manual_dict", "lru_cache")
             and r.get("steps_between") not in (None, "")]
    observe_row = next(
        (r for r in cache_rows if r.get("case_type") == "observe_invalidation"),
        None,
    )
    if not sweep:
        print("  [plot] No cache invalidation data — skipping plot_cache_invalidation")
        return

    manual = sorted(
        [r for r in sweep if r.get("case_type") == "manual_dict"],
        key=lambda r: int(float(r["steps_between"])),
    )
    lru = sorted(
        [r for r in sweep if r.get("case_type") == "lru_cache"],
        key=lambda r: int(float(r["steps_between"])),
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    if manual:
        steps_m = [int(float(r["steps_between"])) for r in manual]
        err_m = [float(r["cache_error_pct"]) for r in manual]
        ax.plot(steps_m, err_m, marker="o", color=COLORS[0],
                linewidth=1.8, label="Manual dict cache")

    if lru:
        steps_l = [int(float(r["steps_between"])) for r in lru]
        err_l = [float(r["cache_error_pct"]) for r in lru]
        ax.plot(steps_l, err_l, marker="s", color=COLORS[1],
                linewidth=1.8, linestyle="--", label="lru_cache")

    if observe_row:
        obs_err = float(observe_row.get("cache_error_pct", 0))
        ax.axhline(obs_err, color=COLORS[2], linewidth=1.5, linestyle=":",
                   label=f"Observe-invalidation ({obs_err:.2f}%)")

    ax.set_xlabel("Intervening read steps between cache population and hit")
    ax.set_ylabel("Cache error (%)")
    ax.set_title("Cache staleness: error % vs intervening drift steps")
    ax.legend(fontsize=9)

    _save(fig, "python_cache_invalidation")
    plt.close(fig)

def plot_a3_analogue(rows: list) -> None:
    _configure_mpl()
    import matplotlib.pyplot as plt

    a3 = sorted(
        [r for r in rows if r.get("axis") == "A3_py"],
        key=lambda r: int(r.get("steps", 0)),
    )
    if len(a3) < 2:
        print("  [plot] Insufficient A3 data — skipping plot_a3_analogue")
        return

    steps = [int(r["steps"]) for r in a3]
    stds = [float(r["std"]) for r in a3]
    marginals = [stds[i + 1] - stds[i] for i in range(len(stds) - 1)]
    marginal_labels = [f"{steps[i]}→{steps[i+1]}" for i in range(len(steps) - 1)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.plot(steps, stds, marker="o", color=COLORS[0], linewidth=1.8)
    ax1.set_xlabel("Add steps")
    ax1.set_ylabel("Standard deviation")
    ax1.set_title("(a) Std vs program length")

    bar_colors = [COLORS[0] if m >= 0 else COLORS[1] for m in marginals]
    ax2.bar(marginal_labels, marginals, color=bar_colors, alpha=0.85)
    ax2.set_xlabel("Step transition")
    ax2.set_ylabel("Δ Std")
    ax2.set_title("(b) Marginal Δstd (non-decreasing = compounding)")
    ax2.tick_params(axis="x", rotation=30)

    _save(fig, "python_a3_length_scaling")
    plt.close(fig)

def plot_all(descriptor_rows: list = None, sle_rows: list = None,
             cache_rows: list = None, sweep_rows: list = None) -> None:
    from analysis.summarize import _summarize_descriptor_raw, _summarize_sle_raw, _summarize_cache_raw

    d_rows = descriptor_rows if descriptor_rows is not None else _summarize_descriptor_raw()
    s_rows = sle_rows if sle_rows is not None else _summarize_sle_raw()
    if sweep_rows:
        s_rows = sweep_rows
    c_rows = cache_rows if cache_rows is not None else _summarize_cache_raw()

    for fn, args, name in [
        (plot_a1_analogue, (d_rows,), "plot_a1_analogue"),
        (plot_sle, (s_rows,), "plot_sle"),
        (plot_cache_invalidation, (c_rows,), "plot_cache_invalidation"),
        (plot_a3_analogue, (d_rows,), "plot_a3_analogue"),
    ]:
        try:
            fn(*args)
        except Exception as exc:
            print(f"  [plot] {name} failed: {exc}")
