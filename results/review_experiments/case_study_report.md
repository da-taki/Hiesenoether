# Review Experiment Case Studies

This report supplies concrete examples for presentation. Controlled examples use benchmark labels; PyPI examples remain pending manual review.

## Controlled True-Positive Style Examples

### TP-style 1: `CachedDriftingProperty`

- Source: `analysis/benchmark_examples.py`
- Expected label: MEDIUM
- Analyzer label: MEDIUM
- Why analyzer flagged it: P1: method value() (line 137): mutates self.{n} and returns a value derived from self state
- Matches OSDS pattern: yes by controlled benchmark label
- Latent state changes: reader-side counter/state mutation
- Later read consumes: the same reader's returned value
- Risk interpretation: Risky: the controlled label says this class exhibits the target OSDS-style mechanism.

```python
128:         self.n += 1
129:         return self.n + self.e
130:     def snapshot(self): self.e += 1
131:
132:
133: class CachedDriftingProperty:
134:     expected_risk = "MEDIUM"
135:     def __init__(self): self.n = 0
136:     @property
137:     def value(self):
138:         self.n += 1
```

### TP-style 2: `FullP1P2Counter`

- Source: `analysis/benchmark_examples.py`
- Expected label: HIGH
- Analyzer label: HIGH
- Why analyzer flagged it: P1: method read() (line 79): mutates self.{n} and returns a value derived from self state | P2: method observe() (line 82): mutates self.{e}
- Matches OSDS pattern: yes by controlled benchmark label
- Latent state changes: observer-mutated fields in the class
- Later read consumes: later access-sensitive read method/property
- Risk interpretation: Risky: the controlled label says this class exhibits the target OSDS-style mechanism.

```python
71:     expected_risk = "LOW"
72:     def __init__(self): self.e = 0
73:     def watch(self): self.e += 1
74:
75:
76: class FullP1P2Counter:
77:     expected_risk = "HIGH"
78:     def __init__(self): self.n, self.e = 0, 1
79:     def read(self):
80:         self.n += 1
81:         return self.n * self.e
```

### TP-style 3: `FullP1P2Descriptor`

- Source: `analysis/benchmark_examples.py`
- Expected label: HIGH
- Analyzer label: HIGH
- Why analyzer flagged it: P1: method __get__() (line 88): mutates self.{n} and returns a value derived from self state | P2: method inspect() (line 91): mutates self.{e}
- Matches OSDS pattern: yes by controlled benchmark label
- Latent state changes: observer-mutated fields in the class
- Later read consumes: later access-sensitive read method/property
- Risk interpretation: Risky: the controlled label says this class exhibits the target OSDS-style mechanism.

```python
80:         self.n += 1
81:         return self.n * self.e
82:     def observe(self): self.e += 1
83:
84:
85: class FullP1P2Descriptor:
86:     expected_risk = "HIGH"
87:     def __init__(self): self.n, self.e = 0, 1
88:     def __get__(self, obj, owner=None):
89:         self.n += 1
90:         return self.n + self.e
```

## Controlled Benign Near-Misses

### Benign 1: `FalsePositiveInternalMultiply`

- Source: `analysis/benchmark_examples.py`
- Expected label: SAFE
- Analyzer label: SAFE
- Why analyzer flagged it: no analyzer evidence emitted
- Matches OSDS pattern: no by controlled benchmark label
- Latent state changes: none by controlled label
- Later read consumes: none by controlled label
- Risk interpretation: Benign: the controlled label says this is a near-miss rather than target OSDS behavior.

```python
98:         self.n += 1
99:         return self.n * self.e
100:     def observe(self): self.e += 1
101:
102:
103: class FalsePositiveInternalMultiply:
104:     expected_risk = "SAFE"
105:     def __init__(self): self.a, self.b = 2, 3
106:     def area(self): return self.a * self.b
107:
108:
```

### Benign 2: `FalsePositiveObserverName`

- Source: `analysis/benchmark_examples.py`
- Expected label: SAFE
- Analyzer label: SAFE
- Why analyzer flagged it: no analyzer evidence emitted
- Matches OSDS pattern: no by controlled benchmark label
- Latent state changes: none by controlled label
- Later read consumes: none by controlled label
- Risk interpretation: Benign: the controlled label says this is a near-miss rather than target OSDS behavior.

