import shutil
import subprocess
import tempfile
from pathlib import Path

from .ast import AST
from .emitter import Emitter
from .exceptions import TaipanCompilationError, TaipanFileError
from .parser import Parser

COMPILER_OPTIONS = ["-Ofast"]


def find_clang() -> Path:
    clang = shutil.which("clang")
    if clang is None:
        raise TaipanCompilationError("clang not found in PATH")
    return Path(clang)


def find_clang_format() -> Path | None:
    clang_format = shutil.which("clang-format")
    if clang_format is None:
        print("clang-format not found in PATH")
        return None
    return Path(clang_format)


def generate_c_code(input: Path) -> str:
    parser = Parser(input)
    ast = AST(parser.program())

    emitter = Emitter()
    emitter.emit(ast.root)
    return emitter.code


def save_code_to_tempfile(temp_dir: str, code: str) -> Path:
    temp = tempfile.NamedTemporaryFile("w+t", dir=temp_dir, suffix=".c", delete=False)
    temp.write(code)
    temp.close()

    return Path(temp.name)


def generate_executable(temp_dir: str, clang: Path, source: Path) -> Path:
    temp = tempfile.NamedTemporaryFile("w+b", dir=temp_dir, suffix=".c", delete=False)
    temp.close()

    result = subprocess.run(
        [clang, *COMPILER_OPTIONS, "-o", temp.name, source],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8")

    return Path(temp.name)


def compile_to_c(input: Path, output: Path) -> None:
    code = generate_c_code(input)
    file = output.with_suffix(".c")
    file.write_text(code)

    clang_format = find_clang_format()
    if clang_format is not None:
        subprocess.run([clang_format, "-i", file])


def compile(input: Path, output: Path) -> None:
    clang = find_clang()
    code = generate_c_code(input)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_source = save_code_to_tempfile(temp_dir, code)
        temp_output = generate_executable(temp_dir, clang, temp_source)

        output.touch()
        try:
            output.write_bytes(temp_output.read_bytes())
        except OSError as error:
            raise TaipanFileError(output, error.strerror)


def run(input: Path, args: tuple[str]) -> int:
    clang = find_clang()
    code = generate_c_code(input)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_source = save_code_to_tempfile(temp_dir, code)
        temp_output = generate_executable(temp_dir, clang, temp_source)

        return subprocess.run([temp_output, *args]).returncode
