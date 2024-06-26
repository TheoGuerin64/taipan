from .ast import (
    Assignment,
    BinaryExpression,
    Block,
    Comparaison,
    Declaration,
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


class Emitter:
    def __init__(self) -> None:
        self.libraries: set[str] = set()
        self.code = ""

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
                self.libraries.add("stdio.h")
                self.code += 'if(!scanf("%lf",&'
                self.emit(node.identifier)
                self.code += "))"
                self.emit(node.identifier)
                self.code += "=0;"
            case Print():
                self.libraries.add("stdio.h")
                match node.value:
                    case String():
                        format = "%s"
                    case _:
                        format = "%lf"
                self.code += f'printf("{format}\\n",'
                self.emit(node.value)
                self.code += ");"
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
            case Comparaison():
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
        self.code = f"int main(){{{self.code}return 0;}}"

    def emit_header(self) -> None:
        header = ""
        for library in self.libraries:
            header += f"#include <{library}>\n"
        self.code = header + self.code
