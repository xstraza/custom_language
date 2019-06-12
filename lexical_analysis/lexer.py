from lexical_analysis.token import Token
from lexical_analysis.token_type import *


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line_count = 1
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Neocekivani karakter {} | Linija {}'.format(self.current_char, self.line_count))

    def advance(self):
        self.pos += 1

        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def integer(self):
        number = ""
        while self.current_char is not None and self.current_char.isdigit():
            number += self.current_char
            self.advance()
        if self.current_char == '.':
            number += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                number += self.current_char
                self.advance()
            return Token(FLOAT, float(number))
        return Token(INTEGER, int(number))

    def string(self):
        result = '\''
        while self.current_char is not None and self.current_char != '\'':
            result += str(self.current_char)
            self.advance()
        result += '\''
        self.advance()
        return result

    def _id(self):
        result = ""
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()

        if result == 'TRU' or result == 'FLS':
            return Token(BOOL, result)
        if result == 'l':
            return Token(LENGTH, result)
        if result == 'o':
            return Token(RETURN, result)
        if result == 'f':
            return Token(FOR, result)
        if result == 'b':
            return Token(BREAK, result)
        if result == 'w':
            return Token(WHILE, result)
        if result == 'r':
            return Token(READ, result)
        if result == 'ps':
            return Token(PRINT_STRING, result)
        if result == 'pi':
            return Token(PRINT_INT, result)
        if result == 'u':
            return Token(IMPORT, result)
        if result == 'd':
            return Token(DEFINE, result)
        if result[0] == 'F':
            return Token(FUNCTION_NAME, result)
        if result[0] == 'V':
            return Token(VARIABLE_NAME, result)
        if result[0] == 'U':
            return Token(IMPORT_AS, result)

        return Token(NAME, result)

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line_count += 1
            self.advance()

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()

            # print('------')
            # print(self.current_char)
            # print('******')

            if self.current_char is None:
                return Token(EOF, None)

            if self.current_char.isdigit():
                return self.integer()

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == '?':
                self.advance()
                return Token(IF, '?')
            if self.current_char == ':':
                self.advance()
                return Token(ELSE, ':')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '{':
                self.advance()
                return Token(LCB, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RCB, '}')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    return Token('ARROW', '->')
                if self.current_char == '-':
                    self.advance()
                    if self.current_char == '>':
                        self.advance()
                        return Token(BLOCK_END, '-->')
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '%':
                self.advance()
                return Token(MOD, '%')

            if self.current_char == '/':
                self.advance()
                if self.current_char == '/':
                    self.advance()
                    return Token(NDIV, '//')
                return Token(DIV, '/')

            if self.current_char == '\'':
                self.advance()
                return Token(STRING, self.string())

            if self.current_char == '(':
                self.advance()
                return Token(LP, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RP, ')')

            if self.current_char == '[':
                self.advance()
                return Token(LSB, '[')

            if self.current_char == ']':
                self.advance()
                return Token(RSB, ']')

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LESS_EQ, '<=')
                if self.current_char == '-':
                    self.advance()
                    if self.current_char == '-':
                        self.advance()
                        return Token(BLOCK_BEGIN, '<--')
                return Token(LESS, '<')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GREATER_EQ, '>=')
                return Token(GREATER, '>')

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQUAL, '==')
                self.error()

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NOT_EQUAL, '!=')
                return Token(NOT, '!')

            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token('AND', 'and')
                self.error()

            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token('OR', 'or')
                self.error()

            self.error()

        return Token(EOF, None)
