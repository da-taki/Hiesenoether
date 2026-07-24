class ImmutableValue:
    def __init__(self, base):
        self.base = base

    def read(self):
        return self.base

    def observe(self):
        return {"base": self.base}

def hot_path():
    x = ImmutableValue(10.0)
    return x.read() + x.read() + x.read()
