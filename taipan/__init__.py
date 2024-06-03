import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from taipan.emitter import Emitter

from .ast import AST
from .lexer import Lexer
from .parser import Parser


class TaipanError(Exception):
    pass


def compile(input: Path, output: Path, c: bool) -> None:
    gcc_path = shutil.which("gcc")
    if gcc_path is None:
        raise TaipanError("gcc not found")

    lexer = Lexer(input)
    parser = Parser(lexer)
    emitter = Emitter()

    ast = AST(parser.program())
    emitter.emit(ast.root)

    if c:
        output.with_suffix(".c").write_text(emitter.code)
        return

    with NamedTemporaryFile(mode="w+", suffix=".c") as temp:
        temp.write(emitter.code)
        temp.flush()

        subprocess.call([gcc_path, "-o", str(output), temp.name])
