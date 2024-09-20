from pathlib import Path

import pytest

from taipan.ast import (
    ArithmeticOperator,
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    ComparisonOperator,
    Declaration,
    Identifier,
    If,
    Input,
    Number,
    ParentheseExpression,
    Print,
    Program,
    String,
    UnaryExpression,
    UnaryOperator,
    While,
)
from taipan.exceptions import TaipanSyntaxError
from taipan.parser import Parser
from taipan.symbol_table import SymbolTable
from taipan.utils import Location

DEFAULT_FILE = Path("file.tp")


class TestParser:
    def test_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        number = parser._number()
        assert number == Number(location=Location(DEFAULT_FILE, 1, 1), value=1)

    def test_identifier(self) -> None:
        parser = Parser(DEFAULT_FILE, "x")
        identifier = parser._identifier()
        assert identifier == Identifier(location=Location(DEFAULT_FILE, 1, 1), name="x")

    def test_literal_with_identifier(self) -> None:
        parser = Parser(DEFAULT_FILE, "hello")
        literal = parser._literal()
        assert literal == Identifier(location=Location(DEFAULT_FILE, 1, 1), name="hello")

    def test_literal_with_keyword(self) -> None:
        parser = Parser(DEFAULT_FILE, "print")
        with pytest.raises(TaipanSyntaxError):
            parser._literal()

    def test_unary_without_sign(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        unary = parser._unary()
        assert unary == Number(location=Location(DEFAULT_FILE, 1, 1), value=1)

    def test_unary_with_negative_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "-1")
        unary = parser._unary()
        assert unary == UnaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            operator=UnaryOperator.NEGATIVE,
            value=Number(location=Location(DEFAULT_FILE, 1, 2), value=1),
        )

    def test_term_with_multiplication(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 * 2")
        term = parser._multiplicative()
        assert term == BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=Number(location=Location(DEFAULT_FILE, 1, 1), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 5), value=2),
            operator=ArithmeticOperator.MULTIPLY,
        )

    def test_term_with_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        term = parser._multiplicative()
        assert term == Number(location=Location(DEFAULT_FILE, 1, 1), value=1)

    def test_term_with_multiple_operations(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 * 2 / 3 % 4")
        term = parser._multiplicative()
        expected_term = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=Number(location=Location(DEFAULT_FILE, 1, 1), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 5), value=2),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_term = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=expected_term,
            right=Number(location=Location(DEFAULT_FILE, 1, 9), value=3),
            operator=ArithmeticOperator.DIVIDE,
        )
        expected_term = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=expected_term,
            right=Number(location=Location(DEFAULT_FILE, 1, 13), value=4),
            operator=ArithmeticOperator.MODULO,
        )
        assert term == expected_term

    def test_non_finished_term(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 * ")
        with pytest.raises(TaipanSyntaxError):
            parser._multiplicative()

    def test_expression_with_addition(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 + 2")
        expression = parser._expression()
        assert expression == BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=Number(location=Location(DEFAULT_FILE, 1, 1), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 5), value=2),
            operator=ArithmeticOperator.ADD,
        )

    def test_expression_with_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        expression = parser._expression()
        assert expression == Number(location=Location(DEFAULT_FILE, 1, 1), value=1)

    def test_expression_with_multiple_operations(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 + 2 * 3 - 4")
        expression = parser._expression()
        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 5),
            left=Number(location=Location(DEFAULT_FILE, 1, 5), value=2),
            right=Number(location=Location(DEFAULT_FILE, 1, 9), value=3),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=Number(location=Location(DEFAULT_FILE, 1, 1), value=1),
            right=expected_expression,
            operator=ArithmeticOperator.ADD,
        )
        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=expected_expression,
            right=Number(location=Location(DEFAULT_FILE, 1, 13), value=4),
            operator=ArithmeticOperator.SUBTRACT,
        )
        assert expression == expected_expression

    def test_non_finished_expression(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 + ")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_missing_close_parentheses(self) -> None:
        parser = Parser(DEFAULT_FILE, "(1 + 2")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_missing_open_parentheses(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let a = 1 + 2)}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_missing_empty_parentheses(self) -> None:
        parser = Parser(DEFAULT_FILE, "()")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_negative_parentheses(self) -> None:
        parser = Parser(DEFAULT_FILE, "-(1)")
        expression = parser._expression()
        assert expression == UnaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            operator=UnaryOperator.NEGATIVE,
            value=ParentheseExpression(
                location=Location(DEFAULT_FILE, 1, 2),
                value=Number(
                    location=Location(DEFAULT_FILE, 1, 3),
                    value=1,
                ),
            ),
        )

    def test_expression_with_parentheses(self) -> None:
        parser = Parser(DEFAULT_FILE, "(1 + (2 - 3)) * (4)")
        expression = parser._expression()

        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 7),
            left=Number(
                location=Location(DEFAULT_FILE, 1, 7),
                value=2,
            ),
            operator=ArithmeticOperator.SUBTRACT,
            right=Number(
                location=Location(DEFAULT_FILE, 1, 11),
                value=3,
            ),
        )
        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 2),
            left=Number(
                location=Location(DEFAULT_FILE, 1, 2),
                value=1,
            ),
            operator=ArithmeticOperator.ADD,
            right=ParentheseExpression(
                location=Location(DEFAULT_FILE, 1, 6),
                value=expected_expression,
            ),
        )
        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 1),
            left=ParentheseExpression(
                location=Location(DEFAULT_FILE, 1, 1),
                value=expected_expression,
            ),
            operator=ArithmeticOperator.MULTIPLY,
            right=ParentheseExpression(
                location=Location(DEFAULT_FILE, 1, 17),
                value=Number(
                    location=Location(DEFAULT_FILE, 1, 18),
                    value=4,
                ),
            ),
        )
        assert expression == expected_expression

    def test_comparison(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 == 1")
        comparison = parser._expression()
        assert comparison == Comparison(
            location=Location(DEFAULT_FILE, 1, 1),
            left=Number(location=Location(DEFAULT_FILE, 1, 1), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 6), value=1),
            operator=ComparisonOperator.EQUAL,
        )

    def test_comparison_with_multiple_operations(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 > 2 == 3 < 4")
        comparison = parser._expression()
        expected_comparison = Comparison(
            location=Location(DEFAULT_FILE, 1, 1),
            left=Number(location=Location(DEFAULT_FILE, 1, 1), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 5), value=2),
            operator=ComparisonOperator.GREATER,
        )
        expected_comparison = Comparison(
            location=Location(DEFAULT_FILE, 1, 1),
            left=expected_comparison,
            right=Number(location=Location(DEFAULT_FILE, 1, 10), value=3),
            operator=ComparisonOperator.EQUAL,
        )
        expected_comparison = Comparison(
            location=Location(DEFAULT_FILE, 1, 1),
            left=expected_comparison,
            right=Number(location=Location(DEFAULT_FILE, 1, 14), value=4),
            operator=ComparisonOperator.LESS,
        )
        assert comparison == expected_comparison

    def test_non_finished_comparison(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 == ")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_empty_block(self) -> None:
        parser = Parser(DEFAULT_FILE, "{}")
        block = parser._block()
        assert block == Block(location=Location(DEFAULT_FILE, 1, 1))

    def test_block_missing_open_brace(self) -> None:
        parser = Parser(DEFAULT_FILE, "print 1}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_block_missing_closing_brace(self) -> None:
        parser = Parser(DEFAULT_FILE, "{print 1")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_nested_blocks(self) -> None:
        parser = Parser(DEFAULT_FILE, "{{{}\n}\n}")
        block = parser._block()
        expected_block = Block(location=Location(DEFAULT_FILE, 1, 3))
        expected_block = Block(location=Location(DEFAULT_FILE, 1, 2), statements=[expected_block])
        expected_block = Block(location=Location(DEFAULT_FILE, 1, 1), statements=[expected_block])
        assert block == expected_block

    def test_block_with_newline(self) -> None:
        parser = Parser(DEFAULT_FILE, "\n\n{\n\n\nprint 1\n\n}\n")
        block = parser._block()
        expected_statement = Print(
            location=Location(DEFAULT_FILE, 6, 1),
            value=Number(location=Location(DEFAULT_FILE, 6, 7), value=1),
        )
        assert block == Block(
            location=Location(DEFAULT_FILE, 3, 1),
            statements=[expected_statement],
        )

    def test_block_missing_newline(self) -> None:
        parser = Parser(DEFAULT_FILE, "{print 1}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_if_statement(self) -> None:
        parser = Parser(DEFAULT_FILE, "if 1 == 1 {}")
        statement = parser._statement()
        expected_comparison = Comparison(
            location=Location(DEFAULT_FILE, 1, 4),
            left=Number(location=Location(DEFAULT_FILE, 1, 4), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 9), value=1),
            operator=ComparisonOperator.EQUAL,
        )
        assert statement == If(
            location=Location(DEFAULT_FILE, 1, 1),
            condition=expected_comparison,
            block=Block(location=Location(DEFAULT_FILE, 1, 11)),
        )

    def test_while_statement(self) -> None:
        parser = Parser(DEFAULT_FILE, "while 1 != 1 {}")
        statement = parser._statement()
        expected_comparison = Comparison(
            location=Location(DEFAULT_FILE, 1, 7),
            left=Number(location=Location(DEFAULT_FILE, 1, 7), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 12), value=1),
            operator=ComparisonOperator.NOT_EQUAL,
        )
        assert statement == While(
            location=Location(DEFAULT_FILE, 1, 1),
            condition=expected_comparison,
            block=Block(location=Location(DEFAULT_FILE, 1, 14)),
        )

    def input_statement(self) -> None:
        parser = Parser(DEFAULT_FILE, "input x")
        statement = parser._statement()
        assert statement == Input(
            location=Location(DEFAULT_FILE, 1, 1),
            identifier=Identifier(location=Location(DEFAULT_FILE, 1, 7), name="x"),
        )

    def test_print_statement_with_string(self) -> None:
        parser = Parser(DEFAULT_FILE, 'print "hello"')
        statement = parser._statement()
        assert statement == Print(
            location=Location(DEFAULT_FILE, 1, 1),
            value=String(location=Location(DEFAULT_FILE, 1, 7), value="hello"),
        )

    def test_print_statement_with_expression(self) -> None:
        parser = Parser(DEFAULT_FILE, "print 1 + 1")
        statement = parser._statement()
        expected_expression = BinaryExpression(
            location=Location(DEFAULT_FILE, 1, 7),
            left=Number(location=Location(DEFAULT_FILE, 1, 7), value=1),
            right=Number(location=Location(DEFAULT_FILE, 1, 11), value=1),
            operator=ArithmeticOperator.ADD,
        )
        assert statement == Print(location=Location(DEFAULT_FILE, 1, 1), value=expected_expression)

    def test_declaration_statement_with_value(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let x = 1\n}")
        block = parser._block()
        expected_statement = Declaration(
            location=Location(DEFAULT_FILE, 1, 2),
            identifier=Identifier(location=Location(DEFAULT_FILE, 1, 6), name="x"),
            expression=Number(location=Location(DEFAULT_FILE, 1, 10), value=1),
        )
        assert block == Block(
            location=Location(DEFAULT_FILE, 1, 1),
            statements=[expected_statement],
            symbol_table=SymbolTable({"x": Location(DEFAULT_FILE, 1, 2)}),
        )

    def test_declaration_statement_without_value(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let x\n}")
        block = parser._block()
        expected_statement = Declaration(
            location=Location(DEFAULT_FILE, 1, 2),
            identifier=Identifier(location=Location(DEFAULT_FILE, 1, 6), name="x"),
            expression=None,
        )
        assert block == Block(
            location=Location(DEFAULT_FILE, 1, 1),
            statements=[expected_statement],
            symbol_table=SymbolTable({"x": Location(DEFAULT_FILE, 1, 2)}),
        )

    def test_declaration_statement_missing_identifier(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let\n}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_declaration_statement_missing_value(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let x =\n}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_assignment_statement(self) -> None:
        parser = Parser(DEFAULT_FILE, "x = 1")
        statement = parser._statement()
        assert statement == Assignment(
            location=Location(DEFAULT_FILE, 1, 1),
            identifier=Identifier(location=Location(DEFAULT_FILE, 1, 1), name="x"),
            expression=Number(location=Location(DEFAULT_FILE, 1, 5), value=1),
        )

    def test_assignment_statement_missing_value(self) -> None:
        parser = Parser(DEFAULT_FILE, "x =")
        with pytest.raises(TaipanSyntaxError):
            parser._statement()

    def test_assignment_statement_operator(self) -> None:
        parser = Parser(DEFAULT_FILE, "x")
        with pytest.raises(TaipanSyntaxError):
            parser._statement()

    def test_statement_with_unknown_keyword(self) -> None:
        parser = Parser(DEFAULT_FILE, "unknown")
        with pytest.raises(TaipanSyntaxError):
            parser._statement()

    def test_program(self) -> None:
        parser = Parser(DEFAULT_FILE, "{}")
        program = parser._program()
        assert program == Program(
            location=Location(DEFAULT_FILE, 0, 0),
            block=Block(location=Location(DEFAULT_FILE, 1, 1)),
        )

    def test_programm_with_empty_DEFAULT_FILE(self) -> None:
        parser = Parser(DEFAULT_FILE, "")
        with pytest.raises(TaipanSyntaxError):
            parser._program()

    def test_programm_with_newlines(self) -> None:
        parser = Parser(DEFAULT_FILE, "\n\n\n")
        with pytest.raises(TaipanSyntaxError):
            parser._program()
