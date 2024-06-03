from pathlib import Path


class TaipanException(Exception):
    pass


class FileError(TaipanException):
    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path


class SyntaxError(TaipanException):
    def __init__(self, message: str) -> None:
        super().__init__(f"SyntaxError: {message}")
