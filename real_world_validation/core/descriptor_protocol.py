# descriptor_protocol.py

from .unstable_object import UnstableObject, INITIAL_ENTROPY


class UnstableDescriptor:
    """Python data descriptor wrapping UnstableObject.

    Every attribute read on an owning instance calls UnstableObject.read(),
    making each access non-idempotent at the Python runtime level.
    """

    def __init__(self, base: float, initial_entropy: float = INITIAL_ENTROPY) -> None:
        self._obj = UnstableObject(base, initial_entropy)
        self._name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._obj.read()

    def __set__(self, instance, value: float) -> None:
        self._obj = UnstableObject(value, self._obj._initial_entropy)

    def observe(self) -> dict:
        return self._obj.observe()

    def reset(self) -> None:
        self._obj.reset()

    def state_snapshot(self) -> dict:
        return self._obj.state_snapshot()


class DescriptorHost:
    """Concrete host class exposing two UnstableDescriptors.

    Descriptors are class-level: all instances share the same UnstableObject.
    Call DescriptorHost.x.reset() between runs.
    """

    x = UnstableDescriptor(base=10.0)
    accumulator = UnstableDescriptor(base=0.0)

    def __init__(self) -> None:
        pass