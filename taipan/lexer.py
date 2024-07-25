from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from .exceptions import TaipanFileError, TaipanSyntaxError


class TokenKind(Enum):
    EOF = auto()
    NEWLINE = auto()
    IDENTIFIER = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    NUMBER = auto()
    STRING = auto()
    IF = auto()
    WHILE = auto()
    INPUT = auto()
    PRINT = auto()
    DECLARATION = auto()
    ASSIGNMENT = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLICATION = auto()
    DIVISION = auto()
    MODULO = auto()
    NOT = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()


@dataclass
class Token:
    kind: TokenKind
    line: int
    column: int
    value: str | float | None = None


class Lexer:
    def __init__(self, input: Path) -> None:
        if input.suffix != ".tp":
            raise TaipanFileError(input, "File must have a .tp extension")

        try:
            with input.open() as file:
                raw_source = file.read()
        except OSError as error:
            raise TaipanFileError(input, error.strerror)

        self.input = input
        self.source = raw_source + "\n"
        self.index = -1
        self.line = 1
        self.column = 0
        self.char = ""
        self.read_char()

    def read_char(self) -> None:
        if self.char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.index += 1
        try:
            self.char = self.source[self.index]
        except IndexError:
            self.char = "\0"

    def peek_char(self) -> str:
        try:
            return self.source[self.index + 1]
        except IndexError:
            return "\0"

    def skip_whitespaces(self) -> None:
        while self.char == " " or self.char == "\t":
            self.read_char()

    def skip_comments(self) -> None:
        if self.char == "#":
            while self.char != "\n":
                self.read_char()

    def get_one_char_token(self, kind: TokenKind) -> Token:
        return Token(kind, self.line, self.column)

    def get_two_char_token(self, next: str, if_next: TokenKind, otherwise: TokenKind) -> Token:
        column = self.column
        if self.peek_char() == next:
            self.read_char()
            return Token(if_next, self.line, column)
        return Token(otherwise, self.line, column)

    def get_string_token(self) -> Token:
        column = self.column
        self.read_char()

        start = self.index
        while self.char != '"':
            if self.char == "\n":
                raise TaipanSyntaxError(self.input, self.line, column, "Missing closing quote")
            self.read_char()

        return Token(TokenKind.STRING, self.line, column, self.source[start : self.index])

    def get_number_token(self) -> Token:
        column = self.column

        start = self.index
        while self.peek_char().isdigit():
            self.read_char()
        if self.peek_char() == ".":
            self.read_char()
            while self.peek_char().isdigit():
                self.read_char()

        value = self.source[start : self.index + 1]
        if value == ".":
            raise TaipanSyntaxError(self.input, self.line, column, "Invalid number")

        return Token(TokenKind.NUMBER, self.line, column, float(value))

    def read_identifier(self) -> str:
        start = self.index
        while self.peek_char().isalnum() or self.peek_char() == "_":
            self.read_char()
        return self.source[start : self.index + 1]

    def get_identifier_token(self) -> Token:
        column = self.column
        identifier = self.read_identifier()
        match identifier:
            case "if":
                return Token(TokenKind.IF, self.line, column)
            case "while":
                return Token(TokenKind.WHILE, self.line, column)
            case "input":
                return Token(TokenKind.INPUT, self.line, column)
            case "print":
                return Token(TokenKind.PRINT, self.line, column)
            case "let":
                return Token(TokenKind.DECLARATION, self.line, column)
            case _:
                return Token(TokenKind.IDENTIFIER, self.line, column, identifier)

    def next_token(self) -> Token:
        self.skip_whitespaces()
        self.skip_comments()

        match self.char:
            case "\0":
                token = self.get_one_char_token(TokenKind.EOF)
            case "\n":
                token = self.get_one_char_token(TokenKind.NEWLINE)
            case "+":
                token = self.get_one_char_token(TokenKind.PLUS)
            case "-":
                token = self.get_one_char_token(TokenKind.MINUS)
            case "*":
                token = self.get_one_char_token(TokenKind.MULTIPLICATION)
            case "/":
                token = self.get_one_char_token(TokenKind.DIVISION)
            case "%":
                token = self.get_one_char_token(TokenKind.MODULO)
            case "{":
                token = self.get_one_char_token(TokenKind.OPEN_BRACE)
            case "}":
                token = self.get_one_char_token(TokenKind.CLOSE_BRACE)
            case "=":
                token = self.get_two_char_token("=", TokenKind.EQUAL, TokenKind.ASSIGNMENT)
            case "!":
                token = self.get_two_char_token("=", TokenKind.NOT_EQUAL, TokenKind.NOT)
            case "<":
                token = self.get_two_char_token("=", TokenKind.LESS_EQUAL, TokenKind.LESS)
            case ">":
                token = self.get_two_char_token("=", TokenKind.GREATER_EQUAL, TokenKind.GREATER)
            case '"':
                token = self.get_string_token()
            case char if char.isdigit() or char == ".":
                token = self.get_number_token()
            case char if char.isalpha() or char == "_":
                token = self.get_identifier_token()
            case other:
                raise TaipanSyntaxError(
                    self.input, self.line, self.column, f"Got unexpected token: {other!r}"
                )

        self.read_char()
        return token
