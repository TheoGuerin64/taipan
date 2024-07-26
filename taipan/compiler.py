import os
import shutil
import subprocess
from pathlib import Path

from .ast import AST
from .emitter import Emitter
from .exceptions import TaipanCompilationError
from .parser import Parser

COMPILER_OPTIONS = ["-Ofast"]
TEMP_DIR = Path("tmp")


def _find_clang() -> Path:
    clang = shutil.which("clang")
    if clang is None:
        raise TaipanCompilationError("clang not found in PATH")
    return Path(clang)


def _find_clang_format() -> Path | None:
    clang_format = shutil.which("clang-format")
    if clang_format is None:
        print("clang-format not found in PATH")
        return None
    return Path(clang_format)


def _ensure_temp_directory() -> None:
    if not TEMP_DIR.exists():
        TEMP_DIR.mkdir()
    elif not TEMP_DIR.is_dir():
        raise TaipanCompilationError(f"{TEMP_DIR} is not a directory")


def _generate_c_code(input: Path) -> str:
    parser = Parser(input)
    ast = AST(parser.program())

    emitter = Emitter()
    emitter.emit(ast.root)
    return emitter.code


def _clang_compile(code: str, destination: Path) -> None:
    clang = _find_clang()
    result = subprocess.run(
        [clang, *COMPILER_OPTIONS, "-o", destination, "-xc", "-"],
        input=code.encode("utf-8"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8")


def compile_to_c(input: Path, output: Path) -> None:
    code = _generate_c_code(input)
    file = output.with_suffix(".c")
    file.write_text(code)

    clang_format = _find_clang_format()
    if clang_format is not None:
        subprocess.run([clang_format, "-i", file])


def compile(input: Path, output: Path) -> None:
    code = _generate_c_code(input)
    _clang_compile(code, output)


def run(input: Path, output_name: str, args: tuple[str]) -> int:
    code = _generate_c_code(input)

    _ensure_temp_directory()
    temp_output = TEMP_DIR / output_name

    _clang_compile(code, temp_output)
    os.execl(temp_output, temp_output, *args)
