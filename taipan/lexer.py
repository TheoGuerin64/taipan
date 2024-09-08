from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from taipan.exceptions import TaipanFileError, TaipanSyntaxError
from taipan.utils import Location


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
    location: Location
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
        self.source = raw_source + "\n"

        self.file = input
        self.line = 1
        self.column = 0

        self.index = -1
        self.char = ""
        self._read_char()

    @property
    def location(self) -> Location:
        return Location(self.file, self.line, self.column)

    def _read_char(self) -> None:
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

    def _peek_char(self) -> str:
        try:
            return self.source[self.index + 1]
        except IndexError:
            return "\0"

    def _skip_whitespaces(self) -> None:
        while self.char == " " or self.char == "\t":
            self._read_char()

    def _skip_comments(self) -> None:
        if self.char == "#":
            while self.char != "\n":
                self._read_char()

    def _get_one_char_token(self, kind: TokenKind) -> Token:
        return Token(kind, self.location)

    def _get_two_char_token(self, next: str, if_next: TokenKind, otherwise: TokenKind) -> Token:
        location = self.location
        if self._peek_char() == next:
            self._read_char()
            return Token(if_next, location)
        return Token(otherwise, location)

    def _get_string_token(self) -> Token:
        location = self.location
        self._read_char()

        start = self.index
        while self.char != '"':
            if self.char == "\n":
                raise TaipanSyntaxError(location, "Missing closing quote")
            self._read_char()

        return Token(TokenKind.STRING, location, self.source[start : self.index])

    def _get_number_token(self) -> Token:
        location = self.location

        start = self.index
        while self._peek_char().isdigit():
            self._read_char()
        if self._peek_char() == ".":
            self._read_char()
            while self._peek_char().isdigit():
                self._read_char()

        value = self.source[start : self.index + 1]
        if value == ".":
            raise TaipanSyntaxError(location, "Invalid number")

        return Token(TokenKind.NUMBER, location, float(value))

    def _read_identifier(self) -> str:
        start = self.index
        while self._peek_char().isalnum() or self._peek_char() == "_":
            self._read_char()
        return self.source[start : self.index + 1]

    def _get_identifier_token(self) -> Token:
        location = self.location
        identifier = self._read_identifier()
        match identifier:
            case "if":
                return Token(TokenKind.IF, location)
            case "while":
                return Token(TokenKind.WHILE, location)
            case "input":
                return Token(TokenKind.INPUT, location)
            case "print":
                return Token(TokenKind.PRINT, location)
            case "let":
                return Token(TokenKind.DECLARATION, location)
            case name:
                return Token(TokenKind.IDENTIFIER, location, name)

    def next_token(self) -> Token:
        self._skip_whitespaces()
        self._skip_comments()

        match self.char:
            case "\0":
                token = self._get_one_char_token(TokenKind.EOF)
            case "\n":
                token = self._get_one_char_token(TokenKind.NEWLINE)
            case "+":
                token = self._get_one_char_token(TokenKind.PLUS)
            case "-":
                token = self._get_one_char_token(TokenKind.MINUS)
            case "*":
                token = self._get_one_char_token(TokenKind.MULTIPLICATION)
            case "/":
                token = self._get_one_char_token(TokenKind.DIVISION)
            case "%":
                token = self._get_one_char_token(TokenKind.MODULO)
            case "{":
                token = self._get_one_char_token(TokenKind.OPEN_BRACE)
            case "}":
                token = self._get_one_char_token(TokenKind.CLOSE_BRACE)
            case "=":
                token = self._get_two_char_token("=", TokenKind.EQUAL, TokenKind.ASSIGNMENT)
            case "!":
                token = self._get_two_char_token("=", TokenKind.NOT_EQUAL, TokenKind.NOT)
            case "<":
                token = self._get_two_char_token("=", TokenKind.LESS_EQUAL, TokenKind.LESS)
            case ">":
                token = self._get_two_char_token("=", TokenKind.GREATER_EQUAL, TokenKind.GREATER)
            case '"':
                token = self._get_string_token()
            case char if char.isdigit() or char == ".":
                token = self._get_number_token()
            case char if char.isalpha() or char == "_":
                token = self._get_identifier_token()
            case other:
                raise TaipanSyntaxError(self.location, f"Got unexpected token: {other!r}")

        self._read_char()
        return token
