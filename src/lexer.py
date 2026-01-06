import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()
    
    # Keywords
    ENERGY = auto()
    STABLE = auto()
    STABILIZE = auto()
    DECLARE = auto()
    FN = auto()
    PURE = auto()
    UNSTABLE = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    PRINT = auto()
    INSPECT = auto()
    QUERY = auto()
    INVARIANT = auto()
    ASSERT = auto()
    REMOVE = auto()
    
    # Operators
    ASSIGN = auto()         # <-
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %
    EQ = auto()             # ==
    NEQ = auto()            # !=
    LT = auto()             # <
    GT = auto()             # >
    LTE = auto()            # <=
    GTE = auto()            # >=
    AND = auto()            # and
    OR = auto()             # or
    NOT = auto()            # not
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    COMMA = auto()          # ,
    QUESTION = auto()       # ?
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        self.keywords = {
            'energy': TokenType.ENERGY,
            'stable': TokenType.STABLE,
            'stabilize': TokenType.STABILIZE,
            'declare': TokenType.DECLARE,
            'fn': TokenType.FN,
            'pure': TokenType.PURE,
            'unstable': TokenType.UNSTABLE,
            'return': TokenType.RETURN,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'print': TokenType.PRINT,
            'inspect': TokenType.INSPECT,
            'query': TokenType.QUERY,
            'invariant': TokenType.INVARIANT,
            'assert': TokenType.ASSERT,
            'remove': TokenType.REMOVE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
        }
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset=1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#' and self.peek_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        start_col = self.column
        num_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        value = float(num_str) if has_dot else int(num_str)
        return Token(TokenType.NUMBER, value, self.line, start_col)
    
    def read_identifier(self) -> Token:
        start_col = self.column
        id_str = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()
        
        token_type = self.keywords.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str, self.line, start_col)
    
    def read_string(self) -> Token:
        start_col = self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string_val = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() in 'ntr"\'\\':
                    escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'", '\\': '\\'}
                    string_val += escape_chars.get(self.current_char(), self.current_char())
                    self.advance()
            else:
                string_val += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, string_val, self.line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.current_char() is not None:
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            # Comments
            if self.current_char() == '#' and self.peek_char() == '#':
                self.skip_comment()
                continue
            
            # Newlines
            if self.current_char() == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.tokens.append(token)
                self.advance()
                continue
            
            # Numbers
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Strings
            if self.current_char() in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Two-character operators
            start_col = self.column
            char = self.current_char()
            next_char = self.peek_char()
            
            if char == '<' and next_char == '-':
                self.tokens.append(Token(TokenType.ASSIGN, '<-', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '=' and next_char == '=':
                self.tokens.append(Token(TokenType.EQ, '==', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '!' and next_char == '=':
                self.tokens.append(Token(TokenType.NEQ, '!=', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '<' and next_char == '=':
                self.tokens.append(Token(TokenType.LTE, '<=', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            if char == '>' and next_char == '=':
                self.tokens.append(Token(TokenType.GTE, '>=', self.line, start_col))
                self.advance()
                self.advance()
                continue
            
            # Single-character tokens
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.STAR,
                '/': TokenType.SLASH,
                '%': TokenType.PERCENT,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ',': TokenType.COMMA,
                '?': TokenType.QUESTION,
            }
            
            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, self.line, start_col))
                self.advance()
                continue
            
            # Unknown character
            raise SyntaxError(f"Unknown character '{char}' at line {self.line}, column {self.column}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens