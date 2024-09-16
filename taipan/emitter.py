from typing import Any

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
    Program,
    Statement,
    String,
    UnaryExpression,
    While,
)
from taipan.templates.functions import Functions


class Emitter:
    def __init__(self) -> None:
        self.libraries = set[str]()

    @classmethod
    def emit(cls, ast: AST) -> str:
        emitter = cls()
        return emitter._emit_program(ast.root)

    def _emit_program(self, program: Program) -> str:
        code = self._emit_statement(program.block)
        return self._emit_header() + self._emit_main(code)

    def _emit_main(self, code: str) -> str:
        return f"int main(){{{code}return 0;}}\n"

    def _emit_header(self) -> str:
        header = ""
        for library in self.libraries:
            header += f"#include<{library}>\n"

        return header

    def _emit_statement(self, statement: Statement) -> str:
        match statement:
            case Block():
                code = ""
                for statement in statement.statements:
                    code += self._emit_statement(statement)

                return code
            case If():
                condition = self._emit_comparison(statement.condition)
                block = self._emit_statement(statement.block)
                return f"if({condition}){{{block}}}"
            case While():
                condition = self._emit_comparison(statement.condition)
                block = self._emit_statement(statement.block)
                return f"while({condition}){{{block}}}"
            case Input():
                return self._emit_function(Functions.input, identifier=statement.identifier.name)
            case Print():
                match statement.value:
                    case String():
                        is_number = False
                        value = self._emit_string(statement.value)
                    case expression:
                        is_number = True
                        value = self._emit_expression(expression)

                return self._emit_function(Functions.print, value=value, is_number=is_number)
            case Declaration():
                indentifier = statement.identifier.name
                match statement.expression:
                    case None:
                        expression = "0.0"
                    case expression:
                        expression = self._emit_expression(expression)

                return f"double {indentifier}={expression};"
            case Assignment():
                identifier = statement.identifier.name
                expression = self._emit_expression(statement.expression)
                return f"{identifier}={expression};"
            case _:
                assert False, statement

    def _emit_function(self, function: Functions, **args: Any) -> str:
        code, libraries = function.render(**args)
        self.libraries.update(libraries)
        return code

    def _emit_expression(self, expression: Expression) -> str:
        match expression:
            case Number():
                return str(expression.value)
            case Identifier():
                return expression.name
            case UnaryExpression():
                return expression.operator.value + self._emit_expression(expression.value)
            case BinaryExpression():
                return (
                    self._emit_expression(expression.left)
                    + expression.operator.value
                    + self._emit_expression(expression.right)
                )
            case ParentheseExpression():
                return f"({self._emit_expression(expression.value)})"
            case _:
                assert False, expression

    def _emit_comparison(self, comparison: Comparison) -> str:
        match comparison.left:
            case Comparison():
                left = self._emit_comparison(comparison.left)
            case expression:
                left = self._emit_expression(expression)

        match comparison.right:
            case Comparison():
                right = self._emit_comparison(comparison.right)
            case expression:
                right = self._emit_expression(expression)

        return left + comparison.operator + right

    def _emit_string(self, string: String) -> str:
        return f'"{string.value}"'
