import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from .ast import AST
from .emitter import Emitter
from .exceptions import TaipanException
from .lexer import Lexer
from .parser import Parser


def find_gcc() -> Path:
    gcc = shutil.which("gcc")
    if gcc is None:
        raise TaipanException("gcc not found in PATH")
    return Path(gcc)


def compile(input: Path, output: Path, *, compile_to_c: bool = False) -> None:
    gcc = find_gcc()
    lexer = Lexer(input)
    parser = Parser(lexer)
    emitter = Emitter()

    ast = AST(parser.program())
    emitter.emit(ast.root)

    if compile_to_c:
        with output.with_suffix(".c").open("w") as file:
            file.write(emitter.code)
    else:
        with NamedTemporaryFile(mode="w", suffix=".c") as temp:
            temp.write(emitter.code)
            temp.flush()

            subprocess.call([gcc, "-o", output, temp.name])
