from collections import deque

from .ast import (
    AST,
    Assignment,
    BinaryExpression,
    Block,
    Comparaison,
    Identifier,
    If,
    Input,
    Node,
    Number,
    Print,
    Program,
    String,
    UnaryExpression,
    While,
)


class Analyzer:
    def __init__(self, ast: AST) -> None:
        self.ast = ast
        self.symbole_tables = deque()

    def analyze(self) -> None:
        self.visit(self.ast.root)

    def is_defined(self, identifier: str) -> bool:
        for table in reversed(self.symbole_tables):
            if identifier in table:
                return True
        return False

    def visit(self, node: Node, declaration: bool = False) -> None:
        match node:
            case Program():
                self.visit(node.block)
            case Block():
                self.symbole_tables.append(node.symbol_table)
                for statement in node.statements:
                    self.visit(statement)
                self.symbole_tables.pop()
            case If() | While():
                self.visit(node.condition)
                self.visit(node.block)
            case Input():
                pass
            case Print():
                self.visit(node.value, True)
            case Assignment():
                pass
            case BinaryExpression():
                pass
            case UnaryExpression():
                pass
            case Comparaison():
                pass
            case Identifier():
                pass
            case Number():
                pass
            case String():
                pass
            # case Program():
            #     self.visit(node.block)
            # case Block():
            #     self.symbole_tables.append(node.symbol_table)
            #     for statement in node.statements:
            #         self.visit(statement)
            #     self.symbole_tables.pop()
            # case Print():
            #     if isinstance(node.value, Node):
            #         self.visit(node.value)
