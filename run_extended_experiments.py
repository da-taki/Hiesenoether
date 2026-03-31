"""
run_extended_experiments.py — Extended Experiment Battery (E1–E5)
=================================================================
E1: Extended Degree Sweep (degrees 1–8 + self-referential)
E2: Entropy Parameter Sensitivity (e0 × de grid)
E3: Full Measured Ablation (noop_inspect, no_entropy, fixed_order)
E4: Entropy Decay / Collapse Sweep (constant, linear_decay, exponential_decay)
E5: Length Scaling Extension (steps up to 100)

All configs use deterministic seeds.
All outputs are backward-compatible with existing summary.csv schema.
"""

import random
import statistics
import csv
import os
import math
import json
import itertools
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results_extended")
os.makedirs(RESULTS_DIR, exist_ok=True)

GLOBAL_SEED = 42
NUM_RUNS = 100_000

NONLIN_SEEDS = {
    "linear": 101,
    "quadratic": 102,
    "cubic": 103,
    "extreme": 104,
    "degree_5": 105,
    "degree_6": 106,
    "degree_7": 107,
    "degree_8": 108,
    "self_ref_yyx2": 109,
    "self_ref_yyy_x": 110,
}

SCHEDULE_SEEDS = {
    "constant": 201,
    "linear_decay": 202,
    "exponential_decay": 203,
}


# ─────────────────────────────────────────────
# Core model (parameterized)
# ─────────────────────────────────────────────

class UnstableValue:
    def __init__(self, base, initial_entropy=1.0, entropy_increment=0.1,
                 schedule="constant", beta=0.0):
        self.base = base
        self.access_count = 0
        self.initial_entropy = initial_entropy
        self.entropy = initial_entropy
        self.entropy_increment = entropy_increment
        self.schedule = schedule   # "constant" | "linear_decay" | "exponential_decay"
        self.beta = beta           # decay parameter

    def _current_increment(self):
        if self.schedule == "constant":
            return self.entropy_increment
        elif self.schedule == "linear_decay":
            # increment decays linearly: de * max(0, 1 - beta * access_count)
            return self.entropy_increment * max(0.0, 1.0 - self.beta * self.access_count)
        elif self.schedule == "exponential_decay":
            # increment decays exponentially: de * exp(-beta * access_count)
            return self.entropy_increment * math.exp(-self.beta * self.access_count)
        return self.entropy_increment

    def get(self):
        drift = self.access_count * self.entropy
        value = self.base + drift
        self.access_count += 1
        self.entropy += self._current_increment()
        return value

    def inspect(self):
        self.entropy += 1.0


class UnstableValueNoEntropy:
    """Ablation: entropy never grows — fixed entropy throughout."""
    def __init__(self, base, initial_entropy=1.0):
        self.base = base
        self.access_count = 0
        self.entropy = initial_entropy

    def get(self):
        drift = self.access_count * self.entropy
        value = self.base + drift
        self.access_count += 1
        # entropy does NOT increment
        return value

    def inspect(self):
        self.entropy += 1.0


# ─────────────────────────────────────────────
# Nonlinearity caps (extended)
# ─────────────────────────────────────────────

def apply_nonlinearity(y, x_obj, nonlinearity):
    if nonlinearity == "linear":
        return y
    elif nonlinearity == "quadratic":
        return y * x_obj.get()
    elif nonlinearity == "cubic":
        return y * x_obj.get() * x_obj.get()
    elif nonlinearity == "extreme":
        return y * y * x_obj.get()
    # E1 extended degrees — each x_obj.get() is a distinct access-sensitive read
    elif nonlinearity == "degree_5":
        return y * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get()        # y * x1*x2*x3*x4
    elif nonlinearity == "degree_6":
        return y * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get()  # y * x1..x5
    elif nonlinearity == "degree_7":
        return y * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get()  # y * x1..x6
    elif nonlinearity == "degree_8":
        return y * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get() * x_obj.get()  # y * x1..x7
    elif nonlinearity == "self_ref_yyx2":
        return y * y * x_obj.get() * x_obj.get()   # y^2 * x1 * x2
    elif nonlinearity == "self_ref_yyy_x":
        return y * y * y * x_obj.get()              # y^3 * x1
    raise ValueError(f"Unknown nonlinearity: {nonlinearity}")


