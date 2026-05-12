"""Example: HIGH risk. P1, P2, P3 all present."""

class UnstableDescriptor:
    def __init__(self, base):
        self.base = base
        self.n = 0
        self.e = 1.0

    def read(self):
        drift = self.n * self.e         # P1: derived from counters
        v = self.base + drift
        self.n += 1                     # P1: mutates counter
        self.e += 0.1
        return v

    def observe(self):                  # P2: observer mutation
        self.e += 1.0


def hot_path():
    x = UnstableDescriptor(10.0)
    return x.read() * x.read() * x.read()   # P3: multiplicative chain