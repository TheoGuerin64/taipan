import shutil
import subprocess
import tempfile
from pathlib import Path

from .ast import AST
from .emitter import Emitter
from .exceptions import TaipanCompilationError, TaipanFileError
from .parser import Parser


def find_gcc() -> Path:
    gcc = shutil.which("gcc")
    if gcc is None:
        raise TaipanCompilationError("gcc not found in PATH")
    return Path(gcc)


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


def generate_executable(temp_dir: str, gcc: Path, source: Path) -> Path:
    temp = tempfile.NamedTemporaryFile("w+b", dir=temp_dir, suffix=".c", delete=False)
    temp.close()

    result = subprocess.run(
        [gcc, "-o", temp.name, source],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8")

    return Path(temp.name)


def compile_to_c(input: Path, output: Path) -> None:
    code = generate_c_code(input)
    output.with_suffix(".c").write_text(code)


def compile(input: Path, output: Path) -> None:
    gcc = find_gcc()
    code = generate_c_code(input)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_source = save_code_to_tempfile(temp_dir, code)
        temp_output = generate_executable(temp_dir, gcc, temp_source)

        output.touch()
        try:
            output.write_bytes(temp_output.read_bytes())
        except OSError as error:
            raise TaipanFileError(output, error.strerror)


def run(input: Path, args: tuple[str]) -> int:
    gcc = find_gcc()
    code = generate_c_code(input)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_source = save_code_to_tempfile(temp_dir, code)
        temp_output = generate_executable(temp_dir, gcc, temp_source)

        return subprocess.run([temp_output, *args]).returncode
