from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from taipan.lexer import Token, TokenKind
from taipan.location import Location
from taipan.symbol_table import SymbolTable

type ExpressionType = (
    Identifier | Number | ParentheseExpression | UnaryExpression | BinaryExpression | Comparison
)
type StatementType = Block | If | While | Input | Print | Declaration | Assignment
type LiteralType = String | Number


@dataclass(kw_only=True, frozen=True, repr=False)
class Node:
    location: Location

    def __repr__(self) -> str:
        return self.__class__.__name__


class Expression(Node):
    pass


class Statement(Node):
    pass


@dataclass(kw_only=True, frozen=True, repr=False)
class Literal[T](Node):
    value: T


class String(Literal[str]):
    pass


class Number(Literal[float], Expression):
    pass


@dataclass(kw_only=True, frozen=True, repr=False)
class Identifier(Expression):
    name: str


@dataclass(kw_only=True, frozen=True, repr=False)
class ParentheseExpression(Expression):
    value: ExpressionType


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
            case _:
                return None


@dataclass(kw_only=True, frozen=True, repr=False)
class UnaryExpression(Expression):
    value: Identifier | Number | ParentheseExpression
    operator: UnaryOperator


class ArithmeticOperator(StrEnum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"

    @staticmethod
    def additive_from_token(token: Token) -> ArithmeticOperator | None:
        match token.kind:
            case TokenKind.PLUS:
                return ArithmeticOperator.ADD
            case TokenKind.MINUS:
                return ArithmeticOperator.SUBTRACT
            case _:
                return None

    @staticmethod
    def multiplicative_from_token(token: Token) -> ArithmeticOperator | None:
        match token.kind:
            case TokenKind.MULTIPLICATION:
                return ArithmeticOperator.MULTIPLY
            case TokenKind.DIVISION:
                return ArithmeticOperator.DIVIDE
            case _:
                return None


@dataclass(kw_only=True, frozen=True, repr=False)
class BinaryExpression(Expression):
    left: ExpressionType
    right: ExpressionType
    operator: ArithmeticOperator


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
            case _:
                return None


@dataclass(kw_only=True, frozen=True, repr=False)
class Comparison(Expression):
    left: ExpressionType
    right: ExpressionType
    operator: ComparisonOperator


@dataclass(kw_only=True, frozen=True, repr=False)
class Block(Statement):
    statements: list[StatementType] = field(default_factory=list)
    symbol_table: SymbolTable = field(default_factory=SymbolTable)


@dataclass(kw_only=True, frozen=True, repr=False)
class If(Statement):
    condition: ExpressionType
    block: Block
    else_: If | Block | None = None


@dataclass(kw_only=True, frozen=True, repr=False)
class While(Statement):
    condition: ExpressionType
    block: Block


@dataclass(kw_only=True, frozen=True, repr=False)
class Input(Statement):
    identifier: Identifier


@dataclass(kw_only=True, frozen=True, repr=False)
class Print(Statement):
    value: ExpressionType | String


@dataclass(kw_only=True, frozen=True, repr=False)
class Declaration(Statement):
    identifier: Identifier
    expression: ExpressionType | None


@dataclass(kw_only=True, frozen=True, repr=False)
class Assignment(Statement):
    identifier: Identifier
    expression: ExpressionType


@dataclass
class Program:
    block: Block


@dataclass
class AST:
    root: Program
