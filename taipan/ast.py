from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from .lexer import Token, TokenKind

type Expression = Identifier | Number | BinaryExpression | UnaryExpression
type Statement = If | While | Input | Print | Assignment


@dataclass(kw_only=True)
class Node:
    pass


@dataclass(kw_only=True)
class Identifier(Node):
    name: str


@dataclass(kw_only=True)
class Literal[T](Node):
    value: T


@dataclass(kw_only=True)
class Number(Literal[float]):
    pass


@dataclass(kw_only=True)
class String(Literal[str]):
    pass


class ArithmeticOperator(Enum):
    ADD = auto()
    SUBSTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()

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


@dataclass(kw_only=True)
class BinaryExpression(Node):
    left: Expression = field(repr=False)
    right: Expression = field(repr=False)
    operator: ArithmeticOperator


class UnaryOperator(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()

    @staticmethod
    def from_token(token: Token) -> UnaryOperator | None:
        match token.kind:
            case TokenKind.PLUS:
                return UnaryOperator.POSITIVE
            case TokenKind.MINUS:
                return UnaryOperator.NEGATIVE


@dataclass(kw_only=True)
class UnaryExpression(Node):
    value: Identifier | Number = field(repr=False)
    operator: UnaryOperator


class ComparaisonOperator(Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

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


@dataclass(kw_only=True)
class Comparaison(Node):
    left: Expression | Comparaison = field(repr=False)
    right: Expression | Comparaison = field(repr=False)
    operator: ComparaisonOperator


@dataclass(kw_only=True)
class Block(Node):
    statements: list[Statement] = field(default_factory=list, repr=False)


@dataclass(kw_only=True)
class Program(Node):
    block: Block = field(default_factory=Block, repr=False)


@dataclass(kw_only=True)
class If(Node):
    condition: Comparaison = field(repr=False)
    block: Block = field(default_factory=Block, repr=False)


@dataclass(kw_only=True)
class While(Node):
    condition: Comparaison = field(repr=False)
    block: Block = field(default_factory=Block, repr=False)


@dataclass(kw_only=True)
class Input(Node):
    identifier: Identifier = field(repr=False)


@dataclass(kw_only=True)
class Print(Node):
    value: Expression | String = field(repr=False)


@dataclass(kw_only=True)
class Assignment(Node):
    identifier: Identifier = field(repr=False)
    expression: Expression = field(repr=False)


@dataclass
class AST:
    root: Node
