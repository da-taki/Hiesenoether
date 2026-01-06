# src/energy.py

from dataclasses import dataclass
from typing import Dict, Set, Any


@dataclass
class EnergyEscrow:
    """Tracks energy escrow for unstable functions."""
    function_name: str
    amount: int
    released: bool = False
    call_count: int = 0
    last_output: Any = None


class EnergySystem:
    """
    Manages the energy budget and enforces conservation.
    """

    def __init__(self):
        self.current_energy: int = 0
        self.max_energy: int = 0
        self.removed_capabilities: Set[str] = set()
        self.escrows: Dict[str, EnergyEscrow] = {}

        self.COSTS = {
            'stabilize': 5,
            'stable_var': 5,
            'declare_fn': 3,
            'declare_pure_fn': 3,
            'declare_unstable_fn': 1,
            'inspect': 2,
            'invariant': 10,
            'assert': 1,
            'stable_if': 3,
        }

        self.GAINS = {
            'unstable_fn_call': 4,
        }

        self.REMOVAL_GAINS = {
            'invariants': 20,
            'stable_control': 15,
            'inspection': 10,
        }

    def set_initial_energy(self, amount: int) -> None:
        self.current_energy = amount
        self.max_energy = amount

    def spend(self, operation: str) -> bool:
        cost = self.COSTS.get(operation, 0)
        if self.current_energy < cost:
            return False
        self.current_energy -= cost
        return True

    def check_cost(self, operation: str) -> int:
        return self.COSTS.get(operation, 0)

    def create_escrow(self, function_name: str) -> None:
        self.escrows[function_name] = EnergyEscrow(
            function_name=function_name,
            amount=self.GAINS['unstable_fn_call'],
        )

    def release_escrow(self, function_name: str, output: Any) -> int:
        escrow = self.escrows.get(function_name)
        if escrow is None:
            return 0

        escrow.call_count += 1

        if escrow.call_count == 1:
            escrow.last_output = output
            escrow.released = True
            self.current_energy += escrow.amount
            return escrow.amount

        if escrow.call_count == 2 and output == escrow.last_output:
            penalty = 6
            self.current_energy -= penalty
            return -penalty

        return 0

    def burn_unreleased_escrows(self) -> int:
        burned = 0
        for escrow in self.escrows.values():
            if not escrow.released:
                burned += escrow.amount
                self.current_energy -= escrow.amount
        return burned

    def remove_capability(self, capability: str) -> bool:
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
