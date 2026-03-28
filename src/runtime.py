from typing import Any, Dict, List, Optional
from src.ast_nodes import *
from src.values import UnstableValue, StableValue, Function
from src.energy import EnergySystem


class RuntimeError(Exception):
    pass


class Runtime:
    """
    The runtime interpreter for Hiesenoether.

    Executes the AST and manages:
    - Variable environments (with closure support)
    - Energy budget (fixed costs, no hidden inflation)
    - Function calls (pure caching, unstable escrow)
    - Invariant checking (deterministic)

    Determinism guarantee:
        The same program will always produce the same output.
        There is no use of hash(), random, or any process-dependent state.
    """

    def __init__(self):
        self.energy = EnergySystem()
        self.globals: Dict[str, Any] = {}
        self.locals_stack: List[Dict[str, Any]] = []
        self.invariants: List[ASTNode] = []
        self.return_value = None
        self.returning = False

    def set_var(self, name: str, value: Any, is_local: bool = False):
        """Set variable in current scope."""
        if is_local and self.locals_stack:
            self.locals_stack[-1][name] = value
        else:
            self.globals[name] = value

    def push_scope(self):
        """Push a new local scope."""
        self.locals_stack.append({})

    def pop_scope(self):
        """Pop the current local scope."""
        if self.locals_stack:
            self.locals_stack.pop()

    def check_invariants(self):
        """
        Check all registered invariants.

        Behavior under energy pressure:
            When pressure > 0.5, invariants are checked in a degraded mode:
            every other invariant (by list index) is skipped. This is
            DETERMINISTIC — the same invariant at the same index is always
            either checked or skipped for a given pressure level.

            When a checked invariant fails under pressure > 0.3, a warning
            is printed instead of raising an error (weakened enforcement).

        When pressure <= 0.5, all invariants are fully enforced.
        """
        if not self.energy.has_capability('invariants'):
            return

        pressure = self.energy.pressure()

        for idx, invariant in enumerate(self.invariants):
            # Deterministic skip: use list index, not hash
            if pressure > 0.5 and idx % 2 == 0:
                continue

            result = self.eval_expr(invariant)
            if not result:
                if pressure < 0.3:
                    raise RuntimeError(f"Invariant violated: {invariant}")
                else:
                    print("## Invariant weakened under energy pressure")

    def run(self, program: Program):
        """Execute a program."""
        for stmt in program.statements:
            self.exec_stmt(stmt)
            self.check_invariants()

        # Burn unreleased escrows at end
        burned = self.energy.burn_unreleased_escrows()
        if burned > 0:
            print(f"## Warning: {burned} energy burned from unreleased escrows")

    def exec_stmt(self, stmt: ASTNode):
        """Execute a statement."""
        if self.returning:
            return

        if isinstance(stmt, EnergyDecl):
            self.energy.set_initial_energy(stmt.amount)

        elif isinstance(stmt, Assignment):
            value = self.eval_expr(stmt.value)

            if stmt.is_stable:
                if not self.energy.spend('stable_var'):
                    raise RuntimeError(
                        f"Insufficient energy for stable assignment "
                        f"(need {self.energy.check_cost('stable_var')})"
                    )
                wrapped_value = StableValue(value)
            else:
                # Unstable by default (free)
                wrapped_value = UnstableValue(value)

            self.set_var(stmt.name, wrapped_value)

        elif isinstance(stmt, Stabilize):
            var = self.get_var(stmt.name)

            if not self.energy.spend('stabilize'):
                raise RuntimeError(
                    f"Insufficient energy to stabilize "
                    f"(need {self.energy.check_cost('stabilize')})"
                )

            if hasattr(var, 'stabilize'):
                var.stabilize()

        elif isinstance(stmt, FunctionDecl):
            if stmt.is_unstable:
                cost_key = 'declare_unstable_fn'
            elif stmt.is_pure:
                cost_key = 'declare_pure_fn'
            else:
                cost_key = 'declare_fn'

            if not self.energy.spend(cost_key):
                raise RuntimeError(
                    f"Insufficient energy to declare function "
                    f"(need {self.energy.check_cost(cost_key)})"
                )

            # Capture current global environment as closure snapshot
            func = Function(
                name=stmt.name,
                params=stmt.params,
                body=stmt.body,
                is_pure=stmt.is_pure,
                is_unstable=stmt.is_unstable,
                closure=dict(self.globals),
            )

            self.set_var(stmt.name, func)

            if stmt.is_unstable:
                self.energy.create_escrow(stmt.name)

        elif isinstance(stmt, Return):
            if stmt.value is not None:
                self.return_value = self.eval_expr(stmt.value)
            else:
                self.return_value = None
            self.returning = True

        elif isinstance(stmt, Print):
            value = self.eval_expr(stmt.value)
            print(value)

        elif isinstance(stmt, Inspect):
            value = self.eval_expr(stmt.value)

            # Inspect rule: observation ONLY mutates state if energy is paid.
            # If energy spend fails, inspection is partial (read-only).
            # If energy spend succeeds, entropy increases (observer effect).
            if self.energy.spend('inspect'):
                # Successful inspection: observer effect applies
                if hasattr(value, 'observe'):
                    value.observe()
                if hasattr(value, 'inspect'):
                    print(f"[INSPECT] {value.inspect()}")
                else:
                    print(f"[INSPECT] {value}")
            else:
                # Failed inspection: read-only, no mutation
                print("[INSPECT] Partial inspection (energy starved)")

        elif isinstance(stmt, QueryEnergy):
            print(f"Energy: {self.energy.get_energy()}/{self.energy.get_max_energy()}")

        elif isinstance(stmt, Invariant):
            if not self.energy.has_capability('invariants'):
                raise RuntimeError("Invariants capability has been removed")

            if not self.energy.spend('invariant'):
                raise RuntimeError(
                    f"Insufficient energy for invariant "
                    f"(need {self.energy.check_cost('invariant')})"
                )

            self.invariants.append(stmt.condition)

            # Check immediately
            if not self.eval_expr(stmt.condition):
                raise RuntimeError(f"Invariant violated on declaration: {stmt.condition}")

        elif isinstance(stmt, Assert):
            if not self.energy.spend('assert'):
                raise RuntimeError(
                    f"Insufficient energy for assert "
                    f"(need {self.energy.check_cost('assert')})"
                )

            if not self.eval_expr(stmt.condition):
                raise RuntimeError(f"Assertion failed: {stmt.condition}")

        elif isinstance(stmt, If):
            # Note: the parser does not produce stable if statements.
            # All if statements are free control flow.
            condition = self.eval_expr(stmt.condition)

            if condition:
                for s in stmt.then_block:
                    self.exec_stmt(s)
            elif stmt.else_block:
                for s in stmt.else_block:
                    self.exec_stmt(s)

        elif isinstance(stmt, While):
            # While loops are free control flow.
            # Energy is spent by operations inside the loop body,
            # not by the loop structure itself.
            while self.eval_expr(stmt.condition):
                for s in stmt.body:
                    self.exec_stmt(s)
                    if self.returning:
                        return

        elif isinstance(stmt, For):
            iterable = self.eval_expr(stmt.iterable)

            if isinstance(iterable, range):
                items = list(iterable)
            elif isinstance(iterable, list):
                items = iterable
            else:
                raise RuntimeError(f"Cannot iterate over {type(iterable)}")

            for item in items:
                self.set_var(stmt.var, StableValue(item), is_local=True)
                for s in stmt.body:
                    self.exec_stmt(s)
                    if self.returning:
                        return

        elif isinstance(stmt, Remove):
            if not self.energy.remove_capability(stmt.capability):
                raise RuntimeError(f"Cannot remove capability: {stmt.capability}")
            print(f"## Removed capability: {stmt.capability}, gained energy")

        elif isinstance(stmt, FunctionCall):
            self.eval_expr(stmt)

    def eval_expr(self, expr: ASTNode) -> Any:
        """Evaluate an expression."""
        if isinstance(expr, Number):
            return expr.value

        elif isinstance(expr, String):
            return expr.value

        elif isinstance(expr, Identifier):
            var = self.get_var(expr.name)

            if isinstance(var, StableValue):
                # Stable values ALWAYS return their stored value.
                # No degradation. No pressure effects. This is the
                # guarantee the programmer paid energy for.
                return var.get()
            if isinstance(var, UnstableValue):
                return var.get()
            return var

        elif isinstance(expr, BinaryOp):
            left = self.eval_expr(expr.left)
            right = self.eval_expr(expr.right)

            ops = {
                '+': lambda a, b: a + b,
                '-': lambda a, b: a - b,
                '*': lambda a, b: a * b,
                '/': lambda a, b: a / b,
                '%': lambda a, b: a % b,
                '==': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '<': lambda a, b: a < b,
                '>': lambda a, b: a > b,
                '<=': lambda a, b: a <= b,
                '>=': lambda a, b: a >= b,
                'and': lambda a, b: a and b,
                'or': lambda a, b: a or b,
            }

            if expr.op in ops:
                return ops[expr.op](left, right)
            else:
                raise RuntimeError(f"Unknown operator: {expr.op}")

        elif isinstance(expr, UnaryOp):
            operand = self.eval_expr(expr.operand)

            if expr.op == '-':
                return -operand
            elif expr.op == 'not':
                return not operand
            else:
                raise RuntimeError(f"Unknown unary operator: {expr.op}")

        elif isinstance(expr, FunctionCall):
            func = self.get_var(expr.name)

            if not isinstance(func, Function):
                raise RuntimeError(f"{expr.name} is not a function")

            args = [self.eval_expr(arg) for arg in expr.args]

            if len(args) != len(func.params):
                raise RuntimeError(
                    f"Function {func.name} expects {len(func.params)} args, "
                    f"got {len(args)}"
                )

            # Pure function caching
            cache_key = None
            if func.is_pure:
                cache_key = tuple(args)
                cache = getattr(func, "_cache", {})
                if cache_key in cache:
                    return cache[cache_key]

            # Create new scope
            self.push_scope()

            # Bind parameters
            for param, arg in zip(func.params, args):
                self.set_var(param, StableValue(arg), is_local=True)

            # Execute body — variable resolution uses closure
            # The closure is accessed through get_var's resolution chain:
            # locals → closure → globals. We temporarily store the active
            # closure so get_var can use it.
            prev_closure = getattr(self, '_active_closure', None)
            self._active_closure = func.closure

            self.returning = False
            for s in func.body:
                self.exec_stmt(s)
                if self.returning:
                    break

            result = self.return_value
            self.return_value = None
            self.returning = False

            self._active_closure = prev_closure
            self.pop_scope()

            # Cache result for pure functions and award energy gain
            if func.is_pure:
                func._cache = getattr(func, "_cache", {})
                func._cache[cache_key] = result
                self.energy.release_pure_fn_gain(func.name)

            # Handle escrow for unstable functions
            if func.is_unstable:
                gained = self.energy.release_escrow(func.name, result)
                if gained < 0:
                    print(f"## Warning: {func.name} lied about instability")

            return result if result is not None else 0

        else:
            raise RuntimeError(f"Cannot evaluate: {type(expr)}")

    def get_var(self, name: str, closure: dict = None) -> Any:
        """
        Get variable from current scope.
        Resolution order: locals → active closure → globals
        """
        # Check locals first
        if self.locals_stack:
            if name in self.locals_stack[-1]:
                return self.locals_stack[-1][name]

        # Then active closure (set during function execution)
        active_closure = getattr(self, '_active_closure', None)
        if active_closure is not None and name in active_closure:
            return active_closure[name]

        # Then globals
        if name in self.globals:
            return self.globals[name]

        raise RuntimeError(f"Undefined variable: {name}")


def run_program(source: str):
    """Parse and execute a Hiesenoether program."""
    from src.parser import parse

    try:
        ast = parse(source)
        runtime = Runtime()
        runtime.run(ast)
    except Exception as e:
        print(f"Error: {e}")
        raise