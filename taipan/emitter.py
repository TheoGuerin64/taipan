from typing import assert_never

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
from taipan.visitor import Visitor


class Emitter(Visitor):
    def __init__(self) -> None:
        self.libraries = set[str]()
        self.code = ""

    @classmethod
    def emit(cls, ast: AST) -> str:
        emitter = cls()
        emitter.visit_block(ast.root.block)

        header = ""
        for library in emitter.libraries:
            header += f"#include<{library}>\n"

        return header + f"int main(){emitter.code}\n"

    def visit_string(self, string: String) -> None:
        self.code += f'"{string.value}"'

    def visit_number(self, number: Number) -> None:
        self.code += str(number.value)

    def visit_identifier(self, identifier: Identifier) -> None:
        self.code += identifier.name

    def visit_parenthese_expression(self, parenthese_expression: ParentheseExpression) -> None:
        self.code += "("
        parenthese_expression.value.accept(self)
        self.code += ")"

    def visit_unary_expression(self, unary_expression: UnaryExpression) -> None:
        self.code += unary_expression.operator.value
        unary_expression.value.accept(self)

    def visit_binary_expression(self, binary_expression: BinaryExpression) -> None:
        binary_expression.left.accept(self)
        self.code += binary_expression.operator.value
        binary_expression.right.accept(self)

    def visit_comparison(self, comparison: Comparison) -> None:
        comparison.left.accept(self)
        self.code += comparison.operator.value
        comparison.right.accept(self)

    def visit_block(self, block: Block) -> None:
        self.code += "{"
        for statement in block.statements:
            statement.accept(self)
        self.code += "}"

    def visit_if(self, if_: If) -> None:
        self.code += "if("
        if_.condition.accept(self)
        self.code += ")"
        if_.block.accept(self)
        if if_.else_:
            self.code += "else "
            if_.else_.accept(self)

    def visit_while(self, while_: While) -> None:
        self.code += "while("
        while_.condition.accept(self)
        self.code += ")"
        while_.block.accept(self)

    def visit_input(self, input_: Input) -> None:
        self.libraries.add("stdio.h")

        self.code += 'if (!scanf("%lf", &'
        input_.identifier.accept(self)
        self.code += "))"
        input_.identifier.accept(self)
        self.code += " = 0;"

    def visit_print(self, print_: Print) -> None:
        self.libraries.add("stdio.h")

        match print_.value:
            case String():
                self.code += "puts("
            case Expression():
                self.code += 'printf("%lf\\n",'
            case other:
                assert_never(other)

        print_.value.accept(self)
        self.code += ");"

    def visit_declaration(self, declaration: Declaration) -> None:
        self.code += "double "
        declaration.identifier.accept(self)
        self.code += "="
        if declaration.expression:
            declaration.expression.accept(self)
        else:
            self.code += "0.0"
        self.code += ";"

    def visit_assignment(self, assignment: Assignment) -> None:
        assignment.identifier.accept(self)
        self.code += "="
        assignment.expression.accept(self)
        self.code += ";"
