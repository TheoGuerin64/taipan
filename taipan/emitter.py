from typing import Any

from taipan.ast import (
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    Declaration,
    Expression,
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
from taipan.templates import functions


def to_string(node: Expression) -> str:
    match node:
        case Number():
            return str(node.value)
        case Identifier():
            return node.name
        case BinaryExpression():
            return to_string(node.left) + node.operator.value + to_string(node.right)
        case UnaryExpression():
            return node.operator.value + to_string(node.value)[0]
        case _:
            assert False, node


class Emitter:
    def __init__(self) -> None:
        self.code = ""
        self.libraries = set[str]()

    def emit_function(self, name: str, **kwargs: Any) -> None:
        code, libraries = functions.render(name, **kwargs)
        self.code += code
        self.libraries.update(libraries)

    def emit(self, node: Node) -> None:
        match node:
            case Program():
                self.emit(node.block)
                self.emit_main()
                self.emit_header()
            case Block():
                for statement in node.statements:
                    self.emit(statement)
            case If():
                self.code += "if("
                self.emit(node.condition)
                self.code += "){"
                self.emit(node.block)
                self.code += "}"
            case While():
                self.code += "while("
                self.emit(node.condition)
                self.code += "){"
                self.emit(node.block)
                self.code += "}"
            case Input():
                self.emit_function("input", identifier=node.identifier.name)
            case Print():
                match node.value:
                    case String():
                        is_number = False
                        value = node.value.value
                    case _:
                        is_number = True
                        value = to_string(node.value)
                self.emit_function("print", value=value, is_number=is_number)
            case Declaration():
                self.code += "double "
                self.emit(node.identifier)
                self.code += "="
                if node.expression:
                    self.emit(node.expression)
                else:
                    self.code += "0.0"
                self.code += ";"
            case Assignment():
                self.emit(node.identifier)
                self.code += "="
                self.emit(node.expression)
                self.code += ";"
            case BinaryExpression():
                self.emit(node.left)
                self.code += node.operator.value
                self.emit(node.right)
            case UnaryExpression():
                self.code += node.operator.value
                self.emit(node.value)
            case Comparison():
                self.emit(node.left)
                self.code += node.operator.value
                self.emit(node.right)
            case Identifier():
                self.code += node.name
            case Number():
                self.code += str(node.value)
            case String():
                self.code += f'"{node.value}"'
            case _:
                assert False, node

    def emit_main(self) -> None:
        self.code = f"int main(){{{self.code}return 0;}}\n"

    def emit_header(self) -> None:
        for library in self.libraries:
            self.code = f"#include<{library}>\n" + self.code
