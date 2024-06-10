from pathlib import Path

from taipan.exceptions import TaipanSyntaxError

from .ast import (
    AST,
    ArithmeticOperator,
    Assignment,
    BinaryExpression,
    Block,
    Comparaison,
    ComparaisonOperator,
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
from .lexer import Lexer, Token, TokenKind


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = Token(kind=TokenKind.EOF)
        self.peek_token = Token(kind=TokenKind.EOF)
        self.next_token()
        self.next_token()

    def match_token(self, token_kind: TokenKind) -> None:
        if self.current_token.kind != token_kind:
            raise TaipanSyntaxError(f"Expected {token_kind}, got {self.current_token.kind}")
        self.next_token()

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def program(self) -> Program:
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()

        return Program(block=self.block())

    def comparaison(self) -> Comparaison:
        left = self.expression()

        operator = ComparaisonOperator.from_token(self.current_token)
        if operator is None:
            raise TaipanSyntaxError(f"Expected comparaison operator, got {self.current_token.kind}")
        self.next_token()

        right = self.expression()

        node = Comparaison(left=left, right=right, operator=operator)
        while operator := ComparaisonOperator.from_token(self.current_token):
            right = self.expression()
            node = Comparaison(left=node, right=right, operator=operator)
            self.next_token()
        return node

    def expression(self) -> BinaryExpression | UnaryExpression | Identifier | Number:
        node = self.term()
        while operator := ArithmeticOperator.expression_from_token(self.current_token):
            self.next_token()
            node = BinaryExpression(left=node, right=self.term(), operator=operator)
        return node

    def term(self) -> BinaryExpression | UnaryExpression | Identifier | Number:
        node = self.unary()
        while operator := ArithmeticOperator.term_from_token(self.current_token):
            self.next_token()
            node = BinaryExpression(left=node, right=self.unary(), operator=operator)
        return node

    def unary(self) -> UnaryExpression | Identifier | Number:
        operator = UnaryOperator.from_token(self.current_token)
        if operator is None:
            return self.literal()

        self.next_token()
        return UnaryExpression(operator=operator, value=self.literal())

    def number(self) -> Number:
        assert isinstance(self.current_token.value, float)
        node = Number(value=self.current_token.value)
        self.next_token()
        return node

    def identifier(self) -> Identifier:
        assert isinstance(self.current_token.value, str)
        node = Identifier(name=self.current_token.value)
        self.next_token()
        return node

    def literal(self) -> Identifier | Number:
        match self.current_token.kind:
            case TokenKind.NUMBER:
                return self.number()
            case TokenKind.IDENTIFIER:
                return self.identifier()
            case _:
                raise TaipanSyntaxError(f"Expected literal, got {self.current_token.kind}")

    def block(self) -> Block:
        block = Block()

        self.match_token(TokenKind.OPEN_BRACE)
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()

        while self.current_token.kind != TokenKind.CLOSE_BRACE:
            block.add_statement(self.statement())
            self.nl()
        self.next_token()

        return block

    def if_statement(self) -> If:
        self.next_token()
        return If(condition=self.comparaison(), block=self.block())

    def while_statement(self) -> While:
        self.next_token()
        return While(condition=self.comparaison(), block=self.block())

    def input_statement(self) -> Input:
        self.next_token()
        node = Input(identifier=self.identifier())
        return node

    def print_statement(self) -> Print:
        self.next_token()
        match self.current_token.kind:
            case TokenKind.STRING:
                assert isinstance(self.current_token.value, str)
                value = String(value=self.current_token.value)
                self.next_token()
            case _:
                value = self.expression()
        return Print(value=value)

    def assignment_statement(self) -> Assignment:
        identifier = self.identifier()
        self.match_token(TokenKind.ASSIGNMENT)
        return Assignment(identifier=identifier, expression=self.expression())

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
            case TokenKind.IDENTIFIER:
                return self.assignment_statement()
            case _:
                raise TaipanSyntaxError(f"Expected statement, got {self.current_token.kind}")

    def nl(self) -> None:
        self.match_token(TokenKind.NEWLINE)
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()


def run(input: Path) -> AST:
    lexer = Lexer(input)
    parser = Parser(lexer)
    root = parser.program()
    return AST(root)
