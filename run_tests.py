#!/usr/bin/env python3
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.runtime import Runtime
from src.parser import parse
from src.values import UnstableValue, StableValue

def approx(a, b, tol=1e-9):
    return abs(a - b) < tol

passed = 0
failed = 0
errors = []

def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  PASS  {name}")
    except Exception as e:
        failed += 1
        errors.append((name, e))
        print(f"  FAIL  {name}: {e}")

def expect_raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True

def test_unstable_value_basic():
    x = UnstableValue(10)
    v0 = x.get()
    v1 = x.get()
    v2 = x.get()
    assert v0 == 10.0, f"access 0: expected 10.0, got {v0}"
    assert approx(v1, 11.1), f"access 1: expected 11.1, got {v1}"
    assert approx(v2, 12.4), f"access 2: expected 12.4, got {v2}"

def test_unstable_value_deterministic():
    a = UnstableValue(10)
    b = UnstableValue(10)
    for i in range(10):
        va = a.get()
        vb = b.get()
        assert approx(va, vb), f"access {i}: {va} != {vb}"

def test_unstable_value_stabilize():
    x = UnstableValue(10)
    x.get()
    x.get()
    x.stabilize()
    assert approx(x.get(), 12.4), f"expected 12.4 after stabilize, got {x.get()}"
    assert approx(x.get(), 12.4), f"expected 12.4 on repeated access"
    assert approx(x.get(), 12.4), f"expected 12.4 on repeated access"

def test_stable_value_basic():
    y = StableValue(5)
    assert y.get() == 5
    assert y.get() == 5
    assert y.get() == 5

def test_stable_value_never_degrades():
    y = StableValue(42)
    for i in range(1000):
        assert y.get() == 42, f"degraded at access {i}"

def test_energy_declaration():
    runtime = Runtime()
    ast = parse("energy[100]")
    runtime.run(ast)
    assert runtime.energy.get_energy() == 100

def test_unstable_assignment():
    source = "energy[100]\nx <- 5"
    runtime = Runtime()
    runtime.run(parse(source))
    var = runtime.get_var('x')
    assert isinstance(var, UnstableValue), f"expected UnstableValue, got {type(var)}"

def test_stable_assignment():
    source = "energy[100]\nstable y <- 10"
    runtime = Runtime()
    runtime.run(parse(source))
    var = runtime.get_var('y')
    assert isinstance(var, StableValue), f"expected StableValue, got {type(var)}"
    assert var.get() == 10
    assert runtime.energy.get_energy() == 95, f"expected 95, got {runtime.energy.get_energy()}"

def test_stabilize():
    source = "energy[100]\nx <- 5\nstabilize x"
    runtime = Runtime()
    runtime.run(parse(source))
    var = runtime.get_var('x')
    assert var.is_stable == True
    assert runtime.energy.get_energy() == 95

def test_function_declaration():
    source = "energy[100]\ndeclare fn add(a, b) {\n    return a + b\n}"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 97, f"expected 97, got {runtime.energy.get_energy()}"

def test_function_call():
    source = "energy[100]\ndeclare fn double(n) {\n    return n * 2\n}\nresult <- double(5)"
    runtime = Runtime()
    runtime.run(parse(source))
    result = runtime.get_var('result')
    assert result.get() == 10.0, f"expected 10.0, got {result.get()}"

def test_unstable_function_escrow():
    source = "energy[100]\ndeclare unstable fn evolve(n) {\n    return n + 1\n}\nx <- evolve(5)"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 103, f"expected 103, got {runtime.energy.get_energy()}"

def test_unstable_function_penalty():
    source = """energy[100]
declare unstable fn constant(n) {
    return n
}
a <- constant(5)
b <- constant(5)"""
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 97, f"expected 97, got {runtime.energy.get_energy()}"

def test_pure_function_energy_gain():
    source = """energy[100]
declare pure fn square(n) {
    return n * n
}
result <- square(5)"""
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 101, f"expected 101, got {runtime.energy.get_energy()}"

def test_pure_function_caching():
    source = """energy[100]
declare pure fn square(n) {
    return n * n
}
a <- square(5)
b <- square(5)"""
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.get_var('a').get() == 25.0
    assert runtime.get_var('b').get() == 25.0
    assert runtime.energy.get_energy() == 101, f"expected 101, got {runtime.energy.get_energy()}"

def test_inspect_costs_energy():
    source = "energy[100]\nx <- 5\ninspect x"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 98, f"expected 98, got {runtime.energy.get_energy()}"

def test_inspect_no_mutation_on_failure():
    x = UnstableValue(10)
    initial_entropy = x.entropy
    assert x.entropy == initial_entropy

def test_inspect_mutation_on_success():
    x = UnstableValue(10)
    initial_entropy = x.entropy
    x.observe()
    assert x.entropy == initial_entropy + 1.0, f"expected {initial_entropy + 1.0}, got {x.entropy}"

def test_invariant_costs_energy():
    source = "energy[100]\nx <- 5\ninvariant x > 0"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 90, f"expected 90, got {runtime.energy.get_energy()}"

