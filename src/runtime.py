from typing import Any, Dict, List, Optional
from src.ast_nodes import *
from src.values import UnstableValue, StableValue, Function
from src.energy import EnergySystem

class RuntimeError(Exception):
    pass

class Runtime:

    def __init__(self):
        self.energy = EnergySystem()
        self.globals: Dict[str, Any] = {}
        self.locals_stack: List[Dict[str, Any]] = []
        self.invariants: List[ASTNode] = []
        self.return_value = None
        self.returning = False

    def set_var(self, name: str, value: Any, is_local: bool = False):
        if is_local and self.locals_stack:
            self.locals_stack[-1][name] = value
        else:
            self.globals[name] = value

    def push_scope(self):
        self.locals_stack.append({})

    def pop_scope(self):
        if self.locals_stack:
            self.locals_stack.pop()

    def check_invariants(self):
        if not self.energy.has_capability('invariants'):
            return

        pressure = self.energy.pressure()

        for idx, invariant in enumerate(self.invariants):
            if pressure > 0.5 and idx % 2 == 0:
                continue

            result = self.eval_expr(invariant)
            if not result:
                if pressure < 0.3:
                    raise RuntimeError(f"Invariant violated: {invariant}")
                else:
                    print("## Invariant weakened under energy pressure")

    def run(self, program: Program):
        for stmt in program.statements:
            self.exec_stmt(stmt)
            self.check_invariants()

        burned = self.energy.burn_unreleased_escrows()
        if burned > 0:
            print(f"## Warning: {burned} energy burned from unreleased escrows")

    def exec_stmt(self, stmt: ASTNode):
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
            if isinstance(stmt.value, Identifier):
                target = self.get_var(stmt.value.name)
            else:
                target = self.eval_expr(stmt.value)

            if self.energy.spend('inspect'):
                if hasattr(target, 'observe'):
                    target.observe()
                if hasattr(target, 'inspect'):
                    print(f"[INSPECT] {target.inspect()}")
                else:
                    print(f"[INSPECT] {target}")
            else:
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
            condition = self.eval_expr(stmt.condition)

            if condition:
                for s in stmt.then_block:
                    self.exec_stmt(s)
            elif stmt.else_block:
                for s in stmt.else_block:
                    self.exec_stmt(s)

        elif isinstance(stmt, While):
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
        if isinstance(expr, Number):
            return expr.value

        elif isinstance(expr, String):
            return expr.value

        elif isinstance(expr, Identifier):
            var = self.get_var(expr.name)

            if isinstance(var, StableValue):
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

            cache_key = None
            if func.is_pure:
                cache_key = tuple(args)
                cache = getattr(func, "_cache", {})
                if cache_key in cache:
                    return cache[cache_key]

            self.push_scope()

            for param, arg in zip(func.params, args):
                self.set_var(param, StableValue(arg), is_local=True)

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

            if func.is_pure:
                func._cache = getattr(func, "_cache", {})
                func._cache[cache_key] = result
                self.energy.release_pure_fn_gain(func.name)

            if func.is_unstable:
                gained = self.energy.release_escrow(func.name, result)
                if gained < 0:
                    print(f"## Warning: {func.name} lied about instability")

            return result if result is not None else 0

        else:
            raise RuntimeError(f"Cannot evaluate: {type(expr)}")

    def get_var(self, name: str, closure: dict = None) -> Any:
        if self.locals_stack:
            if name in self.locals_stack[-1]:
                return self.locals_stack[-1][name]

        active_closure = getattr(self, '_active_closure', None)
        if active_closure is not None and name in active_closure:
            return active_closure[name]

        if name in self.globals:
            return self.globals[name]

        raise RuntimeError(f"Undefined variable: {name}")

def run_program(source: str):
    from src.parser import parse

    try:
        ast = parse(source)
        runtime = Runtime()
        runtime.run(ast)
    except Exception as e:
        print(f"Error: {e}")
        raise
