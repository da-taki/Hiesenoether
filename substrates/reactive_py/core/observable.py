from __future__ import annotations
from typing import Callable, List, Optional


ENTROPY_INIT = 1.0
ENTROPY_ACCESS = 0.1
ENTROPY_OBSERVE = 1.0


class Observable:
    """An observable whose .value drifts on each .get() (P1).

    Mirrors MobX's observable() / Vue's ref() / SolidJS createSignal()
    with one semantic addition: read is access-sensitive."""

    __slots__ = ("_base", "_n", "_e", "_subs", "_name")

    def __init__(self, value: float, name: str = "<anon>"):
        self._base = float(value)
        self._n = 0
        self._e = ENTROPY_INIT
        self._subs: List[Callable] = []
        self._name = name

    def get(self) -> float:
        """Read the current value. Access advances internal state (P1)."""
        drift = self._n * self._e
        v = self._base + drift
        self._n += 1
        self._e += ENTROPY_ACCESS
        for s in self._subs:
            s()
        return v

    def observe(self) -> None:
        """Observation perturbation (P2). Permanently bumps entropy.
        Mirrors MobX's runInAction triggered by a tracker, or a Vue
        watcher firing — but here, the observation itself perturbs."""
        self._e += ENTROPY_OBSERVE

    def subscribe(self, callback: Callable) -> Callable:
        """Reaction hook (standard reactive-framework primitive)."""
        self._subs.append(callback)
        return lambda: self._subs.remove(callback)

    def state(self) -> dict:
        return {"base": self._base, "n": self._n,
                "e": round(self._e, 4), "name": self._name}


class Computed:

    __slots__ = ("_fn", "_name")

    def __init__(self, fn: Callable[[], float], name: str = "<computed>"):
        self._fn = fn
        self._name = name

    def get(self) -> float:
        return self._fn()


def reaction(fn: Callable[[], None]) -> Callable:
    return fn