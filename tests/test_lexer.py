from pathlib import Path

import pytest

from taipan.exceptions import TaipanFileError, TaipanSyntaxError
from taipan.lexer import Lexer, Token, TokenKind


class Tests:
    def test_invalid_extension(self, tmp_path: Path) -> None:
        file = tmp_path / "file.txt"
        file.touch()

        with pytest.raises(TaipanFileError) as e_info:
            Lexer(file)
            assert e_info.value.path == file

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

    def test_valid_file(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.touch()

        Lexer(file)

    def test_empty(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.touch()

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_whitespaces(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text(" \t")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=3)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_comments(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("# comment")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=10)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_non_closed_string(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text('"string')

        lexer = Lexer(file)
        with pytest.raises(TaipanSyntaxError):
            lexer.next_token()

    def test_valid_string(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text('"string"')

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.STRING, value="string", line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=9)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_dot(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text(".")

        lexer = Lexer(file)
        with pytest.raises(TaipanSyntaxError):
            lexer.next_token()

    def test_left_dot(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text(".0")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NUMBER, value=0, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=3)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_right_dot(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("0.")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NUMBER, value=0, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=3)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_consecutive_numbers(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1.2.3")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NUMBER, value=1.2, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NUMBER, value=0.3, line=1, column=4)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=6)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_valid_number(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("123.456")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NUMBER, value=123.456, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=8)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_start_with_number_identifier(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("0identifier")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NUMBER, value=0, line=1, column=1)
        assert lexer.next_token() == Token(
            kind=TokenKind.IDENTIFIER, value="identifier", line=1, column=2
        )
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=12)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_valid_identifier(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("_identifier64")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(
            kind=TokenKind.IDENTIFIER, value="_identifier64", line=1, column=1
        )
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=14)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_invalid_token(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("@")

        lexer = Lexer(file)
        with pytest.raises(TaipanSyntaxError):
            lexer.next_token()

    def test_two_char_token(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("== !=")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.EQUAL, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NOT_EQUAL, line=1, column=4)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=6)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=2, column=1)

    def test_multiline(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("\n  a\ne")

        lexer = Lexer(file)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=1, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.IDENTIFIER, value="a", line=2, column=3)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=2, column=4)
        assert lexer.next_token() == Token(kind=TokenKind.IDENTIFIER, value="e", line=3, column=1)
        assert lexer.next_token() == Token(kind=TokenKind.NEWLINE, line=3, column=2)
        assert lexer.next_token() == Token(kind=TokenKind.EOF, line=4, column=1)
