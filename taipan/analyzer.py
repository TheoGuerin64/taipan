from collections import deque

from taipan.ast import (
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


def _is_defined(symbol_tables: deque[SymbolTable], identifier: Identifier) -> bool:
    for table in reversed(symbol_tables):
        symbol = table.lookup(identifier.name)
        if not symbol:
            continue
        if identifier.location.line > symbol.line:
            return True
    return False


def analyze(node: Node, symbol_tables: deque[SymbolTable] | None = None) -> None:
    if symbol_tables is None:
        symbol_tables = deque()

    match node:
        case Program():
            analyze(node.block, symbol_tables)
        case Block():
            symbol_tables.append(node.symbol_table)
            for statement in node.statements:
                analyze(statement, symbol_tables)
            symbol_tables.pop()
        case If() | While():
            analyze(node.condition, symbol_tables)
            analyze(node.block, symbol_tables)
        case Input():
            analyze(node.identifier, symbol_tables)
        case Print():
            analyze(node.value, symbol_tables)
        case Assignment():
            analyze(node.identifier, symbol_tables)
            analyze(node.expression, symbol_tables)
        case BinaryExpression():
            analyze(node.left, symbol_tables)
            analyze(node.right, symbol_tables)
        case UnaryExpression():
            analyze(node.value, symbol_tables)
        case Comparison():
            analyze(node.left, symbol_tables)
            analyze(node.right, symbol_tables)
        case Identifier():
            if not _is_defined(symbol_tables, node):
                raise TaipanSemanticError(node.location, f"Identifier '{node.name}' is not defined")
