from dataclasses import dataclass, field
from typing import List, Any, Optional

class UnstableValue:

    def __init__(self, value):
        self.base_value = value
        self.access_count = 0
        self.entropy = 1.0
        self.is_stable = False
        self._frozen_value = None

    def get(self):
        if self.is_stable:
            return self._frozen_value

        drift = self.access_count * self.entropy
        value = self.base_value + drift

        self.access_count += 1
        self.entropy += 0.1

        return value

    def stabilize(self):
        if not self.is_stable:
            drift = self.access_count * self.entropy
            self._frozen_value = self.base_value + drift
            self.access_count += 1
            self.entropy += 0.1
            self.is_stable = True

    def observe(self):
        self.entropy += 1.0

    def inspect(self):
        return {
            "base_value": self.base_value,
            "access_count": self.access_count,
            "entropy": round(self.entropy, 2),
            "stable": self.is_stable,
            "frozen_value": self._frozen_value,
        }

class StableValue:

    def __init__(self, value):
        self.value = value
        self.is_stable = True

    def get(self):
        return self.value

    def stabilize(self):
        pass

    def inspect(self) -> dict:
        return {
            'value': self.value,
            'is_stable': True,
            'access_count': 0,
        }

@dataclass
class Function:
    name: str
    params: List[str]
    body: List[Any]
    is_pure: bool = False
    is_unstable: bool = False
    closure: Optional[dict] = None

    def __repr__(self):
        mods = []
        if self.is_pure:
            mods.append("pure")
        if self.is_unstable:
            mods.append("unstable")
        mod_str = " ".join(mods)
        return f"<Function {self.name}({', '.join(self.params)}) {mod_str}>"
