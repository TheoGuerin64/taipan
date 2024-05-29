from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from .lexer import TokenKind


@dataclass(kw_only=True)
class Node:
    childrens: list[Node] = field(default_factory=list, repr=False)


@dataclass(kw_only=True)
class ProgramNode(Node):
    pass


class KeywordKind(Enum):
    IF = auto()
    WHILE = auto()
    INPUT = auto()
    PRINT = auto()


@dataclass(kw_only=True)
class KeywordNode(Node):
    kind: KeywordKind


@dataclass(kw_only=True)
class AssignmentNode(Node):
    pass


@dataclass(kw_only=True)
class ExpressionNode(Node):
    pass


@dataclass(kw_only=True)
class ComparaisonNode(ExpressionNode):
    pass


class LiteralKind(Enum):
    NUMBER = auto()
    STRING = auto()


@dataclass(kw_only=True)
class LiteralNode(Node):
    kind: LiteralKind
    value: str | float


@dataclass(kw_only=True)
class IdentifierNode(Node):
    name: str


class UnaryOperatorKind(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()

    @classmethod
    def from_token_kind(cls, token_kind: TokenKind) -> UnaryOperatorKind | None:
        match token_kind:
            case TokenKind.PLUS:
                return cls.POSITIVE
            case TokenKind.MINUS:
                return cls.NEGATIVE
            case _:
                return None


@dataclass(kw_only=True)
class UnaryOperatorNode(Node):
    kind: UnaryOperatorKind


class ArithmeticOperatorKind(Enum):
    ADD = auto()
    SUBSTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()


@dataclass(kw_only=True)
class ArithmeticOperatorNode(Node):
    kind: ArithmeticOperatorKind


class ComparaisonOperatorKind(Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    @classmethod
    def from_token_kind(cls, token_kind: TokenKind) -> ComparaisonOperatorKind | None:
        match token_kind:
            case TokenKind.EQUAL:
                return cls.EQUAL
            case TokenKind.NOT_EQUAL:
                return cls.NOT_EQUAL
            case TokenKind.LESS:
                return cls.LESS
            case TokenKind.LESS_OR_EQUAL:
                return cls.LESS_EQUAL
            case TokenKind.GREATER:
                return cls.GREATER
            case TokenKind.GREATER_OR_EQUAL:
                return cls.GREATER_EQUAL
            case _:
                return None


@dataclass(kw_only=True)
class ComparaisonOperatorNode(Node):
    kind: ComparaisonOperatorKind


@dataclass(kw_only=True)
class AST:
    root: ProgramNode = field(default_factory=ProgramNode)


if __debug__:

    def show_node(node: Node) -> None:
        import tkinter as tk
        from tkinter import ttk

        import sv_ttk

        root = tk.Tk()
        root.title("AST")

        treeview = ttk.Treeview(show="tree")

        def populate_tree(node: Node, parent: str):
            item = treeview.insert(parent, tk.END, text=str(node))
            for child in node.childrens:
                populate_tree(child, item)

        populate_tree(node, "")
        treeview.pack(expand=tk.YES, fill=tk.BOTH)

        sv_ttk.set_theme("dark")
        root.mainloop()
