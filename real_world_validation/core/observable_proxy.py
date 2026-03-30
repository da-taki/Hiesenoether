# observable_proxy.py

from dataclasses import dataclass, field
from .unstable_object import UnstableObject, INITIAL_ENTROPY


@dataclass
class ObservableProxyConfig:
    backend: str = "unstable_object"


class ObservableProxy:
    """Generic proxy wrapping UnstableObject.

    Provides a stable interface for future NumPy or alternative backends.
    Currently delegates all operations to UnstableObject unchanged.
    """

    def __init__(
        self,
        target: UnstableObject | None = None,
        base: float = 10.0,
        initial_entropy: float = INITIAL_ENTROPY,
        config: ObservableProxyConfig | None = None,
    ) -> None:
        self._config = config or ObservableProxyConfig()
        self._target = target if target is not None else UnstableObject(base, initial_entropy)

    def read(self) -> float:
        return self._target.read()

    def observe(self) -> dict:
        return self._target.observe()

    def reset(self) -> None:
        self._target.reset()

    def state_snapshot(self) -> dict:
        return self._target.state_snapshot()

    @property
    def backend(self) -> str:
        return self._config.backend