from .ast import (
    AST,
    ArithmeticOperatorKind,
    ArithmeticOperatorNode,
    AssignmentNode,
    ComparaisonNode,
    ComparaisonOperatorKind,
    ComparaisonOperatorNode,
    ExpressionNode,
    IdentifierNode,
    KeywordKind,
    KeywordNode,
    LiteralKind,
    LiteralNode,
    Node,
    UnaryOperatorKind,
    UnaryOperatorNode,
)
from .lexer import Lexer, Token, TokenKind


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = Token(kind=TokenKind.EOF)
        self.peek_token = Token(kind=TokenKind.EOF)
        self.next_token()
        self.next_token()

    def parse(self) -> AST:
        ast = AST()
        self.program(ast.root)
        return ast

    def match_token(self, token_kind: TokenKind) -> None:
        if self.current_token.kind != token_kind:
            raise ParserError(f"Expected {token_kind}, got {self.current_token.kind}")
        self.next_token()

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def program(self, parent: Node) -> None:
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()

        while self.current_token.kind != TokenKind.EOF:
            self.statement(parent)

    def comparaison(self, parent: Node) -> None:
        comparaison_node = ComparaisonNode()
        parent.childrens.append(comparaison_node)

        self.expression(comparaison_node)
        kind = ComparaisonOperatorKind.from_token_kind(self.current_token.kind)
        if kind is None:
            raise ParserError(f"Expected comparaison operator, got {self.current_token.kind}")
        comparaison_node.childrens.append(ComparaisonOperatorNode(kind=kind))

        self.next_token()
        self.expression(comparaison_node)

        while kind := ComparaisonOperatorKind.from_token_kind(self.current_token.kind):
            node = ComparaisonOperatorNode(kind=kind)
            comparaison_node.childrens.append(node)

            self.next_token()
            self.expression(node)

    def expression(self, parent: Node) -> None:
        node = ExpressionNode()
        parent.childrens.append(node)

        self.term(node)
        while True:
            match self.current_token.kind:
                case TokenKind.PLUS:
                    kind = ArithmeticOperatorKind.ADD
                case TokenKind.MINUS:
                    kind = ArithmeticOperatorKind.SUBSTRACT
                case _:
                    break
            node.childrens.append(ArithmeticOperatorNode(kind=kind))

            self.next_token()
            self.term(node)

    def term(self, parent: Node) -> None:
        self.unary(parent)
        while True:
            match self.current_token.kind:
                case TokenKind.MULTIPLICATION:
                    kind = ArithmeticOperatorKind.MULTIPLY
                case TokenKind.DIVISION:
                    kind = ArithmeticOperatorKind.DIVIDE
                case TokenKind.MODULO:
                    kind = ArithmeticOperatorKind.MODULO
                case _:
                    break
            parent.childrens.append(ArithmeticOperatorNode(kind=kind))

            self.next_token()
            self.unary(parent)

    def unary(self, parent: Node) -> None:
        kind = UnaryOperatorKind.from_token_kind(self.current_token.kind)
        if kind is not None:
            parent.childrens.append(UnaryOperatorNode(kind=kind))
            self.next_token()

        self.literal(parent)

    def literal(self, parent: Node) -> None:
        match self.current_token.kind:
            case TokenKind.NUMBER:
                assert isinstance(self.current_token.value, float)
                parent.childrens.append(
                    LiteralNode(kind=LiteralKind.NUMBER, value=self.current_token.value)
                )
            case TokenKind.IDENTIFIER:
                assert isinstance(self.current_token.value, str)
                parent.childrens.append(IdentifierNode(name=self.current_token.value))
            case _:
                raise ParserError(f"Expected literal expression, got {self.current_token.kind}")
        self.next_token()

    def print_statement(self, parent: Node) -> None:
        node = KeywordNode(kind=KeywordKind.PRINT)
        parent.childrens.append(node)

        self.next_token()
        match self.current_token.kind:
            case TokenKind.STRING:
                assert isinstance(self.current_token.value, str)
                node.childrens.append(
                    LiteralNode(kind=LiteralKind.STRING, value=self.current_token.value)
                )
                self.next_token()
            case _:
                self.expression(node)

    def if_statement(self, parent: Node) -> None:
        node = KeywordNode(kind=KeywordKind.IF)
        parent.childrens.append(node)

        self.next_token()
        self.comparaison(node)

        self.match_token(TokenKind.OPEN_BRACE)
        self.next_token()

        while self.current_token.kind != TokenKind.CLOSE_BRACE:
            self.statement(node)
        self.next_token()

    def while_statement(self, parent: Node) -> None:
        node = KeywordNode(kind=KeywordKind.WHILE)
        parent.childrens.append(node)

        self.next_token()
        self.comparaison(node)

        self.match_token(TokenKind.OPEN_BRACE)
        while self.current_token.kind != TokenKind.CLOSE_BRACE:
            self.statement(node)
        self.next_token()

    def input_statement(self, parent: Node) -> None:
        node = KeywordNode(kind=KeywordKind.INPUT)
        parent.childrens.append(node)
        self.next_token()

        if self.current_token.kind != TokenKind.IDENTIFIER:
            raise ParserError(f"Expected identifier, got {self.current_token.kind}")
        assert isinstance(self.current_token.value, str)
        node.childrens.append(IdentifierNode(name=self.current_token.value))
        self.next_token()

    def assignment_statement(self, parent: Node) -> None:
        node = AssignmentNode()
        parent.childrens.append(node)

        assert isinstance(self.current_token.value, str)
        node.childrens.append(IdentifierNode(name=self.current_token.value))
        self.next_token()

        self.match_token(TokenKind.ASSIGNMENT)
        self.expression(node)

    def statement(self, parent: Node) -> None:
        match self.current_token.kind:
            case TokenKind.PRINT:
                self.print_statement(parent)
            case TokenKind.IF:
                self.if_statement(parent)
            case TokenKind.WHILE:
                self.while_statement(parent)
            case TokenKind.INPUT:
                self.input_statement(parent)
            case TokenKind.IDENTIFIER:
                self.assignment_statement(parent)
            case _:
                raise ParserError(f"Unknown statement: {self.current_token.kind}")

    def nl(self) -> None:
        self.match_token(TokenKind.NEWLINE)
        while self.current_token.kind == TokenKind.NEWLINE:
            self.next_token()