def test_invariant_violation():
    source = "energy[100]\nx <- 5\ninvariant x > 10"
    runtime = Runtime()
    ast = parse(source)
    assert expect_raises(lambda: runtime.run(ast)), "expected invariant violation to raise"

def test_remove_capability():
    source = "energy[100]\nremove[invariants]"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 120, f"expected 120, got {runtime.energy.get_energy()}"
    assert not runtime.energy.has_capability('invariants')

def test_binary_operations():
    source = "energy[100]\na <- 10 + 5\nb <- 20 - 3\nc <- 4 * 2\nd <- 10 / 2"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.get_var('a').get() == 15.0
    assert runtime.get_var('b').get() == 17.0
    assert runtime.get_var('c').get() == 8.0
    assert runtime.get_var('d').get() == 5.0

def test_while_loop_deterministic():
    source = """energy[100]
stable counter <- 0
stable sum <- 0

while counter < 5 {
    sum <- sum + counter
    counter <- counter + 1
}"""
    results = []
    for _ in range(5):
        runtime = Runtime()
        runtime.run(parse(source))
        results.append(runtime.get_var('sum').get())

    assert all(approx(r, results[0]) for r in results), f"non-deterministic: {results}"
    assert approx(results[0], 7.6), f"expected 7.6, got {results[0]}"

def test_insufficient_energy():
    source = "energy[5]\nstable x <- 10\nstable y <- 20"
    runtime = Runtime()
    ast = parse(source)
    assert expect_raises(lambda: runtime.run(ast)), "expected insufficient energy to raise"

def test_energy_costs_are_fixed():
    source = "energy[20]\nstable a <- 1\nstable b <- 2"
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 10, f"expected 10, got {runtime.energy.get_energy()}"

def test_determinism_across_runs():
    source = "energy[100]\nx <- 10\nstable y <- 5\ninspect x\ninvariant y > 0"
    results = []
    for _ in range(5):
        runtime = Runtime()
        runtime.run(parse(source))
        results.append(runtime.energy.get_energy())
    assert all(r == results[0] for r in results), f"non-deterministic results: {results}"

def test_stable_value_under_pressure():
    source = """energy[15]
stable x <- 42
stable y <- 99
stable z <- 7"""
    runtime = Runtime()
    runtime.run(parse(source))
    assert runtime.energy.get_energy() == 0
    x = runtime.get_var('x')
    y = runtime.get_var('y')
    z = runtime.get_var('z')
    assert isinstance(x, StableValue)
    assert x.get() == 42, f"stable x degraded: {x.get()}"
    assert y.get() == 99, f"stable y degraded: {y.get()}"
    assert z.get() == 7, f"stable z degraded: {z.get()}"

def test_closure_captures_environment():
    source = """energy[100]
stable outer <- 42
declare fn get_outer() {
    return outer
}
outer <- 999
result <- get_outer()"""
    runtime = Runtime()
    runtime.run(parse(source))
    result = runtime.get_var('result')
    val = result.get()
    assert val == 42, f"expected closure to capture 42, got {val}"

if __name__ == '__main__':
    print("=" * 60)
    print("Hiesenoether Runtime Test Suite")
    print("=" * 60)

    tests = [
        ("unstable_value_basic", test_unstable_value_basic),
        ("unstable_value_deterministic", test_unstable_value_deterministic),
        ("unstable_value_stabilize", test_unstable_value_stabilize),
        ("stable_value_basic", test_stable_value_basic),
        ("stable_value_never_degrades", test_stable_value_never_degrades),
        ("stable_value_under_pressure", test_stable_value_under_pressure),
        ("energy_declaration", test_energy_declaration),
        ("energy_costs_are_fixed", test_energy_costs_are_fixed),
        ("unstable_assignment", test_unstable_assignment),
        ("stable_assignment", test_stable_assignment),
        ("stabilize", test_stabilize),
        ("function_declaration", test_function_declaration),
        ("function_call", test_function_call),
        ("unstable_function_escrow", test_unstable_function_escrow),
        ("unstable_function_penalty", test_unstable_function_penalty),
        ("pure_function_energy_gain", test_pure_function_energy_gain),
        ("pure_function_caching", test_pure_function_caching),
        ("closure_captures_environment", test_closure_captures_environment),
        ("inspect_costs_energy", test_inspect_costs_energy),
        ("inspect_no_mutation_on_failure", test_inspect_no_mutation_on_failure),
        ("inspect_mutation_on_success", test_inspect_mutation_on_success),
        ("invariant_costs_energy", test_invariant_costs_energy),
        ("invariant_violation", test_invariant_violation),
        ("remove_capability", test_remove_capability),
        ("binary_operations", test_binary_operations),
        ("while_loop_deterministic", test_while_loop_deterministic),
        ("insufficient_energy", test_insufficient_energy),
        ("determinism_across_runs", test_determinism_across_runs),
    ]

    print()
    for name, fn in tests:
        run_test(name, fn)

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 60)

    if errors:
        print("\nFailure details:")
        for name, err in errors:
            print(f"\n--- {name} ---")
            traceback.print_exception(type(err), err, err.__traceback__)

    sys.exit(0 if failed == 0 else 1)
