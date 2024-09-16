from collections import deque
from pathlib import Path

from taipan.ast import (
    AST,
    ArithmeticOperator,
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    ComparisonOperator,
    Declaration,
    Expression,
    Identifier,
    If,
    Input,
    Number,
    ParentheseExpression,
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
        self._next_token()
        self._next_token()

    @classmethod
    def parse(cls, input: Path) -> AST:
        parser = cls(input)
        return AST(parser._program())

    def _expect_token(self, token_kind: TokenKind) -> None:
        if self.current_token.kind != token_kind:
            raise TaipanSyntaxError(
                self.current_token.location,
                f"Expected {token_kind}, got {self.current_token.kind}",
            )

    def _match_token(self, token_kind: TokenKind) -> None:
        self._expect_token(token_kind)
        self._next_token()

    def _next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def _program(self) -> Program:
        return Program(
            block=self._block(),
            location=Location(self.lexer.file, 0, 0),
        )

    def _block(self) -> Block:
        self._skip_nl()
        self._expect_token(TokenKind.OPEN_BRACE)
        return self._block_statement()

    def _comparison(self) -> Comparison:
        left = self._expression()
        operator = ComparisonOperator.from_token(self.current_token)
        if operator is None:
            raise TaipanSyntaxError(
                self.current_token.location,
                f"Expected comparison operator, got {self.current_token.kind}",
            )
        self._next_token()
        right = self._expression()

        comparison = Comparison(
            left=left,
            right=right,
            operator=operator,
            location=left.location,
        )
        while operator := ComparisonOperator.from_token(self.current_token):
            self._next_token()
            comparison = Comparison(
                left=comparison,
                right=self._expression(),
                operator=operator,
                location=left.location,
            )

        return comparison

    def _expression(self) -> Expression:
        node = self._term()
        while operator := ArithmeticOperator.expression_from_token(self.current_token):
            self._next_token()
            node = BinaryExpression(
                left=node,
                right=self._term(),
                operator=operator,
                location=node.location,
            )

        return node

    def _term(
        self,
    ) -> Number | Identifier | UnaryExpression | BinaryExpression | ParentheseExpression:
        node = self._parentheses()
        while operator := ArithmeticOperator.term_from_token(self.current_token):
            self._next_token()
            node = BinaryExpression(
                left=node,
                right=self._parentheses(),
                operator=operator,
                location=node.location,
            )

        return node

    def _parentheses(self) -> Number | Identifier | UnaryExpression | ParentheseExpression:
        if self.current_token.kind != TokenKind.OPEN_PARENTHESE:
            return self._unary()

        location = self.current_token.location
        self._next_token()

        node = ParentheseExpression(
            location=location,
            value=self._expression(),
        )
        self._match_token(TokenKind.CLOSE_PARENTHESE)

        return node

    def _unary(self) -> Number | Identifier | UnaryExpression:
        operator = UnaryOperator.from_token(self.current_token)
        if operator is None:
            return self._literal()

        location = self.current_token.location

        self._next_token()
        return UnaryExpression(
            operator=operator,
            value=self._literal(),
            location=location,
        )

    def _number(self) -> Number:
        assert isinstance(self.current_token.value, float)
        node = Number(
            value=self.current_token.value,
            location=self.current_token.location,
        )

        self._next_token()
        return node

    def _identifier(self) -> Identifier:
        assert isinstance(self.current_token.value, str)
        node = Identifier(
            name=self.current_token.value,
            location=self.current_token.location,
        )

        self._next_token()
        return node

    def _literal(self) -> Number | Identifier:
        match self.current_token.kind:
            case TokenKind.NUMBER:
                return self._number()
            case TokenKind.IDENTIFIER:
                return self._identifier()
            case _:
                raise TaipanSyntaxError(
                    self.current_token.location,
                    f"Expected literal, got {self.current_token.kind}",
                )

    def _block_statement(self) -> Block:
        block = Block(location=self.current_token.location)
        self.symbol_tables.append(block.symbol_table)

        self._next_token()
        self._skip_nl()

        while self.current_token.kind != TokenKind.CLOSE_BRACE:
            block.statements.append(self._statement())
            self._nl()
        self._next_token()

        self.symbol_tables.pop()
        return block

    def _if_statement(self) -> If:
        location = self.current_token.location

        self._next_token()
        return If(
            condition=self._comparison(),
            block=self._block(),
            location=location,
        )

    def _while_statement(self) -> While:
        location = self.current_token.location

        self._next_token()
        return While(
            condition=self._comparison(),
            block=self._block(),
            location=location,
        )

    def _input_statement(self) -> Input:
        location = self.current_token.location

        self._next_token()
        return Input(
            identifier=self._identifier(),
            location=location,
        )

    def _print_statement(self) -> Print:
        location = self.current_token.location

        self._next_token()
        match self.current_token.kind:
            case TokenKind.STRING:
                assert isinstance(self.current_token.value, str)
                value = String(
                    value=self.current_token.value,
                    location=self.current_token.location,
                )
                self._next_token()
            case _:
                value = self._expression()

        return Print(value=value, location=location)

    def _declaration_statement(self) -> Declaration:
        location = self.current_token.location

        self._next_token()
        if self.current_token.kind != TokenKind.IDENTIFIER:
            raise TaipanSyntaxError(
                self.current_token.location,
                f"Expected identifier, got {self.current_token.kind}",
            )
        identifier = self._identifier()
        self.symbol_tables[-1].define(identifier.name, location)

        if self.current_token.kind == TokenKind.ASSIGNMENT:
            self._next_token()
            expression = self._expression()
        else:
            expression = None

        return Declaration(identifier=identifier, expression=expression, location=location)

    def _assignment_statement(self) -> Assignment:
        identifier = self._identifier()
        self._match_token(TokenKind.ASSIGNMENT)
        return Assignment(
            identifier=identifier,
            expression=self._expression(),
            location=identifier.location,
        )

    def _statement(self) -> Statement:
        match self.current_token.kind:
            case TokenKind.OPEN_BRACE:
                return self._block_statement()
            case TokenKind.IF:
                return self._if_statement()
            case TokenKind.WHILE:
                return self._while_statement()
            case TokenKind.INPUT:
                return self._input_statement()
            case TokenKind.PRINT:
                return self._print_statement()
            case TokenKind.DECLARATION:
                return self._declaration_statement()
            case TokenKind.IDENTIFIER:
                return self._assignment_statement()
            case _:
                raise TaipanSyntaxError(
                    self.current_token.location,
                    f"Expected statement, got {self.current_token.kind}",
                )

    def _skip_nl(self) -> None:
        while self.current_token.kind == TokenKind.NEWLINE:
            self._next_token()

    def _nl(self) -> None:
        self._match_token(TokenKind.NEWLINE)
        self._skip_nl()
