from . import datatypes
import re
from .exceptions import InterpreterException


STRING_VALUE = re.compile('"(.*)"')

# === [ Calculations ] === #
class Expression:
    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs
    
    def get(self, scope):
        return datatypes.box(self.unbox(scope))
    
    def set(self, scope, value):
        raise InterpreterException('Cannot set the value of an expression')

class Addition(Expression):
    def unbox(self, scope):
        lhs, rhs = self.lhs.unbox(scope), self.rhs.unbox(scope)
        return lhs + rhs

class Subtraction(Expression):
    def unbox(self, scope):
        lhs, rhs = self.lhs.unbox(scope), self.rhs.unbox(scope)
        return lhs - rhs

class Multiplication(Expression):
    def unbox(self, scope):
        lhs, rhs = self.lhs.unbox(scope), self.rhs.unbox(scope)
        return lhs * rhs

class Division(Expression):
    def unbox(self, scope):
        lhs, rhs = self.lhs.unbox(scope), self.rhs.unbox(scope)
        return lhs / rhs

# === [ Instructions ] === #
class Assign:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def __call__(self, scope):
        self.variable.set(scope, self.value.get(scope))

class FunctionCall:
    def __init__(self, name, params):
        self.name = name
        self.params = params
    
    def __call__(self, scope):
        scope.get_function(self.name)(scope, self.params)

# === [ Translators ] === #
def strict_assign(child, translator):
    return translator.translate(*child.children)[0]

def assign(child, translator):
    children = translator.translate(*child.children)
    return Assign(children[0], children[1])

def var_name(child, translator):
    return translator.translate(child.children[0])[0]

class KeywordTranslator:
    def __init__(self):
        self._cache = {}
    
    def __call__(self, child, translator):
        return self._cache.setdefault(child.value, datatypes.Variable(child.value))

def expression(child, translator):
    lhs = translator.translate(child.children[0])[0]
    rhs = translator.translate(child.children[2])[0]
    operator = child.children[1].name

    operation = None

    try:
        if operator == 'ADD_OP':
            operation = Addition(lhs, rhs)
        elif operator == 'SUB_OP':
            operation = Subtraction(lhs, rhs)
        elif operator == 'MULT_OP':
            operation = Multiplication(lhs, rhs)
        elif operator == 'DIV_OP':
            operation = Division(lhs, rhs)
    except:
        raise InterpreterException(f'Failed {operator} operation with {lhs} and {rhs}')
    
    if not operation:
        raise InterpreterException(f'Unrecognized operator {operator}')

    if lhs is datatypes.Literal and rhs is datatypes.Literal:
        return operation.get(None)
    return operation

def string_literal(child, translator):
    return datatypes.String(STRING_VALUE.match(child.value).group(1))

def integer_literal(child, translator):
    return datatypes.Integer(int(child.value))

def float_literal(child, translator):
    return datatypes.Float(float(child.value))

def function_params(child, translator):
    return datatypes.FuncParams(translator.translate(*child.children))

def function_call(child, translator):
    name = child.children[0].value
    params = translator.translate(*child.children[1:])
    return FunctionCall(name, datatypes.FuncParams(params))

def body(child, translator):
    return translator.translate(*child.children)

TRANSLATORS = {
    'STRICT_ASSIGN': strict_assign,
    'ASSIGN': assign,
    'KEY_WORD': KeywordTranslator(),
    'EXPRESSION': expression,
    'STR_LITERAL': string_literal,
    'FLOAT_LITERAL': float_literal,
    'INT_LITERAL': integer_literal,
    'VAR_NAME': var_name,
    'FUNC_PARAMS': function_params,
    'FUNC_CALL': function_call,
    'BODY': body
}