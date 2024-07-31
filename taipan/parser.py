from collections import deque
from pathlib import Path

from taipan.ast import (
    ArithmeticOperator,
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    ComparisonOperator,
    Declaration,
    Identifier,
    If,
    Input,
    Number,
    Print,
    Program,
    Statement,
    String,
    UnaryExpression,
    UnaryOperator,
    While,
)
from taipan.exceptions import TaipanSyntaxError
from taipan.lexer import Lexer, Token, TokenKind
from taipan.symbol_table import SymbolTable
from taipan.utils import Location

INVALID_TOKEN = Token(TokenKind.EOF, Location(Path(""), -1, -1))


class Parser:
    def __init__(self, input: Path) -> None:
        self.lexer = Lexer(input)
        self.symbol_tables = deque[SymbolTable]()

        self.current_token = INVALID_TOKEN
        self.peek_token = INVALID_TOKEN
        self.next_token()
        self.next_token()

    def match_token(self, token_kind: TokenKind) -> None:
        if self.current_token.kind != token_kind:
            raise TaipanSyntaxError(
                self.current_token.location,
                f"Expected {token_kind}, got {self.current_token.kind}",
            )
        self.next_token()

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def program(self) -> Program:
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()

        return Program(
            block=self.block(),
            location=Location(self.lexer.file, 0, 0),
        )

    def comparison(self) -> Comparison:
        left = self.expression()

        operator = ComparisonOperator.from_token(self.current_token)
        if operator is None:
            raise TaipanSyntaxError(
                self.current_token.location,
                f"Expected comparison operator, got {self.current_token.kind}",
            )
        self.next_token()

        right = self.expression()

        comparison = Comparison(
            left=left,
            right=right,
            operator=operator,
            location=left.location,
        )
        while operator := ComparisonOperator.from_token(self.current_token):
            right = self.expression()
            comparison = Comparison(
                left=comparison,
                right=right,
                operator=operator,
                location=comparison.location,
            )
            self.next_token()

        return comparison

    def expression(self) -> BinaryExpression | UnaryExpression | Identifier | Number:
        node = self.term()
        while operator := ArithmeticOperator.expression_from_token(self.current_token):
            self.next_token()
            node = BinaryExpression(
                left=node,
                right=self.term(),
                operator=operator,
                location=node.location,
            )

        return node

    def term(self) -> BinaryExpression | UnaryExpression | Identifier | Number:
        node = self.unary()
        while operator := ArithmeticOperator.term_from_token(self.current_token):
            self.next_token()
            node = BinaryExpression(
                left=node,
                right=self.unary(),
                operator=operator,
                location=node.location,
            )

        return node

    def unary(self) -> UnaryExpression | Identifier | Number:
        operator = UnaryOperator.from_token(self.current_token)
        if operator is None:
            return self.literal()

        location = self.current_token.location

        self.next_token()
        return UnaryExpression(
            operator=operator,
            value=self.literal(),
            location=location,
        )

    def number(self) -> Number:
        assert isinstance(self.current_token.value, float)
        node = Number(
            value=self.current_token.value,
            location=self.current_token.location,
        )

        self.next_token()
        return node

    def identifier(self) -> Identifier:
        assert isinstance(self.current_token.value, str)
        node = Identifier(
            name=self.current_token.value,
            location=self.current_token.location,
        )

        self.next_token()
        return node

    def literal(self) -> Identifier | Number:
        match self.current_token.kind:
            case TokenKind.NUMBER:
                return self.number()
            case TokenKind.IDENTIFIER:
                return self.identifier()
            case _:
                raise TaipanSyntaxError(
                    self.current_token.location,
                    f"Expected literal, got {self.current_token.kind}",
                )

    def block(self) -> Block:
        symbol_table = SymbolTable()
        block = Block(
            symbol_table=symbol_table,
            location=self.current_token.location,
        )
        self.symbol_tables.append(symbol_table)

        self.match_token(TokenKind.OPEN_BRACE)
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()

        while self.current_token.kind != TokenKind.CLOSE_BRACE:
            block.statements.append(self.statement())
            self.nl()
        self.next_token()

        self.symbol_tables.pop()
        return block

    def if_statement(self) -> If:
        location = self.current_token.location

        self.next_token()
        return If(
            condition=self.comparison(),
            block=self.block(),
            location=location,
        )

    def while_statement(self) -> While:
        location = self.current_token.location

        self.next_token()
        return While(
            condition=self.comparison(),
            block=self.block(),
            location=location,
        )

    def input_statement(self) -> Input:
        location = self.current_token.location

        self.next_token()
        return Input(
            identifier=self.identifier(),
            location=location,
        )

    def print_statement(self) -> Print:
        location = self.current_token.location

        self.next_token()
        match self.current_token.kind:
            case TokenKind.STRING:
                assert isinstance(self.current_token.value, str)
                value = String(value=self.current_token.value, location=location)
                self.next_token()
            case _:
                value = self.expression()

        return Print(value=value, location=location)

    def declaration_statement(self) -> Declaration:
        location = self.current_token.location

        self.next_token()
        identifier = self.identifier()
        self.symbol_tables[-1].define(identifier.name, location)

        if self.current_token.kind == TokenKind.ASSIGNMENT:
            self.next_token()
            expression = self.expression()
        else:
            expression = None

        return Declaration(identifier=identifier, expression=expression, location=location)

    def assignment_statement(self) -> Assignment:
        identifier = self.identifier()
        self.match_token(TokenKind.ASSIGNMENT)
        return Assignment(
            identifier=identifier,
            expression=self.expression(),
            location=identifier.location,
        )

    def statement(self) -> Statement:
        match self.current_token.kind:
            case TokenKind.OPEN_BRACE:
                return self.block()
            case TokenKind.IF:
                return self.if_statement()
            case TokenKind.WHILE:
                return self.while_statement()
            case TokenKind.INPUT:
                return self.input_statement()
            case TokenKind.PRINT:
                return self.print_statement()
            case TokenKind.DECLARATION:
                return self.declaration_statement()
            case TokenKind.IDENTIFIER:
                return self.assignment_statement()
            case _:
                raise TaipanSyntaxError(
                    self.current_token.location,
                    f"Expected statement, got {self.current_token.kind}",
                )

    def nl(self) -> None:
        self.match_token(TokenKind.NEWLINE)
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()
