from pathlib import Path

from scripts.node_shower import show_node

from .ast import AST
from .lexer import Lexer
from .parser import Parser


def compile(input: Path, output: Path) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    ast = AST(parser.program())
    show_node(ast.root)