```python
113:         if self.cached is None:
114:             self.cached = 5
115:         return 5
116:
117:
118: class FalsePositiveObserverName:
119:     expected_risk = "SAFE"
120:     def __init__(self): self.e = 0
121:     def observe(self): return self.e + 1
122:
123:
```

### Benign 3: `FalsePositivePureCache`

- Source: `analysis/benchmark_examples.py`
- Expected label: SAFE
- Analyzer label: MEDIUM
- Why analyzer flagged it: P1: method get() (line 112): mutates self.{cached} and returns a value derived from self state
- Matches OSDS pattern: no by controlled benchmark label
- Latent state changes: none by controlled label
- Later read consumes: none by controlled label
- Risk interpretation: Benign: the controlled label says this is a near-miss rather than target OSDS behavior.

```python
104:     expected_risk = "SAFE"
105:     def __init__(self): self.a, self.b = 2, 3
106:     def area(self): return self.a * self.b
107:
108:
109: class FalsePositivePureCache:
110:     expected_risk = "SAFE"
111:     def __init__(self): self.cached = None
112:     def get(self):
113:         if self.cached is None:
114:             self.cached = 5
```

## PyPI Flagged Examples

### PyPI flagged example 1: `sympy.LRASolver`

- Package/version: sympy 1.14.0
- File: `sympy-1.14.0\sympy\logic\algorithms\lra_theory.py`
- Analyzer label: MEDIUM
- Why analyzer flagged it: method assert_lit() (line 373): mutates self.{is_sat} and returns a value derived from self state
- Matches OSDS pattern: pending manual review; no label is invented here.
- Latent state changes: inferred syntactically from analyzer evidence, pending review.
- Later read consumes: inferred syntactically from analyzer evidence, pending review.
- Risk interpretation: review queue candidate, not a confirmed true positive.

```python
138:
139: # if true ~Q.gt(x, y) implies Q.le(x, y)
140: HANDLE_NEGATION = True
141:
142: class LRASolver():
143:     """
144:     Linear Arithmetic Solver for DPLL(T) implemented with an algorithm based on
145:     the Dual Simplex method. Uses Bland's pivoting rule to avoid cycling.
146:
```

### PyPI flagged example 2: `hypothesis.LazyStrategy`

- Package/version: hypothesis 6.155.7
- File: `hypothesis-6.155.7\src\hypothesis\strategies\_internal\lazy.py`
- Analyzer label: MEDIUM
- Why analyzer flagged it: method wrapped_strategy() (line 107): mutates self.{__wrapped_strategy} and returns a value derived from self state
- Matches OSDS pattern: pending manual review; no label is invented here.
- Latent state changes: inferred syntactically from analyzer evidence, pending review.
- Later read consumes: inferred syntactically from analyzer evidence, pending review.
- Risk interpretation: review queue candidate, not a confirmed true positive.

```python
62:             threadlocal.unwrap_cache.clear()
63:         assert threadlocal.unwrap_depth >= 0
64:
65:
66: class LazyStrategy(SearchStrategy[Ex]):
67:     """A strategy which is defined purely by conversion to and from another
68:     strategy.
69:
70:     Its parameter and distribution come from that other strategy.
```

### PyPI flagged example 3: `sympy.KanesMethod`

- Package/version: sympy 1.14.0
- File: `sympy-1.14.0\sympy\physics\mechanics\kane.py`
- Analyzer label: MEDIUM
- Why analyzer flagged it: method _form_fr() (line 405): mutates self.{_forcelist,_fr} and returns a value derived from self state
- Matches OSDS pattern: pending manual review; no label is invented here.
- Latent state changes: inferred syntactically from analyzer evidence, pending review.
- Later read consumes: inferred syntactically from analyzer evidence, pending review.
- Risk interpretation: review queue candidate, not a confirmed true positive.

```python
15:
16: __all__ = ['KanesMethod']
17:
18:
19: class KanesMethod(_Methods):
20:     r"""Kane's method object.
21:
22:     Explanation
23:     ===========
```
