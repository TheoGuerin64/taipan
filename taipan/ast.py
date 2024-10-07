from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import override

from taipan._lexer import Token, TokenKind
from taipan._visitor import Visitor
from taipan.location import Location
from taipan.symbol_table import SymbolTable

type ExpressionType = (
    Identifier | Number | ParentheseExpression | UnaryExpression | BinaryExpression | Comparison
)
type StatementType = Block | If | While | Input | Print | Declaration | Assignment
type LiteralType = String | Number


@dataclass(kw_only=True, frozen=True, repr=False)
class Node(ABC):
    location: Location

    @abstractmethod
    def accept(self, visitor: Visitor) -> None: ...

    @override
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
    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_string(self)


class Number(Literal[float], Expression):
    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_number(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class Identifier(Expression):
    name: str

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_identifier(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class ParentheseExpression(Expression):
    value: ExpressionType

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_parenthese_expression(self)


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

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_unary_expression(self)


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

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_binary_expression(self)


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

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_comparison(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class Block(Statement):
    statements: list[StatementType] = field(default_factory=list)
    symbol_table: SymbolTable = field(default_factory=SymbolTable)

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_block(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class If(Statement):
    condition: ExpressionType
    block: Block
    else_: If | Block | None = None

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_if(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class While(Statement):
    condition: ExpressionType
    block: Block

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_while(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class Input(Statement):
    identifier: Identifier

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_input(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class Print(Statement):
    value: ExpressionType | String

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_print(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class Declaration(Statement):
    identifier: Identifier
    expression: ExpressionType | None

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declaration(self)


@dataclass(kw_only=True, frozen=True, repr=False)
class Assignment(Statement):
    identifier: Identifier
    expression: ExpressionType

    @override
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_assignment(self)


@dataclass
class Program:
    block: Block


@dataclass
class AST:
    root: Program


__all__ = [
    "Node",
    "ExpressionType",
    "StatementType",
    "LiteralType",
    "Expression",
    "Statement",
    "Literal",
    "Number",
    "Identifier",
    "ParentheseExpression",
    "String",
    "UnaryOperator",
    "UnaryExpression",
    "ArithmeticOperator",
    "BinaryExpression",
    "ComparisonOperator",
    "Comparison",
    "Block",
    "If",
    "While",
    "Input",
    "Print",
    "Declaration",
    "Assignment",
    "Program",
    "AST",
]
