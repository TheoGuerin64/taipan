import pytest

from taipan._parser import Parser
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
from taipan.symbol_table import SymbolTable


class TestParser:
    def test_number(self) -> None:
        parser = Parser("1")
        number = parser._number()
        assert number == Number(
            value=1,
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )

    def test_identifier(self) -> None:
        parser = Parser("x")
        identifier = parser._identifier()
        assert identifier == Identifier(
            name="x",
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )

    def test_literal_with_identifier(self) -> None:
        parser = Parser("hello")
        literal = parser._literal()
        assert literal == Identifier(
            name="hello",
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
        )

    def test_literal_with_keyword(self) -> None:
        parser = Parser("print")
        with pytest.raises(TaipanSyntaxError):
            parser._literal()

    def test_unary_without_sign(self) -> None:
        parser = Parser("1")
        unary = parser._unary()
        assert unary == Number(
            value=1,
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
        )

    def test_unary_with_negative_number(self) -> None:
        parser = Parser("-1")
        unary = parser._unary()
        assert unary == UnaryExpression(
            operator=UnaryOperator.NEGATIVE,
            value=Number(
                value=1,
                location=Location(
                    None,
                    start=Position(1, 2),
                    end=Position(1, 3),
                ),
            ),
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
        )

    def test_term_with_multiplication(self) -> None:
        parser = Parser("1 * 2")
        term = parser._multiplicative()
        assert term == BinaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.MULTIPLY,
        )

    def test_term_with_number(self) -> None:
        parser = Parser("1")
        term = parser._multiplicative()
        assert term == Number(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
            value=1,
        )

    def test_term_with_multiple_operations(self) -> None:
        parser = Parser("1 * 2 / 3")
        term = parser._multiplicative()
        expected_term = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_term = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 10),
            ),
            left=expected_term,
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 9),
                    end=Position(1, 10),
                ),
                value=3,
            ),
            operator=ArithmeticOperator.DIVIDE,
        )
        assert term == expected_term

    def test_non_finished_term(self) -> None:
        parser = Parser("1 * ")
        with pytest.raises(TaipanSyntaxError):
            parser._multiplicative()

    def test_expression_with_addition(self) -> None:
        parser = Parser("1 + 2")
        expression = parser._expression()
        assert expression == BinaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.ADD,
        )

    def test_expression_with_number(self) -> None:
        parser = Parser("1")
        expression = parser._expression()
        assert expression == Number(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 2),
            ),
            value=1,
        )

    def test_expression_with_multiple_operations(self) -> None:
        parser = Parser("1 + 2 * 3 - 4")
        expression = parser._expression()
        expected_expression = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 5),
                end=Position(1, 10),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 9),
                    end=Position(1, 10),
                ),
                value=3,
            ),
            operator=ArithmeticOperator.MULTIPLY,
        )
        expected_expression = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 10),
            ),
            left=Number(
                location=Location(
                    None,
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
                None,
                start=Position(1, 1),
                end=Position(1, 14),
            ),
            left=expected_expression,
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 13),
                    end=Position(1, 14),
                ),
                value=4,
            ),
            operator=ArithmeticOperator.SUBTRACT,
        )
        assert expression == expected_expression

    def test_non_finished_expression(self) -> None:
        parser = Parser("1 + ")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_missing_close_parentheses(self) -> None:
        parser = Parser("(1 + 2")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_missing_open_parentheses(self) -> None:
        parser = Parser("{let a = 1 + 2)}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_missing_empty_parentheses(self) -> None:
        parser = Parser("()")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_negative_parentheses(self) -> None:
        parser = Parser("-(1)")
        expression = parser._expression()
        assert expression == UnaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 5),
            ),
            operator=UnaryOperator.NEGATIVE,
            value=ParentheseExpression(
                location=Location(
                    None,
                    start=Position(1, 2),
                    end=Position(1, 5),
                ),
                value=Number(
                    location=Location(
                        None,
                        start=Position(1, 3),
                        end=Position(1, 4),
                    ),
                    value=1,
                ),
            ),
        )

    def test_expression_with_parentheses(self) -> None:
        parser = Parser("(1 + (2 - 3)) * (4)")
        expression = parser._expression()

        expected_expression = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 7),
                end=Position(1, 12),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                value=2,
            ),
            operator=ArithmeticOperator.SUBTRACT,
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 11),
                    end=Position(1, 12),
                ),
                value=3,
            ),
        )
        expected_expression = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 2),
                end=Position(1, 13),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 2),
                    end=Position(1, 3),
                ),
                value=1,
            ),
            operator=ArithmeticOperator.ADD,
            right=ParentheseExpression(
                location=Location(
                    None,
                    start=Position(1, 6),
                    end=Position(1, 13),
                ),
                value=expected_expression,
            ),
        )
        expected_expression = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 20),
            ),
            left=ParentheseExpression(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 14),
                ),
                value=expected_expression,
            ),
            operator=ArithmeticOperator.MULTIPLY,
            right=ParentheseExpression(
                location=Location(
                    None,
                    start=Position(1, 17),
                    end=Position(1, 20),
                ),
                value=Number(
                    location=Location(
                        None,
                        start=Position(1, 18),
                        end=Position(1, 19),
                    ),
                    value=4,
                ),
            ),
        )
        assert expression == expected_expression

    def test_comparison(self) -> None:
        parser = Parser("1 == 1")
        comparison = parser._expression()
        assert comparison == Comparison(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 7),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 6),
                    end=Position(1, 7),
                ),
                value=1,
            ),
            operator=ComparisonOperator.EQUAL,
        )

    def test_comparison_with_multiple_operations(self) -> None:
        parser = Parser("1 > 2 == 3 < 4")
        comparison = parser._expression()
        expected_comparison = Comparison(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=2,
            ),
            operator=ComparisonOperator.GREATER,
        )
        expected_comparison = Comparison(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 11),
            ),
            left=expected_comparison,
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 10),
                    end=Position(1, 11),
                ),
                value=3,
            ),
            operator=ComparisonOperator.EQUAL,
        )
        expected_comparison = Comparison(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 15),
            ),
            left=expected_comparison,
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 14),
                    end=Position(1, 15),
                ),
                value=4,
            ),
            operator=ComparisonOperator.LESS,
        )
        assert comparison == expected_comparison

    def test_non_finished_comparison(self) -> None:
        parser = Parser("1 == ")
        with pytest.raises(TaipanSyntaxError):
            parser._expression()

    def test_empty_block(self) -> None:
        parser = Parser("{}")
        block = parser._block()
        assert block == Block(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 3),
            ),
        )

    def test_block_missing_open_brace(self) -> None:
        parser = Parser("print 1}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_block_missing_closing_brace(self) -> None:
        parser = Parser("{print 1")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_nested_blocks(self) -> None:
        parser = Parser("{{{}\n}\n}")
        block = parser._block()
        expected_block = Block(
            location=Location(
                None,
                start=Position(1, 3),
                end=Position(1, 5),
            ),
        )
        expected_block = Block(
            location=Location(
                None,
                start=Position(1, 2),
                end=Position(2, 2),
            ),
            statements=[expected_block],
        )
        expected_block = Block(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(3, 2),
            ),
            statements=[expected_block],
        )
        assert block == expected_block

    def test_block_with_newline(self) -> None:
        parser = Parser("\n\n{\n\n\nprint 1\n\n}\n")
        block = parser._block()
        expected_statement = Print(
            location=Location(
                None,
                start=Position(6, 1),
                end=Position(6, 8),
            ),
            value=Number(
                location=Location(
                    None,
                    start=Position(6, 7),
                    end=Position(6, 8),
                ),
                value=1,
            ),
        )
        assert block == Block(
            location=Location(
                None,
                start=Position(3, 1),
                end=Position(8, 2),
            ),
            statements=[expected_statement],
        )

    def test_block_missing_newline(self) -> None:
        parser = Parser("{print 1}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_if_statement(self) -> None:
        parser = Parser("if 1 == 1 {}")
        statement = parser._statement()
        expected_comparison = Comparison(
            location=Location(
                None,
                start=Position(1, 4),
                end=Position(1, 10),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 4),
                    end=Position(1, 5),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 9),
                    end=Position(1, 10),
                ),
                value=1,
            ),
            operator=ComparisonOperator.EQUAL,
        )
        assert statement == If(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 13),
            ),
            condition=expected_comparison,
            block=Block(
                location=Location(
                    None,
                    start=Position(1, 11),
                    end=Position(1, 13),
                ),
            ),
        )

    def test_if_statement_with_else(self) -> None:
        parser = Parser("if 1 {} else {}")
        statement = parser._statement()
        assert statement == If(
            location=Location(
                None,
                Position(1, 1),
                Position(1, 16),
            ),
            condition=Number(
                value=1,
                location=Location(
                    None,
                    Position(1, 4),
                    Position(1, 5),
                ),
            ),
            block=Block(
                location=Location(
                    None,
                    Position(1, 6),
                    Position(1, 8),
                ),
            ),
            else_=Block(
                location=Location(
                    None,
                    Position(1, 14),
                    Position(1, 16),
                ),
            ),
        )

    def test_if_statement_with_else_if(self) -> None:
        parser = Parser("if (1 - 1) {} else if 1 {}")
        statement = parser._statement()
        assert statement == If(
            location=Location(
                None,
                Position(1, 1),
                Position(1, 27),
            ),
            condition=ParentheseExpression(
                location=Location(
                    None,
                    Position(1, 4),
                    Position(1, 11),
                ),
                value=BinaryExpression(
                    location=Location(
                        None,
                        Position(1, 5),
                        Position(1, 10),
                    ),
                    left=Number(
                        location=Location(
                            None,
                            Position(1, 5),
                            Position(1, 6),
                        ),
                        value=1,
                    ),
                    right=Number(
                        location=Location(
                            None,
                            Position(1, 9),
                            Position(1, 10),
                        ),
                        value=1,
                    ),
                    operator=ArithmeticOperator.SUBTRACT,
                ),
            ),
            block=Block(
                location=Location(
                    None,
                    Position(1, 12),
                    Position(1, 14),
                ),
            ),
            else_=If(
                location=Location(
                    None,
                    Position(1, 20),
                    Position(1, 27),
                ),
                condition=Number(
                    location=Location(
                        None,
                        Position(1, 23),
                        Position(1, 24),
                    ),
                    value=1,
                ),
                block=Block(
                    location=Location(
                        None,
                        Position(1, 25),
                        Position(1, 27),
                    ),
                ),
                else_=None,
            ),
        )

    def test_if_statement_with_else_if_else_with_newlines(self) -> None:
        parser = Parser("if 1 {\nprint 1\n} else if 1 {\nprint 2\n} else {\nprint 3\n}")
        statement = parser._statement()

        expected_else = Block(
            location=Location(
                None,
                Position(5, 8),
                Position(7, 2),
            ),
            statements=[
                Print(
                    location=Location(
                        None,
                        Position(6, 1),
                        Position(6, 8),
                    ),
                    value=Number(
                        location=Location(
                            None,
                            Position(6, 7),
                            Position(6, 8),
                        ),
                        value=3,
                    ),
                ),
            ],
        )
        expected_else_if = If(
            location=Location(
                None,
                Position(3, 8),
                Position(7, 2),
            ),
            condition=Number(
                location=Location(
                    None,
                    Position(3, 11),
                    Position(3, 12),
                ),
                value=1,
            ),
            block=Block(
                location=Location(
                    None,
                    Position(3, 13),
                    Position(5, 2),
                ),
                statements=[
                    Print(
                        location=Location(
                            None,
                            Position(4, 1),
                            Position(4, 8),
                        ),
                        value=Number(
                            location=Location(
                                None,
                                Position(4, 7),
                                Position(4, 8),
                            ),
                            value=2,
                        ),
                    ),
                ],
            ),
            else_=expected_else,
        )
        assert statement == If(
            location=Location(
                None,
                Position(1, 1),
                Position(7, 2),
            ),
            condition=Number(
                location=Location(
                    None,
                    Position(1, 4),
                    Position(1, 5),
                ),
                value=1,
            ),
            block=Block(
                location=Location(
                    None,
                    Position(1, 6),
                    Position(3, 2),
                ),
                statements=[
                    Print(
                        location=Location(
                            None,
                            Position(2, 1),
                            Position(2, 8),
                        ),
                        value=Number(
                            location=Location(
                                None,
                                Position(2, 7),
                                Position(2, 8),
                            ),
                            value=1,
                        ),
                    ),
                ],
            ),
            else_=expected_else_if,
        )

    def test_while_statement(self) -> None:
        parser = Parser("while 1 != 1 {}")
        statement = parser._statement()
        expected_comparison = Comparison(
            location=Location(
                None,
                start=Position(1, 7),
                end=Position(1, 13),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 12),
                    end=Position(1, 13),
                ),
                value=1,
            ),
            operator=ComparisonOperator.NOT_EQUAL,
        )
        assert statement == While(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 16),
            ),
            condition=expected_comparison,
            block=Block(
                location=Location(
                    None,
                    start=Position(1, 14),
                    end=Position(1, 16),
                ),
            ),
        )

    def teste_input_statement(self) -> None:
        parser = Parser("input x")
        statement = parser._statement()
        assert statement == Input(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 8),
            ),
            identifier=Identifier(
                location=Location(
                    None,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                name="x",
            ),
        )

    def test_print_statement_with_string(self) -> None:
        parser = Parser('print "hello"')
        statement = parser._statement()
        assert statement == Print(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 14),
            ),
            value=String(
                location=Location(
                    None,
                    start=Position(1, 7),
                    end=Position(1, 14),
                ),
                value="hello",
            ),
        )

    def test_print_statement_with_expression(self) -> None:
        parser = Parser("print 1 + 1")
        statement = parser._statement()
        expected_expression = BinaryExpression(
            location=Location(
                None,
                start=Position(1, 7),
                end=Position(1, 12),
            ),
            left=Number(
                location=Location(
                    None,
                    start=Position(1, 7),
                    end=Position(1, 8),
                ),
                value=1,
            ),
            right=Number(
                location=Location(
                    None,
                    start=Position(1, 11),
                    end=Position(1, 12),
                ),
                value=1,
            ),
            operator=ArithmeticOperator.ADD,
        )
        assert statement == Print(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 12),
            ),
            value=expected_expression,
        )

    def test_declaration_statement_with_value(self) -> None:
        parser = Parser("{let x = 1\n}")
        block = parser._block()
        expected_statement = Declaration(
            location=Location(
                None,
                start=Position(1, 2),
                end=Position(1, 11),
            ),
            identifier=Identifier(
                location=Location(
                    None,
                    start=Position(1, 6),
                    end=Position(1, 7),
                ),
                name="x",
            ),
            expression=Number(
                location=Location(
                    None,
                    start=Position(1, 10),
                    end=Position(1, 11),
                ),
                value=1,
            ),
        )
        assert block == Block(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(2, 2),
            ),
            statements=[expected_statement],
            symbol_table=SymbolTable(
                {
                    "x": Location(None, start=Position(1, 6), end=Position(1, 7)),
                },
            ),
        )

    def test_declaration_statement_without_value(self) -> None:
        parser = Parser("{let x\n}")
        block = parser._block()
        expected_statement = Declaration(
            location=Location(
                None,
                start=Position(1, 2),
                end=Position(1, 7),
            ),
            identifier=Identifier(
                location=Location(
                    None,
                    start=Position(1, 6),
                    end=Position(1, 7),
                ),
                name="x",
            ),
            expression=None,
        )
        assert block == Block(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(2, 2),
            ),
            statements=[expected_statement],
            symbol_table=SymbolTable(
                {
                    "x": Location(None, start=Position(1, 6), end=Position(1, 7)),
                },
            ),
        )

    def test_declaration_statement_missing_identifier(self) -> None:
        parser = Parser("{let\n}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_declaration_statement_missing_value(self) -> None:
        parser = Parser("{let x =\n}")
        with pytest.raises(TaipanSyntaxError):
            parser._block()

    def test_assignment_statement(self) -> None:
        parser = Parser("x = 1")
        statement = parser._statement()
        assert statement == Assignment(
            location=Location(
                None,
                start=Position(1, 1),
                end=Position(1, 6),
            ),
            identifier=Identifier(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 2),
                ),
                name="x",
            ),
            expression=Number(
                location=Location(
                    None,
                    start=Position(1, 5),
                    end=Position(1, 6),
                ),
                value=1,
            ),
        )

    def test_assignment_statement_missing_value(self) -> None:
        parser = Parser("x =")
        with pytest.raises(TaipanSyntaxError):
            parser._statement()

    def test_assignment_statement_operator(self) -> None:
        parser = Parser("x")
        with pytest.raises(TaipanSyntaxError):
            parser._statement()

    def test_statement_with_unknown_keyword(self) -> None:
        parser = Parser("unknown")
        with pytest.raises(TaipanSyntaxError):
            parser._statement()

    def test_program(self) -> None:
        parser = Parser("{}")
        program = parser._program()
        assert program == Program(
            block=Block(
                location=Location(
                    None,
                    start=Position(1, 1),
                    end=Position(1, 3),
                ),
            ),
        )

    def test_programm_with_empty_program(self) -> None:
        parser = Parser("")
        with pytest.raises(TaipanSyntaxError):
            parser._program()

    def test_programm_with_newlines(self) -> None:
        parser = Parser("\n\n\n")
        with pytest.raises(TaipanSyntaxError):
            parser._program()
