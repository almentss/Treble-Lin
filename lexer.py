# lexer.py
import sys

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', {self.literal}, line {self.line})"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.had_error = False 

        self.token_types = {
            '(': "LEFT_PAREN", ')': "RIGHT_PAREN",
            '{': "LEFT_BRACE", '}': "RIGHT_BRACE",
            '[': "LEFT_BRACKET", ']': "RIGHT_BRACKET",
            ',': "COMMA", '.': "DOT", '-': "MINUS", '+': "PLUS",
            ';': "SEMICOLON", '*': "STAR", '/': "SLASH",'%': "MODULO",

            '!': "BANG", '!=': "BANG_EQUAL",
            '=': "EQUAL", '==': "EQUAL_EQUAL",
            '<': "LESS", '<=': "LESS_EQUAL",
            '>': "GREATER", '>=': "GREATER_EQUAL",
        }

        self.keywords = {
            "and": "LOGICAL_AND",
            "class": "CLASS",  # Not implemented yet but good to have
            "else": "ELSE",
            "false": "FALSE",
            "for": "FOR",
            "fun": "FUN",
            "if": "IF",
            "nil": "NIL",
            "or": "LOGICAL_OR",
            "return": "RETURN",
            "super": "SUPER", # Not implemented yet
            "this": "THIS",   # Not implemented yet
            "true": "TRUE",
            "let": "VAR", 
            "while": "WHILE",
            "break": "BREAK",
            "continue": "CONTINUE",
            "try": "TRY",
            "catch": "CATCH",
            "not": "LOGICAL_NOT",
        }

    def scan_tokens(self):
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens

    def _is_at_end(self):
        return self.current >= len(self.source)

    def _advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def _peek(self):
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _match(self, expected):
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def _error(self, line, message):
        print(f"[line {line}] Error: {message}", file=sys.stderr)
        self.had_error = True

    def _scan_token(self):
        char = self._advance()
        if char == '(': self._add_token("LEFT_PAREN")
        elif char == ')': self._add_token("RIGHT_PAREN")
        elif char == '{': self._add_token("LEFT_BRACE")
        elif char == '}': self._add_token("RIGHT_BRACE")
        elif char == '[': self._add_token("LEFT_BRACKET")
        elif char == ']': self._add_token("RIGHT_BRACKET")
        elif char == ',': self._add_token("COMMA")
        elif char == ';': self._add_token("SEMICOLON")
        elif char == '+': self._add_token("PLUS")
        elif char == '-': self._add_token("MINUS")
        elif char == '*': self._add_token("STAR")
        elif char == '%': self._add_token("MODULO")
        elif char == '.': self._add_token("DOT")
        elif char == '/':
            if self._match('/'): 
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            elif self._match('*'):
                self._multi_line_comment()
            else:
                self._add_token("SLASH")
        elif char == '!':
            self._add_token("BANG_EQUAL" if self._match('=') else "BANG")
        elif char == '=':
            self._add_token("EQUAL_EQUAL" if self._match('=') else "EQUAL")
        elif char == '<':
            self._add_token("LESS_EQUAL" if self._match('=') else "LESS")
        elif char == '>':
            self._add_token("GREATER_EQUAL" if self._match('=') else "GREATER")
        elif char == '"':
            self._string()
        elif char.isdigit():
            self._number()
        elif char.isalpha() or char == '_':
            self._identifier()
        elif char in [' ', '\r', '\t']:
            pass 
        elif char == '\n':
            self.line += 1
        else:
            self._error(self.line, f"Unexpected character '{char}'.")

    def _string(self):
        is_escaping = False
        parsed_value = []

        while self._peek() != '"' and not self._is_at_end():
            char = self._advance()

            if is_escaping:
                if char == 'n':
                    parsed_value.append('\n')
                elif char == 't':
                    parsed_value.append('\t')
                elif char == '\\':
                    parsed_value.append('\\')
                elif char == '"': 
                    parsed_value.append('"')
                else:
                    parsed_value.append('\\')
                    parsed_value.append(char)
                is_escaping = False
            elif char == '\\':
                is_escaping = True
            else:
                parsed_value.append(char)

            if self._peek() == '\n': 
                self.line += 1

        if self._is_at_end():
            print(f"Error at line {self.line}: Unterminated string.", file=sys.stderr)
            self.had_error = True
            return

        self._advance() 

        value = "".join(parsed_value)
        self._add_token("STRING", value)

    def _number(self):
        while self._peek().isdigit():
            self._advance()

        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance() 
            while self._peek().isdigit():
                self._advance()

        value = float(self.source[self.start:self.current]) if '.' in self.source[self.start:self.current] else int(self.source[self.start:self.current])
        self._add_token("NUMBER", value)

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, "IDENTIFIER")
        literal = None
        if token_type == "TRUE": literal = True
        elif token_type == "FALSE": literal = False
        elif token_type == "NIL": literal = None
        self._add_token(token_type, literal)

    def _multi_line_comment(self):
        while not (self._peek() == '*' and self._peek_next() == '/') and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()

        if self._is_at_end():
            self._error(self.line, "Unterminated multi-line comment.")
            return

        self._advance() 
        self._advance()
