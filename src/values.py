from dataclasses import dataclass
from typing import List, Any, Optional


class UnstableValue:
    """
    An unstable value evolves every time it is accessed.

    The evolution is deterministic and depends on execution order.
    Each access advances an internal counter.
    """

    def __init__(self, value):
        self.base_value = value
        self.access_count = 0
        self.is_stable = False

    def get(self):
        """
        Return the current value and advance internal state.
        If stabilized, returns the frozen value.
        """
        if self.is_stable:
            return self.base_value
        
        current = self.base_value + self.access_count
        self.access_count += 1
        return current
    
    def stabilize(self):
        """
        Freeze the value at its current state.
        Future accesses will return the same value.
        """
        if not self.is_stable:
            # Stabilize at current computed value
            self.base_value = self.base_value + self.access_count
            self.is_stable = True
    
    def inspect(self) -> dict:
        """
        Return detailed internal state (costs energy)
        """
        return {
            'base_value': self.base_value,
            'access_count': self.access_count,
            'is_stable': self.is_stable,
            'current_value': self.base_value if self.is_stable else self.base_value + self.access_count
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