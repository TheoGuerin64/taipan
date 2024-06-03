from pathlib import Path

from scripts.node_shower import show_node

from . import parser


def run(input: Path, output: Path) -> None:
    ast = parser.run(input)
    show_node(ast.root)
