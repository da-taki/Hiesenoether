from dataclasses import dataclass
from typing import List, Any, Optional


class UnstableValue:
    """
    An unstable value whose evolution accelerates under energy pressure.
    """

    def __init__(self, value):
        self.base_value = value
        self.access_count = 0
        self.entropy = 1
        self.is_stable = False

    def get(self, energy=None):
        if self.is_stable:
            return self.base_value

        pressure = 1
        if energy is not None:
            pressure += max(0, (energy.max_energy - energy.current_energy) // 10)

        drift = self.access_count * self.entropy * pressure
        value = self.base_value + drift

        self.access_count += 1
        self.entropy += pressure * 0.1

        return value

    def stabilize(self):
        if not self.is_stable:
            self.base_value = self.get()
            self.is_stable = True

    def inspect(self):
        return {
            "base_value": self.base_value,
            "access_count": self.access_count,
            "entropy": round(self.entropy, 2),
            "stable": self.is_stable
        }

class StableValue:
    """
    A stable value does not change when accessed.
    """

    def __init__(self, value):
        self.value = value
        self.is_stable = True

    def get(self):
        """
        Always return the same value.
        """
        return self.value
    
    def stabilize(self):
        """
        Already stable, no-op.
        """
        pass
    
    def inspect(self) -> dict:
        """
        Return detailed internal state (costs energy)
        """
        return {
            'value': self.value,
            'is_stable': True,
            'access_count': 0
        }


@dataclass
class Function:
    """
    Represents a user-defined function.
    """
    name: str
    params: List[str]
    body: List[Any]  # List of AST nodes
    is_pure: bool = False
    is_unstable: bool = False
    closure: Optional[dict] = None  # Captured environment
    
    def __repr__(self):
        mods = []
        if self.is_pure:
            mods.append("pure")
        if self.is_unstable:
            mods.append("unstable")
        mod_str = " ".join(mods)
        return f"<Function {self.name}({', '.join(self.params)}) {mod_str}>"