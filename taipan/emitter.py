from pathlib import Path

from .ast import (
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


class Emitter:
    def __init__(self) -> None:
        self.libraries: set[str] = set()
        self.variables: set[str] = set()
        self.code = ""

    def emit(self, node: Node) -> None:
        match node:
            case Program():
                self.emit(node.block)
                self.emit_variables()
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
                self.variables.add(node.name)
                self.code += node.name
            case Number():
                self.code += str(node.value)
            case String():
                self.code += f'"{node.value}"'
            case _:
                raise ValueError(f"Unknown node: {node}")

    def emit_variables(self) -> None:
        variables = ""
        if self.variables:
            variables += "double "
            for index, variable in enumerate(self.variables):
                if index > 0:
                    variables += ","
                variables += variable
            variables += ";"
        self.code = variables + self.code

    def emit_main(self) -> None:
        self.code = f"int main(){{{self.code}return 0;}}"

    def emit_header(self) -> None:
        header = ""
        for library in self.libraries:
            header += f"#include <{library}>\n"
        self.code = header + self.code

    def write_to_file(self, path: Path):
        with path.open("w") as file:
            file.write(self.code)
