from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from taipan.exceptions import TaipanFileError, TaipanSyntaxError
from taipan.location import Location, Position


class TokenKind(Enum):
    EOF = auto()
    NEWLINE = auto()

    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_PARENTHESE = auto()
    CLOSE_PARENTHESE = auto()

    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DECLARATION = auto()
    ASSIGNMENT = auto()

    INPUT = auto()
    PRINT = auto()

    PLUS = auto()
    MINUS = auto()
    MULTIPLICATION = auto()
    DIVISION = auto()

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


ONE_CHAR_TOKEN_KIND = {
    "\n": TokenKind.NEWLINE,
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.MULTIPLICATION,
    "/": TokenKind.DIVISION,
    "{": TokenKind.OPEN_BRACE,
    "}": TokenKind.CLOSE_BRACE,
    "(": TokenKind.OPEN_PARENTHESE,
    ")": TokenKind.CLOSE_PARENTHESE,
}

TWO_CHAR_TOKEN_KIND = {
    "=": ("=", TokenKind.EQUAL, TokenKind.ASSIGNMENT),
    "!": ("=", TokenKind.NOT_EQUAL, None),
    "<": ("=", TokenKind.LESS_EQUAL, TokenKind.LESS),
    ">": ("=", TokenKind.GREATER_EQUAL, TokenKind.GREATER),
}

KEYWORD_TOKEN_KIND = {
    "if": TokenKind.IF,
    "else": TokenKind.ELSE,
    "while": TokenKind.WHILE,
    "input": TokenKind.INPUT,
    "print": TokenKind.PRINT,
    "let": TokenKind.DECLARATION,
}


class Lexer:
    def __init__(self, input_: Path, raw_source: str | None = None) -> None:
        if raw_source is None:
            try:
                raw_source = input_.read_text()
            except OSError as error:
                raise TaipanFileError(input_, error.strerror)

        self.source = raw_source + "\n"

        self.file = input_
        self.line = 1
        self.column = 0

        self.index = -1
        self.char = ""
        self._read_char()

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

    def _get_location(self, size: int) -> Location:
        return Location(
            self.file,
            Position(self.line, self.column),
            Position(self.line, self.column + size),
        )

    def _get_two_char_token(
        self, next: str, if_next: TokenKind, otherwise: TokenKind | None
    ) -> Token:
        start_position = Position(self.line, self.column)

        peek = self._peek_char()
        if peek != next:
            location = Location(
                self.file,
                start_position,
                Position(self.line, self.column + 1),
            )

            if not otherwise:
                raise TaipanSyntaxError(location, f"Got unexpected token: {peek!r}")
            return Token(otherwise, location)

        self._read_char()
        location = Location(
            self.file,
            start_position,
            Position(self.line, self.column + 1),
        )
        return Token(if_next, location)

    def _get_string_token(self) -> Token:
        start_position = Position(self.line, self.column)
        self._read_char()

        start = self.index
        while self.char != '"':
            if self.char == "\n":
                location = Location(
                    self.file,
                    start_position,
                    Position(self.line, self.column),
                )
                raise TaipanSyntaxError(location, "Missing closing quote")
            self._read_char()

        location = location = Location(
            self.file,
            start_position,
            Position(self.line, self.column + 1),
        )
        return Token(TokenKind.STRING, location, self.source[start : self.index])

    def _get_number_token(self) -> Token:
        start_position = Position(self.line, self.column)

        start = self.index
        while self._peek_char().isdigit():
            self._read_char()
        if self._peek_char() == ".":
            self._read_char()
            while self._peek_char().isdigit():
                self._read_char()

        value = self.source[start : self.index + 1]
        location = Location(
            self.file,
            start_position,
            Position(self.line, self.column + 1),
        )
        if value == ".":
            raise TaipanSyntaxError(location, "Invalid number")

        return Token(TokenKind.NUMBER, location, float(value))

    def _read_identifier(self) -> str:
        start = self.index
        while self._peek_char().isalnum() or self._peek_char() == "_":
            self._read_char()
        return self.source[start : self.index + 1]

    def _get_identifier_token(self) -> Token:
        start_position = Position(self.line, self.column)
        identifier = self._read_identifier()
        location = Location(
            self.file,
            start_position,
            Position(self.line, self.column + 1),
        )

        if keyword_kind := KEYWORD_TOKEN_KIND.get(identifier):
            return Token(keyword_kind, location)

        if len(identifier) > 32:
            raise TaipanSyntaxError(location, "Identifier is too long")
        return Token(TokenKind.IDENTIFIER, location, identifier)

    def next_token(self) -> Token:
        self._skip_whitespaces()
        self._skip_comments()

        match self.char:
            case "\0":
                location = self._get_location(0)
                token = Token(TokenKind.EOF, location)
            case char if token_kind := ONE_CHAR_TOKEN_KIND.get(char):
                location = self._get_location(1)
                token = Token(token_kind, location)
            case char if token_info := TWO_CHAR_TOKEN_KIND.get(char):
                token = self._get_two_char_token(*token_info)
            case '"':
                token = self._get_string_token()
            case char if char.isdigit() or char == ".":
                token = self._get_number_token()
            case char if char.isalpha() or char == "_":
                token = self._get_identifier_token()
            case other:
                location = self._get_location(1)
                raise TaipanSyntaxError(location, f"Got unexpected token: {other!r}")

        self._read_char()
        return token
