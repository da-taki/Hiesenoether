import random
import statistics
import csv
import os
from tqdm import tqdm

# ─────────────────────────────────────────────
# SAFE PATH (fixes your earlier bug)
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results_2m")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
NUM_RUNS = 157143  # 14 configs → ~2.2M total

# ─────────────────────────────────────────────
# CORE MODEL
# ─────────────────────────────────────────────

class UnstableValue:
    def __init__(self, base):
        self.base = base
        self.access_count = 0
        self.entropy = 1

    def get(self):
        drift = self.access_count * self.entropy
        value = self.base + drift
        self.access_count += 1
        self.entropy += 0.1
        return value

    def inspect(self):
        self.entropy += 1

# ─────────────────────────────────────────────
# PROGRAM EXECUTION
# ─────────────────────────────────────────────

def run_program(order, nonlinearity):
    x = UnstableValue(10)
    y = 0

    for op in order:
        if op == "add":
            y += x.get()
        elif op == "inspect":
            x.inspect()

    if nonlinearity == "linear":
        return y
    elif nonlinearity == "quadratic":
        return y * x.get()
    elif nonlinearity == "cubic":
        return y * x.get() * x.get()
    elif nonlinearity == "extreme":
        return y * y * x.get()

# ─────────────────────────────────────────────
# CONFIGS (same as before)
# ─────────────────────────────────────────────

CONFIGS = [
    ("inspect_0", 6, 0, "quadratic"),
    ("inspect_1", 6, 1, "quadratic"),
    ("inspect_2", 6, 2, "quadratic"),
    ("inspect_3", 6, 3, "quadratic"),
    ("inspect_4", 6, 4, "quadratic"),
    ("inspect_5", 6, 5, "quadratic"),

    ("linear", 6, 1, "linear"),
    ("quadratic", 6, 1, "quadratic"),
    ("cubic", 6, 1, "cubic"),
    ("extreme", 6, 1, "extreme"),

    ("steps_3", 3, 1, "quadratic"),
    ("steps_6", 6, 1, "quadratic"),
    ("steps_9", 9, 1, "quadratic"),
    ("steps_12", 12, 1, "quadratic"),
]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def build_order(add_steps, inspect_count):
    ops = ["add"] * add_steps + ["inspect"] * inspect_count
    random.shuffle(ops)
    return ops

def compute_stats(results):
    return {
        "mean": round(statistics.mean(results), 4),
        "std": round(statistics.stdev(results), 4),
        "min": round(min(results), 4),
        "max": round(max(results), 4),
        "range": round(max(results) - min(results), 4)
    }

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run_config(name, steps, inspects, nonlin):
    results = []

    for _ in range(NUM_RUNS):
        order = build_order(steps, inspects)
        results.append(run_program(order, nonlin))

    stats = compute_stats(results)

    return {
        "config": name,
        "steps": steps,
        "inspects": inspects,
        "nonlinearity": nonlin,
        **stats
    }

def main():
    summary = []

    for cfg in tqdm(CONFIGS):
        summary.append(run_config(*cfg))

    with open(os.path.join(RESULTS_DIR, "summary_2.2m.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)

    print("Done. Results in results_2m/")

if __name__ == "__main__":
    main()