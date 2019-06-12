from lexical_analysis.token_type import *
from syntax_analysis.interpreter_marko import *
from syntax_analysis.util import restorable


class Parser(object):
    def parse(self):
        return self.program()

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, expected, found):
        raise Exception(
            'Greska u parsiranju, nadjeno {}, ocekivano {}\nLinija {}'.format(found, expected, self.lexer.line_count))

    def eat(self, type):
        if self.current_token.type == type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(type, self.current_token.type)

    def program(self):
        sections = []

        while self.current_token.type == IMPORT:
            sections.append(self.library())
        while self.current_token.type == DEFINE:
            sections.append(self.f_declaration())
        sections.append(self.line_list())

        return Program(self.lexer.line_count, sections)

    def library(self):
        self.eat(IMPORT)
        self.eat(LCB)
        local_name = self.current_token.value
        self.eat(IMPORT_AS)
        self.eat(LCB)
        lib_name = self.current_token.value
        self.eat(NAME)
        self.eat(LCB)
        f_name = self.current_token.value
        self.eat(NAME)
        self.eat(RCB)
        self.eat(RCB)
        self.eat(RCB)
        return Library(self.lexer.line_count, local_name, lib_name, f_name)

    def f_declaration(self):
        self.eat(DEFINE)
        self.eat(LCB)
        f_name = self.current_token.value
        self.eat(FUNCTION_NAME)
        self.eat(LCB)
        param_list = ParamList(self.lexer.line_count, self.param_list())
        self.eat(RCB)
        self.eat(RCB)
        self.eat(BLOCK_BEGIN)
        # f_body = LineList(self.line_list())
        f_body = self.line_list()
        self.eat(BLOCK_END)
        return Fdeclaration(self.lexer.line_count, f_name, param_list, f_body)

    def while_statement(self):
        self.eat(WHILE)
        self.eat(LCB)
        condition = self.bool_expr()
        self.eat(RCB)
        self.eat(BLOCK_BEGIN)
        # w_body = LineList(self.line_list())
        w_body = self.line_list()
        self.eat(BLOCK_END)
        return WhileStatement(self.lexer.line_count, condition, w_body)

    def for_statement(self):
        self.eat(FOR)
        self.eat(LCB)
        var = self.var()
        self.eat(LCB)
        start = self.expr()
        self.eat(ARROW)
        stop = self.expr()
        self.eat(RCB)
        self.eat(RCB)
        self.eat(BLOCK_BEGIN)
        f_body = self.line_list()
        if len(f_body) < 1:
            raise Exception("For ne sme biti prazan")
        self.eat(BLOCK_END)
        return ForStatement(self.lexer.line_count, var, start, stop, f_body)

    def if_statement(self):
        self.eat(IF)
        self.eat(LCB)
        condition = self.bool_expr()
        self.eat(RCB)
        self.eat(BLOCK_BEGIN)
        if_body = self.line_list()
        if len(if_body) < 1:
            raise Exception("If blok ne sme biti prazan")
        self.eat(BLOCK_END)
        els = None
        if self.current_token.type == ELSE:
            els = self.else_statement()
        return IfStatement(self.lexer.line_count, condition, if_body, elsee=els)

    def else_statement(self):
        self.eat(ELSE)
        self.eat(LCB)
        condition = None
        if self.current_token.type != RCB:
            condition = self.bool_expr()
        self.eat(RCB)
        self.eat(BLOCK_BEGIN)
        # body = LineList(self.line_list())
        body = self.line_list()
        self.eat(BLOCK_END)
        return ElseStatement(self.lexer.line_count, body, condition=condition)

    def line_list(self):
        lines = []
        while self.current_token.type in [LENGTH, RETURN, READ, PRINT_STRING,
                                          PRINT_INT, FUNCTION_NAME, IMPORT_AS, VARIABLE_NAME, IF, FOR, WHILE, BREAK]:
            if self.current_token.type == BREAK:
                lines.append(Break(self.lexer.line_count))
                self.eat(BREAK)
            elif self.current_token.type == FOR:
                lines.append(self.for_statement())
            elif self.current_token.type == WHILE:
                lines.append(self.while_statement())
            elif self.current_token.type == IF:
                lines.append(self.if_statement())
            elif self.current_token.type == VARIABLE_NAME:
                lines.append(self.var_assignment())
            elif self.current_token.type == FUNCTION_NAME:
                lines.append(self.user_f())
            elif self.current_token.type == RETURN:
                lines.append(self.defined_f())
            else:
                lines.append(self.f_call())
        return lines

    def f_call(self):
        if self.current_token.type == FUNCTION_NAME:
            return self.user_f()
        elif self.current_token.type == IMPORT_AS:
            return self.import_f()
        else:
            return self.defined_f()

    def user_f(self):
        name = self.current_token.value
        self.eat(FUNCTION_NAME)
        self.eat(LCB)
        args = self.args()
        self.eat(RCB)
        return UserFCall(self.lexer.line_count, name, args)

    def import_f(self):
        local_name = self.current_token.value
        self.eat(IMPORT_AS)
        self.eat(DOT)
        f_name = self.current_token.value
        self.eat(NAME)
        self.eat(LCB)
        args = self.args()
        self.eat(RCB)
        return ImportedFCall(self.lexer.line_count, local_name, f_name, args)

    def defined_f(self):
        type = self.current_token.type
        self.eat(type)
        self.eat(LCB)
        args = self.args()
        self.eat(RCB)
        return DefinedFCall(self.lexer.line_count, type, args)

    def args(self):
        args = []
        while self.current_token.type != RCB:
            if self.is_bool_expr():
                args.append(self.bool_expr())
            else:
                args.append(self.expr())
            if self.current_token.type == COMMA:
                self.eat(COMMA)
        return args

    def param_list(self):
        params = []
        while self.current_token.type != RCB:
            params.append(self.var())
            if self.current_token.type == COMMA:
                self.eat(COMMA)
        return params

    def value(self):
        if self.current_token.type == STRING:
            string = self.current_token.value
            self.eat(STRING)
            return Value(self.lexer.line_count, STRING, string)
        if self.current_token.type == BOOL:
            boole = self.current_token.value
            self.eat(BOOL)
            return Value(self.lexer.line_count, BOOL, boole)
        if self.current_token.type == INTEGER:
            integer = self.current_token.value
            self.eat(INTEGER)
            return Value(self.lexer.line_count, INTEGER, integer)

    def var(self):
        if self.current_token.type == VARIABLE_NAME:
            name = self.current_token.value
            self.eat(VARIABLE_NAME)
            indeks = -1
            if self.current_token.type == LSB:
                self.eat(LSB)
                indeks = self.expr()
                self.eat(RSB)
            return Var(self.lexer.line_count, name, indeks=indeks)

    def var_assignment(self):
        var = self.var()
        self.eat(LCB)
        val = None
        if self.is_bool_expr():
            val = self.bool_expr()
        else:
            val = self.expr()
        self.eat(RCB)
        return VarAssignment(self.lexer.line_count, var, val)

    def factor(self):
        token = self.current_token
        if token.type == MINUS:
            self.eat(MINUS)
            return UnOp(self.lexer.line_count, self.expr())
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Value(self.lexer.line_count, token.type, token.value)
        if token.type == FLOAT:
            self.eat(FLOAT)
            return Value(self.lexer.line_count, token.type, token.value)
        if token.type == STRING:
            self.eat(STRING)
            return Value(self.lexer.line_count, token.type, token.value)
        if token.type == BOOL:
            self.eat(BOOL)
            return Value(self.lexer.line_count, token.type, token.value)
        if token.value == '[':
            self.eat(LSB)
            self.eat(RSB)
            return Value(self.lexer.line_count, LIST, [])
        elif token.type == VARIABLE_NAME:
            return self.var()
        elif token.type in [LENGTH, RETURN, READ, PRINT_STRING,
                            PRINT_INT, FUNCTION_NAME, IMPORT_AS, VARIABLE_NAME, IF, FOR, WHILE, BREAK]:
            return self.f_call()
        elif token.type == LP:
            self.eat(LP)
            node = None

            if self.is_bool_expr():
                node = self.bool_expr()
            else:
                node = self.expr()
            self.eat(RP)
            return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV, NDIV, MOD):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            elif token.type == NDIV:
                self.eat(NDIV)
            elif token.type == MOD:
                self.eat(MOD)
            else:
                self.error('*, /, // or %', token.type)
            node = BinOp(self.lexer.line_count, left=node, op=token, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            else:
                self.error('+ or -', self.current_token.type)
            node = BinOp(self.lexer.line_count, left=node, op=token, right=self.expr())
        return node

    def bool_expr(self):
        return self.bool_comparison_expr()

    def bool_comparison_expr(self):
        left = self.expr()
        op = self.current_token
        if op.type in [LESS, LESS_EQ, GREATER, GREATER_EQ, EQUAL, NOT_EQUAL, AND, OR]:
            self.eat(op.type)
        else:
            return self.error(RCB, op.type)
        right = self.expr()
        return BinOp(self.lexer.line_count, left, op, right)

    def bool_logical_expr(self):
        if self.current_token.type == NOT:
            node = self.unar_expr()
        else:
            node = self.bool_comparison_expr()

        while self.current_token.type in (AND, OR):
            token = self.current_token
            self.eat(self.current_token.type)

            if self.current_token.type == NOT:
                un_token = self.current_token
                self.eat(NOT)
                self.eat(LP)
                node = BinOp(self.lexer.line_count, node, token, UnOp(un_token, self.bool_comparison_expr()),
                             self.lexer.line_count)
                self.eat(RP)

            else:
                # self.eat(LP)
                node = BinOp(self.lexer.line_count, node, token, self.bool_comparison_expr())
                # self.eat(RP)

        return node

    def unar_expr(self):
        self.eat(NOT)
        self.eat(LP)
        node = self.bool_expr()
        self.eat(RP)
        return UnOp(self.lexer.line_count, node)

    @restorable
    def is_bool_expr(self):
        res = False
        open_cnt = 0
        while self.current_token.type not in [RP, EOF]:
            if self.current_token.type in [LCB]:
                open_cnt += 1
            if self.current_token.type in [RCB]:
                open_cnt -= 1
                if open_cnt < 0:
                    break
            if self.current_token.type in [LESS, LESS_EQ, GREATER, GREATER_EQ, EQUAL, NOT_EQUAL, AND, OR, NOT]:
                res = True
                self.eat(self.current_token.type)
                break
            self.eat(self.current_token.type)
        return res
