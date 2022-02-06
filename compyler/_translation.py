from . import datatypes
import re


STRING_VALUE = re.compile('"(.*)"')

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

def keyword(child, translator):
    return datatypes.Variable(child.value)

def expression(child, translator):
    lhs = translator.translate(child.children[0])[0]
    rhs = translator.translate(child.children[2])[0]
    return datatypes.Expression(lhs, rhs, child.children[1].name)

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
    if len(child.children) > 1:
        params = translator.translate(child.children[1])[0]
    else:
        params = datatypes.FuncParams([])
    return FunctionCall(name, params)

def body(child, translator):
    return translator.translate(*child.children)

TRANSLATORS = {
    'STRICT_ASSIGN': strict_assign,
    'ASSIGN': assign,
    'KEY_WORD': keyword,
    'EXPRESSION': expression,
    'STR_LITERAL': string_literal,
    'FLOAT_LITERAL': float_literal,
    'INT_LITERAL': integer_literal,
    'VAR_NAME': var_name,
    'FUNC_PARAMS': function_params,
    'FUNC_CALL': function_call,
    'BODY': body
}