import pytest
from runtime import Runtime, run_program
from parser import parse
from values import UnstableValue, StableValue


def test_unstable_value_basic():
    """Test that unstable values evolve on each access"""
    x = UnstableValue(10)
    assert x.get() == 10
    assert x.get() == 11
    assert x.get() == 12


def test_stable_value_basic():
    """Test that stable values don't change"""
    y = StableValue(5)
    assert y.get() == 5
    assert y.get() == 5
    assert y.get() == 5


def test_energy_declaration():
    """Test energy declaration"""
    source = "energy[100]"
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    assert runtime.energy.get_energy() == 100


def test_unstable_assignment():
    """Test that assignments create unstable values by default"""
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
    """Test stable assignment costs energy"""
    source = """
energy[100]
stable y <- 10
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    
    var = runtime.get_var('y')
    assert isinstance(var, StableValue)
    assert runtime.energy.get_energy() == 95  # 100 - 5


def test_stabilize():
    """Test stabilizing an unstable value"""
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


def test_function_declaration():
    """Test function declaration costs energy"""
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
    """Test function calls work correctly"""
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
    assert result.get() == 10


def test_unstable_function_escrow():
    """Test unstable function energy escrow"""
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
    
    # Declared unstable fn: -1 energy
    # First call releases escrow: +4 energy
    # Net: +3 energy, so 103
    assert runtime.energy.get_energy() == 103


def test_inspect_costs_energy():
    """Test that inspect costs energy"""
    source = """
energy[100]
x <- 5
inspect x
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    
    assert runtime.energy.get_energy() == 98  # 100 - 2


def test_invariant_costs_energy():
    """Test that invariants cost energy"""
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
    """Test that violated invariants raise errors"""
    source = """
energy[100]
x <- 5
invariant x > 10
"""
    runtime = Runtime()
    ast = parse(source)
    
    with pytest.raises(Exception):
        runtime.run(ast)


def test_stable_if_costs_energy():
    """Test stable if costs energy"""
    source = """
energy[100]
x <- 5
stable if x > 0 {
    print x
}
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    
    assert runtime.energy.get_energy() == 97  # 100 - 3


def test_remove_capability():
    """Test removing capabilities gains energy"""
    source = """
energy[100]
remove[invariants]
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    
    assert runtime.energy.get_energy() == 120  # 100 + 20
    assert not runtime.energy.has_capability('invariants')


def test_binary_operations():
    """Test arithmetic and comparison operations"""
    source = """
energy[100]
a <- 10 + 5
b <- 20 - 3
c <- 4 * 2
d <- 10 / 2
result <- a > b
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    
    assert runtime.get_var('a').get() == 15
    assert runtime.get_var('b').get() == 17
    assert runtime.get_var('c').get() == 8
    assert runtime.get_var('d').get() == 5.0
    assert runtime.get_var('result').get() == False


def test_while_loop():
    """Test while loops work"""
    source = """
energy[100]
stable counter <- 0
stable sum <- 0

while counter < 5 {
    sum <- sum + counter
    counter <- counter + 1
}
"""
    runtime = Runtime()
    ast = parse(source)
    runtime.run(ast)
    
    # sum should be 0+1+2+3+4 = 10
    assert runtime.get_var('sum').get() == 10


def test_insufficient_energy():
    """Test that operations fail when energy is insufficient"""
    source = """
energy[5]
stable x <- 10
stable y <- 20
"""
    runtime = Runtime()
    ast = parse(source)
    
    # Should fail on second stable assignment
    with pytest.raises(Exception):
        runtime.run(ast)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])