import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from taipan._analyzer import Analyzer
from taipan._emitter import Emitter
from taipan._parser import Parser
from taipan.exceptions import TaipanCompilationError

_OPTIMIZATION_FLAG = "-Ofast"


def _find_clang() -> Path:
    clang = shutil.which("clang")
    if clang is None:
        raise TaipanCompilationError("clang not found in PATH")

    return Path(clang)


def _find_clang_format() -> Path | None:
    clang_format = shutil.which("clang-format")
    if clang_format is None:
        print("clang-format not found in PATH", file=sys.stderr)
        return None

    return Path(clang_format)


def _generate_c_code(input: Path) -> str:
    ast = Parser.parse(input)
    Analyzer.analyze(ast)

    return Emitter.emit(ast)


def _clang_compile(code: str, destination: Path, optimize: bool) -> None:
    clang = _find_clang()

    command = [str(clang)]
    if optimize:
        command.append(_OPTIMIZATION_FLAG)
    command.extend(["-o", str(destination), "-xc", "-"])

    result = subprocess.run(
        command,
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


def compile(input: Path, output: Path, optimize: bool) -> None:
    code = _generate_c_code(input)
    _clang_compile(code, output, optimize)


def run(input: Path, output_name: str, args: tuple[str, ...], optimize: bool) -> int:
    code = _generate_c_code(input)
    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        temp_output = Path(temp_dir) / output_name
        _clang_compile(code, temp_output, optimize)

    import atexit
    import os

    atexit.register(shutil.rmtree, temp_dir)
    os.execl(temp_output, temp_output, *args)
