from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taipan.ast import (
        Assignment,
        BinaryExpression,
        Block,
        Comparison,
        Declaration,
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


class Visitor:
    def __init__(self):
        pass

    def visit_string(self, string: String) -> None:
        pass

    def visit_number(self, number: Number) -> None:
        pass

    def visit_identifier(self, identifier: Identifier) -> None:
        pass

    def visit_parenthese_expression(self, parenthese_expression: ParentheseExpression) -> None:
        parenthese_expression.value.accept(self)

    def visit_unary_expression(self, unary_expression: UnaryExpression) -> None:
        unary_expression.value.accept(self)

    def visit_binary_expression(self, binary_expression: BinaryExpression) -> None:
        binary_expression.left.accept(self)
        binary_expression.right.accept(self)

    def visit_comparison(self, comparison: Comparison) -> None:
        comparison.left.accept(self)
        comparison.right.accept(self)

    def visit_block(self, block: Block) -> None:
        for statement in block.statements:
            statement.accept(self)

    def visit_if(self, if_: If) -> None:
        if_.condition.accept(self)
        if_.block.accept(self)
        if if_.else_:
            if_.else_.accept(self)

    def visit_while(self, while_: While) -> None:
        while_.condition.accept(self)
        while_.block.accept(self)

    def visit_input(self, input_: Input) -> None:
        input_.identifier.accept(self)

    def visit_print(self, print_: Print) -> None:
        print_.value.accept(self)

    def visit_declaration(self, declaration: Declaration) -> None:
        declaration.identifier.accept(self)
        if declaration.expression:
            declaration.expression.accept(self)

    def visit_assignment(self, assignment: Assignment) -> None:
        assignment.identifier.accept(self)
        assignment.expression.accept(self)
