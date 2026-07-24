import subprocess
import random
import statistics
import csv
import os
import math
import json
import sys
import io
from contextlib import redirect_stdout

from src.parser import parse as hn_parse
from src.runtime import Runtime

try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm...")
    subprocess.run([sys.executable, "-m", "pip", "install", "tqdm"], check=True)
    from tqdm import tqdm

NUM_RUNS     = 100_000
RESULTS_DIR  = "results"
CHECKPOINT   = os.path.join(RESULTS_DIR, "checkpoint.json")

os.makedirs(RESULTS_DIR, exist_ok=True)

TEMPLATE = """\
energy[100]

x <- 10
y <- 0

{BODY}

print y
"""

ALL_CONFIGS = [
    ("A1", "A1_inspect0", 6,  0, "quadratic"),
    ("A1", "A1_inspect1", 6,  1, "quadratic"),
    ("A1", "A1_inspect2", 6,  2, "quadratic"),
    ("A1", "A1_inspect3", 6,  3, "quadratic"),
    ("A1", "A1_inspect4", 6,  4, "quadratic"),
    ("A1", "A1_inspect5", 6,  5, "quadratic"),

    ("A2", "A2_linear",    6, 1, "linear"),
    ("A2", "A2_quadratic", 6, 1, "quadratic"),
    ("A2", "A2_cubic",     6, 1, "cubic"),
    ("A2", "A2_extreme",   6, 1, "extreme"),

    ("A3", "A3_steps3",  3,  1, "quadratic"),
    ("A3", "A3_steps6",  6,  1, "quadratic"),
    ("A3", "A3_steps9",  9,  1, "quadratic"),
    ("A3", "A3_steps12", 12, 1, "quadratic"),
    ("A3", "A3_steps15", 15, 1, "quadratic"),
    ("A3", "A3_steps20", 20, 1, "quadratic"),

    ("A4", "A4_low",    3,  0, "linear"),
    ("A4", "A4_medium", 9,  2, "quadratic"),
    ("A4", "A4_high",   20, 5, "extreme"),

    ("A4", "A4_max_inspect_only", 6,  5, "quadratic"),
    ("A4", "A4_max_nonlin_only",  6,  1, "extreme"),
    ("A4", "A4_max_length_only",  20, 1, "quadratic"),
]

NONLINEAR_LINE = {
    "linear":    None,
    "quadratic": "y <- y * x",
    "cubic":     "y <- y * x * x",
    "extreme":   "y <- y * y * x",
}

def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT) as f:
            return json.load(f)
    return {}

def save_checkpoint(done: dict):
    with open(CHECKPOINT, "w") as f:
        json.dump(done, f, indent=2)

def build_body(add_steps, inspect_count, nonlinearity):
    lines = (["y <- y + x"] * add_steps) + (["inspect x"] * inspect_count)
    random.shuffle(lines)
    inspect_positions = [i for i, l in enumerate(lines) if l == "inspect x"]
    nl = NONLINEAR_LINE[nonlinearity]
    if nl:
        lines.append(nl)
    return "\n".join(lines), inspect_positions

def run_program(body):
    program = TEMPLATE.format(BODY=body)
    try:
        ast   = hn_parse(program)
        rt    = Runtime()
        buf   = io.StringIO()
        with redirect_stdout(buf):
            rt.run(ast)
        output = buf.getvalue().strip().split("\n")
        for line in reversed(output):
            try:
                return float(line)
            except Exception:
                continue
        return None
    except Exception:
        return None

def deciles(data):
    s = sorted(data)
    n = len(s)
    out = {}
    for d in range(0, 11):
        idx = min(int(d / 10 * n), n - 1)
        out[f"p{d*10}"] = round(s[idx], 4)
    return out

