import csv
import math
import statistics
from pathlib import Path

try:
    import config
    RAW_DIR = config.RESULTS_RAW_DIR
    SUMMARY_DIR = config.RESULTS_SUMMARY_DIR
    LOGS_DIR = config.RESULTS_LOGS_DIR
except ImportError:
    RAW_DIR = Path("real_world_validation/results/raw")
    SUMMARY_DIR = Path("real_world_validation/results/summary")
    LOGS_DIR = Path("real_world_validation/results/logs")

def compute_stats(values: list) -> dict:
    n = len(values)
    if n == 0:
        return {"mean": None, "std": None, "min": None, "max": None,
                "range": None, "log_range": None, "cv": None, "variance": None, "n": 0}
    if n == 1:
        return {"mean": round(values[0], 4), "std": 0.0, "min": round(values[0], 4),
                "max": round(values[0], 4), "range": 0.0, "log_range": 0.0,
                "cv": 0.0, "variance": 0.0, "n": 1}
    mean_ = statistics.mean(values)
    std_ = statistics.stdev(values)
    var_ = statistics.variance(values)
    min_ = min(values)
    max_ = max(values)
    range_ = max_ - min_
    log_range = math.log(range_) if range_ > 1.0 else 0.0
    cv = std_ / abs(mean_) if mean_ != 0 else float("inf")
    return {
        "mean": round(mean_, 4),
        "std": round(std_, 4),
        "min": round(min_, 4),
        "max": round(max_, 4),
        "range": round(range_, 4),
        "log_range": round(log_range, 6),
        "cv": round(cv, 6),
        "variance": round(var_, 4),
        "n": n,
    }

