from collections import deque
from pathlib import Path

from taipan.ast import (
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
from taipan.exceptions import TaipanSemanticError
from taipan.symbol_table import SymbolTable


def analyze(file: Path, ast: AST) -> None:
    _visit(file, deque(), ast.root)


def _is_defined(symbol_tables: deque[SymbolTable], identifier: Identifier) -> bool:
    for table in reversed(symbol_tables):
        symbol = table.lookup(identifier.name)
        if not symbol:
            continue
        if identifier.line > symbol.line:
            return True
    return False


def _visit(file: Path, symbol_tables: deque[SymbolTable], node: Node) -> None:
    match node:
        case Program():
            _visit(file, symbol_tables, node.block)
        case Block():
            symbol_tables.append(node.symbol_table)
            for statement in node.statements:
                _visit(file, symbol_tables, statement)
            symbol_tables.pop()
        case If() | While():
            _visit(file, symbol_tables, node.condition)
            _visit(file, symbol_tables, node.block)
        case Input():
            _visit(file, symbol_tables, node.identifier)
        case Print():
            _visit(file, symbol_tables, node.value)
        case Assignment():
            _visit(file, symbol_tables, node.identifier)
            _visit(file, symbol_tables, node.expression)
        case BinaryExpression():
            _visit(file, symbol_tables, node.left)
            _visit(file, symbol_tables, node.right)
        case UnaryExpression():
            _visit(file, symbol_tables, node.value)
        case Comparison():
            _visit(file, symbol_tables, node.left)
            _visit(file, symbol_tables, node.right)
        case Identifier():
            if not _is_defined(symbol_tables, node):
                raise TaipanSemanticError(
                    file,
                    node.line,
                    node.column,
                    f"Identifier '{node.name}' is not defined",
                )
