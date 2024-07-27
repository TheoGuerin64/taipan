from collections import deque
from pathlib import Path

from taipan.exceptions import TaipanSemanticError

from .ast import (
    AST,
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    Identifier,
    If,
    Input,
    Node,
    Print,
    Program,
    UnaryExpression,
    While,
)
from .symbol_table import SymbolTable


def analyze(file: Path, ast: AST) -> None:
    visit(file, deque(), ast.root)


def is_defined(symbol_tables: deque[SymbolTable], identifier: Identifier) -> bool:
    for table in reversed(symbol_tables):
        symbol = table.lookup(identifier.name)
        if not symbol:
            continue
        if identifier.line > symbol.line:
            return True
    return False


def visit(file: Path, symbol_tables: deque[SymbolTable], node: Node) -> None:
    match node:
        case Program():
            visit(file, symbol_tables, node.block)
        case Block():
            symbol_tables.append(node.symbol_table)
            for statement in node.statements:
                visit(file, symbol_tables, statement)
            symbol_tables.pop()
        case If() | While():
            visit(file, symbol_tables, node.condition)
            visit(file, symbol_tables, node.block)
        case Input():
            visit(file, symbol_tables, node.identifier)
        case Print():
            visit(file, symbol_tables, node.value)
        case Assignment():
            visit(file, symbol_tables, node.identifier)
            visit(file, symbol_tables, node.expression)
        case BinaryExpression():
            visit(file, symbol_tables, node.left)
            visit(file, symbol_tables, node.right)
        case UnaryExpression():
            visit(file, symbol_tables, node.value)
        case Comparison():
            visit(file, symbol_tables, node.left)
            visit(file, symbol_tables, node.right)
        case Identifier():
            if not is_defined(symbol_tables, node):
                raise TaipanSemanticError(
                    file,
                    node.line,
                    node.column,
                    f"Identifier '{node.name}' is not defined",
                )
