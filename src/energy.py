from dataclasses import dataclass
from typing import Dict, Set, Any

@dataclass
class EnergyEscrow:
    function_name: str
    amount: int
    released: bool = False
    call_count: int = 0
    observed_outputs: list = None

    def __post_init__(self):
        if self.observed_outputs is None:
            self.observed_outputs = []

class EnergySystem:

    def __init__(self):
        self.current_energy: int = 0
        self.max_energy: int = 0
        self.removed_capabilities: Set[str] = set()
        self.escrows: Dict[str, EnergyEscrow] = {}
        self.pure_fn_called: Set[str] = set()

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
        if self.max_energy == 0:
            return 1.0
        return max(0.0, min(1.0, 1 - (self.current_energy / self.max_energy)))

    def spend(self, operation: str) -> bool:
        cost = self.COSTS.get(operation, 0)

        if self.current_energy < cost:
            self.current_energy = 0
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
            escrow.observed_outputs.append(output)
            escrow.released = True
            self.current_energy += escrow.amount
            return escrow.amount

        if output in escrow.observed_outputs:
            penalty = 6
            self.current_energy -= penalty
            return -penalty

        escrow.observed_outputs.append(output)
        return 0

    def release_pure_fn_gain(self, function_name: str) -> int:
        if function_name in self.pure_fn_called:
            return 0
        self.pure_fn_called.add(function_name)
        gain = self.GAINS['pure_fn_call']
        self.current_energy += gain
        return gain

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
