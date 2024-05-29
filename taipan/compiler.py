from pathlib import Path

from .ast import show_node
from .lexer import Lexer
from .parser import Parser


def compile(input: Path, output: Path) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    ast = parser.parse()
    show_node(ast.root)
