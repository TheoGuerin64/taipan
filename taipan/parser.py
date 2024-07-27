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
from taipan.symbol_table import Symbol, SymbolTable


class Parser:
    def __init__(self, input: Path) -> None:
        self.lexer = Lexer(input)
        self.current_token = Token(TokenKind.EOF, -1, -1)
        self.peek_token = Token(TokenKind.EOF, -1, -1)
        self.symbol_tables: deque[SymbolTable] = deque()
        self.next_token()
        self.next_token()

    def match_token(self, token_kind: TokenKind) -> None:
        if self.current_token.kind != token_kind:
            raise TaipanSyntaxError(
                self.lexer.input,
                self.current_token.line,
                self.current_token.column,
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
            line=0,
            column=0,
        )

    def comparison(self) -> Comparison:
        left = self.expression()

        operator = ComparisonOperator.from_token(self.current_token)
        if operator is None:
            raise TaipanSyntaxError(
                self.lexer.input,
                self.current_token.line,
                self.current_token.column,
                f"Expected comparison operator, got {self.current_token.kind}",
            )
        self.next_token()

        right = self.expression()

        comparison = Comparison(
            left=left,
            right=right,
            operator=operator,
            line=left.line,
            column=left.column,
        )
        while operator := ComparisonOperator.from_token(self.current_token):
            right = self.expression()
            comparison = Comparison(
                left=comparison,
                right=right,
                operator=operator,
                line=comparison.line,
                column=comparison.column,
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
                line=node.line,
                column=node.column,
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
                line=node.line,
                column=node.column,
            )

        return node

    def unary(self) -> UnaryExpression | Identifier | Number:
        operator = UnaryOperator.from_token(self.current_token)
        if operator is None:
            return self.literal()

        line = self.current_token.line
        column = self.current_token.column

        self.next_token()
        return UnaryExpression(
            operator=operator,
            value=self.literal(),
            line=line,
            column=column,
        )

    def number(self) -> Number:
        assert isinstance(self.current_token.value, float)
        node = Number(
            value=self.current_token.value,
            line=self.current_token.line,
            column=self.current_token.column,
        )

        self.next_token()
        return node

    def identifier(self) -> Identifier:
        assert isinstance(self.current_token.value, str)
        node = Identifier(
            name=self.current_token.value,
            line=self.current_token.line,
            column=self.current_token.column,
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
                    self.lexer.input,
                    self.current_token.line,
                    self.current_token.column,
                    f"Expected literal, got {self.current_token.kind}",
                )

    def block(self) -> Block:
        symbol_table = SymbolTable(self.lexer.input)
        block = Block(
            line=self.current_token.line,
            column=self.current_token.column,
            symbol_table=symbol_table,
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
        line = self.current_token.line
        column = self.current_token.column

        self.next_token()
        return If(
            condition=self.comparison(),
            block=self.block(),
            line=line,
            column=column,
        )

    def while_statement(self) -> While:
        line = self.current_token.line
        column = self.current_token.column

        self.next_token()
        return While(
            condition=self.comparison(),
            block=self.block(),
            line=line,
            column=column,
        )

    def input_statement(self) -> Input:
        line = self.current_token.line
        column = self.current_token.column

        self.next_token()
        return Input(
            identifier=self.identifier(),
            line=line,
            column=column,
        )

    def print_statement(self) -> Print:
        line = self.current_token.line
        column = self.current_token.column

        self.next_token()
        match self.current_token.kind:
            case TokenKind.STRING:
                assert isinstance(self.current_token.value, str)
                value = String(
                    value=self.current_token.value,
                    line=self.current_token.line,
                    column=self.current_token.column,
                )
                self.next_token()
            case _:
                value = self.expression()

        return Print(
            value=value,
            line=line,
            column=column,
        )

    def declaration_statement(self) -> Declaration:
        line = self.current_token.line
        column = self.current_token.column

        self.next_token()
        identifier = self.identifier()
        self.symbol_tables[-1].define(Symbol(identifier.name, line, column))

        if self.current_token.kind == TokenKind.ASSIGNMENT:
            self.next_token()
            expression = self.expression()
        else:
            expression = None

        return Declaration(
            identifier=identifier,
            expression=expression,
            line=line,
            column=column,
        )

    def assignment_statement(self) -> Assignment:
        identifier = self.identifier()
        self.match_token(TokenKind.ASSIGNMENT)
        return Assignment(
            identifier=identifier,
            expression=self.expression(),
            line=identifier.line,
            column=identifier.column,
        )

    def statement(self) -> Statement:
        match self.current_token.kind:
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
                    self.lexer.input,
                    self.current_token.line,
                    self.current_token.column,
                    f"Expected statement, got {self.current_token.kind}",
                )

    def nl(self) -> None:
        self.match_token(TokenKind.NEWLINE)
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()
