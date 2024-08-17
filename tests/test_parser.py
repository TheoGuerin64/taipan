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
    NodeList,
    Number,
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


class TestParser:
    def test_number(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1")

        parser = Parser(file)
        number = parser.number()
        assert number == Number(location=Location(file, 1, 1), value=1)

    def test_identifier(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("x")

        parser = Parser(file)
        identifier = parser.identifier()
        assert identifier == Identifier(location=Location(file, 1, 1), name="x")

    def test_literal_with_identifier(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("hello")

        parser = Parser(file)
        literal = parser.literal()
        assert literal == Identifier(location=Location(file, 1, 1), name="hello")

    def test_literal_with_keyword(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("print")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.literal()

    def test_unary_without_sign(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1")

        parser = Parser(file)
        unary = parser.unary()
        assert unary == Number(location=Location(file, 1, 1), value=1)

    def test_unary_with_negative_number(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("-1")

        parser = Parser(file)
        unary = parser.unary()
        assert unary == UnaryExpression(
            location=Location(file, 1, 1),
            operator=UnaryOperator.NEGATIVE,
            value=Number(location=Location(file, 1, 2), value=1),
        )

    def test_term_with_multiplication(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 * 2")

        parser = Parser(file)
        term = parser.term()
        assert term == BinaryExpression(
            location=Location(file, 1, 1),
            left=Number(location=Location(file, 1, 1), value=1),
            right=Number(location=Location(file, 1, 5), value=2),
            operator=ArithmeticOperator.MULTIPLY,
        )

    def test_term_with_number(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1")

        parser = Parser(file)
        term = parser.term()
        assert term == Number(location=Location(file, 1, 1), value=1)

    def test_term_with_multiple_operations(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 * 2 / 3 % 4")

        parser = Parser(file)
        term = parser.term()
        expected_term = BinaryExpression(
            location=Location(file, 1, 1),
            left=Number(location=Location(file, 1, 1), value=1),
            right=Number(location=Location(file, 1, 5), value=2),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_term = BinaryExpression(
            location=Location(file, 1, 1),
            left=expected_term,
            right=Number(location=Location(file, 1, 9), value=3),
            operator=ArithmeticOperator.DIVIDE,
        )
        expected_term = BinaryExpression(
            location=Location(file, 1, 1),
            left=expected_term,
            right=Number(location=Location(file, 1, 13), value=4),
            operator=ArithmeticOperator.MODULO,
        )
        assert term == expected_term

    def test_non_finished_term(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 * ")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.term()

    def test_expression_with_addition(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 + 2")

        parser = Parser(file)
        expression = parser.expression()
        assert expression == BinaryExpression(
            location=Location(file, 1, 1),
            left=Number(location=Location(file, 1, 1), value=1),
            right=Number(location=Location(file, 1, 5), value=2),
            operator=ArithmeticOperator.ADD,
        )

    def test_expression_with_number(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1")

        parser = Parser(file)
        expression = parser.expression()
        assert expression == Number(location=Location(file, 1, 1), value=1)

    def test_expression_with_multiple_operations(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 + 2 * 3 - 4")

        parser = Parser(file)
        expression = parser.expression()
        expected_expression = BinaryExpression(
            location=Location(file, 1, 5),
            left=Number(location=Location(file, 1, 5), value=2),
            right=Number(location=Location(file, 1, 9), value=3),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_expression = BinaryExpression(
            location=Location(file, 1, 1),
            left=Number(location=Location(file, 1, 1), value=1),
            right=expected_expression,
            operator=ArithmeticOperator.ADD,
        )
        expected_expression = BinaryExpression(
            location=Location(file, 1, 1),
            left=expected_expression,
            right=Number(location=Location(file, 1, 13), value=4),
            operator=ArithmeticOperator.SUBTRACT,
        )
        assert expression == expected_expression

    def test_non_finished_expression(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 + ")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.expression()

    def test_comparison(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 == 1")

        parser = Parser(file)
        comparison = parser.comparison()
        assert comparison == Comparison(
            location=Location(file, 1, 1),
            left=Number(location=Location(file, 1, 1), value=1),
            right=Number(location=Location(file, 1, 6), value=1),
            operator=ComparisonOperator.EQUAL,
        )

    def test_comparison_with_multiple_operations(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 > 2 == 3 < 4")

        parser = Parser(file)
        comparison = parser.comparison()
        expected_comparison = Comparison(
            location=Location(file, 1, 1),
            left=Number(location=Location(file, 1, 1), value=1),
            right=Number(location=Location(file, 1, 5), value=2),
            operator=ComparisonOperator.GREATER,
        )
        expected_comparison = Comparison(
            location=Location(file, 1, 1),
            left=expected_comparison,
            right=Number(location=Location(file, 1, 10), value=3),
            operator=ComparisonOperator.EQUAL,
        )
        expected_comparison = Comparison(
            location=Location(file, 1, 1),
            left=expected_comparison,
            right=Number(location=Location(file, 1, 14), value=4),
            operator=ComparisonOperator.LESS,
        )
        assert comparison == expected_comparison

    def test_non_finished_comparison(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("1 == ")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.comparison()

    def test_empty_block(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{}")

        parser = Parser(file)
        block = parser.block()
        assert block == Block(location=Location(file, 1, 1))

    def test_block_missing_open_brace(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("print 1}")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.block()

    def test_block_missing_closing_brace(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{print 1")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.block()

    def test_nested_blocks(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{{{}\n}\n}")

        parser = Parser(file)
        block = parser.block()
        expected_block = Block(location=Location(file, 1, 3))
        expected_block = Block(location=Location(file, 1, 2), statements=NodeList([expected_block]))
        expected_block = Block(location=Location(file, 1, 1), statements=NodeList([expected_block]))
        assert block == expected_block

    def test_block_missing_newline(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{print 1}")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.block()

    def test_if_statement(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("if 1 == 1 {}")

        parser = Parser(file)
        statement = parser.statement()
        expected_comparison = Comparison(
            location=Location(file, 1, 4),
            left=Number(location=Location(file, 1, 4), value=1),
            right=Number(location=Location(file, 1, 9), value=1),
            operator=ComparisonOperator.EQUAL,
        )
        assert statement == If(
            location=Location(file, 1, 1),
            condition=expected_comparison,
            block=Block(location=Location(file, 1, 11)),
        )

    def test_while_statement(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("while 1 != 1 {}")

        parser = Parser(file)
        statement = parser.statement()
        expected_comparison = Comparison(
            location=Location(file, 1, 7),
            left=Number(location=Location(file, 1, 7), value=1),
            right=Number(location=Location(file, 1, 12), value=1),
            operator=ComparisonOperator.NOT_EQUAL,
        )
        assert statement == While(
            location=Location(file, 1, 1),
            condition=expected_comparison,
            block=Block(location=Location(file, 1, 14)),
        )

    def input_statement(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("input x")

        parser = Parser(file)
        statement = parser.statement()
        assert statement == Input(
            location=Location(file, 1, 1),
            identifier=Identifier(location=Location(file, 1, 7), name="x"),
        )

    def test_print_statement_with_string(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text('print "hello"')

        parser = Parser(file)
        statement = parser.statement()
        assert statement == Print(
            location=Location(file, 1, 1),
            value=String(location=Location(file, 1, 7), value="hello"),
        )

    def test_print_statement_with_expression(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("print 1 + 1")

        parser = Parser(file)
        statement = parser.statement()
        expected_expression = BinaryExpression(
            location=Location(file, 1, 7),
            left=Number(location=Location(file, 1, 7), value=1),
            right=Number(location=Location(file, 1, 11), value=1),
            operator=ArithmeticOperator.ADD,
        )
        assert statement == Print(location=Location(file, 1, 1), value=expected_expression)

    def test_declaration_statement_with_value(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{let x = 1\n}")

        parser = Parser(file)
        block = parser.block()
        expected_statement = Declaration(
            location=Location(file, 1, 2),
            identifier=Identifier(location=Location(file, 1, 6), name="x"),
            expression=Number(location=Location(file, 1, 10), value=1),
        )
        assert block == Block(
            location=Location(file, 1, 1),
            statements=NodeList([expected_statement]),
            symbol_table=SymbolTable({"x": Location(file, 1, 2)}),
        )

    def test_declaration_statement_without_value(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{let x\n}")

        parser = Parser(file)
        block = parser.block()
        expected_statement = Declaration(
            location=Location(file, 1, 2),
            identifier=Identifier(location=Location(file, 1, 6), name="x"),
            expression=None,
        )
        assert block == Block(
            location=Location(file, 1, 1),
            statements=NodeList([expected_statement]),
            symbol_table=SymbolTable({"x": Location(file, 1, 2)}),
        )

    def test_declaration_statement_missing_identifier(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{let\n}")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.block()

    def test_declaration_statement_missing_value(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{let x =\n}")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.block()

    def test_assignment_statement(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("x = 1")

        parser = Parser(file)
        statement = parser.statement()
        assert statement == Assignment(
            location=Location(file, 1, 1),
            identifier=Identifier(location=Location(file, 1, 1), name="x"),
            expression=Number(location=Location(file, 1, 5), value=1),
        )

    def test_assignment_statement_missing_value(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("x =")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.statement()

    def test_assignment_statement_operator(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("x")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.statement()

    def test_statement_with_unknown_keyword(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("unknown")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.statement()

    def test_program(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("{}")

        parser = Parser(file)
        program = parser.program()
        assert program == Program(
            location=Location(file, 0, 0),
            block=Block(location=Location(file, 1, 1)),
        )

    def test_programm_with_empty_file(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.program()

    def test_programm_with_newlines(self, tmp_path: Path) -> None:
        file = tmp_path / "file.tp"
        file.write_text("\n\n\n")

        parser = Parser(file)
        with pytest.raises(TaipanSyntaxError):
            parser.program()
