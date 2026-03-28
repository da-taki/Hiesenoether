# src/energy.py

from dataclasses import dataclass
from typing import Dict, Set, Any


@dataclass
class EnergyEscrow:
    """
    Tracks energy escrow for unstable functions.
    
    Lifecycle:
        1. Created when an unstable function is declared
        2. On first call: escrow is released, energy is gained
        3. On subsequent calls: if output matches ANY previous output,
           a penalty is applied (the function isn't truly unstable)
    """
    function_name: str
    amount: int
    released: bool = False
    call_count: int = 0
    observed_outputs: list = None

    def __post_init__(self):
        if self.observed_outputs is None:
            self.observed_outputs = []


class EnergySystem:
    """
    Manages the energy budget and enforces conservation.

    All costs are FIXED. There is no hidden inflation or scaling.
    The documented cost is always the actual cost.

    Energy can only increase through:
        - Releasing unstable function escrows (first call)
        - Pure function energy gain (first call)
        - Removing capabilities

    Energy decreases through:
        - Stabilizing values (-5)
        - Stable variable declaration (-5)
        - Function declaration (-3 normal, -3 pure, -1 unstable)
        - Exact introspection / inspect (-2)
        - Invariant declaration (-10)
        - Assert (-1)
    """

    def __init__(self):
        self.current_energy: int = 0
        self.max_energy: int = 0
        self.removed_capabilities: Set[str] = set()
        self.escrows: Dict[str, EnergyEscrow] = {}
        self.pure_fn_called: Set[str] = set()

        # All costs are fixed — no inflation, no scaling
        self.COSTS = {
            'stabilize': 5,
            'stable_var': 5,
            'declare_fn': 3,
            'declare_pure_fn': 3,
            'declare_unstable_fn': 1,
            'inspect': 2,
            'invariant': 10,
            'assert': 1,
        }

        self.GAINS = {
            'unstable_fn_call': 4,
            'pure_fn_call': 4,
        }

        self.REMOVAL_GAINS = {
            'invariants': 20,
            'stable_control': 15,
            'inspection': 10,
        }

    def set_initial_energy(self, amount: int) -> None:
        self.current_energy = amount
        self.max_energy = amount

    def pressure(self) -> float:
        """
        How starved the system is (0.0 → 1.0).

        This is a READ-ONLY metric. It does NOT affect costs.
        It is available for display/query purposes and for
        unstable value evolution if desired in future extensions.
        """
        if self.max_energy == 0:
            return 1.0
        return max(0.0, min(1.0, 1 - (self.current_energy / self.max_energy)))

    def spend(self, operation: str) -> bool:
        """
        Spend energy for an operation. Returns True if successful.
        
        Costs are FIXED — the documented cost is always the actual cost.
        If insufficient energy, energy is set to 0 and False is returned.
        """
        cost = self.COSTS.get(operation, 0)

        if self.current_energy < cost:
            self.current_energy = 0
            return False

        self.current_energy -= cost
        return True

    def check_cost(self, operation: str) -> int:
        """Return the fixed cost for an operation."""
        return self.COSTS.get(operation, 0)

    def create_escrow(self, function_name: str) -> None:
        """Create an energy escrow for an unstable function."""
        self.escrows[function_name] = EnergyEscrow(
            function_name=function_name,
            amount=self.GAINS['unstable_fn_call'],
        )

    def release_escrow(self, function_name: str, output: Any) -> int:
        """
        Process an unstable function call for escrow purposes.

        First call: releases escrow, gains energy.
        Subsequent calls: if output matches any previously observed
        output, a penalty of 6 is applied (function isn't truly unstable).
        New unique outputs are recorded without penalty.
        """
        escrow = self.escrows.get(function_name)
        if escrow is None:
            return 0

        escrow.call_count += 1

        if escrow.call_count == 1:
            # First call — release escrow
            escrow.observed_outputs.append(output)
            escrow.released = True
            self.current_energy += escrow.amount
            return escrow.amount

        # Subsequent calls — check for repeated output
        if output in escrow.observed_outputs:
            penalty = 6
            self.current_energy -= penalty
            return -penalty

        escrow.observed_outputs.append(output)
        return 0

    def release_pure_fn_gain(self, function_name: str) -> int:
        """
        Award energy gain for first call to a pure function.

        Pure functions gain +4 energy on first call, representing
        the runtime's reward for reducing global uncertainty.
        Subsequent calls use cache and award nothing additional.
        """
        if function_name in self.pure_fn_called:
            return 0
        self.pure_fn_called.add(function_name)
        gain = self.GAINS['pure_fn_call']
        self.current_energy += gain
        return gain

    def burn_unreleased_escrows(self) -> int:
        """
        At program end, penalize unreleased escrows.
        If an unstable function was declared but never called,
        the escrowed energy is lost.
        """
        burned = 0
        for escrow in self.escrows.values():
            if not escrow.released:
                burned += escrow.amount
                self.current_energy -= escrow.amount
        return burned

    def remove_capability(self, capability: str) -> bool:
        """
        Permanently remove a capability to gain energy.
        This is irreversible.
        """
        if capability in self.removed_capabilities:
            return False

        gain = self.REMOVAL_GAINS.get(capability)
        if gain is None:
            return False

        self.removed_capabilities.add(capability)
        self.max_energy += gain
        self.current_energy += gain
        return True

    def has_capability(self, capability: str) -> bool:
        return capability not in self.removed_capabilities

    def get_energy(self) -> int:
        return self.current_energy

    def get_max_energy(self) -> int:
        return self.max_energy

    def __repr__(self) -> str:
        return f"Energy({self.current_energy}/{self.max_energy})"