def compute_stats(results, inspect_pos_list, add_steps):
    if not results:
        return {
            "min": None, "max": None, "mean": None, "std": None,
            "range": None, "log_range": None, "cv": None, "skewness": None,
            "n_valid": 0, "frac_inspect_early": None,
            **{f"p{d*10}": None for d in range(11)},
        }

    mn   = min(results)
    mx   = max(results)
    mean = statistics.mean(results)
    std  = statistics.stdev(results) if len(results) > 1 else 0.0
    rng  = mx - mn
    cv   = (std / abs(mean)) if mean != 0 else float("inf")
    log_range = math.log(rng) if rng > 1 else 0.0

    n_r  = len(results)
    skew = 0.0
    if std > 0:
        skew = (sum((x - mean) ** 3 for x in results) / n_r) / (std ** 3)

    if inspect_pos_list and add_steps > 0:
        early_count = sum(
            1 for positions in inspect_pos_list
            if positions and max(positions) < add_steps / 2
        )
        frac_early = round(early_count / len(inspect_pos_list), 4)
    else:
        frac_early = None

    return {
        "min":                round(mn, 4),
        "max":                round(mx, 4),
        "mean":               round(mean, 4),
        "std":                round(std, 4),
        "range":              round(rng, 4),
        "log_range":          round(log_range, 6),
        "cv":                 round(cv, 6),
        "skewness":           round(skew, 6),
        "n_valid":            n_r,
        "frac_inspect_early": frac_early,
        **deciles(results),
    }

SUMMARY_FIELDS = [
    "axis", "config", "add_steps", "inspects", "nonlinear", "n_valid",
    "min", "max", "mean", "std", "range", "log_range", "cv", "skewness",
    "frac_inspect_early",
    "p0","p10","p20","p30","p40","p50","p60","p70","p80","p90","p100",
]

def append_to_summary(row):
    path = os.path.join(RESULTS_DIR, "summary.csv")
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in SUMMARY_FIELDS})

