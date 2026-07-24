from .unstable_object import UnstableObject, INITIAL_ENTROPY

class UnstableDescriptor:

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

    x = UnstableDescriptor(base=10.0)
    accumulator = UnstableDescriptor(base=0.0)

    def __init__(self) -> None:
        pass
