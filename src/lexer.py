# src/lexer.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()

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

    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()

    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Optional[str]
    line: int
    column: int


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

    def peek_char(self) -> Optional[str]:
        nxt = self.pos + 1
        if nxt >= len(self.source):
            return None
        return self.source[nxt]

    def advance(self) -> None:
        ch = self.current_char()
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1

    def tokenize(self) -> List[Token]:
        while True:
            ch = self.current_char()
            if ch is None:
                break

            if ch in ' \t\r':
                self.advance()
                continue

            if ch == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, None, self.line, self.column))
                self.advance()
                continue

            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue

            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier())
                continue

            if ch in ('"', "'"):
                self.tokens.append(self.read_string())
                continue

            start_col = self.column
            nxt = self.peek_char()

            if ch == '<' and nxt == '-':
                self.tokens.append(Token(TokenType.ASSIGN, '<-', self.line, start_col))
                self.advance()
                self.advance()
                continue

            single = {
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
            }

            if ch in single:
                self.tokens.append(Token(single[ch], ch, self.line, start_col))
                self.advance()
                continue

            raise SyntaxError(f"Unknown character '{ch}' at {self.line}:{self.column}")

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def read_number(self) -> Token:
        start = self.column
        num = ''
        ch = self.current_char()

        while ch is not None and (ch.isdigit() or ch == '.'):
            num += ch
            self.advance()
            ch = self.current_char()

        return Token(TokenType.NUMBER, num, self.line, start)

    def read_identifier(self) -> Token:
        start = self.column
        ident = ''
        ch = self.current_char()

        while ch is not None and (ch.isalnum() or ch == '_'):
            ident += ch
            self.advance()
            ch = self.current_char()

        token_type = self.keywords.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, self.line, start)

    def read_string(self) -> Token:
        start = self.column
        quote = self.current_char()
        self.advance()

        val = ''
        ch = self.current_char()
        while ch is not None and ch != quote:
            val += ch
            self.advance()
            ch = self.current_char()

        if self.current_char() == quote:
            self.advance()

        return Token(TokenType.STRING, val, self.line, start)