# ─────────────────────────────────────────────
# Program execution helpers
# ─────────────────────────────────────────────

def build_order(add_steps, inspect_count, rng=None):
    ops = ["add"] * add_steps + ["inspect"] * inspect_count
    if rng is None:
        rng = random.Random(GLOBAL_SEED)
    rng.shuffle(ops)
    return ops


def run_program_standard(order, nonlinearity, initial_entropy=1.0,
                         entropy_increment=0.1, schedule="constant", beta=0.0):
    x = UnstableValue(10.0, initial_entropy=initial_entropy,
                      entropy_increment=entropy_increment,
                      schedule=schedule, beta=beta)
    y = 0.0
    for op in order:
        if op == "add":
            y += x.get()
        elif op == "inspect":
            x.inspect()
    return apply_nonlinearity(y, x, nonlinearity)


def run_program_ablation_noop_inspect(order, nonlinearity):
    """E3: inspect is a no-op (does not change entropy)."""
    x = UnstableValue(10.0)
    y = 0.0
    for op in order:
        if op == "add":
            y += x.get()
        # inspect deliberately skipped — noop
    return apply_nonlinearity(y, x, nonlinearity)


def run_program_ablation_no_entropy(order, nonlinearity):
    """E3: entropy never grows."""
    x = UnstableValueNoEntropy(10.0)
    y = 0.0
    for op in order:
        if op == "add":
            y += x.get()
        elif op == "inspect":
            x.inspect()
    return apply_nonlinearity(y, x, nonlinearity)


def run_program_ablation_fixed_order(add_steps, inspect_count, nonlinearity):
    """E3: fixed order — all inspects before all adds (no shuffle)."""
    x = UnstableValue(10.0)
    y = 0.0
    for _ in range(inspect_count):
        x.inspect()
    for _ in range(add_steps):
        y += x.get()
    return apply_nonlinearity(y, x, nonlinearity)


# ─────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────

def compute_stats(results):
    if not results:
        return {"mean": None, "std": None, "min": None, "max": None, "range": None,
                "log_range": None, "n": 0}
    n = len(results)
    mean_ = statistics.mean(results)
    std_ = statistics.stdev(results) if n > 1 else 0.0
    mn = min(results)
    mx = max(results)
    rng = mx - mn
    log_range = math.log(rng) if rng > 1.0 else 0.0
    return {
        "mean": round(mean_, 4),
        "std": round(std_, 4),
        "min": round(mn, 4),
        "max": round(mx, 4),
        "range": round(rng, 4),
        "log_range": round(log_range, 6),
        "n": n,
    }


