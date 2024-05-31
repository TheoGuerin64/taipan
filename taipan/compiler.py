from pathlib import Path

from . import parser
from .ast import show_node
from .lexer import Lexer


def run(input: Path, output: Path) -> None:
    lexer = Lexer(input)
    ast = parser.run(lexer)
    show_node(ast.root)
