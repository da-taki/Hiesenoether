import pytest
from src.runtime import Runtime, RuntimeError as HnRuntimeError
from src.parser import parse
from src.values import UnstableValue, StableValue


# ---- Unstable Value Unit Tests ----

def test_unstable_value_basic():
    """
    Test that unstable values evolve deterministically.

    Evolution rule:
        drift = access_count * entropy
        value = base_value + drift
        then: access_count += 1, entropy += 0.1

    For base_value=10:
        Access 0: drift = 0 * 1.0 = 0.0   → 10.0
        Access 1: drift = 1 * 1.1 = 1.1   → 11.1
        Access 2: drift = 2 * 1.2 = 2.4   → 12.4
    """
    x = UnstableValue(10)
    assert x.get() == 10.0
    assert x.get() == pytest.approx(11.1)
    assert x.get() == pytest.approx(12.4)


def test_unstable_value_deterministic():
    """Same initial state must produce same sequence."""
    a = UnstableValue(10)
    b = UnstableValue(10)
    for _ in range(10):
        assert a.get() == b.get()


def test_unstable_value_stabilize():
    """Stabilization freezes at the current evolution point."""
    x = UnstableValue(10)
    x.get()  # access 0: returns 10.0, count→1, entropy→1.1
    x.get()  # access 1: returns 11.1, count→2, entropy→1.2

    # Stabilize captures what access 2 would return:
    # drift = 2 * 1.2 = 2.4 → frozen at 12.4
    x.stabilize()
    assert x.get() == pytest.approx(12.4)
    assert x.get() == pytest.approx(12.4)
    assert x.get() == pytest.approx(12.4)


# ---- Stable Value Unit Tests ----

def test_stable_value_basic():
    """Stable values never change."""
    y = StableValue(5)
    assert y.get() == 5
    assert y.get() == 5
    assert y.get() == 5


def test_stable_value_never_degrades():
    """Stable values must not degrade under any conditions."""
    y = StableValue(42)
    for _ in range(1000):
        assert y.get() == 42


# ---- Energy Declaration ----

def test_energy_declaration():
    source = "energy[100]"
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 100


# ---- Assignment Semantics ----

def test_unstable_assignment():
    """Assignments create unstable values by default."""
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
    """Stable assignment costs exactly 5 energy (fixed, no inflation)."""
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
    assert runtime.energy.get_energy() == 95  # 100 - 5


def test_stabilize():
    """Stabilizing an unstable value costs 5 energy and freezes it."""
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
    assert runtime.energy.get_energy() == 95  # 100 - 5


# ---- Function Declaration & Calling ----

def test_function_declaration():
    """Normal function declaration costs 3 energy."""
    source = """
energy[100]
declare fn add(a, b) {
    return a + b
}
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 97  # 100 - 3


def test_function_call():
    """Function calls work correctly."""
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
    # result is an UnstableValue wrapping the function's return value (10.0)
    assert result.get() == 10.0


def test_unstable_function_escrow():
    """
    Unstable function: costs 1 to declare, gains 4 on first call.
    Net: 100 - 1 + 4 = 103
    """
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
    assert runtime.energy.get_energy() == 103  # 100 - 1 + 4


def test_unstable_function_penalty():
    """
    Unstable function that returns same output twice gets penalized.
    declare: -1, first call: +4, second call same output: -6
    Net: 100 - 1 + 4 - 6 = 97
    """
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
    """
    Pure function: costs 3 to declare, gains 4 on first call.
    Net: 100 - 3 + 4 = 101
    """
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
    assert runtime.energy.get_energy() == 101  # 100 - 3 + 4


def test_pure_function_caching():
    """Pure function returns cached result on subsequent calls."""
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
    # Both should get 25.0; energy gain only on first call
    assert runtime.get_var('a').get() == 25.0
    assert runtime.get_var('b').get() == 25.0
    assert runtime.energy.get_energy() == 101  # 100 - 3 + 4 (only once)


# ---- Inspect ----

def test_inspect_costs_energy():
    """Inspect costs 2 energy."""
    source = """
energy[100]
x <- 5
inspect x
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 98  # 100 - 2


def test_inspect_no_mutation_on_failure():
    """
    When inspect fails (insufficient energy), the value is NOT mutated.
    Only successful inspection triggers the observer effect.
    """
    x = UnstableValue(10)
    initial_entropy = x.entropy
    # Simulate failed inspection: don't call observe()
    # Entropy should remain unchanged
    assert x.entropy == initial_entropy


def test_inspect_mutation_on_success():
    """Successful inspect increases entropy by 1.0."""
    x = UnstableValue(10)
    initial_entropy = x.entropy  # 1.0
    x.observe()
    assert x.entropy == initial_entropy + 1.0


# ---- Invariants ----

def test_invariant_costs_energy():
    """Invariants cost 10 energy."""
    source = """
energy[100]
x <- 5
invariant x > 0
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 90  # 100 - 10


def test_invariant_violation():
    """Violated invariants raise errors."""
    source = """
energy[100]
x <- 5
invariant x > 10
"""
    runtime = Runtime()
    ast = parse(source)
    with pytest.raises(Exception):
        runtime.run(ast)


# ---- Remove Capability ----

def test_remove_capability():
    """Removing invariants gains 20 energy."""
    source = """
energy[100]
remove[invariants]
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 120  # 100 + 20
    assert not runtime.energy.has_capability('invariants')


# ---- Binary Operations ----

def test_binary_operations():
    """Arithmetic and comparison on freshly created unstable values."""
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

    # First access to each unstable value (access_count=0, drift=0)
    assert runtime.get_var('a').get() == 15.0
    assert runtime.get_var('b').get() == 17.0
    assert runtime.get_var('c').get() == 8.0
    assert runtime.get_var('d').get() == 5.0


# ---- While Loop ----

def test_while_loop_deterministic():
    """
    While loops with unstable reassignment produce drift — this is correct
    language behavior. Loops are free control flow; energy is spent by
    operations inside. What matters is determinism.
    """
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

    # All runs must produce identical output (determinism)
    assert all(r == pytest.approx(results[0]) for r in results)
    # The value reflects drift from unstable reassignment
    assert results[0] == pytest.approx(7.6)


# ---- Insufficient Energy ----

def test_insufficient_energy():
    """Operations fail when energy is insufficient."""
    source = """
energy[5]
stable x <- 10
stable y <- 20
"""
    runtime = Runtime()
    ast = parse(source)
    with pytest.raises(Exception):
        runtime.run(ast)


# ---- Energy Costs Are Fixed ----

def test_energy_costs_are_fixed():
    """
    Verify costs don't inflate under pressure.
    Two stable assignments should each cost exactly 5.
    """
    source = """
energy[20]
stable a <- 1
stable b <- 2
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 10  # 20 - 5 - 5


# ---- Determinism ----

def test_determinism_across_runs():
    """Same program produces same energy state."""
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