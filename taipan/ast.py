from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from taipan.lexer import Token, TokenKind
from taipan.symbol_table import SymbolTable

type Expression = Identifier | Number | BinaryExpression | UnaryExpression
type Statement = Block | If | While | Input | Print | Declaration | Assignment


@dataclass(kw_only=True, frozen=True, repr=False)
class Node:
    line: int
    column: int

    def __repr__(self) -> str:
        attributes = [
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if key != "parent" and not isinstance(value, (Node, NodeList))
        ]
        return f"{self.__class__.__name__}({', '.join(attributes)})"


class NodeList[T: Node](list[T]):
    pass


@dataclass(kw_only=True, frozen=True, repr=False)
class Identifier(Node):
    name: str


@dataclass(kw_only=True, frozen=True, repr=False)
class Literal[T](Node):
    value: T


@dataclass(kw_only=True, frozen=True, repr=False)
class Number(Literal[float]):
    pass


@dataclass(kw_only=True, frozen=True, repr=False)
class String(Literal[str]):
    pass


class ArithmeticOperator(StrEnum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"

    @staticmethod
    def expression_from_token(token: Token) -> ArithmeticOperator | None:
        match token.kind:
            case TokenKind.PLUS:
                return ArithmeticOperator.ADD
            case TokenKind.MINUS:
                return ArithmeticOperator.SUBTRACT

    @staticmethod
    def term_from_token(token: Token) -> ArithmeticOperator | None:
        match token.kind:
            case TokenKind.MULTIPLICATION:
                return ArithmeticOperator.MULTIPLY
            case TokenKind.DIVISION:
                return ArithmeticOperator.DIVIDE
            case TokenKind.MODULO:
                return ArithmeticOperator.MODULO


@dataclass(kw_only=True, frozen=True, repr=False)
class BinaryExpression(Node):
    left: Expression
    right: Expression
    operator: ArithmeticOperator


class UnaryOperator(StrEnum):
    POSITIVE = "+"
    NEGATIVE = "-"

    @staticmethod
    def from_token(token: Token) -> UnaryOperator | None:
        match token.kind:
            case TokenKind.PLUS:
                return UnaryOperator.POSITIVE
            case TokenKind.MINUS:
                return UnaryOperator.NEGATIVE


@dataclass(kw_only=True, frozen=True, repr=False)
class UnaryExpression(Node):
    value: Identifier | Number
    operator: UnaryOperator


class ComparisonOperator(StrEnum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="

    @staticmethod
    def from_token(token: Token) -> ComparisonOperator | None:
        match token.kind:
            case TokenKind.EQUAL:
                return ComparisonOperator.EQUAL
            case TokenKind.NOT_EQUAL:
                return ComparisonOperator.NOT_EQUAL
            case TokenKind.LESS:
                return ComparisonOperator.LESS
            case TokenKind.LESS_EQUAL:
                return ComparisonOperator.LESS_EQUAL
            case TokenKind.GREATER:
                return ComparisonOperator.GREATER
            case TokenKind.GREATER_EQUAL:
                return ComparisonOperator.GREATER_EQUAL


@dataclass(kw_only=True, frozen=True, repr=False)
class Comparison(Node):
    left: Expression | Comparison
    right: Expression | Comparison
    operator: ComparisonOperator


@dataclass(kw_only=True, frozen=True, repr=False)
class Block(Node):
    statements: NodeList[Statement] = field(default_factory=NodeList)
    symbol_table: SymbolTable


@dataclass(kw_only=True, frozen=True, repr=False)
class Program(Node):
    block: Block


@dataclass(kw_only=True, frozen=True, repr=False)
class If(Node):
    condition: Comparison
    block: Block


@dataclass(kw_only=True, frozen=True, repr=False)
class While(Node):
    condition: Comparison
    block: Block


@dataclass(kw_only=True, frozen=True, repr=False)
class Input(Node):
    identifier: Identifier


@dataclass(kw_only=True, frozen=True, repr=False)
class Print(Node):
    value: Expression | String


@dataclass(kw_only=True, frozen=True, repr=False)
class Declaration(Node):
    identifier: Identifier
    expression: Expression | None


@dataclass(kw_only=True, frozen=True, repr=False)
class Assignment(Node):
    identifier: Identifier
    expression: Expression


@dataclass
class AST:
    root: Program
