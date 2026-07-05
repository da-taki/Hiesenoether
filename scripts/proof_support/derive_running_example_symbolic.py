from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RESULTS_DIR = REPO / "results" / "proof_support"
JSON_PATH = RESULTS_DIR / "running_example_derivation.json"
MD_PATH = RESULTS_DIR / "running_example_derivation.md"

BASE = Fraction(10)
INITIAL_ENTROPY = Fraction(1)
ACCESS_DELTA = Fraction(1, 10)
OBS_DELTA = Fraction(1)
CAP_DEGREE = 2
ORDER_A = ("OBS", "READ", "READ")
ORDER_B = ("READ", "READ", "OBS")


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def state_payload(base: Fraction, access_count: int, entropy: Fraction) -> dict:
    return {
        "base": fraction_text(base),
        "access_count": access_count,
        "drift_state": fraction_text(entropy),
    }


def read_step(base: Fraction, access_count: int, entropy: Fraction) -> tuple[Fraction, Fraction, int, Fraction]:
    drift = Fraction(access_count) * entropy
    exposed = base + drift
    return exposed, drift, access_count + 1, entropy + ACCESS_DELTA


def derive_order(name: str, operations: tuple[str, ...]) -> dict:
    base = BASE
    access_count = 0
    entropy = INITIAL_ENTROPY
    accumulator = Fraction(0)
    steps = [
        {
            "step": 0,
            "operation": "INITIAL",
            "state": state_payload(base, access_count, entropy),
            "accumulator": fraction_text(accumulator),
        }
    ]
    read_values: list[str] = []

    for step, operation in enumerate(operations, start=1):
        if operation == "READ":
            exposed, drift, access_count, entropy = read_step(base, access_count, entropy)
            accumulator += exposed
            read_values.append(fraction_text(exposed))
            steps.append(
                {
                    "step": step,
                    "operation": "READ",
                    "exposed_read_value": fraction_text(exposed),
                    "drift": fraction_text(drift),
                    "state_after": state_payload(base, access_count, entropy),
                    "accumulator": fraction_text(accumulator),
                }
            )
        elif operation == "OBS":
            before = state_payload(base, access_count, entropy)
            entropy += OBS_DELTA
            steps.append(
                {
                    "step": step,
                    "operation": "OBS",
                    "state_before": before,
                    "state_after": state_payload(base, access_count, entropy),
                    "accumulator": fraction_text(accumulator),
                    "observation_exposes_value": False,
                }
            )
        else:
            raise ValueError(f"unknown operation: {operation}")

    cap_factors = []
    cap_output = accumulator
    for cap_index in range(max(0, CAP_DEGREE - 1)):
        exposed, drift, access_count, entropy = read_step(base, access_count, entropy)
        cap_output *= exposed
        cap_factors.append(
            {
                "cap_read": cap_index + 1,
                "exposed_read_value": fraction_text(exposed),
                "drift": fraction_text(drift),
                "state_after": state_payload(base, access_count, entropy),
            }
        )

    return {
        "name": name,
        "operations": list(operations),
        "read_values": read_values,
        "body_accumulator": fraction_text(accumulator),
        "cap": {
            "degree": CAP_DEGREE,
            "formula": "body_accumulator * next_read",
            "factors": cap_factors,
            "output": fraction_text(cap_output),
        },
        "steps": steps,
    }


def build_derivation() -> dict:
    if Counter(ORDER_A) != Counter(ORDER_B):
        raise AssertionError("operation orders must have the same multiset")
    order_a = derive_order("A", ORDER_A)
    order_b = derive_order("B", ORDER_B)
    divergence = abs(Fraction(order_a["cap"]["output"]) - Fraction(order_b["cap"]["output"]))
    return {
        "initial_value": state_payload(BASE, 0, INITIAL_ENTROPY),
        "access_entropy_increment": fraction_text(ACCESS_DELTA),
        "observation_entropy_increment": fraction_text(OBS_DELTA),
        "orders": [order_a, order_b],
        "final_outputs": {
            "A": order_a["cap"]["output"],
            "B": order_b["cap"]["output"],
        },
        "final_divergence": fraction_text(divergence),
        "uses_exact_arithmetic": True,
        "numeric_representation": "fractions-as-strings",
        "paper_explanation": (
            "Both executions use the same multiset of operations. Placing OBS before the reads "
            "raises latent drift before the second body read, so order A has body accumulator 221/10 "
            "while order B has body accumulator 211/10. The compositional cap uses the same next-read "
            "factor 72/5 in both orders, producing final outputs 7956/25 and 7596/25 and exact "
            "divergence 72/5."
        ),
    }


def write_markdown(payload: dict) -> None:
    order_a, order_b = payload["orders"]
    lines = [
        "# Running Example Exact Derivation",
        "",
        "This derivation uses exact rational arithmetic only. Fractions are written as integers or `p/q` strings.",
        "",
        "## Initial Value",
        "",
        f"- Base: {payload['initial_value']['base']}",
        f"- Access count: {payload['initial_value']['access_count']}",
        f"- Drift state: {payload['initial_value']['drift_state']}",
        f"- Access entropy increment: {payload['access_entropy_increment']}",
        f"- Observation entropy increment: {payload['observation_entropy_increment']}",
        "",
        "## Operation Orders",
        "",
        f"- Order A: {', '.join(order_a['operations'])}",
        f"- Order B: {', '.join(order_b['operations'])}",
        "",
        "## Body and Cap Outputs",
        "",
        "| Order | Body read values | Body accumulator | Cap factor | Final output |",
        "| --- | --- | --- | --- | --- |",
        f"| A | {', '.join(order_a['read_values'])} | {order_a['body_accumulator']} | {order_a['cap']['factors'][0]['exposed_read_value']} | {order_a['cap']['output']} |",
        f"| B | {', '.join(order_b['read_values'])} | {order_b['body_accumulator']} | {order_b['cap']['factors'][0]['exposed_read_value']} | {order_b['cap']['output']} |",
        "",
        f"Final divergence: `{payload['final_divergence']}`.",
        "",
        "## Step Trace",
        "",
    ]
    for order in payload["orders"]:
        lines.extend([f"### Order {order['name']}", ""])
        for step in order["steps"]:
            lines.append(f"- Step {step['step']} `{step['operation']}`: accumulator `{step['accumulator']}`")
            if step["operation"] == "READ":
                lines.append(
                    f"  - exposed `{step['exposed_read_value']}`, drift `{step['drift']}`, state after `{step['state_after']}`"
                )
            elif step["operation"] == "OBS":
                lines.append(f"  - state before `{step['state_before']}`, state after `{step['state_after']}`")
            else:
                lines.append(f"  - state `{step['state']}`")
        lines.append("")
        lines.append(f"Cap output: `{order['cap']['output']}`.")
        lines.append("")
    lines.extend(["## Paper Explanation", "", payload["paper_explanation"], ""])
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_derivation()
    JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"wrote {JSON_PATH}")
    print(f"wrote {MD_PATH}")
    print(f"final_divergence={payload['final_divergence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
