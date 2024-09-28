from collections import deque

from taipan.ast import (
    AST,
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    Declaration,
    Expression,
    Identifier,
    If,
    Input,
    Number,
    ParentheseExpression,
    Print,
    Statement,
    String,
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
        if identifier.location.start.line > symbol.start.line:
            return True
    return False


class Analyzer:
    def __init__(self) -> None:
        self.symbol_tables = deque[SymbolTable]()

    @classmethod
    def analyze(cls, ast: AST) -> None:
        analyzer = cls()
        analyzer._analyze_statement(ast.root.block)

    def _analyze_statement(self, statement: Statement) -> None:
        match statement:
            case Block():
                self.symbol_tables.append(statement.symbol_table)
                for statement in statement.statements:
                    self._analyze_statement(statement)
                self.symbol_tables.pop()
            case If() | While():
                self._analyze_expression(statement.condition)
                self._analyze_statement(statement.block)
            case Input():
                self._analyze_expression(statement.identifier)
            case Print():
                match statement.value:
                    case String():
                        pass  # No need to analyze string
                    case Expression():
                        self._analyze_expression(statement.value)
                    case _:
                        assert False, statement.value
            case Assignment():
                self._analyze_expression(statement.identifier)
                self._analyze_expression(statement.expression)
            case Declaration():
                pass  # No need to analyze declaration
            case _:
                assert False, statement

    def _analyze_expression(self, expression: Expression) -> None:
        match expression:
            case Number():
                pass  # No need to analyze number
            case Identifier():
                if not _is_defined(self.symbol_tables, expression):
                    raise TaipanSemanticError(
                        expression.location, f"Identifier '{expression.name}' is not defined"
                    )
            case UnaryExpression():
                self._analyze_expression(expression.value)
            case BinaryExpression() | Comparison():
                self._analyze_expression(expression.left)
                self._analyze_expression(expression.right)
            case ParentheseExpression():
                self._analyze_expression(expression.value)
            case _:
                assert False, expression
