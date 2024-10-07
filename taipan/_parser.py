from collections import deque
from pathlib import Path
from typing import overload

from taipan._lexer import Lexer, Token, TokenKind
from taipan.ast import (
    AST,
    ArithmeticOperator,
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    ComparisonOperator,
    Declaration,
    ExpressionType,
    Identifier,
    If,
    Input,
    Number,
    ParentheseExpression,
    Print,
    Program,
    StatementType,
    String,
    UnaryExpression,
    UnaryOperator,
    While,
)
from taipan.exceptions import TaipanSyntaxError
from taipan.location import Location, Position
from taipan.symbol_table import SymbolTable

_INVALID_TOKEN = Token(TokenKind.EOF, Location(Path(""), Position(-1, -1), Position(-1, -1)))


class Parser:
    def __init__(self, input_: Path | str) -> None:
        self._lexer = Lexer(input_)
        self._symbol_tables = deque[SymbolTable]()

        self._current_token = _INVALID_TOKEN
        self._peek_token = _INVALID_TOKEN
        self._next_token()
        self._next_token()

    def parse(self) -> AST:
        return AST(self._program())

    def _expect_token(self, token_kind: TokenKind) -> None:
        if self._current_token.kind != token_kind:
            raise TaipanSyntaxError(
                self._current_token.location,
                f"Expected {token_kind}, got {self._current_token.kind}",
            )

    def _match_token(self, token_kind: TokenKind) -> None:
        self._expect_token(token_kind)
        self._next_token()

    def _next_token(self) -> None:
        self._current_token = self._peek_token
        self._peek_token = self._lexer.next_token()

    def _program(self) -> Program:
        return Program(self._block())

    def _block(self) -> Block:
        self._skip_nl()
        self._expect_token(TokenKind.OPEN_BRACE)
        return self._block_statement()

    def _expression(self) -> ExpressionType:
        left = self._additive()
        while operator := ComparisonOperator.from_token(self._current_token):
            self._next_token()

            right = self._additive()
            location = Location(
                left.location.file,
                left.location.start,
                right.location.end,
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
        while operator := ArithmeticOperator.additive_from_token(self._current_token):
            self._next_token()

            right = self._multiplicative()
            location = Location(
                left.location.file,
                left.location.start,
                right.location.end,
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
        while operator := ArithmeticOperator.multiplicative_from_token(self._current_token):
            self._next_token()

            right = self._unary()
            location = Location(
                left.location.file,
                left.location.start,
                right.location.end,
            )

            left = BinaryExpression(
                left=left,
                right=right,
                operator=operator,
                location=location,
            )

        return left

    def _unary(self) -> Number | Identifier | ParentheseExpression | UnaryExpression:
        operator = UnaryOperator.from_token(self._current_token)
        if operator is None:
            return self._parentheses()

        start_position = self._current_token.location.start
        self._next_token()

        value = self._parentheses()
        location = Location(
            self._current_token.location.file,
            start_position,
            value.location.end,
        )

        return UnaryExpression(
            operator=operator,
            value=value,
            location=location,
        )

    def _parentheses(self) -> Number | Identifier | ParentheseExpression:
        if self._current_token.kind != TokenKind.OPEN_PARENTHESE:
            return self._literal()

        start_position = self._current_token.location.start
        self._next_token()

        value = self._expression()
        location = Location(
            self._current_token.location.file,
            start_position,
            self._current_token.location.end,
        )

        self._match_token(TokenKind.CLOSE_PARENTHESE)
        return ParentheseExpression(
            value=value,
            location=location,
        )

    def _literal(self) -> Number | Identifier:
        match self._current_token.kind:
            case TokenKind.NUMBER:
                return self._number()
            case TokenKind.IDENTIFIER:
                return self._identifier()
            case _:
                raise TaipanSyntaxError(
                    self._current_token.location,
                    f"Expected literal, got {self._current_token.kind}",
                )

    def _number(self) -> Number:
        assert isinstance(self._current_token.value, float)
        node = Number(
            value=self._current_token.value,
            location=self._current_token.location,
        )

        self._next_token()
        return node

    def _identifier(self) -> Identifier:
        assert isinstance(self._current_token.value, str)
        node = Identifier(
            name=self._current_token.value,
            location=self._current_token.location,
        )

        self._next_token()
        return node

    def _block_statement(self) -> Block:
        start_position = self._current_token.location.start
        self._next_token()
        self._skip_nl()

        symbol_table = SymbolTable()
        self._symbol_tables.append(symbol_table)

        statements = list[StatementType]()
        while self._current_token.kind != TokenKind.CLOSE_BRACE:
            statements.append(self._statement())
            self._nl()

        location = Location(
            self._current_token.location.file,
            start_position,
            self._current_token.location.end,
        )
        self._next_token()

        self._symbol_tables.pop()

        return Block(
            statements=statements,
            symbol_table=symbol_table,
            location=location,
        )

    def _if_statement(self) -> If:
        start_position = self._current_token.location.start
        self._next_token()

        expression = self._expression()
        block = self._block()

        if self._current_token.kind != TokenKind.ELSE:
            return If(
                condition=expression,
                block=block,
                else_=None,
                location=Location(
                    self._current_token.location.file,
                    start_position,
                    block.location.end,
                ),
            )
        self._next_token()

        if self._current_token.kind == TokenKind.IF:
            else_ = self._if_statement()
        else:
            else_ = self._block()

        return If(
            condition=expression,
            block=block,
            else_=else_,
            location=Location(
                self._current_token.location.file,
                start_position,
                else_.location.end,
            ),
        )

    def _while_statement(self) -> While:
        start_position = self._current_token.location.start
        self._next_token()

        expression = self._expression()
        block = self._block()
        return While(
            condition=expression,
            block=block,
            location=Location(
                self._current_token.location.file,
                start_position,
                block.location.end,
            ),
        )

    def _input_statement(self) -> Input:
        start_position = self._current_token.location.start
        self._next_token()

        identifier = self._identifier()
        return Input(
            identifier=identifier,
            location=Location(
                self._current_token.location.file,
                start_position,
                identifier.location.end,
            ),
        )

    def _print_statement(self) -> Print:
        start_position = self._current_token.location.start
        self._next_token()

        match self._current_token.kind:
            case TokenKind.STRING:
                assert isinstance(self._current_token.value, str)
                value = String(
                    value=self._current_token.value,
                    location=self._current_token.location,
                )
                self._next_token()
            case _:
                value = self._expression()

        return Print(
            value=value,
            location=Location(
                self._current_token.location.file,
                start_position,
                value.location.end,
            ),
        )

    def _declaration_statement(self) -> Declaration:
        start_position = self._current_token.location.start

        self._next_token()
        if self._current_token.kind != TokenKind.IDENTIFIER:
            raise TaipanSyntaxError(
                self._current_token.location,
                f"Expected identifier, got {self._current_token.kind}",
            )

        identifier = self._identifier()
        self._symbol_tables[-1].define(identifier.name, identifier.location)

        if self._current_token.kind == TokenKind.ASSIGNMENT:
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
                self._current_token.location.file,
                start_position,
                end_position,
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
                self._current_token.location.file,
                identifier.location.start,
                expression.location.end,
            ),
        )

    def _statement(self) -> StatementType:
        match self._current_token.kind:
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
                    self._current_token.location,
                    f"Expected statement, got {self._current_token.kind}",
                )

    def _skip_nl(self) -> None:
        while self._current_token.kind == TokenKind.NEWLINE:
            self._next_token()

    def _nl(self) -> None:
        self._match_token(TokenKind.NEWLINE)
        self._skip_nl()


@overload
def parse(input_: Path) -> AST:
    """Parse from a file."""


@overload
def parse(input_: str) -> AST:
    """Parse from a string."""


def parse(input_: Path | str) -> AST:
    parser = Parser(input_)
    return parser.parse()
