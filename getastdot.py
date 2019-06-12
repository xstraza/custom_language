import textwrap

from lexical_analysis.lexer import Lexer
from syntax_analysis.interpreter_marko import NodeVisitor
from syntax_analysis.parser_marko import Parser


class ASTVisualizer(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.nodecount = 1
        self.dot_heder = [textwrap.dedent("""
            digraph astgraph {
                node [shape=box, fontsize=12, fontname="Courier", height=.1];
                ranksep=.3;   
                edge [arrowsize=.5]
        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def visit_Program(self, node):
        s = 'node{} [label="Program"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

        for section in node.sections:
            if type(section) is not list:
                self.visit(section)
                s = 'node{} -> node{}\n'.format(node.num, section.num)
                self.dot_body.append(s)
            else:
                for line in section:
                    self.visit(line)
                    s = 'node{} -> node{}\n'.format(node.num, line.num)
                    self.dot_body.append(s)

    def visit_Library(self, node):
        s = 'node{} [label="Library: {}, As: {}, Function: {}"]\n'.format(self.nodecount, node.lib_name,
                                                                          node.local_name, node.f_name)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

    def visit_ForStatement(self, node):
        s = 'node{} [label="For"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        self.visit(node.counter)
        s = 'node{} -> node{}\n'.format(node.num, node.counter.num)
        self.dot_body.append(s)
        self.visit(node.start)
        s = 'node{} -> node{}\n'.format(node.num, node.start.num)
        self.dot_body.append(s)
        self.visit(node.stop)
        s = 'node{} -> node{}\n'.format(node.num, node.stop.num)
        self.dot_body.append(s)
        for line in node.f_body:
            self.visit(line)
            s = 'node{} -> node{}\n'.format(node.num, line.num)
            self.dot_body.append(s)

    def visit_IfStatement(self, node):
        s = 'node{} [label="If"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        self.visit(node.condition)
        s = 'node{} -> node{}\n'.format(node.num, node.condition.num)
        self.dot_body.append(s)
        for line in node.if_body:
            self.visit(line)
            s = 'node{} -> node{}\n'.format(node.num, line.num)
            self.dot_body.append(s)
        if node.else_body is not None:
            self.visit(node.else_body)
            s = 'node{} -> node{}\n'.format(node.num, node.else_body.num)
            self.dot_body.append(s)

    def visit_ElseStatement(self, node):
        s = 'node{} [label="Else"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        if node.condition is not None:
            self.visit(node.condition)
            s = 'node{} -> node{}\n'.format(node.num, node.condition.num)
            self.dot_body.append(s)
        for line in node.body:
            self.visit(line)
            s = 'node{} -> node{}\n'.format(node.num, line.num)
            self.dot_body.append(s)

    def visit_WhileStatement(self, node):
        s = 'node{} [label="While"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        self.visit(node.condition)
        s = 'node{} -> node{}\n'.format(node.num, node.condition.num)
        self.dot_body.append(s)
        for line in node.w_body:
            self.visit(line)
            s = 'node{} -> node{}\n'.format(node.num, line.num)
            self.dot_body.append(s)

    def visit_Fdeclaration(self, node):
        s = 'node{} [label="Funkcija: {}"]\n'.format(self.nodecount, node.f_name)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

        self.visit(node.param_list)
        s = 'node{} -> node{}\n'.format(node.num, node.param_list.num)
        self.dot_body.append(s)

        self.visit(node.f_body)
        s = 'node{} -> node{}\n'.format(node.num, node.f_body.num)
        self.dot_body.append(s)

    def visit_VarAssignment(self, node):
        s = 'node{} [label="VarAssignment"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        self.visit(node.var)
        s = 'node{} -> node{}\n'.format(node.num, node.var.num)
        self.dot_body.append(s)
        self.visit(node.value)
        s = 'node{} -> node{}\n'.format(node.num, node.value.num)
        self.dot_body.append(s)

    def visit_Args(self, node):
        s = 'node{} [label="Args"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

        for child in node.args:
            self.visit(child)
            s = 'node{} -> node{}\n'.format(node.num, child.num)
            self.dot_body.append(s)

    def visit_ParamList(self, node):
        s = 'node{} [label="Params"\n]'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        for param in node.params:
            self.visit(param)
            s = 'node{} -> node{}\n'.format(node.num, param.num)
            self.dot_body.append(s)

    def visit_LineList(self, node):
        s = 'node{} [label="Lines"\n]'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        for line in node.lines:
            self.visit(line)
            s = 'node{} -> node{}\n'.format(node.num, line.num)
            self.dot_body.append(s)

    def visit_DefinedFCall(self, node):
        s = 'node{} [label="Function call: {}"\n]'.format(self.nodecount, node.type)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        for arg in node.arg_list:
            self.visit(arg)
            s = 'node{} -> node{}\n'.format(node.num, arg.num)
            self.dot_body.append(s)

    def visit_ImportedFCall(self, node):
        s = 'node{} [label="Function call: {}, Local name: {}, "\n]'.format(self.nodecount, node.f_name,
                                                                            node.local_name)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        for arg in node.arg_list:
            self.visit(arg)
            s = 'node{} -> node{}\n'.format(node.num, arg.num)
            self.dot_body.append(s)

    def visit_Var(self, node):
        s = 'node{} [label="Var: {}"]\n'.format(self.nodecount, node.var_name)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        if node.indeks != -1:
            self.visit(node.indeks)
            s = 'node{} -> node{}\n'.format(node.num, node.indeks.num)
            self.dot_body.append(s)

    def visit_Value(self, node):
        s = 'node{} [label="Val Type: {}, Value: {}"]\n'.format(self.nodecount, node.type, node.value)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

    def visit_BinOp(self, node):
        s = 'node{} [label="{}"]\n'.format(self.nodecount, node.op)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

        self.visit(node.left)
        s = 'node{} -> node{}\n'.format(node.num, node.left.num)
        self.dot_body.append(s)

        self.visit(node.right)
        s = 'node{} -> node{}\n'.format(node.num, node.right.num)
        self.dot_body.append(s)

    def visit_Break(self, node):
        s = 'node{} [label="Break"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)

    def visit_UnOp(self, node):
        s = 'node{} [label="Not"]\n'.format(self.nodecount)
        node.num = self.nodecount
        self.nodecount += 1
        self.dot_body.append(s)
        self.visit(node.value)
        s = 'node{} -> node{}\n'.format(node.num, node.value.num)
        self.dot_body.append(s)

    def genDot(self):
        tree = self.parser.parse()
        self.visit(tree)
        return ''.join(self.dot_heder + self.dot_body + self.dot_footer)


def main():
    fname = './examples/ulaz5.txt'
    text = open(fname, 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    viz = ASTVisualizer(parser)
    content = viz.genDot()

    print(content)


if __name__ == '__main__':
    main()
