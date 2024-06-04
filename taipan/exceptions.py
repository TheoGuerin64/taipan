from pathlib import Path


class TaipanError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TaipanFileError(TaipanError):
    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path


class TaipanSyntaxError(TaipanError):
    def __init__(self, message: str) -> None:
        super().__init__(f"SyntaxError: {message}")


class TaipanCompilationError(TaipanError):
    def __init__(self, message: str) -> None:
        super().__init__(f"CompilationError: {message}")
