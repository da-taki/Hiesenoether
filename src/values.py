from dataclasses import dataclass, field
from typing import List, Any, Optional


class UnstableValue:
    """
    An unstable value that evolves deterministically on each access.

    Evolution rule:
        On access N (0-indexed):
            drift = access_count * entropy
            returned_value = base_value + drift
            access_count += 1

    Where:
        - base_value is the initial value, never mutated by access
        - access_count starts at 0 and increments on each get()
        - entropy starts at 1.0 and increases by 0.1 on each get()
        - drift is computed BEFORE incrementing access_count

    Example for base_value = 10:
        Access 0: drift = 0 * 1.0 = 0    → 10.0   (then count=1, entropy=1.1)
        Access 1: drift = 1 * 1.1 = 1.1  → 11.1   (then count=2, entropy=1.2)
        Access 2: drift = 2 * 1.2 = 2.4  → 12.4   (then count=3, entropy=1.3)

    Stabilization freezes the value at whatever get() would return at that
    moment, using the current access_count and entropy. After stabilization,
    get() always returns that frozen value.

    Inspect (when paid for) increases entropy by 1.0, representing the
    cost of observation on future uncertainty. This only happens when the
    energy spend succeeds.
    """

    def __init__(self, value):
        self.base_value = value
        self.access_count = 0
        self.entropy = 1.0
        self.is_stable = False
        self._frozen_value = None

    def get(self):
        """
        Return the current value. If unstable, compute drift and advance state.
        If stable (post-stabilization), return frozen value.
        """
        if self.is_stable:
            return self._frozen_value

        drift = self.access_count * self.entropy
        value = self.base_value + drift

        self.access_count += 1
        self.entropy += 0.1

        return value

    def stabilize(self):
        """
        Freeze the value at the current point in evolution.
        The frozen value is what get() would return RIGHT NOW — computed
        using current access_count and entropy, then state advances one
        final time before freezing.
        """
        if not self.is_stable:
            # Compute what would be returned, advance state, then freeze
            drift = self.access_count * self.entropy
            self._frozen_value = self.base_value + drift
            self.access_count += 1
            self.entropy += 0.1
            self.is_stable = True

    def observe(self):
        """
        Called when a successful inspect occurs. Increases entropy,
        representing the observer effect on future uncertainty.
        Only called when the energy cost is actually paid.
        """
        self.entropy += 1.0

    def inspect(self):
        """
        Return detailed internal state. This is the data displayed to
        the programmer. Does NOT mutate state — mutation happens via
        observe() which is called separately by the runtime.
        """
        return {
            "base_value": self.base_value,
            "access_count": self.access_count,
            "entropy": round(self.entropy, 2),
            "stable": self.is_stable,
            "frozen_value": self._frozen_value,
        }


class StableValue:
    """
    A stable value NEVER changes after creation.
    
    Accessing a stable value always returns exactly the value it was
    created with. There are no conditions under which this guarantee
    degrades. This is the core promise of spending energy on stability.
    """

    def __init__(self, value):
        self.value = value
        self.is_stable = True

    def get(self):
        """Always return the same value. No exceptions."""
        return self.value

    def stabilize(self):
        """Already stable, no-op."""
        pass

    def inspect(self) -> dict:
        """Return detailed internal state (costs energy)."""
        return {
            'value': self.value,
            'is_stable': True,
            'access_count': 0,
        }


@dataclass
class Function:
    """
    Represents a user-defined function.

    Closure semantics: When a function is declared, the current global
    environment is captured as a snapshot. During execution, the function
    resolves variables first from its local scope, then from the captured
    closure, then from the live global scope.
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