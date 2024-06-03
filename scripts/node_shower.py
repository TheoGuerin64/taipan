import tkinter as tk
from tkinter import ttk

import sv_ttk

from taipan.ast import (
    Assignment,
    BinaryExpression,
    Block,
    Comparaison,
    If,
    Input,
    Node,
    Print,
    Program,
    UnaryExpression,
    While,
)


def show_node(node: Node) -> None:
    root = tk.Tk()
    root.title("Node Viewer")

    treeview = ttk.Treeview(show="tree")

    def populate_tree(node: Node, parent: str) -> None:
        item = treeview.insert(parent, tk.END, text=str(node))
        match node:
            case Program():
                populate_tree(node.block, item)
            case Block():
                for statement in node.statements:
                    populate_tree(statement, item)
            case If() | While():
                populate_tree(node.condition, item)
                populate_tree(node.block, item)
            case Comparaison() | BinaryExpression():
                populate_tree(node.left, item)
                populate_tree(node.right, item)
            case UnaryExpression():
                populate_tree(node.value, item)
            case Input():
                populate_tree(node.identifier, item)
            case Print():
                populate_tree(node.value, item)
            case Assignment():
                populate_tree(node.identifier, item)
                populate_tree(node.expression, item)

    populate_tree(node, "")
    treeview.pack(expand=tk.YES, fill=tk.BOTH)

    sv_ttk.set_theme("dark")
    root.mainloop()
