from __future__ import annotations

from pathlib import Path
from typing import IO, Any, override

import click
from click._compat import get_text_stderr

from taipan.location import Location


class TaipanError(click.ClickException):
    ERROR_TYPE = "Error"

    def __init__(self, message: str) -> None:
        super().__init__(message)

    @override
    def show(self, file: IO[Any] | None = None) -> None:
        if file is None:
            file = get_text_stderr()

        click.echo(f"{self.ERROR_TYPE}: {self.format_message()}", file=file)


class TaipanFileError(TaipanError):
    ERROR_TYPE = "FileError"

    def __init__(self, path: Path, message: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path


class TaipanLocationError(TaipanError):
    ERROR_TYPE = "LocationError"

    def __init__(self, location: Location, message: str) -> None:
        super().__init__(
            f"{location.file}:{location.start.line}:{location.start.column}: {message}"
        )
        self.location = location


class TaipanSyntaxError(TaipanLocationError):
    ERROR_TYPE = "SyntaxError"


class TaipanSemanticError(TaipanLocationError):
    ERROR_TYPE = "SemanticError"


class TaipanCompilationError(TaipanError):
    ERROR_TYPE = "CompilationError"
