from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class EnergyEscrow:
    """Tracks energy in escrow for unstable functions"""
    function_name: str
    amount: int
    released: bool = False
    call_count: int = 0
    last_output: any = None


class EnergySystem:
    """
    Manages the energy budget and tracks costs/gains.
    
    Energy starts at a declared amount and is consumed by guarantees.
    Energy can be gained by giving up guarantees (via escrow).
    """
    
    def __init__(self):
        self.current_energy = 0
        self.max_energy = 0
        self.removed_capabilities: Set[str] = set()
        self.escrows: Dict[str, EnergyEscrow] = {}
        
        # Energy costs
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
            'stable_while': 3,
        }
        
        # Energy gains (via escrow)
        self.GAINS = {
            'pure_fn_proof': 4,
            'unstable_fn_call': 4,
        }
        
        # Capability removal gains
        self.REMOVAL_GAINS = {
            'invariants': 20,
            'stable_control': 15,
            'inspection': 10,
        }
    
    def set_initial_energy(self, amount: int):
        """Set the initial energy budget"""
        self.current_energy = amount
        self.max_energy = amount
    
    def spend(self, operation: str) -> bool:
        """
        Attempt to spend energy on an operation.
        Returns True if successful, False if insufficient energy.
        """
        cost = self.COSTS.get(operation, 0)
        
        if self.current_energy >= cost:
            self.current_energy -= cost
            return True
        else:
            return False
    
    def check_cost(self, operation: str) -> int:
        """Return the cost of an operation without spending"""
        return self.COSTS.get(operation, 0)
    
    def create_escrow(self, function_name: str, is_unstable: bool = False):
        """
        Create an escrow for a function declaration.
        
        For unstable functions, energy goes into escrow and is released
        on first call if the function proves to be unstable.
        """
        if is_unstable:
            self.escrows[function_name] = EnergyEscrow(
                function_name=function_name,
                amount=self.GAINS['unstable_fn_call']
            )
    
    def release_escrow(self, function_name: str, output: any) -> int:
        """
        Attempt to release escrow energy for an unstable function.
        
        Returns the amount of energy gained (0 if already released or if
        function acts stable).
        """
        if function_name not in self.escrows:
            return 0
        
        escrow = self.escrows[function_name]
        escrow.call_count += 1
        
        # First call: release escrow
        if escrow.call_count == 1:
            escrow.last_output = output
            escrow.released = True
            self.current_energy += escrow.amount
            return escrow.amount
        
        # Second call: check if output is different (proving instability)
        elif escrow.call_count == 2:
            if output == escrow.last_output:
                # Function lied about being unstable! Penalty
                penalty = 6
                self.current_energy -= penalty
                return -penalty
        
        return 0
    
    def burn_unreleased_escrows(self) -> int:
        """
        At end of program, burn all unreleased escrows.
        Returns total energy lost.
        """
        total_burned = 0
        for escrow in self.escrows.values():
            if not escrow.released:
                total_burned += escrow.amount
        return total_burned
    
    def remove_capability(self, capability: str) -> bool:
        """
        Permanently remove a capability to gain max energy.
        Returns True if successful.
        """
        if capability in self.removed_capabilities:
            return False
        
        gain = self.REMOVAL_GAINS.get(capability, 0)
        if gain > 0:
            self.removed_capabilities.add(capability)
            self.max_energy += gain
            self.current_energy += gain
            return True
        
        return False
    
    def has_capability(self, capability: str) -> bool:
        """Check if a capability is still available"""
        return capability not in self.removed_capabilities
    
    def get_energy(self) -> int:
        """Return current energy"""
        return self.current_energy
    
    def get_max_energy(self) -> int:
        """Return maximum energy"""
        return self.max_energy
    
    def __repr__(self):
        return f"Energy({self.current_energy}/{self.max_energy})"