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
from taipan.utils import Location, Position

INVALID_TOKEN = Token(TokenKind.EOF, Location(Path(""), Position(-1, -1), Position(-1, -1)))


class Parser:
    def __init__(self, input: Path, raw_source: str | None = None) -> None:
        self.lexer = Lexer(input, raw_source)
        self.symbol_tables = deque[SymbolTable]()

        self.current_token = INVALID_TOKEN
        self.peek_token = INVALID_TOKEN
        self._next_token()
        self._next_token()

    @classmethod
    def parse(cls, input: Path, raw_source: str | None = None) -> AST:
        parser = cls(input, raw_source)
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
        block = self._block()
        return Program(
            block=block,
            location=block.location,
        )

    def _block(self) -> Block:
        self._skip_nl()
        self._expect_token(TokenKind.OPEN_BRACE)
        return self._block_statement()

    def _expression(self) -> Expression:
        left = self._additive()
        while operator := ComparisonOperator.from_token(self.current_token):
            self._next_token()

            right = self._additive()
            location = Location(
                file=left.location.file,
                start=left.location.start,
                end=right.location.end,
            )

            left = Comparison(
                left=left,
                right=right,
                operator=operator,
                location=location,
            )

        return left

    def _additive(
        self,
    ) -> Number | Identifier | ParentheseExpression | UnaryExpression | BinaryExpression:
        left = self._multiplicative()
        while operator := ArithmeticOperator.additive_from_token(self.current_token):
            self._next_token()

            right = self._multiplicative()
            location = Location(
                file=left.location.file,
                start=left.location.start,
                end=right.location.end,
            )

            left = BinaryExpression(
                left=left,
                right=right,
                operator=operator,
                location=location,
            )

        return left

    def _multiplicative(
        self,
    ) -> Number | Identifier | ParentheseExpression | UnaryExpression | BinaryExpression:
        left = self._unary()
        while operator := ArithmeticOperator.multiplicative_from_token(self.current_token):
            self._next_token()

            right = self._unary()
            location = Location(
                file=left.location.file,
                start=left.location.start,
                end=right.location.end,
            )

            left = BinaryExpression(
                left=left,
                right=right,
                operator=operator,
                location=location,
            )

        return left

    def _unary(self) -> Number | Identifier | ParentheseExpression | UnaryExpression:
        operator = UnaryOperator.from_token(self.current_token)
        if operator is None:
            return self._parentheses()

        start_position = self.current_token.location.start
        self._next_token()

        value = self._parentheses()
        location = Location(
            self.current_token.location.file,
            start_position,
            value.location.end,
        )

        return UnaryExpression(
            operator=operator,
            value=value,
            location=location,
        )

    def _parentheses(self) -> Number | Identifier | ParentheseExpression:
        if self.current_token.kind != TokenKind.OPEN_PARENTHESE:
            return self._literal()

        start_position = self.current_token.location.start
        self._next_token()

        value = self._expression()
        location = Location(
            self.current_token.location.file,
            start_position,
            self.current_token.location.end,
        )

        self._match_token(TokenKind.CLOSE_PARENTHESE)
        return ParentheseExpression(
            location=location,
            value=value,
        )

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

    def _block_statement(self) -> Block:
        start_position = self.current_token.location.start
        self._next_token()
        self._skip_nl()

        symbol_table = SymbolTable()
        self.symbol_tables.append(symbol_table)

        statements = []
        while self.current_token.kind != TokenKind.CLOSE_BRACE:
            statements.append(self._statement())
            self._nl()

        location = Location(
            file=self.current_token.location.file,
            start=start_position,
            end=self.current_token.location.end,
        )
        self._next_token()

        self.symbol_tables.pop()

        return Block(
            statements=statements,
            symbol_table=symbol_table,
            location=location,
        )

    def _if_statement(self) -> If:
        start_position = self.current_token.location.start
        self._next_token()

        expression = self._expression()
        block = self._block()
        return If(
            condition=expression,
            block=block,
            location=Location(
                file=self.current_token.location.file,
                start=start_position,
                end=block.location.end,
            ),
        )

    def _while_statement(self) -> While:
        start_position = self.current_token.location.start
        self._next_token()

        expression = self._expression()
        block = self._block()
        return While(
            condition=expression,
            block=block,
            location=Location(
                file=self.current_token.location.file,
                start=start_position,
                end=block.location.end,
            ),
        )

    def _input_statement(self) -> Input:
        start_position = self.current_token.location.start
        self._next_token()

        identifier = self._identifier()
        return Input(
            identifier=identifier,
            location=Location(
                file=self.current_token.location.file,
                start=start_position,
                end=identifier.location.end,
            ),
        )

    def _print_statement(self) -> Print:
        start_position = self.current_token.location.start
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

        return Print(
            value=value,
            location=Location(
                file=self.current_token.location.file,
                start=start_position,
                end=value.location.end,
            ),
        )

    def _declaration_statement(self) -> Declaration:
        start_position = self.current_token.location.start

        self._next_token()
        if self.current_token.kind != TokenKind.IDENTIFIER:
            raise TaipanSyntaxError(
                self.current_token.location,
                f"Expected identifier, got {self.current_token.kind}",
            )

        identifier = self._identifier()
        self.symbol_tables[-1].define(identifier.name, identifier.location)

        if self.current_token.kind == TokenKind.ASSIGNMENT:
            self._next_token()
            expression = self._expression()
            end_position = expression.location.end
        else:
            expression = None
            end_position = identifier.location.end

        return Declaration(
            identifier=identifier,
            expression=expression,
            location=Location(
                file=self.current_token.location.file,
                start=start_position,
                end=end_position,
            ),
        )

    def _assignment_statement(self) -> Assignment:
        identifier = self._identifier()
        self._match_token(TokenKind.ASSIGNMENT)
        expression = self._expression()

        return Assignment(
            identifier=identifier,
            expression=expression,
            location=Location(
                file=self.current_token.location.file,
                start=identifier.location.start,
                end=expression.location.end,
            ),
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
