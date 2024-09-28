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
from taipan.location import Location, Position
from taipan.parser import Parser
from taipan.symbol_table import SymbolTable

DEFAULT_FILE = Path("file.tp")


class TestParser:
    def test_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        number = parser._number()
        assert number == Number(
            value=1,
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )

    def test_identifier(self) -> None:
        parser = Parser(DEFAULT_FILE, "x")
        identifier = parser._identifier()
        assert identifier == Identifier(
            name="x",
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )

    def test_literal_with_identifier(self) -> None:
        parser = Parser(DEFAULT_FILE, "hello")
        literal = parser._literal()
        assert literal == Identifier(
            name="hello",
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
        )

    def test_literal_with_keyword(self) -> None:
        parser = Parser(DEFAULT_FILE, "print")
        with pytest.raises(TaipanSyntaxError):
            parser._literal()

    def test_unary_without_sign(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        unary = parser._unary()
        assert unary == Number(
            value=1,
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )

    def test_unary_with_negative_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "-1")
        unary = parser._unary()
        assert unary == UnaryExpression(
            operator=UnaryOperator.NEGATIVE,
            value=Number(
                value=1,
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 2),
                    end=Position(1, 3),
                ),
            ),
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
        )

    def test_term_with_multiplication(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 * 2")
        term = parser._multiplicative()
        assert term == BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.MULTIPLY,
        )

    def test_term_with_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        term = parser._multiplicative()
        assert term == Number(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
            value=1,
        )

    def test_term_with_multiple_operations(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 * 2 / 3 % 4")
        term = parser._multiplicative()
        expected_term = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_term = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 10),
            ),
            left=expected_term,
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 9),
                    end=Position(1, 10),
                ),
                value=3,
            ),
            operator=ArithmeticOperator.DIVIDE,
        )
        expected_term = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 14),
            ),
            left=expected_term,
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 13),
                    end=Position(1, 14),
                ),
                value=4,
            ),
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
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.ADD,
        )

    def test_expression_with_number(self) -> None:
        parser = Parser(DEFAULT_FILE, "1")
        expression = parser._expression()
        assert expression == Number(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
            value=1,
        )

    def test_expression_with_multiple_operations(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 + 2 * 3 - 4")
        expression = parser._expression()
        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 5),
                end=Position(1, 10),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 9),
                    end=Position(1, 10),
                ),
                value=3,
            ),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 10),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=expected_expression,
            operator=ArithmeticOperator.ADD,
        )
        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 14),
            ),
            left=expected_expression,
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 13),
                    end=Position(1, 14),
                ),
                value=4,
            ),
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
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 5),
            ),
            operator=UnaryOperator.NEGATIVE,
            value=ParentheseExpression(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 2),
                    end=Position(1, 5),
                ),
                value=Number(
                    location=Location(
                        DEFAULT_FILE,
                        start=Position(1, 3),
                        end=Position(1, 4),
                    ),
                    value=1,
                ),
            ),
        )

    def test_expression_with_parentheses(self) -> None:
        parser = Parser(DEFAULT_FILE, "(1 + (2 - 3)) * (4)")
        expression = parser._expression()

        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 7),
                end=Position(1, 12),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.SUBTRACT,
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 11),
                    end=Position(1, 12),
                ),
                value=3,
            ),
        )
        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 2),
                end=Position(1, 13),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 2),
                    end=Position(1, 3),
                ),
                value=1,
            ),
            operator=ArithmeticOperator.ADD,
            right=ParentheseExpression(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 6),
                    end=Position(1, 13),
                ),
                value=expected_expression,
            ),
        )
        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 20),
            ),
            left=ParentheseExpression(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 14),
                ),
                value=expected_expression,
            ),
            operator=ArithmeticOperator.MULTIPLY,
            right=ParentheseExpression(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 17),
                    end=Position(1, 20),
                ),
                value=Number(
                    location=Location(
                        DEFAULT_FILE,
                        start=Position(1, 18),
                        end=Position(1, 19),
                    ),
                    value=4,
                ),
            ),
        )
        assert expression == expected_expression

    def test_comparison(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 == 1")
        comparison = parser._expression()
        assert comparison == Comparison(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 7),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 6),
                    end=Position(1, 7),
                ),
                value=1,
            ),
            operator=ComparisonOperator.EQUAL,
        )

    def test_comparison_with_multiple_operations(self) -> None:
        parser = Parser(DEFAULT_FILE, "1 > 2 == 3 < 4")
        comparison = parser._expression()
        expected_comparison = Comparison(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ComparisonOperator.GREATER,
        )
        expected_comparison = Comparison(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 11),
            ),
            left=expected_comparison,
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 10),
                    end=Position(1, 11),
                ),
                value=3,
            ),
            operator=ComparisonOperator.EQUAL,
        )
        expected_comparison = Comparison(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 15),
            ),
            left=expected_comparison,
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 14),
                    end=Position(1, 15),
                ),
                value=4,
            ),
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
        assert block == Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
        )

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
        expected_block = Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 3),
                end=Position(1, 5),
            ),
        )
        expected_block = Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 2),
                end=Position(2, 2),
            ),
            statements=[expected_block],
        )
        expected_block = Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(3, 2),
            ),
            statements=[expected_block],
        )
        assert block == expected_block

    def test_block_with_newline(self) -> None:
        parser = Parser(DEFAULT_FILE, "\n\n{\n\n\nprint 1\n\n}\n")
        block = parser._block()
        expected_statement = Print(
            location=Location(
                DEFAULT_FILE,
                start=Position(6, 1),
                end=Position(6, 8),
            ),
            value=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(6, 7),
                    end=Position(6, 8),
                ),
                value=1,
            ),
        )
        assert block == Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(3, 1),
                end=Position(8, 2),
            ),
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
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 4),
                end=Position(1, 10),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 4),
                    end=Position(1, 5),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 9),
                    end=Position(1, 10),
                ),
                value=1,
            ),
            operator=ComparisonOperator.EQUAL,
        )
        assert statement == If(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 13),
            ),
            condition=expected_comparison,
            block=Block(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 11),
                    end=Position(1, 13),
                ),
            ),
        )

    def test_while_statement(self) -> None:
        parser = Parser(DEFAULT_FILE, "while 1 != 1 {}")
        statement = parser._statement()
        expected_comparison = Comparison(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 7),
                end=Position(1, 13),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 12),
                    end=Position(1, 13),
                ),
                value=1,
            ),
            operator=ComparisonOperator.NOT_EQUAL,
        )
        assert statement == While(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 16),
            ),
            condition=expected_comparison,
            block=Block(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 14),
                    end=Position(1, 16),
                ),
            ),
        )

    def teste_input_statement(self) -> None:
        parser = Parser(DEFAULT_FILE, "input x")
        statement = parser._statement()
        assert statement == Input(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 8),
            ),
            identifier=Identifier(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                name="x",
            ),
        )

    def test_print_statement_with_string(self) -> None:
        parser = Parser(DEFAULT_FILE, 'print "hello"')
        statement = parser._statement()
        assert statement == Print(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 14),
            ),
            value=String(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 7),
                    end=Position(1, 14),
                ),
                value="hello",
            ),
        )

    def test_print_statement_with_expression(self) -> None:
        parser = Parser(DEFAULT_FILE, "print 1 + 1")
        statement = parser._statement()
        expected_expression = BinaryExpression(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 7),
                end=Position(1, 12),
            ),
            left=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 11),
                    end=Position(1, 12),
                ),
                value=1,
            ),
            operator=ArithmeticOperator.ADD,
        )
        assert statement == Print(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 12),
            ),
            value=expected_expression,
        )

    def test_declaration_statement_with_value(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let x = 1\n}")
        block = parser._block()
        expected_statement = Declaration(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 2),
                end=Position(1, 11),
            ),
            identifier=Identifier(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 6),
                    end=Position(1, 7),
                ),
                name="x",
            ),
            expression=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 10),
                    end=Position(1, 11),
                ),
                value=1,
            ),
        )
        assert block == Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(2, 2),
            ),
            statements=[expected_statement],
            symbol_table=SymbolTable(
                {
                    "x": Location(DEFAULT_FILE, start=Position(1, 6), end=Position(1, 7)),
                },
            ),
        )

    def test_declaration_statement_without_value(self) -> None:
        parser = Parser(DEFAULT_FILE, "{let x\n}")
        block = parser._block()
        expected_statement = Declaration(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 2),
                end=Position(1, 7),
            ),
            identifier=Identifier(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 6),
                    end=Position(1, 7),
                ),
                name="x",
            ),
            expression=None,
        )
        assert block == Block(
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(2, 2),
            ),
            statements=[expected_statement],
            symbol_table=SymbolTable(
                {
                    "x": Location(DEFAULT_FILE, start=Position(1, 6), end=Position(1, 7)),
                },
            ),
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
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            identifier=Identifier(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                name="x",
            ),
            expression=Number(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=1,
            ),
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
            location=Location(
                DEFAULT_FILE,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
            block=Block(
                location=Location(
                    DEFAULT_FILE,
                    start=Position(1, 1),
                    end=Position(1, 3),
                ),
            ),
        )

    def test_programm_with_empty_program(self) -> None:
        parser = Parser(DEFAULT_FILE, "")
        with pytest.raises(TaipanSyntaxError):
            parser._program()

    def test_programm_with_newlines(self) -> None:
        parser = Parser(DEFAULT_FILE, "\n\n\n")
        with pytest.raises(TaipanSyntaxError):
            parser._program()
