from typing import List, Optional
from lexer import Token, TokenType, Lexer
from ast_nodes import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def peek_token(self, offset=1) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self):
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
    
    def skip_newlines(self):
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        statements = []
        self.skip_newlines()
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
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
            # Could be assignment or function call
            if self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
            elif self.peek_token().type == TokenType.LPAREN:
                return self.parse_expression()  # Function call as statement
            else:
                raise SyntaxError(f"Unexpected identifier at line {token.line}")
        else:
            raise SyntaxError(f"Unexpected token {token.type.name} at line {token.line}")
    
    def parse_energy_decl(self) -> EnergyDecl:
        self.expect(TokenType.ENERGY)
        self.expect(TokenType.LBRACKET)
        amount_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.RBRACKET)
        return EnergyDecl(int(amount_token.value))
    
    def parse_stable_assignment(self) -> Assignment:
        self.expect(TokenType.STABLE)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name_token.value, value, is_stable=True)
    
    def parse_assignment(self) -> Assignment:
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name_token.value, value, is_stable=False)
    
    def parse_stabilize(self) -> Stabilize:
        self.expect(TokenType.STABILIZE)
        name_token = self.expect(TokenType.IDENTIFIER)
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
        
        self.expect(TokenType.LPAREN)
        params = []
        while self.current_token().type != TokenType.RPAREN:
            param_token = self.expect(TokenType.IDENTIFIER)
            params.append(param_token.value)
            if self.current_token().type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return FunctionDecl(name_token.value, params, body, is_pure, is_unstable)
    
    def parse_return(self) -> Return:
        self.expect(TokenType.RETURN)
        if self.current_token().type in [TokenType.NEWLINE, TokenType.RBRACE]:
            return Return(None)
        value = self.parse_expression()
        return Return(value)
    
    def parse_print(self) -> Print:
        self.expect(TokenType.PRINT)
        value = self.parse_expression()
        return Print(value)
    
    def parse_inspect(self) -> Inspect:
        self.expect(TokenType.INSPECT)
        value = self.parse_expression()
        return Inspect(value)
    
    def parse_query_energy(self) -> QueryEnergy:
        self.expect(TokenType.QUERY)
        self.expect(TokenType.ENERGY)
        return QueryEnergy()
    
    def parse_invariant(self) -> Invariant:
        self.expect(TokenType.INVARIANT)
        condition = self.parse_expression()
        return Invariant(condition)
    
    def parse_assert(self) -> Assert:
        self.expect(TokenType.ASSERT)
        condition = self.parse_expression()
        return Assert(condition)
    
    def parse_if(self) -> If:
        is_stable = False
        
        if self.current_token().type == TokenType.STABLE:
            is_stable = True
            self.advance()
        
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        then_block = []
        while self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        else_block = None
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.LBRACE)
            self.skip_newlines()
            
            else_block = []
            while self.current_token().type != TokenType.RBRACE:
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
                self.skip_newlines()
            
            self.expect(TokenType.RBRACE)
        
        return If(condition, then_block, else_block, is_stable)
    
    def parse_while(self) -> While:
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
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
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
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
        capability_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.RBRACKET)
        return Remove(capability_token.value)
    
    def parse_expression(self) -> ASTNode:
        return self.parse_or()
    
    def parse_or(self) -> ASTNode:
        left = self.parse_and()
        
        while self.current_token().type == TokenType.OR:
            op = self.current_token().value
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_and(self) -> ASTNode:
        left = self.parse_comparison()
        
        while self.current_token().type == TokenType.AND:
            op = self.current_token().value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        
        while self.current_token().type in [TokenType.EQ, TokenType.NEQ, 
                                            TokenType.LT, TokenType.GT,
                                            TokenType.LTE, TokenType.GTE]:
            op = self.current_token().value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        
        while self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token().value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()
        
        while self.current_token().type in [TokenType.STAR, TokenType.SLASH, TokenType.PERCENT]:
            op = self.current_token().value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        if self.current_token().type in [TokenType.MINUS, TokenType.NOT]:
            op = self.current_token().value
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> ASTNode:
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return Number(token.value)
        
        elif token.type == TokenType.STRING:
            self.advance()
            return String(token.value)
        
        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.advance()
            
            # Function call
            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.current_token().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    if self.current_token().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, args)
            
            # Just an identifier
            return Identifier(name)
        
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        else:
            raise SyntaxError(f"Unexpected token {token.type.name} at line {token.line}")


def parse(source: str) -> Program:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()