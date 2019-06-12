import textwrap

from lexical_analysis.lexer import Lexer
from lexical_analysis.token_type import *
from syntax_analysis.interpreter_marko import NodeVisitor, Value, Var
from syntax_analysis.parser_marko import Parser


class ASTVisualizer(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.tab_count = 0
        self.code = ''
        self.variables = dict()
        self.curr_type = None
        self.libs = set()
        self.functions = set()

    def tabs(self):
        s = ''
        for i in range(self.tab_count):
            s += '    '
        return s

    def visit_Program(self, node):
        for section in node.sections:
            if type(section) is not list:
                self.visit(section)
            else:
                for line in section:
                    self.visit(line)

    def visit_Library(self, node):
        self.code += self.tabs()
        self.libs.add(node.local_name + node.f_name)
        if node.f_name == 'rrange':
            self.code += 'import random\n\n\ndef {}{}(a, b):\n    return random.randrange(a, b)\n\n\n'.format(
                node.local_name,
                node.f_name)
        if node.f_name == 'up':
            self.code += 'def {}{}(a):\n    return a.upper()\n\n\n'.format(node.local_name, node.f_name)
        if node.f_name == 'isa':
            self.code += 'def {}{}(a):\n    return a.isalpha()\n\n\n'.format(node.local_name, node.f_name)
        if node.f_name == 'isn':
            self.code += 'def {}{}(a):\n    return a.isdigit()\n\n\n'.format(node.local_name, node.f_name)
        if node.f_name == 'splt':
            self.code += 'def {}{}(a):\n    return a.split()\n\n\n'.format(node.local_name, node.f_name)
        if node.f_name == 'rt':
            self.code += 'def {}{}(a):\n    f = open(a, \'r\')\n    s = f.read()\n    f.close()\n    return s\n\n\n'.format(
                node.local_name, node.f_name)

    def visit_LineList(self, node):
        self.code += self.tabs()
        for line in node.lines:
            self.visit(line)
            self.code += '\n'

    def visit_ForStatement(self, node):
        self.code += self.tabs()
        self.code += 'for '
        self.visit(node.counter)
        self.code += ' in range('
        self.visit(node.start)
        self.code += ', '
        self.visit(node.stop)
        self.code += '):\n'
        self.tab_count += 1
        for line in node.f_body:
            self.visit(line)
        self.tab_count -= 1

    def visit_WhileStatement(self, node):
        self.code += self.tabs()
        self.code += 'while '
        self.visit(node.condition)
        self.code += ':\n'
        self.tab_count += 1
        for line in node.w_body:
            self.visit(line)
        self.tab_count -= 1

    def visit_Break(self, node):
        self.code += self.tabs()
        self.code += 'break\n'

    def visit_IfStatement(self, node):
        self.code += self.tabs()
        self.code += 'if '
        self.visit(node.condition)
        self.code += ':\n'
        self.tab_count += 1
        for line in node.if_body:
            self.visit(line)
        self.tab_count -= 1
        if node.else_body is not None:
            self.visit(node.else_body)

    def visit_ElseStatement(self, node):
        self.code += self.tabs()
        if node.condition is not None:
            self.code += 'elif '
            self.visit(node.condition)
            self.code += ':\n'
        else:
            self.code += 'else:\n'
        self.tab_count += 1
        for line in node.body:
            self.visit(line)
        self.tab_count -= 1

    def visit_Fdeclaration(self, node):
        print(node.f_name)
        self.code += self.tabs()
        self.code += 'def ' + node.f_name + '('
        self.functions.add(node.f_name)
        self.visit(node.param_list)
        self.code += '):\n'
        self.tab_count += 1
        for line in node.f_body:
            self.visit(line)
        self.tab_count -= 1

    def visit_ImportedFCall(self, node):
        if node.local_name + node.f_name not in self.libs:
            raise Exception("{}.{} not imported".format(node.local_name, node.f_name))
        self.code += node.local_name + node.f_name + '('
        for arg in node.arg_list:
            self.visit(arg)
            self.code += ', '
        self.code = self.code[:-2]
        self.code += ')'

    def visit_UserFCall(self, node):
        if node.name not in self.functions:
            raise Exception(node.name + ' not defined')
        self.code += node.name + '('
        for arg in node.arg_list:
            self.visit(arg)
            self.code += ', '
        self.code = self.code[:-2]
        self.code += ')'

    def visit_DefinedFCall(self, node):
        type = node.type
        if type == READ:
            self.code += self.tabs()
            for arg in node.arg_list:
                self.visit(arg)
            self.code += ' = eval(input())\n'
        else:
            if type == PRINT_INT:
                self.code += self.tabs()
                self.code += 'print('
            elif type == PRINT_STRING:
                self.code += self.tabs()
                self.code += 'print('
            elif type == LENGTH:
                self.code += 'len('
                self.visit(node.arg_list[0])
                self.code += ')'
                return
            for arg in node.arg_list:
                self.visit(arg)
            self.code += ')\n'

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.code += ' ' + str(node.op.value) + ' '
        if str(node.op.value) == '+':
            if self.curr_type is not None:
                if self.curr_type == LIST:
                    self.code += '['
                    self.visit(node.right)
                    self.code += ']'
                    return
                if self.curr_type == STRING:
                    self.code += 'str('
                    self.visit(node.right)
                    self.code += ')'
                    return
        self.visit(node.right)

    def visit_Args(self, node):
        for child in node.args:
            self.visit(child)

    def visit_ParamList(self, node):
        for child in node.params:
            self.visit(child)

    def visit_VarAssignment(self, node):
        self.code += self.tabs()
        self.visit(node.var)
        if node.var.var_name not in self.variables:
            self.variables[node.var.var_name] = node.type
        else:
            self.curr_type = self.variables[node.var.var_name]
        self.code += ' = '
        self.visit(node.value)
        self.code += '\n'

    def visit_Var(self, node):
        self.code += node.var_name
        if node.indeks != -1:
            self.code += '['
            self.visit(node.indeks)
            self.code += ']'

    def visit_Value(self, node):
        if node.type == FLOAT:
            self.code += str(node.value)
        if node.type == STRING:
            self.code += node.value
        if node.type == INTEGER:
            self.code += str(node.value)
        if node.type == LIST:
            self.code += '[]'
        if node.type == BOOL:
            if node.value == 'TRU':
                self.code += 'True'
            else:
                self.code += 'False'

    def visit_UnOp(self, node):
        self.code += ' not '
        self.visit(node.value)

    def genDot(self):
        tree = self.parser.parse()
        self.visit(tree)
        return self.code


def main():
    fname = './examples/ulaz1.txt'
    text = open(fname, 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    viz = ASTVisualizer(parser)
    content = viz.genDot()

    print(content)
    out = open('./examples/compiled_files/sample_compiled.py', 'w')
    out.write(content)


if __name__ == '__main__':
    main()
