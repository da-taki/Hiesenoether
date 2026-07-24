from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class EnergyDecl(ASTNode):
    amount: int

@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode
    is_stable: bool = False

@dataclass
class Stabilize(ASTNode):
    name: str

@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]
    is_pure: bool = False
    is_unstable: bool = False

@dataclass
class Return(ASTNode):
    value: Optional[ASTNode] = None

@dataclass
class FunctionCall(ASTNode):
    name: str
    args: List[ASTNode]

@dataclass
class Print(ASTNode):
    value: ASTNode

@dataclass
class Inspect(ASTNode):
    value: ASTNode

@dataclass
class QueryEnergy(ASTNode):
    pass

@dataclass
class Invariant(ASTNode):
    condition: ASTNode

@dataclass
class Assert(ASTNode):
    condition: ASTNode

@dataclass
class If(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None
    is_stable: bool = False

@dataclass
class While(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class For(ASTNode):
    var: str
    iterable: ASTNode
    body: List[ASTNode]

@dataclass
class Remove(ASTNode):
    capability: str

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Number(ASTNode):
    value: float

@dataclass
class String(ASTNode):
    value: str

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class Range(ASTNode):
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode] = None
