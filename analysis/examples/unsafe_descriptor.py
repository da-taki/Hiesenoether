class UnstableDescriptor:
    def __init__(self, base):
        self.base = base
        self.n = 0
        self.e = 1.0

    def read(self):
        drift = self.n * self.e
        v = self.base + drift
        self.n += 1
        self.e += 0.1
        return v

    def observe(self):
        self.e += 1.0

def hot_path():
    x = UnstableDescriptor(10.0)
    return x.read() * x.read() * x.read()
