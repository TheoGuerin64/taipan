from pathlib import Path

import pytest

from taipan.exceptions import TaipanFileError, TaipanSyntaxError
from taipan.lexer import Lexer, Token, TokenKind
from taipan.utils import Location, Position

DEFAULT_FILE = Path("file.tp")


class TestLexer:
    def assert_end_of_file(self, lexer: Lexer, line: int, column: int) -> None:
        assert lexer.next_token() == Token(
            kind=TokenKind.NEWLINE,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(line=line, column=column),
                end=Position(line=line, column=column + 1),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.EOF,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(line=line + 1, column=1),
                end=Position(line=line + 1, column=1),
            ),
        )

    def test_missing_permissions(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.touch()
        file.chmod(0o000)

        with pytest.raises(TaipanFileError):
            Lexer(file)

    def test_missing_file(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"

        with pytest.raises(TaipanFileError):
            Lexer(file)

    def test_folder(self, tmp_path: Path) -> None:
        with pytest.raises(TaipanFileError):
            Lexer(tmp_path)

    def test_empty(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "")
        self.assert_end_of_file(lexer, 1, 1)

    def test_whitespaces(self) -> None:
        lexer = Lexer(DEFAULT_FILE, " \t")
        self.assert_end_of_file(lexer, 1, 3)

    def test_comments(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "# comment")
        self.assert_end_of_file(lexer, 1, 10)

    def test_non_closed_string(self) -> None:
        lexer = Lexer(DEFAULT_FILE, '"string')

        with pytest.raises(TaipanSyntaxError):
            lexer.next_token()

    def test_valid_string(self) -> None:
        lexer = Lexer(DEFAULT_FILE, '"string"')

        assert lexer.next_token() == Token(
            kind=TokenKind.STRING,
            value="string",
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 9),
            ),
        )
        self.assert_end_of_file(lexer, 1, 9)

    def test_dot(self) -> None:
        lexer = Lexer(DEFAULT_FILE, ".")

        with pytest.raises(TaipanSyntaxError):
            lexer.next_token()

    def test_left_dot(self) -> None:
        lexer = Lexer(DEFAULT_FILE, ".0")

        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=0,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
        )
        self.assert_end_of_file(lexer, 1, 3)

    def test_right_dot(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "0.")

        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=0,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
        )
        self.assert_end_of_file(lexer, 1, 3)

    def test_consecutive_numbers(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "1.2.3")

        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=1.2,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 4),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=0.3,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 4),
                end=Position(1, 6),
            ),
        )
        self.assert_end_of_file(lexer, 1, 6)

    def test_negative_number(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "-1")

        assert lexer.next_token() == Token(
            kind=TokenKind.MINUS,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=1,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 2),
                end=Position(1, 3),
            ),
        )
        self.assert_end_of_file(lexer, 1, 3)

    def test_valid_number(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "123.456")

        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=123.456,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 8),
            ),
        )
        self.assert_end_of_file(lexer, 1, 8)

    def test_start_with_number_identifier(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "0identifier")

        assert lexer.next_token() == Token(
            kind=TokenKind.NUMBER,
            value=0,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.IDENTIFIER,
            value="identifier",
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 2),
                end=Position(1, 12),
            ),
        )
        self.assert_end_of_file(lexer, 1, 12)

    def test_valid_identifier(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "_identifier64")

        assert lexer.next_token() == Token(
            kind=TokenKind.IDENTIFIER,
            value="_identifier64",
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 14),
            ),
        )
        self.assert_end_of_file(lexer, 1, 14)

    def test_invalid_token(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "@")

        with pytest.raises(TaipanSyntaxError):
            lexer.next_token()

    def test_two_char_token(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "= !=")

        assert lexer.next_token() == Token(
            kind=TokenKind.ASSIGNMENT,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.NOT_EQUAL,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 3),
                end=Position(1, 5),
            ),
        )
        self.assert_end_of_file(lexer, 1, 5)

    def test_multiline(self) -> None:
        lexer = Lexer(DEFAULT_FILE, "\n  a\ne")

        assert lexer.next_token() == Token(
            kind=TokenKind.NEWLINE,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.IDENTIFIER,
            value="a",
            location=Location(
                file=DEFAULT_FILE,
                start=Position(2, 3),
                end=Position(2, 4),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.NEWLINE,
            location=Location(
                file=DEFAULT_FILE,
                start=Position(2, 4),
                end=Position(2, 5),
            ),
        )
        assert lexer.next_token() == Token(
            kind=TokenKind.IDENTIFIER,
            value="e",
            location=Location(
                file=DEFAULT_FILE,
                start=Position(3, 1),
                end=Position(3, 2),
            ),
        )
        self.assert_end_of_file(lexer, 3, 2)
