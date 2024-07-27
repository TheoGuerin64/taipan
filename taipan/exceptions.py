from __future__ import annotations

from pathlib import Path


class TaipanError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TaipanFileError(TaipanError):
    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path


class TaipanLocationError(TaipanError):
    ERROR_TYPE = "LocationError"

    def __init__(self, file: Path, line: int, column: int, message: str) -> None:
        super().__init__(f"{file}:{line}:{column}: {self.ERROR_TYPE}: {message}")


class TaipanSyntaxError(TaipanLocationError):
    ERROR_TYPE = "SyntaxError"


class TaipanSemanticError(TaipanLocationError):
    ERROR_TYPE = "SemanticError"


class TaipanCompilationError(TaipanError):
    def __init__(self, message: str) -> None:
        super().__init__(f"CompilationError: {message}")
