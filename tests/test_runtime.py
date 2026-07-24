import pytest
from src.runtime import Runtime, RuntimeError as HnRuntimeError
from src.parser import parse
from src.values import UnstableValue, StableValue

def test_unstable_value_basic():
    x = UnstableValue(10)
    assert x.get() == 10.0
    assert x.get() == pytest.approx(11.1)
    assert x.get() == pytest.approx(12.4)

def test_unstable_value_deterministic():
    a = UnstableValue(10)
    b = UnstableValue(10)
    for _ in range(10):
        assert a.get() == b.get()

def test_unstable_value_stabilize():
    x = UnstableValue(10)
    x.get()
    x.get()

    x.stabilize()
    assert x.get() == pytest.approx(12.4)
    assert x.get() == pytest.approx(12.4)
    assert x.get() == pytest.approx(12.4)

def test_stable_value_basic():
    y = StableValue(5)
    assert y.get() == 5
    assert y.get() == 5
    assert y.get() == 5

def test_stable_value_never_degrades():
    y = StableValue(42)
    for _ in range(1000):
        assert y.get() == 42

def test_energy_declaration():
    source = "energy[100]"
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 100

def test_unstable_assignment():
    source = """
energy[100]
x <- 5
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    var = runtime.get_var('x')
    assert isinstance(var, UnstableValue)

def test_stable_assignment():
    source = """
energy[100]
stable y <- 10
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    var = runtime.get_var('y')
    assert isinstance(var, StableValue)
    assert var.get() == 10
    assert runtime.energy.get_energy() == 95

def test_stabilize():
    source = """
energy[100]
x <- 5
stabilize x
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    var = runtime.get_var('x')
    assert var.is_stable == True
    assert runtime.energy.get_energy() == 95

def test_function_declaration():
    source = """
energy[100]
declare fn add(a, b) {
    return a + b
}
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 97

def test_function_call():
    source = """
energy[100]
declare fn double(n) {
    return n * 2
}
result <- double(5)
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    result = runtime.get_var('result')
    assert result.get() == 10.0

def test_unstable_function_escrow():
    source = """
energy[100]
declare unstable fn evolve(n) {
    return n + 1
}
x <- evolve(5)
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 103

def test_unstable_function_penalty():
    source = """
energy[100]
declare unstable fn constant(n) {
    return n
}
a <- constant(5)
b <- constant(5)
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 97

def test_pure_function_energy_gain():
    source = """
energy[100]
declare pure fn square(n) {
    return n * n
}
result <- square(5)
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 101

def test_pure_function_caching():
    source = """
energy[100]
declare pure fn square(n) {
    return n * n
}
a <- square(5)
b <- square(5)
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.get_var('a').get() == 25.0
    assert runtime.get_var('b').get() == 25.0
    assert runtime.energy.get_energy() == 101

def test_inspect_costs_energy():
    source = """
energy[100]
x <- 5
inspect x
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 98

def test_inspect_no_mutation_on_failure():
    x = UnstableValue(10)
    initial_entropy = x.entropy
    assert x.entropy == initial_entropy

def test_inspect_mutation_on_success():
    x = UnstableValue(10)
    initial_entropy = x.entropy
    x.observe()
    assert x.entropy == initial_entropy + 1.0

def test_invariant_costs_energy():
    source = """
energy[100]
x <- 5
invariant x > 0
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 90

def test_invariant_violation():
    source = """
energy[100]
x <- 5
invariant x > 10
"""
    runtime = Runtime()
    ast = parse(source)
    with pytest.raises(Exception):
        runtime.run(ast)

def test_remove_capability():
    source = """
energy[100]
remove[invariants]
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 120
    assert not runtime.energy.has_capability('invariants')

def test_binary_operations():
    source = """
energy[100]
a <- 10 + 5
b <- 20 - 3
c <- 4 * 2
d <- 10 / 2
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)

    assert runtime.get_var('a').get() == 15.0
    assert runtime.get_var('b').get() == 17.0
    assert runtime.get_var('c').get() == 8.0
    assert runtime.get_var('d').get() == 5.0

def test_while_loop_deterministic():
    source = """
energy[100]
stable counter <- 0
stable sum <- 0

while counter < 5 {
    sum <- sum + counter
    counter <- counter + 1
}
"""
    results = []
    for _ in range(5):
        runtime = Runtime()
        ast = parse(source)
        runtime.run(ast)
        results.append(runtime.get_var('sum').get())

    assert all(r == pytest.approx(results[0]) for r in results)
    assert results[0] == pytest.approx(7.6)

def test_insufficient_energy():
    source = """
energy[5]
stable x <- 10
stable y <- 20
"""
    runtime = Runtime()
    ast = parse(source)
    with pytest.raises(Exception):
        runtime.run(ast)

def test_energy_costs_are_fixed():
    source = """
energy[20]
stable a <- 1
stable b <- 2
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 10

def test_determinism_across_runs():
    source = """
energy[100]
x <- 10
stable y <- 5
inspect x
invariant y > 0
"""
    results = []
    for _ in range(5):
        runtime = Runtime()
        ast = parse(source)
        runtime.run(ast)
        results.append(runtime.energy.get_energy())

    assert all(r == results[0] for r in results)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
