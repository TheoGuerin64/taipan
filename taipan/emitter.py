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
    Number,
    Print,
    Program,
    Statement,
    String,
    UnaryExpression,
    While,
)
from taipan.templates import functions


class Emitter:
    def __init__(self) -> None:
        self.libraries = set[str]()

    def emit_program(self, program: Program) -> str:
        code = self.emit_statement(program.block)
        return self.emit_header() + self.emit_main(code)

    def emit_main(self, code: str) -> str:
        return f"int main(){{{code}return 0;}}\n"

    def emit_header(self) -> str:
        header = ""
        for library in self.libraries:
            header += f"#include<{library}>\n"

        return header

    def emit_statement(self, statement: Statement) -> str:
        match statement:
            case Block():
                code = ""
                for statement in statement.statements:
                    code += self.emit_statement(statement)

                return code
            case If():
                condition = self.emit_comparison(statement.condition)
                block = self.emit_statement(statement.block)
                return f"if({condition}){{{block}}}"
            case While():
                condition = self.emit_comparison(statement.condition)
                block = self.emit_statement(statement.block)
                return f"while({condition}){{{block}}}"
            case Input():
                return self.emit_function("input", identifier=statement.identifier.name)
            case Print():
                match statement.value:
                    case String():
                        is_number = False
                        value = self.emit_string(statement.value)
                    case expression:
                        is_number = True
                        value = self.emit_expression(expression)

                return self.emit_function("print", value=value, is_number=is_number)
            case Declaration():
                indentifier = statement.identifier.name
                match statement.expression:
                    case None:
                        expression = "0.0"
                    case expression:
                        expression = self.emit_expression(expression)

                return f"double {indentifier}={expression};"
            case Assignment():
                identifier = statement.identifier.name
                expression = self.emit_expression(statement.expression)
                return f"{identifier}={expression};"
            case _:
                assert False, statement

    def emit_function(self, name: str, **kwargs: Any) -> str:
        code, libraries = functions.render(name, **kwargs)
        self.libraries.update(libraries)
        return code

    def emit_expression(self, expression: Expression) -> str:
        match expression:
            case Number():
                return str(expression.value)
            case Identifier():
                return expression.name
            case UnaryExpression():
                return expression.operator.value + self.emit_expression(expression.value)
            case BinaryExpression():
                return (
                    self.emit_expression(expression.left)
                    + expression.operator.value
                    + self.emit_expression(expression.right)
                )
            case _:
                assert False, expression

    def emit_comparison(self, comparison: Comparison) -> str:
        match comparison.left:
            case Comparison():
                left = self.emit_comparison(comparison.left)
            case Number() | Identifier() | UnaryExpression() | BinaryExpression():
                left = self.emit_expression(comparison.left)
            case _:
                assert False, comparison

        return left + comparison.operator + self.emit_expression(comparison.right)

    def emit_string(self, string: String) -> str:
        return f'"{string.value}"'
