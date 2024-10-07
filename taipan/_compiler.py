import shutil
import signal
import subprocess
import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from taipan._analyzer import Analyzer
from taipan._emitter import Emitter
from taipan._parser import parse
from taipan.exceptions import TaipanCompilationError

_OPTIMIZATION_FLAG = "-Ofast"


def _find_clang() -> str:
    clang = shutil.which("clang")
    if clang is None:
        raise TaipanCompilationError("clang not found in PATH")

    return clang


def _find_clang_format() -> str | None:
    clang_format = shutil.which("clang-format")
    if clang_format is None:
        print("clang-format not found in PATH", file=sys.stderr)
        return None

    return clang_format


def _generate_c_code(input_: Path | str) -> str:
    ast = parse(input_)
    Analyzer.analyze(ast)

    return Emitter.emit(ast)


def _clang_compile(code: str, destination: Path, optimize: bool) -> None:
    clang = _find_clang()

    command = [clang, "-xc", "-", "-o", destination]
    if optimize:
        command.append(_OPTIMIZATION_FLAG)

    result = subprocess.run(
        command,
        executable=clang,
        input=code.encode("utf-8"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise TaipanCompilationError(result.stderr.decode("utf-8"))


def compile(input: Path, output: Path, optimize: bool) -> None:
    code = _generate_c_code(input)
    _clang_compile(code, output, optimize)


def compile_to_c(input: Path, output: Path) -> None:
    code = _generate_c_code(input)
    output.write_text(code)

    clang_format = _find_clang_format()
    if clang_format is not None:
        subprocess.run([clang_format, "-i", output])


@contextmanager
def _temporary_file_path() -> Generator[Path]:
    temp_output = Path(tempfile.mktemp())
    try:
        yield temp_output
    finally:
        temp_output.unlink(missing_ok=True)


def run(input: Path, args: tuple[str, ...], optimize: bool) -> int:
    code = _generate_c_code(input)

    with _temporary_file_path() as output:
        _clang_compile(code, output, optimize)

        process = subprocess.Popen(args, executable=output)
        try:
            return process.wait()
        except KeyboardInterrupt:
            process.send_signal(signal.SIGINT)
            return 128 - process.wait()
