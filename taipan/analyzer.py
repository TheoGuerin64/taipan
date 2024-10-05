from collections import deque

from taipan.ast import (
    AST,
    Block,
    Declaration,
    Identifier,
)
from taipan.exceptions import TaipanSemanticError
from taipan.symbol_table import SymbolTable
from taipan.visitor import Visitor


def _is_defined(symbol_tables: deque[SymbolTable], identifier: Identifier) -> bool:
    for table in reversed(symbol_tables):
        symbol = table.lookup(identifier.name)
        if not symbol:
            continue
        if identifier.location.start.line > symbol.start.line:
            return True

    return False


class Analyzer(Visitor):
    def __init__(self) -> None:
        self.symbol_tables = deque[SymbolTable]()

    @classmethod
    def analyze(cls, ast: AST) -> None:
        analyzer = cls()
        analyzer.visit_block(ast.root.block)

    def visit_identifier(self, identifier: Identifier) -> None:
        if not _is_defined(self.symbol_tables, identifier):
            raise TaipanSemanticError(
                identifier.location, f"Identifier '{identifier.name}' is not defined"
            )

    def visit_declaration(self, declaration: Declaration) -> None:
        if declaration.expression:
            declaration.expression.accept(self)

    def visit_block(self, block: Block) -> None:
        self.symbol_tables.append(block.symbol_table)
        for statement in block.statements:
            statement.accept(self)
        self.symbol_tables.pop()
