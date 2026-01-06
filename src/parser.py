from typing import List, Optional
from src.lexer import Token, TokenType, Lexer
from src.ast_nodes import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def peek_token(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> None:
        if self.pos < len(self.tokens) - 1:
            self.pos += 1

    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name}, got {token.type.name} "
                f"at line {token.line}, column {token.column}"
            )
        self.advance()
        return token

    def skip_newlines(self) -> None:
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()

    def parse(self) -> Program:
        statements: List[ASTNode] = []
        self.skip_newlines()

        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()

        return Program(statements)

    # ---------------- STATEMENTS ----------------

    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        token = self.current_token()

        if token.type == TokenType.ENERGY:
            return self.parse_energy_decl()
        elif token.type == TokenType.STABLE:
            return self.parse_stable_assignment()
        elif token.type == TokenType.STABILIZE:
            return self.parse_stabilize()
        elif token.type == TokenType.DECLARE:
            return self.parse_function_decl()
        elif token.type == TokenType.RETURN:
            return self.parse_return()
        elif token.type == TokenType.PRINT:
            return self.parse_print()
        elif token.type == TokenType.INSPECT:
            return self.parse_inspect()
        elif token.type == TokenType.QUERY:
            return self.parse_query_energy()
        elif token.type == TokenType.INVARIANT:
            return self.parse_invariant()
        elif token.type == TokenType.ASSERT:
            return self.parse_assert()
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.FOR:
            return self.parse_for()
        elif token.type == TokenType.REMOVE:
            return self.parse_remove()
        elif token.type == TokenType.IDENTIFIER:
            if self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
            elif self.peek_token().type == TokenType.LPAREN:
                return self.parse_expression()
            else:
                raise SyntaxError(f"Unexpected identifier at line {token.line}")
        else:
            raise SyntaxError(f"Unexpected token {token.type.name} at line {token.line}")

    def parse_energy_decl(self) -> EnergyDecl:
        self.expect(TokenType.ENERGY)
        self.expect(TokenType.LBRACKET)
        amount_token = self.expect(TokenType.NUMBER)
        assert amount_token.value is not None
        self.expect(TokenType.RBRACKET)
        return EnergyDecl(int(amount_token.value))

    def parse_stable_assignment(self) -> Assignment:
        self.expect(TokenType.STABLE)
        name_token = self.expect(TokenType.IDENTIFIER)
        assert name_token.value is not None
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name_token.value, value, is_stable=True)

    def parse_assignment(self) -> Assignment:
        name_token = self.expect(TokenType.IDENTIFIER)
        assert name_token.value is not None
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name_token.value, value, is_stable=False)

    def parse_stabilize(self) -> Stabilize:
        self.expect(TokenType.STABILIZE)
        name_token = self.expect(TokenType.IDENTIFIER)
        assert name_token.value is not None
        return Stabilize(name_token.value)

    def parse_function_decl(self) -> FunctionDecl:
        self.expect(TokenType.DECLARE)

        is_pure = False
        is_unstable = False

        if self.current_token().type == TokenType.PURE:
            is_pure = True
            self.advance()
        elif self.current_token().type == TokenType.UNSTABLE:
            is_unstable = True
            self.advance()

        self.expect(TokenType.FN)
        name_token = self.expect(TokenType.IDENTIFIER)
        assert name_token.value is not None

        self.expect(TokenType.LPAREN)
        params: List[str] = []
        while self.current_token().type != TokenType.RPAREN:
            param = self.expect(TokenType.IDENTIFIER)
            assert param.value is not None
            params.append(param.value)
            if self.current_token().type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)

        self.expect(TokenType.LBRACE)
        self.skip_newlines()

        body: List[ASTNode] = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect(TokenType.RBRACE)
        return FunctionDecl(name_token.value, params, body, is_pure, is_unstable)

    def parse_return(self) -> Return:
        self.expect(TokenType.RETURN)
        if self.current_token().type in (TokenType.NEWLINE, TokenType.RBRACE):
            return Return(None)
        return Return(self.parse_expression())

    def parse_print(self) -> Print:
        self.expect(TokenType.PRINT)
        return Print(self.parse_expression())

    def parse_inspect(self) -> Inspect:
        self.expect(TokenType.INSPECT)
        return Inspect(self.parse_expression())

    def parse_query_energy(self) -> QueryEnergy:
        self.expect(TokenType.QUERY)
        self.expect(TokenType.ENERGY)
        return QueryEnergy()

    def parse_invariant(self) -> Invariant:
        self.expect(TokenType.INVARIANT)
        return Invariant(self.parse_expression())

    def parse_assert(self) -> Assert:
        self.expect(TokenType.ASSERT)
        return Assert(self.parse_expression())

    def parse_if(self) -> If:
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()

        then_block: List[ASTNode] = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
            self.skip_newlines()

        self.expect(TokenType.RBRACE)
        return If(condition, then_block)

    def parse_while(self) -> While:
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()

        body: List[ASTNode] = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect(TokenType.RBRACE)
        return While(condition, body)

    def parse_for(self) -> For:
        self.expect(TokenType.FOR)
        var_token = self.expect(TokenType.IDENTIFIER)
        assert var_token.value is not None
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()

        body: List[ASTNode] = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect(TokenType.RBRACE)
        return For(var_token.value, iterable, body)

    def parse_remove(self) -> Remove:
        self.expect(TokenType.REMOVE)
        self.expect(TokenType.LBRACKET)
        cap = self.expect(TokenType.IDENTIFIER)
        assert cap.value is not None
        self.expect(TokenType.RBRACKET)
        return Remove(cap.value)

    # ---------------- EXPRESSIONS ----------------

    def parse_expression(self) -> ASTNode:
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        left = self.parse_and()
        while self.current_token().type == TokenType.OR:
            tok = self.current_token()
            assert tok.value is not None
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, tok.value, right)
        return left

    def parse_and(self) -> ASTNode:
        left = self.parse_comparison()
        while self.current_token().type == TokenType.AND:
            tok = self.current_token()
            assert tok.value is not None
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, tok.value, right)
        return left

    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        while self.current_token().type in (
            TokenType.EQ, TokenType.NEQ,
            TokenType.LT, TokenType.GT,
            TokenType.LTE, TokenType.GTE
        ):
            tok = self.current_token()
            assert tok.value is not None
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, tok.value, right)
        return left

    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            tok = self.current_token()
            assert tok.value is not None
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, tok.value, right)
        return left

    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()
        while self.current_token().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            tok = self.current_token()
            assert tok.value is not None
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, tok.value, right)
        return left

    def parse_unary(self) -> ASTNode:
        if self.current_token().type in (TokenType.MINUS, TokenType.NOT):
            tok = self.current_token()
            assert tok.value is not None
            self.advance()
            return UnaryOp(tok.value, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        tok = self.current_token()

        if tok.type == TokenType.NUMBER:
            assert tok.value is not None
            self.advance()
            return Number(float(tok.value))

        if tok.type == TokenType.STRING:
            assert tok.value is not None
            self.advance()
            return String(tok.value)

        if tok.type == TokenType.IDENTIFIER:
            assert tok.value is not None
            name = tok.value
            self.advance()

            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                args: List[ASTNode] = []
                while self.current_token().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    if self.current_token().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, args)

            return Identifier(name)

        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Unexpected token {tok.type.name} at line {tok.line}")


def parse(source: str) -> Program:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    return Parser(tokens).parse()
