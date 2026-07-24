from __future__ import annotations

from dataclasses import dataclass

class AccessEvolvingPropertyWithObserver:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    @property
    def value(self):
        self.n += 1
        return self.n * self.e
    def observe(self): self.e += 1

class LatentStateDescriptor:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    def __get__(self, obj, owner=None):
        self.n += 1
        return self.n + self.e
    def inspect(self): self.e += 1

class ObserverMutatesLaterRead:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.bias = 0, 0
    def read(self):
        self.n += 1
        return self.n + self.bias
    def observe(self): self.bias += 10

class CounterBasedReadThreshold:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.threshold = 0, 3
    def get(self):
        self.n += 1
        return self.n if self.n < self.threshold else self.n * self.threshold
    def watch(self): self.threshold += 1

class ReactiveDependencyRegistration:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.dependencies = 0, 1
    def current(self):
        self.n += 1
        return self.n * self.dependencies
    def snapshot(self): self.dependencies += 1

class InstrumentationHookPattern:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.hooks = 0, 1
    def fetch(self):
        self.n += 1
        return self.n * self.hooks
    def inspect(self): self.hooks += 1

class CachedValueInvalidationAndRead:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.generation = 0, 1
    def read(self):
        self.n += 1
        return self.n * self.generation
    def observe(self): self.generation += 1
    def invalidate(self): self.generation += 1

class HiddenCounterFetcher:
    expected_risk = "HIGH"
    def __init__(self): self.hidden, self.scale = 0, 1
    def fetch(self):
        self.hidden += 1
        return self.hidden * self.scale
    def snapshot(self): self.scale += 1

class SnapshotThenRead:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.offset = 0, 0
    def read(self):
        self.n += 1
        return self.n + self.offset
    def snapshot(self): self.offset += 5

class DescriptorObserverPair:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.e = 0, 1
    def __get__(self, obj, owner=None):
        self.n += 1
        return self.n * self.e
    def observe(self): self.e += 1

class RollingWindowReader:
    expected_risk = "HIGH"
    def __init__(self): self.index, self.window = 0, 2
    def read(self):
        self.index += 1
        return self.index * self.window
    def inspect(self): self.window += 1

class LazyInvalidatingCell:
    expected_risk = "HIGH"
    def __init__(self): self.n, self.epoch = 0, 1
    def value(self):
        self.n += 1
        return self.n + self.epoch
    def watch(self): self.epoch += 1

class AccessEvolvingPropertyOnly:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    @property
    def value(self):
        self.n += 1
        return self.n

class CounterBasedReaderOnly:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def read(self):
        self.n += 1
        return self.n * 2

class ReadThresholdOnly:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def get(self):
        self.n += 1
        return 0 if self.n < 3 else self.n

class HiddenCounterGetter:
    expected_risk = "MEDIUM"
    def __init__(self): self.hidden = 0
    def get(self):
        self.hidden += 1
        return self.hidden

class RepeatedReadSource:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def read(self):
        self.n += 1
        return self.n + 1

class MeteredCurrentValue:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def current(self):
        self.n += 1
        return self.n * 10

class FetchWithHiddenCounter:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def fetch(self):
        self.n += 1
        return self.n

class NextToken:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def __next__(self):
        self.n += 1
        return f"token-{self.n}"

class AccessingDescriptorOnly:
    expected_risk = "MEDIUM"
    def __init__(self): self.n = 0
    def __get__(self, obj, owner=None):
        self.n += 1
        return self.n

class CachedInvalidationReaderNoObserver:
    expected_risk = "MEDIUM"
    def __init__(self): self.n, self.epoch = 0, 0
    def read(self):
        self.n += 1
        return self.n + self.epoch
    def invalidate(self): self.epoch += 1

class ObserverOnlyInvalidate:
    expected_risk = "LOW"
    def __init__(self): self.epoch = 0
    def observe(self): self.epoch += 1

class SnapshotOnly:
    expected_risk = "LOW"
    def __init__(self): self.version = 0
    def snapshot(self): self.version += 1

class WatchOnly:
    expected_risk = "LOW"
    def __init__(self): self.watchers = 0
    def watch(self): self.watchers += 1

class InspectOnly:
    expected_risk = "LOW"
    def __init__(self): self.inspections = 0
    def inspect(self): self.inspections += 1

class ObserverDescriptorNoRead:
    expected_risk = "LOW"
    def __init__(self): self.version = 0
    def inspect(self): self.version += 1
    def __get__(self, obj, owner=None): return 7

class MetricsObserver:
    expected_risk = "LOW"
    def __init__(self): self.events = 0
    def observe(self): self.events += 1

class StoredProperty:
    expected_risk = "SAFE"
    def __init__(self, value=1): self._value = value
    @property
    def value(self): return self._value

class HarmlessMemoizedProperty:
    expected_risk = "SAFE"
    def __init__(self): self._cached = None
    @property
    def value(self):
        if self._cached is None:
            self._cached = 5
        return self._cached

class CachedHash:
    expected_risk = "SAFE"
    def __init__(self, value=1): self.value, self._hash = value, None
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.value)
        return self._hash

class BuilderPattern:
    expected_risk = "SAFE"
    def __init__(self): self.parts = []
    def add(self, part):
        self.parts.append(part)
        return self

class ContextManagerBookkeeping:
    expected_risk = "SAFE"
    def __init__(self): self.depth = 0
    def __enter__(self):
        self.depth += 1
        return self
    def __exit__(self, exc_type, exc, tb):
        self.depth -= 1

class LoggingNoEffect:
    expected_risk = "SAFE"
    def __init__(self): self.value, self.logs = 1, []
    def read(self):
        self.logs.append("read")
        return self.value

class MetricsCounterIndependent:
    expected_risk = "SAFE"
    def __init__(self): self.value, self.metric = 10, 0
    def get(self):
        self.metric += 1
        return self.value

class StableDescriptorCacheOnce:
    expected_risk = "SAFE"
    def __init__(self): self.cached = None
    def __get__(self, obj, owner=None):
        if self.cached is None:
            self.cached = 7
        return self.cached

@dataclass
class DataclassStyleProperty:
    expected_risk = "SAFE"
    value_number: int = 3
    @property
    def value(self): return self.value_number

class FluentSetter:
    expected_risk = "SAFE"
    def __init__(self): self.name = ""
    def set_name(self, name):
        self.name = name
        return self

class PureAreaCalculator:
    expected_risk = "SAFE"
    def __init__(self): self.width, self.height = 2, 3
    def area(self): return self.width * self.height

class ConstantObserverName:
    expected_risk = "SAFE"
    def __init__(self): self.n = 0
    def observe(self): return self.n + 1

class ConstantAfterMutationNearMiss:
    expected_risk = "SAFE"
    def __init__(self): self.calls = 0
    def get(self):
        self.calls += 1
        return 5

class PureDescriptor:
    expected_risk = "SAFE"
    def __get__(self, obj, owner=None): return 11

class StabilizingDescriptor:
    expected_risk = "SAFE"
    def __init__(self): self.cached = None
    def __get__(self, obj, owner=None):
        if self.cached is None:
            self.cached = 13
        return 13

class LoggingObserverNameNoMutation:
    expected_risk = "SAFE"
    def __init__(self): self.status = "ok"
    def inspect(self): return self.status

def repeated_read_feeding_composition(cell):
    return cell.read() * cell.read()

def cached_value_with_explicit_invalidation_then_use(cell):
    cell.invalidate()
    return cell.read() * cell.read() * cell.read()
