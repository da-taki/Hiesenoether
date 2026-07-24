class DriftingCounter:
    def __init__(self):
        self.n = 0
        self.e = 1.0

    def read(self):
        v = self.n * self.e
        self.n += 1
        self.e += 0.1
        return v

    def observe(self):
        self.e += 1.0

def hot_path():
    c = DriftingCounter()
    s = 0
    for _ in range(5):
        s += c.read()
    return s
