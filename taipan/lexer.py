from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from .exceptions import FileError, SyntaxError


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


@dataclass(kw_only=True)
class Token:
    kind: TokenKind
    value: str | float | None = None


class Lexer:
    def __init__(self, input: Path) -> None:
        if input.suffix != ".tp":
            raise FileError(input, "File must have a .tp extension")

        try:
            with input.open() as file:
                self.source = file.read()
        except OSError as error:
            raise FileError(input, error.strerror)

        self.source += "\n"
        self.index = -1
        self.char = ""
        self.read_char()

    def read_char(self) -> None:
        self.index += 1
        self.char = self.source[self.index] if self.index < len(self.source) else "\0"

    def peek_char(self) -> str:
        return self.source[self.index + 1] if self.index < len(self.source) else "\0"

    def skip_whitespaces(self) -> None:
        while self.char == " " or self.char == "\t":
            self.read_char()

    def skip_comments(self) -> None:
        if self.char == "#":
            while self.char != "\n":
                self.read_char()

    def get_two_char_token(self, next: str, if_next: TokenKind, otherwise: TokenKind) -> Token:
        if self.peek_char() == next:
            self.read_char()
            return Token(kind=if_next)
        return Token(kind=otherwise)

    def get_string_token(self) -> Token:
        self.read_char()
        start = self.index
        while self.char != '"':
            if self.char == "\n":
                raise SyntaxError("Missing closing quote")
            self.read_char()
        return Token(kind=TokenKind.STRING, value=self.source[start : self.index])

    def get_number_token(self) -> Token:
        start = self.index
        while self.peek_char().isdigit():
            self.read_char()
        if self.peek_char() == ".":
            self.read_char()
            while self.peek_char().isdigit():
                self.read_char()

        raw_value = self.source[start : self.index + 1]
        try:
            value = float(raw_value)
        except ValueError:
            raise SyntaxError(f"Invalid number: {raw_value!r}")

        return Token(kind=TokenKind.NUMBER, value=value)

    def read_identifier(self) -> str:
        start = self.index
        while self.peek_char().isalnum() or self.peek_char() == "_":
            self.read_char()
        return self.source[start : self.index + 1]

    def next_token(self) -> Token:
        self.skip_whitespaces()
        self.skip_comments()

        match self.char:
            case "\0":
                token = Token(kind=TokenKind.EOF)
            case "\n":
                token = Token(kind=TokenKind.NEWLINE)
            case "+":
                token = Token(kind=TokenKind.PLUS)
            case "-":
                token = Token(kind=TokenKind.MINUS)
            case "*":
                token = Token(kind=TokenKind.MULTIPLICATION)
            case "/":
                token = Token(kind=TokenKind.DIVISION)
            case "%":
                token = Token(kind=TokenKind.MODULO)
            case "{":
                token = Token(kind=TokenKind.OPEN_BRACE)
            case "}":
                token = Token(kind=TokenKind.CLOSE_BRACE)
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
            case char if char.isdigit():
                token = self.get_number_token()
            case char if char.isalpha() or char == "_":
                identifier = self.read_identifier()
                match identifier:
                    case "if":
                        token = Token(kind=TokenKind.IF)
                    case "while":
                        token = Token(kind=TokenKind.WHILE)
                    case "input":
                        token = Token(kind=TokenKind.INPUT)
                    case "print":
                        token = Token(kind=TokenKind.PRINT)
                    case _:
                        token = Token(kind=TokenKind.IDENTIFIER, value=identifier)
            case other:
                raise SyntaxError(f"Got unexpected token: {other!r}")

        self.read_char()
        return token
