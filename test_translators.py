# === Interpreted Data === #
class Array:
    def __init__(self, values):
        self.values = values
    
    def get_value(self, environment):
        return [value.get_value(environment) for value in self.values]

    def set_value(self, environment, value):
        raise Exception('Cannot set the value of an expression')
    
    def combine(self, array):
        self.values.extend(array.values)
    
    def extend(self, values):
        self.values.extend(values)

class Literal:
    def __init__(self, value):
        self.value = value

    def get_value(self, environment):
        return self.value

    def set_value(self, environment, value):
        raise Exception('Cannot set the value of an expression')

class Expression:
    def __init__(self, lhs, operator, rhs):
        self.lhs, self.operator, self.rhs = lhs, operator, rhs

    def get_value(self, environment):
        lhs = self.lhs.get_value(environment)
        rhs = self.rhs.get_value(environment)

        if self.operator == '+':
            return Literal(lhs + rhs)
        elif self.operator == '-':
            return Literal(lhs - rhs)
        
        return None

    def set_value(self, environment, value):
        raise Exception('Cannot set the value of an expression')

class Variable:
    def __init__(self, keyword):
        self.keyword = keyword
    
    def get_value(self, environment):
        return environment.get_data(self.keyword).get_value(environment)
    
    def set_value(self, environment, value):
        environment.set_data(self.keyword, value)

# === Token Translators === #
class StringTranslator:
    token_name = 'STRING_LITERAL'

    def translate(self, token):
        return Literal(token.value[1:-1])

class IntegerTranslator:
    token_name = 'INTEGER_LITERAL'

    def translate(self, token):
        return Literal(int(token.value))

class DecimalTranslator:
    token_name = 'DECIMAL_LITERAL'

    def translate(self, token):
        return Literal(float(token.value))

class KeywordTranslator:
    token_name = 'KEYWORD'

    def translate(self, token):
        return Variable(token.value)

# === Instructions === #
class SetEnvironmentValue:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self, environment):
        environment.set_data(self.name, self.value)

class DoCalculation:
    def __init__(self, expression):
        self.expression = expression

    def __call__(self, environment):
        return self.expression(environment)

class Body:
    def __init__(self, instructions):
        self.instructions = instructions
    
    def __call__(self, environment):
        for instruction in self.instructions:
            instruction(environment)

class FunctionCall:
    def __init__(self, function_name, args):
        self.function_name = function_name
        self.args = args
    
    def __call__(self, environment):
        environment.get_builtin(self.function_name)(environment, self.args)

# === Tree Translators === #
class BodyTranslator:
    tree_name = 'BODY'

    def translate(self, tree, translation_layer):
        instructions = translation_layer.translate(tree.children)
        return Body(instructions)

class AssignmentTranslator:
    tree_name = 'ASSIGNMENT'

    def translate(self, tree, translation_layer):
        keyword = tree.tokens[0].value
        value = None

        if len(tree.tokens) > 1:
            value = translation_layer.translate_token(tree.tokens[1])
        else:
            value = translation_layer.translate(tree.children)
        
        return SetEnvironmentValue(keyword, value)

class ExpressionTranslator:
    tree_name = 'EXPRESSION'

    def translate(self, tree, translation_layer):
        lhs, rhs = None
        operator = None

        if len(tree.tokens) == 3:
            lhs = translation_layer.translate_token(tree.tokens[0])
            operator = tree.tokens[1].value
            rhs = translation_layer.translate_token(tree.tokens[2])
        elif len(tree.tokens) == 2:
            if tree.tokens[0].name == 'OPERATOR':
                lhs = translation_layer.translate([tree.children[0]])
                operator = tree.tokens[0].value
                rhs = translation_layer.translate_token(tree.tokens[1])
            else:
                lhs = translation_layer.translate_token(tree.tokens[0])
                operator = tree.tokens[1].value
                lhs = translation_layer.translate([tree.children[0]])
        elif len(tree.tokens) == 1:
            operator = tree.tokens[0].value
            lhs = translation_layer.translate([tree.children[0]])
            rhs = translation_layer.translate([tree.children[1]])
        else:
            return translation_layer.translate([tree.children[0]])

        return Expression(lhs, operator, rhs)

class MathematicsTranslator:
    tree_name = 'MATHEMATICS'

    def translate(self, tree, translation_layer):
        lhs, rhs = None
        operator = None

        if len(tree.tokens) == 3:
            lhs = translation_layer.translate_token(tree.tokens[0])
            operator = tree.tokens[1].value
            rhs = translation_layer.translate_token(tree.tokens[2])
        if len(tree.tokens) == 2:
            if tree.tokens[0].name == 'OPERATOR':
                lhs = translation_layer.translate([tree.children[0]])
                operator = tree.tokens[0].value
                rhs = translation_layer.translate_token(tree.tokens[1])
            else:
                lhs = translation_layer.translate_token(tree.tokens[0])
                operator = tree.tokens[1].value
                lhs = translation_layer.translate([tree.children[0]])
        else:
            lhs = translation_layer.translate([tree.children[0]])
            operator = tree.tokens[0].value
            rhs = translation_layer.translate([tree.children[1]])
            
        return Expression(lhs, operator, rhs)

class FunctionTranslator:
    tree_name = 'FUNCTION'

    def translate(self, tree, translation_layer):
        array = Array([])
        if len(tree.tokens) > 1:
            array.extend([translation_layer.translate_token(token) for token in tree.tokens[1:]])
        if tree.children:
            array.combine(translation_layer.translate([tree.children[0]])[0])
        return FunctionCall(tree.tokens[0].value, array)

class ArrayTranslator:
    tree_name = 'ARRAY'

    def translate(self, tree, translation_layer):
        array = Array([])
        if tree.tokens:
            array.extend([translation_layer.translate_token(token) for token in tree.tokens])
        if tree.children:
            array.combine(translation_layer.translate([tree.children[0]])[0])
        return array

# === Translators === #
TOKEN_TRANSLATORS = [
    StringTranslator(),
    DecimalTranslator(),
    IntegerTranslator(),
    KeywordTranslator()
]

TREE_TRANSLATORS = [
    AssignmentTranslator(),
    ExpressionTranslator(),
    MathematicsTranslator(),
    BodyTranslator(),
    FunctionTranslator(),
    ArrayTranslator()
]