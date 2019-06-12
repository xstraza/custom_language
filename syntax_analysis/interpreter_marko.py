class AST(object):
    def __init__(self, line_number):
        self.line_number = line_number


class Program(AST):
    def __init__(self, line_number, sections):
        super().__init__(line_number)
        self.sections = sections


class Library(AST):
    def __init__(self, line_number, local_name, lib_name, f_name):
        super().__init__(line_number)
        self.local_name = local_name
        self.lib_name = lib_name
        self.f_name = f_name


class Fdeclaration(AST):
    def __init__(self, line_number, f_name, param_list, f_body):
        super().__init__(line_number)
        self.f_name = f_name
        self.param_list = param_list
        self.f_body = f_body


class WhileStatement(AST):
    def __init__(self, line_number, condition, w_body):
        super().__init__(line_number)
        self.condition = condition
        self.w_body = w_body


class ForStatement(AST):
    def __init__(self, line_number, counter, start, stop, f_body):
        super().__init__(line_number)
        self.counter = counter
        self.start = start
        self.stop = stop
        self.f_body = f_body


class IfStatement(AST):
    def __init__(self, line_number, condition, if_body, elsee=None):
        super().__init__(line_number)
        self.condition = condition
        self.if_body = if_body
        self.else_body = elsee


class ElseStatement(AST):
    def __init__(self, line_number, body, condition=None):
        super().__init__(line_number)
        self.condition = condition
        self.body = body


class ParamList(AST):
    def __init__(self, line_number, params):
        super().__init__(line_number)
        self.params = params


class UserFCall(AST):
    def __init__(self, line_number, name, arg_list):
        super().__init__(line_number)
        self.name = name
        self.arg_list = arg_list


class DefinedFCall(AST):
    def __init__(self, line_number, type, arg_list):
        super().__init__(line_number)
        self.type = type
        self.arg_list = arg_list


class ImportedFCall(AST):
    def __init__(self, line_number, local_name, f_name, arg_list):
        super().__init__(line_number)
        self.local_name = local_name
        self.f_name = f_name
        self.arg_list = arg_list


class Break(AST):
    def __init__(self, line_number):
        super().__init__(line_number)
        self.name = 'break'


class Var(AST):
    def __init__(self, line_number, var_name, indeks=-1):
        super().__init__(line_number)
        self.var_name = var_name
        self.indeks = indeks
        self.type = 0


class Value(AST):
    def __init__(self, line_number, type, value):
        super().__init__(line_number)
        self.type = type
        self.value = value


class VarAssignment(AST):
    def __init__(self, line_number, var, value):
        super().__init__(line_number)
        self.var = var
        if type(value) == Value:
            self.type = value.type
        else:
            self.type = None
        self.value = value


class BinOp(AST):
    def __init__(self, line_number, left, op, right):
        super().__init__(line_number)
        self.left = left
        self.token = self.op = op
        self.right = right


class UnOp(AST):
    def __init__(self, line_number, value):
        super().__init__(line_number)
        self.value = value


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_{}'.format(type(node).__name__)
        # print(method_name)
        visitor = getattr(self, method_name, self.error)
        return visitor(node)

    def error(self, node):
        raise Exception('Not found {}'.format(type(node).__name__))