def write_raw(values, name):
    path = os.path.join(RESULTS_DIR, f"raw_{name}.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["value"])
        for v in values:
            writer.writerow([round(v, 6)])


def write_summary(rows, filename):
    if not rows:
        return
    path = os.path.join(RESULTS_DIR, filename)
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {path} written ({len(rows)} rows)")


# ─────────────────────────────────────────────
# E1 — Extended Degree Sweep
# ─────────────────────────────────────────────

E1_NONLINEARITIES = [
    # legacy (preserved)
    ("linear",    1),
    ("quadratic", 2),
    ("cubic",     3),
    ("extreme",   4),
    # extended
    ("degree_5",  5),
    ("degree_6",  6),
    ("degree_7",  7),
    ("degree_8",  8),
    # self-referential
    ("self_ref_yyx2",  9),
    ("self_ref_yyy_x", 10),
]

def run_e1(num_runs=NUM_RUNS):
    rows = []
    for nonlin, degree in tqdm(E1_NONLINEARITIES, desc="E1 degree sweep"):
        rng = random.Random(GLOBAL_SEED ^ NONLIN_SEEDS[nonlin])
        results = []
        for _ in range(num_runs):
            order = build_order(6, 1, rng)
            try:
                v = run_program_standard(order, nonlin)
                if math.isfinite(v):
                    results.append(v)
            except Exception:
                pass
        stats = compute_stats(results)
        write_raw(results, f"e1_nonlin_{nonlin}")
        rows.append({
            "experiment": "E1",
            "config": f"e1_{nonlin}",
            "nonlinearity": nonlin,
            "degree": degree,
            "steps": 6,
            "inspects": 1,
            **stats,
        })
        tqdm.write(f"  E1 {nonlin:<20} deg={degree}  range={stats['range']}  log(range)={stats['log_range']}")

    # Fit SLE over all valid degrees
    valid = [(r["degree"], r["log_range"]) for r in rows
             if r["log_range"] and float(r["log_range"]) > 0]
    if len(valid) >= 2:
        xs = [v[0] for v in valid]
        ys = [v[1] for v in valid]
        n = len(xs)
        xm = sum(xs) / n
        ym = sum(ys) / n
        num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
        den = sum((x - xm) ** 2 for x in xs)
        sle = num / den if den else 0.0
        ss_res = sum((y - (ym + sle * (x - xm))) ** 2 for x, y in zip(xs, ys))
        ss_tot = sum((y - ym) ** 2 for y in ys)
        r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
        for row in rows:
            row["sle_e1"] = round(sle, 6)
            row["r2_e1"] = round(r2, 6)
        print(f"  E1 SLE (all degrees): {sle:.4f}  R²={r2:.4f}")

    write_summary(rows, "e1_extended_degree_sweep.csv")

    # Also write SLE data file for downstream use
    sle_rows = [{"degree": r["degree"], "nonlinearity": r["nonlinearity"],
                 "log_range": r["log_range"], "range": r["range"],
                 "sle": r.get("sle_e1"), "r2": r.get("r2_e1")} for r in rows]
    write_summary(sle_rows, "e1_sle_data.csv")
    return rows


# ─────────────────────────────────────────────
# E2 — Entropy Parameter Sensitivity
# ─────────────────────────────────────────────

E2_INITIAL_ENTROPIES = [0.25, 0.5, 1.0, 2.0, 4.0]
E2_ENTROPY_INCREMENTS = [0.02, 0.05, 0.1, 0.2, 0.5]

def run_e2(num_runs=NUM_RUNS):
    rows = []
    grid = list(itertools.product(E2_INITIAL_ENTROPIES, E2_ENTROPY_INCREMENTS))
    for (e0, de) in tqdm(grid, desc="E2 entropy sensitivity"):
        config_name = f"e2_e0_{str(e0).replace('.','p')}_de_{str(de).replace('.','p')}"
        seed = GLOBAL_SEED ^ (int(e0 * 1000) & 0xFFFF) ^ (int(de * 10000) & 0xFFFF)
        rng = random.Random(seed)
        results = []
        for _ in range(num_runs):
            order = build_order(6, 1, rng)
            try:
                v = run_program_standard(order, "quadratic",
                                         initial_entropy=e0,
                                         entropy_increment=de)
                if math.isfinite(v):
                    results.append(v)
            except Exception:
                pass
        stats = compute_stats(results)
        write_raw(results, config_name)
        rows.append({
            "experiment": "E2",
            "config": config_name,
            "nonlinearity": "quadratic",
            "steps": 6,
            "inspects": 1,
            "initial_entropy": e0,
            "entropy_increment": de,
            **stats,
        })
        tqdm.write(f"  E2 e0={e0} de={de}  std={stats['std']}  range={stats['range']}")

    write_summary(rows, "e2_entropy_sensitivity.csv")
    return rows


# ─────────────────────────────────────────────
# E3 — Full Measured Ablation
# ─────────────────────────────────────────────

def run_e3(num_runs=NUM_RUNS):
    rows = []

    # baseline (standard, for comparison)
    rng = random.Random(GLOBAL_SEED)
    baseline_results = []
    for _ in range(num_runs):
        order = build_order(6, 1, rng)
        try:
            v = run_program_standard(order, "quadratic")
            if math.isfinite(v):
                baseline_results.append(v)
        except Exception:
            pass
    baseline_stats = compute_stats(baseline_results)
    write_raw(baseline_results, "e3_baseline")
    rows.append({
        "experiment": "E3",
        "config": "ablation_baseline",
        "ablation": "none",
        "steps": 6, "inspects": 1,
        **baseline_stats,
    })
    tqdm.write(f"  E3 baseline       std={baseline_stats['std']}  range={baseline_stats['range']}")

    # ablation_noop_inspect
    noop_results = []
    rng = random.Random(GLOBAL_SEED + 1)
    for _ in range(num_runs):
        order = build_order(6, 1, rng)
        try:
            v = run_program_ablation_noop_inspect(order, "quadratic")
            if math.isfinite(v):
                noop_results.append(v)
        except Exception:
            pass
    noop_stats = compute_stats(noop_results)
    write_raw(noop_results, "e3_ablation_noop_inspect")
    rows.append({
        "experiment": "E3",
        "config": "ablation_noop_inspect",
        "ablation": "noop_inspect",
        "steps": 6, "inspects": 1,
        **noop_stats,
    })
    tqdm.write(f"  E3 noop_inspect   std={noop_stats['std']}  range={noop_stats['range']}")

    # ablation_no_entropy
    noent_results = []
    rng = random.Random(GLOBAL_SEED + 2)
    for _ in range(num_runs):
        order = build_order(6, 1, rng)
        try:
            v = run_program_ablation_no_entropy(order, "quadratic")
            if math.isfinite(v):
                noent_results.append(v)
        except Exception:
            pass
    noent_stats = compute_stats(noent_results)
    write_raw(noent_results, "e3_ablation_no_entropy")
    rows.append({
        "experiment": "E3",
        "config": "ablation_no_entropy",
        "ablation": "no_entropy",
        "steps": 6, "inspects": 1,
        **noent_stats,
    })
    tqdm.write(f"  E3 no_entropy     std={noent_stats['std']}  range={noent_stats['range']}")

    # ablation_fixed_order
    fixed_results = []
    rng = random.Random(GLOBAL_SEED + 3)  # noqa: F841 — fixed order, rng unused
    for _ in range(num_runs):
        try:
            v = run_program_ablation_fixed_order(6, 1, "quadratic")
            if math.isfinite(v):
                fixed_results.append(v)
        except Exception:
            pass
    fixed_stats = compute_stats(fixed_results)
    write_raw(fixed_results, "e3_ablation_fixed_order")
    rows.append({
        "experiment": "E3",
        "config": "ablation_fixed_order",
        "ablation": "fixed_order",
        "steps": 6, "inspects": 1,
        **fixed_stats,
    })
    tqdm.write(f"  E3 fixed_order    std={fixed_stats['std']}  range={fixed_stats['range']}")

    # Write comparison table
    comp = []
    for row in rows:
        comp.append({
            "config": row["config"],
            "ablation": row["ablation"],
            "std": row["std"],
            "range": row["range"],
            "log_range": row["log_range"],
            "std_vs_baseline": round(float(row["std"] or 0) / float(baseline_stats["std"] or 1), 4),
            "range_vs_baseline": round(float(row["range"] or 0) / float(baseline_stats["range"] or 1), 4),
        })
    write_summary(comp, "e3_ablation_comparison.csv")
    write_summary(rows, "e3_ablation_full.csv")
    return rows


# ─────────────────────────────────────────────
# E4 — Entropy Decay / Collapse Sweep
# ─────────────────────────────────────────────

E4_SCHEDULES = ["constant", "linear_decay", "exponential_decay"]
E4_BETAS = [0.0, 0.05, 0.1, 0.2, 0.5, 1.0]
E4_STEPS = [6, 12, 20, 50]

def run_e4(num_runs=NUM_RUNS):
    rows = []
    configs = [(sched, beta, steps)
               for sched in E4_SCHEDULES
               for beta in E4_BETAS
               for steps in E4_STEPS]
    # skip constant with beta>0 (beta has no effect on constant schedule)
    configs = [(s, b, st) for s, b, st in configs
               if not (s == "constant" and b > 0.0)]

    for (schedule, beta, steps) in tqdm(configs, desc="E4 entropy decay"):
        beta_str = str(beta).replace(".", "p")
        config_name = f"e4_{schedule}_beta_{beta_str}_steps_{steps}"
        seed = GLOBAL_SEED + int(beta * 100) + SCHEDULE_SEEDS[schedule] + steps
        rng = random.Random(seed)
        results = []
        for _ in range(num_runs):
            order = build_order(steps, 1, rng)
            try:
                v = run_program_standard(order, "quadratic",
                                         schedule=schedule, beta=beta)
                if math.isfinite(v):
                    results.append(v)
            except Exception:
                pass
        stats = compute_stats(results)
        write_raw(results, config_name)
        rows.append({
            "experiment": "E4",
            "config": config_name,
            "schedule": schedule,
            "beta": beta,
            "nonlinearity": "quadratic",
            "steps": steps, "inspects": 1,
            **stats,
        })
        tqdm.write(f"  E4 {schedule:<20} beta={beta} steps={steps:<3}  std={stats['std']}  range={stats['range']}")

    # Fix 2: fit log(range) = gamma*log(L) + c per (schedule, beta) group
    from itertools import groupby
    key_fn = lambda r: (r["schedule"], r["beta"])
    sorted_rows = sorted(rows, key=key_fn)
    gamma_map = {}
    for (sched, beta), grp in groupby(sorted_rows, key=key_fn):
        grp = list(grp)
        pts = [(r["steps"], r["log_range"]) for r in grp
               if r["log_range"] and float(r["log_range"]) > 0 and r["steps"] > 0]
        if len(pts) >= 2:
            xs = [math.log(s) for s, _ in pts]
            ys = [float(lr) for _, lr in pts]
            n = len(xs)
            xm = sum(xs) / n
            ym = sum(ys) / n
            num_ = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
            den_ = sum((x - xm) ** 2 for x in xs)
            gamma = num_ / den_ if den_ else 0.0
            ss_res = sum((y - (ym + gamma * (x - xm))) ** 2 for x, y in zip(xs, ys))
            ss_tot = sum((y - ym) ** 2 for y in ys)
            r2g = 1 - ss_res / ss_tot if ss_tot else 0.0
            gamma_map[(sched, beta)] = (round(gamma, 6), round(r2g, 6))
        else:
            gamma_map[(sched, beta)] = (None, None)
    for row in rows:
        g, r2g = gamma_map.get((row["schedule"], row["beta"]), (None, None))
        row["gamma_collapse"] = g
        row["r2_gamma"] = r2g

    write_summary(rows, "e4_entropy_decay_sweep.csv")

    # steps=6 compat subset (mirrors old schema)
    compat_rows = [r for r in rows if r["steps"] == 6]
    write_summary(compat_rows, "e4_entropy_decay_steps6_compat.csv")

    # Per-schedule summaries
    for sched in E4_SCHEDULES:
        sched_rows = [r for r in rows if r["schedule"] == sched]
        if sched_rows:
            write_summary(sched_rows, f"e4_{sched}_summary.csv")
    return rows


# ─────────────────────────────────────────────
# E5 — Length Scaling Extension
# ─────────────────────────────────────────────

# Legacy A3 steps preserved + extended
E5_STEPS = [3, 6, 9, 12, 15, 20, 25, 30, 40, 50, 75, 100]

def run_e5(num_runs=NUM_RUNS):
    rows = []
    for steps in tqdm(E5_STEPS, desc="E5 length scaling"):
        config_name = f"e5_steps_{steps}"
        rng = random.Random(GLOBAL_SEED ^ steps)
        results = []
        for _ in range(num_runs):
            order = build_order(steps, 1, rng)
            try:
                v = run_program_standard(order, "quadratic")
                if math.isfinite(v):
                    results.append(v)
            except Exception:
                pass
        stats = compute_stats(results)
        write_raw(results, config_name)

        rows.append({
            "experiment": "E5",
            "config": config_name,
            "steps": steps,
            "inspects": 1,
            "nonlinearity": "quadratic",
            **stats,
        })
        tqdm.write(f"  E5 steps={steps:<4}  std={stats['std']}  range={stats['range']}")

    # Compute marginal std increments
    stds = [float(r["std"]) for r in rows]
    for i, row in enumerate(rows):
        row["marginal_std"] = None if i == 0 else round(stds[i] - stds[i - 1], 4)

    # Check non-decreasing property for legacy steps
    legacy_steps = [3, 6, 9, 12, 15, 20]
    legacy_stds = [float(r["std"]) for r in rows if r["steps"] in legacy_steps]
    is_nondecreasing = all(legacy_stds[i] <= legacy_stds[i + 1]
                           for i in range(len(legacy_stds) - 1))
    for row in rows:
        row["legacy_nondecreasing"] = is_nondecreasing

    # E5 asymptotic scaling fit: log(std) = alpha * log(L) + c
    valid_fit = [(r["steps"], float(r["std"])) for r in rows
                 if r["std"] and float(r["std"]) > 0]
    alpha_fit = None
    r2_alpha = None
    if len(valid_fit) >= 2:
        xs = [math.log(s) for s, _ in valid_fit]
        ys = [math.log(v) for _, v in valid_fit]
        n = len(xs)
        xm = sum(xs) / n
        ym = sum(ys) / n
        num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
        den = sum((x - xm) ** 2 for x in xs)
        alpha_fit = num / den if den else 0.0
        ss_res = sum((y - (ym + alpha_fit * (x - xm))) ** 2 for x, y in zip(xs, ys))
        ss_tot = sum((y - ym) ** 2 for y in ys)
        r2_alpha = 1 - ss_res / ss_tot if ss_tot else 0.0
        alpha_fit = round(alpha_fit, 6)
        r2_alpha = round(r2_alpha, 6)
        print(f"  E5 power-law fit: alpha={alpha_fit}  R²={r2_alpha}")

    for row in rows:
        row["alpha_fit"] = alpha_fit
        row["r2_alpha_fit"] = r2_alpha

    write_summary(rows, "e5_length_scaling_extended.csv")

    # Backward-compatible A3 subset
    a3_rows = [r for r in rows if r["steps"] in legacy_steps]
    write_summary(a3_rows, "e5_a3_compat.csv")
    return rows


# ─────────────────────────────────────────────
# Master summary
# ─────────────────────────────────────────────

def write_master_summary(e1, e2, e3, e4, e5):
    all_rows = []
    for r in e1:
        all_rows.append({"source": "E1", **r})
    for r in e2:
        all_rows.append({"source": "E2", **r})
    for r in e3:
        all_rows.append({"source": "E3", **r})
    for r in e4:
        all_rows.append({"source": "E4", **r})
    for r in e5:
        all_rows.append({"source": "E5", **r})

    if not all_rows:
        return
    # Union of all keys
    keys = sorted({k for r in all_rows for k in r.keys()})
    path = os.path.join(RESULTS_DIR, "extended_experiments_master.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"  -> {path} written ({len(all_rows)} total rows)")


def write_findings(e1, e2, e3, e4, e5):
    lines = []
    lines.append("=" * 68)
    lines.append("  ORDERED CHAOS — EXTENDED EXPERIMENT FINDINGS (E1–E5)")
    lines.append("=" * 68)
    lines.append("")

    # E1
    lines.append("E1 — Extended Degree Sweep")
    lines.append("-" * 48)
    for r in e1:
        lines.append(f"  {r['nonlinearity']:<22} deg={r['degree']}  range={r['range']}  log(range)={r['log_range']}")
    if e1 and e1[0].get("sle_e1"):
        lines.append(f"  SLE (E1, all degrees): {e1[0]['sle_e1']}  R²={e1[0].get('r2_e1')}")
    lines.append("")

    # E2
    lines.append("E2 — Entropy Parameter Sensitivity")
    lines.append("-" * 48)
    if e2:
        stds = [(r["initial_entropy"], r["entropy_increment"], r["std"]) for r in e2]
        max_row = max(stds, key=lambda x: x[2] or 0)
        min_row = min(stds, key=lambda x: x[2] or 0)
        lines.append(f"  Max std: e0={max_row[0]} de={max_row[1]} → std={max_row[2]}")
        lines.append(f"  Min std: e0={min_row[0]} de={min_row[1]} → std={min_row[2]}")
    lines.append("")

    # E3
    lines.append("E3 — Measured Ablation")
    lines.append("-" * 48)
    for r in e3:
        lines.append(f"  {r['config']:<30} std={r['std']}  range={r['range']}")
    lines.append("")

    # E4
    lines.append("E4 — Entropy Decay Sweep")
    lines.append("-" * 48)
    for sched in E4_SCHEDULES:
        sched_rows = [r for r in e4 if r["schedule"] == sched]
        if sched_rows:
            lines.append(f"  Schedule: {sched}")
            for r in sched_rows:
                lines.append(f"    beta={r['beta']:<6} steps={r['steps']:<4}  std={r['std']}  range={r['range']}")
    lines.append("")

    # E5
    lines.append("E5 — Length Scaling Extension")
    lines.append("-" * 48)
    if e5 and e5[0].get("alpha_fit") is not None:
        lines.append(f"  Power-law fit: alpha={e5[0]['alpha_fit']}  R²={e5[0]['r2_alpha_fit']}")
    for r in e5:
        marginal = r.get("marginal_std")
        m_str = f"  Δstd={marginal}" if marginal is not None else ""
        lines.append(f"  steps={r['steps']:<4}  std={r['std']}  range={r['range']}{m_str}")
    lines.append("")

    lines.append("=" * 68)
    lines.append("  END OF EXTENDED FINDINGS")
    lines.append("=" * 68)

    path = os.path.join(RESULTS_DIR, "extended_findings.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  -> {path} written")

    json_path = os.path.join(RESULTS_DIR, "extended_findings.json")
    with open(json_path, "w") as f:
        json.dump({
            "e1": e1,
            "e2": e2,
            "e3": e3,
            "e4": e4,
            "e5": e5,
        }, f, indent=2, default=str)
    print(f"  -> {json_path} written")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ordered Chaos Extended Experiments E1–E5")
    parser.add_argument("--runs", type=int, default=NUM_RUNS,
                        help=f"Runs per config (default {NUM_RUNS})")
    parser.add_argument("--only", nargs="+", choices=["E1", "E2", "E3", "E4", "E5"],
                        help="Run only specific experiments")
    args = parser.parse_args()

    n = args.runs
    only = set(args.only) if args.only else {"E1", "E2", "E3", "E4", "E5"}

    print("=" * 68)
    print("  Ordered Chaos — Extended Experiment Battery (E1–E5)")
    print(f"  Runs/config : {n:,}")
    print(f"  Output      : ./{os.path.relpath(RESULTS_DIR)}/")
    print(f"  Seed        : {GLOBAL_SEED}")
    print("=" * 68)

    e1 = run_e1(n) if "E1" in only else []
    e2 = run_e2(n) if "E2" in only else []
    e3 = run_e3(n) if "E3" in only else []
    e4 = run_e4(n) if "E4" in only else []
    e5 = run_e5(n) if "E5" in only else []

    print("\n── Writing master summary and findings ──")
    write_master_summary(e1, e2, e3, e4, e5)
    write_findings(e1, e2, e3, e4, e5)

    print("\n" + "=" * 68)
    print("  Complete.")
    print(f"  Results in: ./{os.path.relpath(RESULTS_DIR)}/")
    print("=" * 68)