def _read_raw_csv(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        values = []
        for row in reader:
            try:
                values.append(float(row["value"]))
            except (KeyError, ValueError):
                continue
    return values

def _read_csv_rows(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_summary_csv(rows: list, path: Path) -> None:
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = sorted({key for row in rows for key in row.keys()})

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"  -> {path} written ({len(rows)} rows)")

def _summarize_descriptor_raw() -> list:
    rows = []
    try:
        import config
        observe_counts = config.OBSERVE_COUNTS
        step_counts = config.STEP_COUNTS
    except ImportError:
        observe_counts = [0, 1, 2, 3, 4, 5]
        step_counts = [3, 6, 9, 12, 15, 20]

    for obs in observe_counts:
        for mode in ("shuffled", "cached"):
            path = RAW_DIR / f"descriptor_a1_obs{obs}_{mode}.csv"
            values = _read_raw_csv(path)
            if not values:
                continue
            stats = compute_stats(values)
            rows.append({
                "experiment": "descriptor_a1",
                "axis": "A1_py",
                "config": f"obs_{obs}",
                "observes": obs,
                "steps": 6,
                "nonlinearity": "quadratic",
                "access_mode": mode,
                **stats,
            })

    for steps in step_counts:
        path = RAW_DIR / f"descriptor_a3_steps{steps}.csv"
        values = _read_raw_csv(path)
        if not values:
            continue
        stats = compute_stats(values)
        rows.append({
            "experiment": "descriptor_a3",
            "axis": "A3_py",
            "config": f"steps_{steps}",
            "observes": 1,
            "steps": steps,
            "nonlinearity": "quadratic",
            "access_mode": "shuffled",
            **stats,
        })
    return rows

def _summarize_sle_raw() -> list:
    try:
        import config
        levels = config.NONLINEARITY_LEVELS
    except ImportError:
        levels = ["linear", "quadratic", "cubic", "extreme"]

    degree_map = {"linear": 1, "quadratic": 2, "cubic": 3, "extreme": 4}
    rows = []
    for nonlin in levels:
        path = RAW_DIR / f"sle_nonlin_{nonlin}.csv"
        values = _read_raw_csv(path)
        if not values:
            continue
        stats = compute_stats(values)
        rows.append({
            "experiment": "sle_sweep",
            "nonlinearity": nonlin,
            "degree": degree_map.get(nonlin, 0),
            **stats,
        })

    if len(rows) >= 2:
        from analysis.sle_fit import fit_sle
        degrees = [r["degree"] for r in rows if r.get("log_range", 0) > 0]
        log_ranges = [r["log_range"] for r in rows if r.get("log_range", 0) > 0]
        if len(degrees) >= 2:
            sle, r2 = fit_sle(degrees, log_ranges)
            for r in rows:
                r["sle"] = sle
                r["r_squared"] = r2
    return rows

def _summarize_cache_raw() -> list:
    path = RAW_DIR / "cache_invalidation_cases.csv"
    raw_rows = _read_csv_rows(path)
    summary = []
    for row in raw_rows:
        summary.append({
            "experiment": "cache_invalidation",
            "case_type": row.get("case_type", ""),
            "steps_between": row.get("steps_between", ""),
            "observe_count": row.get("observe_count", ""),
            "cached_result": row.get("cached_result", ""),
            "true_result": row.get("true_result", ""),
            "cache_error": row.get("cache_error", ""),
            "cache_error_pct": row.get("cache_error_pct", ""),
        })
    return summary

def _write_findings_txt(descriptor_rows: list, sle_rows: list,
                        cache_rows: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("=" * 68)
    lines.append("  ORDERED CHAOS — PYTHON RUNTIME VALIDATION FINDINGS")
    lines.append("=" * 68)
    lines.append("")

    lines.append("FINDING 1 — Descriptor Access Drift (A1 Analogue)")
    lines.append("-" * 48)
    a1_shuffled = [r for r in descriptor_rows
                   if r.get("axis") == "A1_py" and r.get("access_mode") == "shuffled"]
    a1_cached = [r for r in descriptor_rows
                 if r.get("axis") == "A1_py" and r.get("access_mode") == "cached"]
    for row in sorted(a1_shuffled, key=lambda r: int(r.get("observes", 0))):
        lines.append(f"  obs={row['observes']} shuffled: std={row['std']}  range={row['range']}")
    lines.append("")
    for row in sorted(a1_cached, key=lambda r: int(r.get("observes", 0))):
        lines.append(f"  obs={row['observes']} cached:   std={row['std']}  range={row['range']}")
    lines.append("")

    lines.append("FINDING 2 — SLE on Python Substrate (A2 Analogue)")
    lines.append("-" * 48)
    sle_val = next((r.get("sle") for r in sle_rows if r.get("sle")), "N/A")
    r2_val = next((r.get("r_squared") for r in sle_rows if r.get("r_squared")), "N/A")
    lines.append(f"  SLE = {sle_val}  R² = {r2_val}")
    for row in sorted(sle_rows, key=lambda r: int(r.get("degree", 0))):
        lines.append(f"  {row['nonlinearity']:<12}: range={row['range']}  log(range)={row['log_range']}")
    lines.append("")

    lines.append("FINDING 3 — Program Length Scaling (A3 Analogue)")
    lines.append("-" * 48)
    a3_rows = [r for r in descriptor_rows if r.get("axis") == "A3_py"]
    for row in sorted(a3_rows, key=lambda r: int(r.get("steps", 0))):
        lines.append(f"  steps={row['steps']:>2}: std={row['std']}  range={row['range']}")
    lines.append("")

    lines.append("FINDING 4 — Cache Invalidation")
    lines.append("-" * 48)
    for row in cache_rows:
        label = f"{row['case_type']} steps={row['steps_between']}"
        lines.append(f"  {label:<35}: error%={row['cache_error_pct']}")
    lines.append("")

    lines.append("=" * 68)
    lines.append("  END OF FINDINGS")
    lines.append("=" * 68)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  -> {path} written")

def summarize_all(descriptor_rows: list = None, sle_result_dict: dict = None,
                  cache_rows: list = None) -> dict:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    desc_rows = descriptor_rows if descriptor_rows is not None else _summarize_descriptor_raw()
    sle_rows = _summarize_sle_raw()
    c_rows = cache_rows if cache_rows is not None else _summarize_cache_raw()

    write_summary_csv(desc_rows, SUMMARY_DIR / "descriptor_experiments.csv")
    write_summary_csv(sle_rows, SUMMARY_DIR / "sle_sweep_summary.csv")
    write_summary_csv(c_rows, SUMMARY_DIR / "cache_invalidation_summary.csv")

    merged = []
    for r in desc_rows:
        merged.append({"source": "descriptor", **r})
    for r in sle_rows:
        merged.append({"source": "sle", **r})
    for r in c_rows:
        merged.append({"source": "cache", **r})
    write_summary_csv(merged, SUMMARY_DIR / "all_experiments_merged.csv")

    _write_findings_txt(desc_rows, sle_rows, c_rows,
                        LOGS_DIR / "findings_python.txt")

    return {
        "descriptor_rows": desc_rows,
        "sle_rows": sle_rows,
        "cache_rows": c_rows,
    }
