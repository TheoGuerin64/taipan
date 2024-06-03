import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from taipan.emitter import Emitter

from .ast import AST
from .lexer import Lexer
from .parser import Parser


def compile(input: Path, output: Path, gcc: Path) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    emitter = Emitter()

    ast = AST(parser.program())
    emitter.emit(ast.root)

    with NamedTemporaryFile(mode="w+", suffix=".c") as temp:
        temp.write(emitter.code)
        temp.flush()

        subprocess.call([str(gcc), "-o", str(output), temp.name])
