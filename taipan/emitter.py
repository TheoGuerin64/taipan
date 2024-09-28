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
        return f"int main(){code}\n"

    def _emit_header(self) -> str:
        header = ""
        for library in self.libraries:
            header += f"#include<{library}>\n"

        return header

    def _emit_function(self, function: Functions, **args: Any) -> str:
        code, libraries = function.render(**args)
        self.libraries.update(libraries)
        return code

    def _emit_statement(self, statement: Statement) -> str:
        match statement:
            case Block():
                code = ""
                for statement in statement.statements:
                    code += self._emit_statement(statement)

                return f"{{{code}}}"
            case If():
                condition = self._emit_expression(statement.condition)
                block = self._emit_statement(statement.block)

                code = f"if({condition}){block}"
                if statement.else_:
                    code += f"else {self._emit_statement(statement.else_)}"
                return code
            case While():
                condition = self._emit_expression(statement.condition)
                block = self._emit_statement(statement.block)
                return f"while({condition}){block}"
            case Input():
                return self._emit_function(Functions.input, identifier=statement.identifier.name)
            case Print():
                match statement.value:
                    case String():
                        value = self._emit_string(statement.value)
                    case Expression():
                        value = self._emit_expression(statement.value)
                    case _:
                        assert False, statement.value

                return self._emit_function(Functions.print, value=value)
            case Declaration():
                identifier = statement.identifier.name
                match statement.expression:
                    case None:
                        expression = "0.0"
                    case Expression():
                        expression = self._emit_expression(statement.expression)
                    case _:
                        assert False, statement.expression

                return f"double {identifier}={expression};"
            case Assignment():
                identifier = statement.identifier.name
                expression = self._emit_expression(statement.expression)
                return f"{identifier}={expression};"
            case _:
                assert False, statement

    def _emit_expression(self, expression: Expression) -> str:
        match expression:
            case Number():
                return str(expression.value)
            case Identifier():
                return expression.name
            case UnaryExpression():
                return expression.operator.value + self._emit_expression(expression.value)
            case BinaryExpression() | Comparison():
                return (
                    self._emit_expression(expression.left)
                    + expression.operator.value
                    + self._emit_expression(expression.right)
                )
            case ParentheseExpression():
                return f"({self._emit_expression(expression.value)})"
            case _:
                assert False, expression

    def _emit_string(self, string: String) -> str:
        return f'"{string.value}"'
