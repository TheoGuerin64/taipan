from typing import override

from taipan._visitor import Visitor
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
    String,
    UnaryExpression,
    While,
)


class Emitter(Visitor):
    def __init__(self) -> None:
        self._libraries = set[str]()
        self._code = ""

    @classmethod
    def emit(cls, ast: AST) -> str:
        emitter = cls()
        emitter.visit_block(ast.root.block)

        header = ""
        for library in emitter._libraries:
            header += f"#include<{library}>\n"

        return header + f"int main(){emitter._code}\n"

    @override
    def visit_string(self, string: String) -> None:
        self._code += f'"{string.value}"'

    @override
    def visit_number(self, number: Number) -> None:
        self._code += str(number.value)

    @override
    def visit_identifier(self, identifier: Identifier) -> None:
        self._code += identifier.name

    @override
    def visit_parenthese_expression(self, parenthese_expression: ParentheseExpression) -> None:
        self._code += "("
        parenthese_expression.value.accept(self)
        self._code += ")"

    @override
    def visit_unary_expression(self, unary_expression: UnaryExpression) -> None:
        self._code += unary_expression.operator.value
        unary_expression.value.accept(self)

    @override
    def visit_binary_expression(self, binary_expression: BinaryExpression) -> None:
        binary_expression.left.accept(self)
        self._code += binary_expression.operator.value
        binary_expression.right.accept(self)

    @override
    def visit_comparison(self, comparison: Comparison) -> None:
        comparison.left.accept(self)
        self._code += comparison.operator.value
        comparison.right.accept(self)

    @override
    def visit_block(self, block: Block) -> None:
        self._code += "{"
        for statement in block.statements:
            statement.accept(self)
        self._code += "}"

    @override
    def visit_if(self, if_: If) -> None:
        self._code += "if("
        if_.condition.accept(self)
        self._code += ")"
        if_.block.accept(self)
        if if_.else_:
            self._code += "else "
            if_.else_.accept(self)

    @override
    def visit_while(self, while_: While) -> None:
        self._code += "while("
        while_.condition.accept(self)
        self._code += ")"
        while_.block.accept(self)

    @override
    def visit_input(self, input_: Input) -> None:
        self._libraries.add("stdio.h")

        self._code += 'if (!scanf("%lf", &'
        input_.identifier.accept(self)
        self._code += "))"
        input_.identifier.accept(self)
        self._code += " = 0;"

    @override
    def visit_print(self, print_: Print) -> None:
        self._libraries.add("stdio.h")

        match print_.value:
            case String():
                self._code += "puts("
            case Expression():
                self._code += 'printf("%lf\\n",'

        print_.value.accept(self)
        self._code += ");"

    @override
    def visit_declaration(self, declaration: Declaration) -> None:
        self._code += "double "
        declaration.identifier.accept(self)
        self._code += "="
        if declaration.expression:
            declaration.expression.accept(self)
        else:
            self._code += "0.0"
        self._code += ";"

    @override
    def visit_assignment(self, assignment: Assignment) -> None:
        assignment.identifier.accept(self)
        self._code += "="
        assignment.expression.accept(self)
        self._code += ";"
