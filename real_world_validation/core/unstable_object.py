from dataclasses import dataclass

INITIAL_ENTROPY: float = 1.0
ENTROPY_INCREMENT: float = 0.1
OBSERVE_ENTROPY_BUMP: float = 1.0

@dataclass
class UnstableObjectConfig:
    base: float
    initial_entropy: float = INITIAL_ENTROPY

class UnstableObject:

    __slots__ = ("base", "access_count", "entropy", "_initial_entropy")

    def __init__(self, base: float, initial_entropy: float = INITIAL_ENTROPY) -> None:
        self.base = base
        self.access_count: int = 0
        self.entropy: float = initial_entropy
        self._initial_entropy: float = initial_entropy

    def read(self) -> float:
        drift = self.access_count * self.entropy
        value = self.base + drift
        self.access_count += 1
        self.entropy += ENTROPY_INCREMENT
        return value

    def observe(self) -> dict:
        snapshot = {
            "base": self.base,
            "access_count": self.access_count,
            "entropy": self.entropy,
        }
        self.entropy += OBSERVE_ENTROPY_BUMP
        return snapshot

    def reset(self) -> None:
        self.access_count = 0
        self.entropy = self._initial_entropy

    def state_snapshot(self) -> dict:
        return {
            "base": self.base,
            "access_count": self.access_count,
            "entropy": self.entropy,
        }
