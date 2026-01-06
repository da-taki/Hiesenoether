from dataclasses import dataclass
from typing import List, Optional, Any


## Base AST Node
@dataclass
class ASTNode:
    pass


## Program
@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


## Energy Declaration
@dataclass
class EnergyDecl(ASTNode):
    amount: int


## Variable Assignment
@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode
    is_stable: bool = False


## Stabilize Statement
@dataclass
class Stabilize(ASTNode):
    name: str


## Function Declaration
@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]
    is_pure: bool = False
    is_unstable: bool = False


## Return Statement
@dataclass
class Return(ASTNode):
    value: Optional[ASTNode] = None


## Function Call
@dataclass
class FunctionCall(ASTNode):
    name: str
    args: List[ASTNode]


## Print Statement
@dataclass
class Print(ASTNode):
    value: ASTNode


## Inspect Statement
@dataclass
class Inspect(ASTNode):
    value: ASTNode


## Query Energy
@dataclass
class QueryEnergy(ASTNode):
    pass


## Invariant Declaration
@dataclass
class Invariant(ASTNode):
    condition: ASTNode


## Assert Statement
@dataclass
class Assert(ASTNode):
    condition: ASTNode


## If Statement
@dataclass
class If(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None
    is_stable: bool = False


## While Loop
@dataclass
class While(ASTNode):
    condition: ASTNode
    body: List[ASTNode]


## For Loop
@dataclass
class For(ASTNode):
    var: str
    iterable: ASTNode
    body: List[ASTNode]


## Remove Capability
@dataclass
class Remove(ASTNode):
    capability: str


## Binary Operations
@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode


## Unary Operations
@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode


## Literals
@dataclass
class Number(ASTNode):
    value: float


@dataclass
class String(ASTNode):
    value: str


@dataclass
class Identifier(ASTNode):
    name: str


## Range (for 'for' loops)
@dataclass
class Range(ASTNode):
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode] = None