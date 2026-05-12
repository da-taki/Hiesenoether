"""Example: SAFE. Reader is pure, no observer mutation, no nonlinear chain."""

class ImmutableValue:
    def __init__(self, base):
        self.base = base

    def read(self):
        return self.base                # no mutation

    def observe(self):
        return {"base": self.base}      # no mutation


def hot_path():
    x = ImmutableValue(10.0)
    return x.read() + x.read() + x.read()   # additive only