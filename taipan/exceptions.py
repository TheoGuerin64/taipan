from __future__ import annotations

from pathlib import Path
from typing import IO, Any

import click
from click._compat import get_text_stderr


class TaipanError(click.ClickException):
    ERROR_TYPE = "Error"

    def __init__(self, message: str) -> None:
        super().__init__(message)

    def show(self, file: IO[Any] | None = None) -> None:
        if file is None:
            file = get_text_stderr()

        click.echo(f"{self.ERROR_TYPE}: {self.format_message()}", file=file)


class TaipanFileError(TaipanError):
    ERROR_TYPE = "FileError"

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path


class TaipanLocationError(TaipanError):
    ERROR_TYPE = "LocationError"

    def __init__(self, file: Path, line: int, column: int, message: str) -> None:
        super().__init__(f"{file}:{line}:{column}: {message}")
        self.line = line
        self.column = column


class TaipanSyntaxError(TaipanLocationError):
    ERROR_TYPE = "SyntaxError"


class TaipanSemanticError(TaipanLocationError):
    ERROR_TYPE = "SemanticError"


class TaipanCompilationError(TaipanError):
    def __init__(self, message: str) -> None:
        super().__init__(f"CompilationError: {message}")
