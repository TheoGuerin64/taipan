from pathlib import Path

from taipan.emitter import Emitter

from .ast import AST
from .lexer import Lexer
from .parser import Parser


def compile(input: Path, output: Path) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    emitter = Emitter()

    ast = AST(parser.program())
    emitter.emit(ast.root)
    emitter.write_to_file(output)
