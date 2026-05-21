"""Toy corpus for Ordered-Chaos static-analyzer evaluation."""


class SafeImmutableValue:
    expected_risk = "SAFE"
    def __init__(self, value): self.value = value
    def read(self): return self.value


class SafeFrozenPair:
    expected_risk = "SAFE"
    def __init__(self, left, right): self.left, self.right = left, right
    def get(self): return self.left + self.right


class SafeCachedProperty:
    expected_risk = "SAFE"
    def __init__(self, value): self._value = value
    @property
    def value(self): return self._value


class SafeDescriptor:
    expected_risk = "SAFE"
    def __get__(self, obj, owner=None): return 7


class SafeObserver:
    expected_risk = "SAFE"
    def __init__(self): self.count = 0
    def observe(self): return {"count": self.count}


class PartialP1Reader:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def read(self):
        self.n += 1
        return self.n


class PartialP1Getter:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def get(self):
        self.n += 1
        return self.n * 2


class PartialP1Next:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def __next__(self):
        self.n += 1
        return self.n


class PartialP2Observer:
    expected_risk = "LOW"
    def __init__(self): self.e = 0
    def observe(self): self.e += 1


class PartialP2Inspect:
    expected_risk = "LOW"
    def __init__(self): self.e = 0
    def inspect(self): self.e += 1


class PartialP2Watch:
    expected_risk = "LOW"
    def __init__(self): self.e = 0
    def watch(self): self.e += 1


class FullP1P2Counter:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    def read(self):
        self.n += 1
        return self.n * self.e
    def observe(self): self.e += 1


class FullP1P2Descriptor:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    def __get__(self, obj, owner=None):
        self.n += 1
        return self.n + self.e
    def inspect(self): self.e += 1


class FullReactiveCell:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    def current(self):
        self.n += 1
        return self.n * self.e
    def observe(self): self.e += 1


class FalsePositiveInternalMultiply:
    expected_risk = "SAFE"
    def __init__(self): self.a, self.b = 2, 3
    def area(self): return self.a * self.b


class FalsePositivePureCache:
    expected_risk = "SAFE"
    def __init__(self): self.cached = None
    def get(self):
        if self.cached is None:
            self.cached = 5
        return 5


class FalsePositiveObserverName:
    expected_risk = "SAFE"
    def __init__(self): self.e = 0
    def observe(self): return self.e + 1


class ReactiveAccumulator:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    def fetch(self):
        self.n += 1
        return self.n + self.e
    def snapshot(self): self.e += 1


class CachedDriftingProperty:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    @property
    def value(self):
        self.n += 1
        return self.n


class ObserverOnlyDescriptor:
    expected_risk = "LOW"
    def __init__(self): self.e = 0
    def inspect(self): self.e += 1
    def __get__(self, obj, owner=None): return self.e


def nonlinear_use(cell):
    return cell.read() * cell.read() * cell.read()