def save_axis_csv(axis_label, rows):
    path = os.path.join(RESULTS_DIR, f"{axis_label}.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in SUMMARY_FIELDS})

def save_raw_values(values, config_label):
    path = os.path.join(RESULTS_DIR, f"raw_{config_label}.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["value"])
        for v in values:
            writer.writerow([round(v, 6)])

def sanity_check():
    print("\n── Sanity checks ──")

    smoke_body = "y <- y + x\ny <- y * x"
    smoke_val  = run_program(smoke_body)
    if smoke_val != 111.0:
        print(f"  ✗ FATAL — interpreter smoke test failed.")
        print(f"    Expected 111.0, got {smoke_val!r}")
        print("    Is the src/ directory reachable from this working directory?")
        sys.exit(1)
    print(f"  ✓ Interpreter smoke test passed (got {smoke_val})")

    vals = []
    for _ in range(3):
        random.seed(42)
        body, _ = build_body(6, 1, "quadratic")
        vals.append(run_program(body))
    if len(set(vals)) == 1:
        print(f"  ✓ Determinism confirmed: 3 identical seeds → {vals[0]}")
    else:
        print(f"  ✗ WARNING — non-determinism detected across seeds: {vals}")
        print("    Interpreter may have non-deterministic behaviour.")
        sys.exit(1)

def run_config(axis, label, add_steps, inspect_count, nonlinearity,
               global_bar, config_bar):
    results          = []
    inspect_pos_list = []
    errors           = 0

    config_bar.reset(total=NUM_RUNS)
    config_bar.set_description(f"{label:<28}")

    for _ in range(NUM_RUNS):
        body, positions = build_body(add_steps, inspect_count, nonlinearity)
        val = run_program(body)
        if val is not None:
            results.append(val)
            inspect_pos_list.append(positions)
        else:
            errors += 1
        config_bar.update(1)
        global_bar.update(1)

    stats = compute_stats(results, inspect_pos_list, add_steps)

    row = {
        "axis":      axis,
        "config":    label,
        "add_steps": add_steps,
        "inspects":  inspect_count,
        "nonlinear": nonlinearity,
        **stats,
    }

    save_raw_values(results, label)
    append_to_summary(row)

    if errors:
        tqdm.write(f"  ⚠  {label}: {errors} failed runs (excluded from stats)")

    tqdm.write(
        f"  ✓ {label:<28} | "
        f"mean={stats['mean']:>10.2f}  "
        f"std={stats['std']:>10.2f}  "
        f"range={stats['range']:>10.2f}  "
        f"log(range)={stats['log_range']:>7.3f}  "
        f"skew={stats['skewness']:>7.3f}"
    )

    return row

def compute_lyapunov(done: dict) -> dict:
    order = ["A2_linear", "A2_quadratic", "A2_cubic", "A2_extreme"]
    degrees = [1, 2, 3, 4]

    rows = []
    for label in order:
        if label in done:
            r = done[label].get("range")
            if r is not None and float(r) > 1:
                rows.append((label, float(r)))
            else:
                rows.append((label, None))
        else:
            rows.append((label, None))

    valid = [(deg, math.log(r)) for deg, (_, r) in zip(degrees, rows) if r is not None]

    if len(valid) < 2:
        return {"sle": None, "note": "Insufficient A2 data to compute SLE."}

    xs = [v[0] for v in valid]
    ys = [v[1] for v in valid]
    n  = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    numerator   = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = sum((x - x_mean) ** 2 for x in xs)

    slope = numerator / denominator if denominator != 0 else 0.0
    ss_res = sum((y - (y_mean + slope * (x - x_mean))) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

    return {
        "sle":            round(slope, 6),
        "r_squared":      round(r2, 6),
        "data_points":    [(order[i], round(math.log(r), 4)) if r else (order[i], None)
                           for i, (_, r) in enumerate(rows)],
        "note": (
            f"Slope of log(range) per nonlinearity degree = {slope:.4f} "
            f"(R²={r2:.4f}). "
            + ("Positive slope confirms exponential range growth with nonlinearity."
               if slope > 0 else "Non-positive slope — check A2 data.")
        ),
    }

def compute_superadditivity(done: dict) -> dict:
    keys = {
        "combined":        "A4_high",
        "isolated_inspect": "A4_max_inspect_only",
        "isolated_nonlin":  "A4_max_nonlin_only",
        "isolated_length":  "A4_max_length_only",
    }

    vals = {}
    for name, label in keys.items():
        if label in done:
            s = done[label].get("std")
            vals[name] = float(s) if s is not None else None
        else:
            vals[name] = None

    if any(v is None for v in vals.values()):
        missing = [k for k, v in vals.items() if v is None]
        return {
            "superadditive": None,
            "note": f"Cannot test — missing configs: {missing}",
            "values": vals,
        }

    sum_isolated = vals["isolated_inspect"] + vals["isolated_nonlin"] + vals["isolated_length"]
    combined     = vals["combined"]
    is_super     = combined > sum_isolated
    ratio        = combined / sum_isolated if sum_isolated != 0 else float("inf")

    return {
        "superadditive":      is_super,
        "std_combined":       round(combined, 4),
        "std_sum_isolated":   round(sum_isolated, 4),
        "ratio":              round(ratio, 4),
        "std_inspect_only":   round(vals["isolated_inspect"], 4),
        "std_nonlin_only":    round(vals["isolated_nonlin"], 4),
        "std_length_only":    round(vals["isolated_length"], 4),
        "note": (
            f"std(combined)={combined:.4f} vs "
            f"sum(isolated)={sum_isolated:.4f} → "
            f"ratio={ratio:.4f}. "
            + ("SUPERADDITIVE — factors compound beyond independent effects. "
               "This confirms multiplicative interaction between observation, "
               "nonlinearity, and program length."
               if is_super else
               "NOT superadditive — factors appear to act independently. "
               "Check A4 config design.")
        ),
    }

def write_findings(done: dict, lyapunov: dict, superadd: dict) -> None:
    lines = []
    lines.append("=" * 68)
    lines.append("  ORDERED CHAOS — KEY FINDINGS")
    lines.append("  Auto-generated from experimental results")
    lines.append("=" * 68)
    lines.append("")

    lines.append("FINDING 1 — Observation multiplicity (Axis A1)")
    lines.append("-" * 48)
    a1_rows = sorted(
        [(label, done[label]) for label in done if label.startswith("A1_")],
        key=lambda x: int(x[0].replace("A1_inspect", ""))
    )
    if a1_rows:
        stds   = [(label, float(row["std"])) for label, row in a1_rows if row.get("std") is not None]
        ranges = [(label, float(row["range"])) for label, row in a1_rows if row.get("range") is not None]
        for label, std in stds:
            n = label.replace("A1_inspect", "")
            lines.append(f"  {n} inspect(s): std = {std:.4f}")
        if len(stds) >= 2:
            growth = stds[-1][1] / stds[1][1] if stds[1][1] > 0 else float("inf")
            lines.append(f"")
            lines.append(f"  std growth from 1→{len(stds)-1} inspects: {growth:.2f}x")
            trend = "super-linear" if growth > len(stds) - 1 else "sub-linear or linear"
            lines.append(f"  Growth is {trend} (expected: super-linear if chaotic).")
    else:
        lines.append("  No A1 data available.")
    lines.append("")

    lines.append("FINDING 2 — Semantic Lyapunov Exponent (Axis A2)")
    lines.append("-" * 48)
    if lyapunov.get("sle") is not None:
        lines.append(f"  SLE (slope of log(range) per nonlinearity degree): {lyapunov['sle']:.6f}")
        lines.append(f"  R² of log-linear fit: {lyapunov['r_squared']:.6f}")
        lines.append(f"  Data points (config, log(range)):")
        for label, val in lyapunov["data_points"]:
            lines.append(f"    {label:<22}: log(range) = {val}")
        lines.append(f"")
        lines.append(f"  Interpretation: {lyapunov['note']}")
    else:
        lines.append(f"  {lyapunov.get('note', 'No data.')}")

    a2_rows = {label: done[label] for label in done if label.startswith("A2_")}
    if a2_rows:
        lines.append("")
        lines.append("  Raw ranges by nonlinearity level:")
        for label in ["A2_linear", "A2_quadratic", "A2_cubic", "A2_extreme"]:
            if label in a2_rows:
                r = a2_rows[label].get("range", "N/A")
                lines.append(f"    {label:<22}: range = {r}")
    lines.append("")

    lines.append("FINDING 3 — Program length scaling (Axis A3)")
    lines.append("-" * 48)
    a3_rows = sorted(
        [(label, done[label]) for label in done if label.startswith("A3_")],
        key=lambda x: int(x[0].replace("A3_steps", ""))
    )
    if a3_rows:
        stds = [(label, float(row["std"])) for label, row in a3_rows if row.get("std") is not None]
        for label, std in stds:
            n = label.replace("A3_steps", "")
            lines.append(f"  {n:>2} add steps: std = {std:.4f}")
        if len(stds) >= 3:
            diffs = [stds[i+1][1] - stds[i][1] for i in range(len(stds)-1)]
            if diffs[-1] < diffs[0]:
                lines.append("")
                lines.append("  Marginal std increases are DECREASING with length.")
                lines.append("  This indicates a plateau — diminishing sensitivity beyond")
                lines.append("  a critical program length. Consistent with bounded drift.")
            else:
                lines.append("")
                lines.append("  Marginal std increases are NON-DECREASING — no plateau detected.")
    else:
        lines.append("  No A3 data available.")
    lines.append("")

    lines.append("FINDING 4 — Interaction superadditivity (Axis A4)")
    lines.append("-" * 48)
    if superadd.get("superadditive") is not None:
        lines.append(f"  std(combined high config) : {superadd['std_combined']:.4f}")
        lines.append(f"  std(max inspect only)     : {superadd['std_inspect_only']:.4f}")
        lines.append(f"  std(max nonlin only)      : {superadd['std_nonlin_only']:.4f}")
        lines.append(f"  std(max length only)      : {superadd['std_length_only']:.4f}")
        lines.append(f"  Sum of isolated stds      : {superadd['std_sum_isolated']:.4f}")
        lines.append(f"  Ratio (combined/sum)      : {superadd['ratio']:.4f}")
        lines.append("")
        lines.append(f"  Result: {'SUPERADDITIVE' if superadd['superadditive'] else 'NOT SUPERADDITIVE'}")
        lines.append(f"  {superadd['note']}")
    else:
        lines.append(f"  {superadd.get('note', 'No A4 data.')}")
    lines.append("")

    lines.append("=" * 68)
    lines.append("  END OF FINDINGS")
    lines.append("=" * 68)

    path = os.path.join(RESULTS_DIR, "findings.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    findings_json = {
        "lyapunov":       lyapunov,
        "superadditivity": superadd,
    }
    json_path = os.path.join(RESULTS_DIR, "findings.json")
    with open(json_path, "w") as f:
        json.dump(findings_json, f, indent=2)

    print(f"  → findings.txt written")
    print(f"  → findings.json written")

if __name__ == "__main__":
    total_configs = len(ALL_CONFIGS)
    total_runs    = total_configs * NUM_RUNS

    print("=" * 68)
    print("  Ordered Chaos — Experiment Battery")
    print(f"  Configs : {total_configs}")
    print(f"  Runs/cfg: {NUM_RUNS:,}")
    print(f"  Total   : {total_runs:,} executions")
    print(f"  Output  : ./{RESULTS_DIR}/")
    print("=" * 68)

    sanity_check()

    done      = load_checkpoint()
    remaining = [c for c in ALL_CONFIGS if c[1] not in done]
    n_done    = total_configs - len(remaining)

    if n_done:
        print(f"\n  Resuming — {n_done}/{total_configs} config(s) already complete.")

    axis_rows = {}
    for label, row in done.items():
        ax = row.get("axis")
        if ax:
            axis_rows.setdefault(ax, []).append(row)

    global_bar = tqdm(
        total=total_runs,
        initial=n_done * NUM_RUNS,
        desc="Overall   ",
        unit="run",
        position=0,
        colour="green",
        dynamic_ncols=True,
    )
    config_bar = tqdm(
        total=NUM_RUNS,
        desc="Config    ",
        unit="run",
        position=1,
        colour="cyan",
        dynamic_ncols=True,
        leave=False,
    )

    try:
        for (axis, label, add_steps, inspects, nonlinearity) in remaining:
            row = run_config(
                axis, label, add_steps, inspects, nonlinearity,
                global_bar, config_bar,
            )
            axis_rows.setdefault(axis, []).append(row)

            done[label] = row
            save_checkpoint(done)

        for axis_label, rows in axis_rows.items():
            save_axis_csv(axis_label, rows)
            tqdm.write(f"  → {axis_label}.csv written ({len(rows)} configs)")

    except KeyboardInterrupt:
        tqdm.write("\n\n  ⚡ Interrupted by user.")
        tqdm.write(f"  All completed configs are saved in ./{RESULTS_DIR}/")
        tqdm.write(f"  Checkpoint at: {CHECKPOINT}")
        tqdm.write("  Re-run the script anytime to resume.")

    finally:
        config_bar.close()
        global_bar.close()

    print("\n── Post-run analysis ──")
    lyapunov  = compute_lyapunov(done)
    superadd  = compute_superadditivity(done)
    write_findings(done, lyapunov, superadd)

    print(f"\n  Semantic Lyapunov Exponent : {lyapunov.get('sle', 'N/A')}")
    print(f"  SLE R²                     : {lyapunov.get('r_squared', 'N/A')}")
    sa = superadd.get('superadditive')
    print(f"  Superadditivity confirmed  : {sa}")
    if superadd.get('ratio') is not None:
        print(f"  Combined/sum(isolated) σ   : {superadd['ratio']:.4f}x")

    print("\n" + "=" * 68)
    print(f"  Complete. Results in ./{RESULTS_DIR}/")
    print(f"  summary.csv        — one row per config (appended live)")
    print(f"  raw_<config>.csv   — full {NUM_RUNS:,} values per config")
    print(f"  A1/A2/A3/A4.csv    — per-axis summaries")
    print(f"  findings.txt       — key results in plain English")
    print(f"  findings.json      — findings as structured data")
    print(f"  checkpoint.json    — resume state")
    print("=" * 68)
