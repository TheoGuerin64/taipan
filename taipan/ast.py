from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .lexer import Token, TokenKind

type Expression = Identifier | Number | BinaryExpression | UnaryExpression
type Statement = If | While | Input | Print | Assignment


@dataclass(kw_only=True, repr=False)
class Node:
    def __repr__(self) -> str:
        attributes = [
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not isinstance(value, Node)
            if not isinstance(value, list) or not any(isinstance(item, Node) for item in value)
        ]
        return f"{self.__class__.__name__}({', '.join(attributes)})"


@dataclass(kw_only=True, repr=False)
class Identifier(Node):
    name: str


@dataclass(kw_only=True, repr=False)
class Literal[T](Node):
    value: T


@dataclass(kw_only=True, repr=False)
class Number(Literal[float]):
    pass


@dataclass(kw_only=True, repr=False)
class String(Literal[str]):
    pass


class ArithmeticOperator(StrEnum):
    ADD = "+"
    SUBSTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"

    @staticmethod
    def expression_from_token(token: Token) -> ArithmeticOperator | None:
        match token.kind:
            case TokenKind.PLUS:
                return ArithmeticOperator.ADD
            case TokenKind.MINUS:
                return ArithmeticOperator.SUBSTRACT

    @staticmethod
    def term_from_token(token: Token) -> ArithmeticOperator | None:
        match token.kind:
            case TokenKind.MULTIPLICATION:
                return ArithmeticOperator.MULTIPLY
            case TokenKind.DIVISION:
                return ArithmeticOperator.DIVIDE
            case TokenKind.MODULO:
                return ArithmeticOperator.MODULO


@dataclass(kw_only=True, repr=False)
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


@dataclass(kw_only=True, repr=False)
class UnaryExpression(Node):
    value: Identifier | Number
    operator: UnaryOperator


class ComparaisonOperator(StrEnum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="

    @staticmethod
    def from_token(token: Token) -> ComparaisonOperator | None:
        match token.kind:
            case TokenKind.EQUAL:
                return ComparaisonOperator.EQUAL
            case TokenKind.NOT_EQUAL:
                return ComparaisonOperator.NOT_EQUAL
            case TokenKind.LESS:
                return ComparaisonOperator.LESS
            case TokenKind.LESS_EQUAL:
                return ComparaisonOperator.LESS_EQUAL
            case TokenKind.GREATER:
                return ComparaisonOperator.GREATER
            case TokenKind.GREATER_EQUAL:
                return ComparaisonOperator.GREATER_EQUAL


@dataclass(kw_only=True, repr=False)
class Comparaison(Node):
    left: Expression | Comparaison
    right: Expression | Comparaison
    operator: ComparaisonOperator


@dataclass(kw_only=True, repr=False)
class Block(Node):
    statements: list[Statement] = field(default_factory=list)


@dataclass(kw_only=True, repr=False)
class Program(Node):
    block: Block = field(default_factory=Block)


@dataclass(kw_only=True, repr=False)
class If(Node):
    condition: Comparaison
    block: Block = field(default_factory=Block)


@dataclass(kw_only=True, repr=False)
class While(Node):
    condition: Comparaison
    block: Block = field(default_factory=Block)


@dataclass(kw_only=True, repr=False)
class Input(Node):
    identifier: Identifier


@dataclass(kw_only=True, repr=False)
class Print(Node):
    value: Expression | String


@dataclass(kw_only=True, repr=False)
class Assignment(Node):
    identifier: Identifier
    expression: Expression


@dataclass
class AST:
    root: Program
