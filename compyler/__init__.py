import json
from .parsing import schema
from .exceptions import InterpreterException
from ._internal.translation import InterpretedTranslationLayer
from ._translation import TRANSLATORS
from .builtins import BUILT_INS


def parse(script):
    return schema.parse(script)

def dump_parse_tree(script, file_name='parsed.json', indent=None, debug=False):
    with open(file_name, 'w') as file:
        json.dump(schema.parse(script, debug=debug).as_json(), file, indent=indent)

def load_script(file_name, debug=False):
    return schema.load(file_name, debug)

class Scope:
    def __init__(self, environment, data={}, labels={}, functions={}, parent=None):
        self.environment = environment
        self.data = data
        self.labels = labels
        self.functions = functions
        self.parent = parent
    
    def get_data(self, name):
        if name in self.data:
            return self.data[name]
        if self.parent:
            return self.parent.get_data(name)
        raise InterpreterException(f'Variable {name} not defined')

    def has_data(self, name):
        if name in self.data:
            return True
        if self.parent:
            return self.parent.has_data(name)
        return False

    def set_data(self, name, value):
        if self.parent:
            self.parent.set_data(name, value)
        if self.environment.strict_mode:
            if name not in self.data:
                raise InterpreterException('You must define variables before using them')
        self.data[name] = value

    def get_label(self, name):
        function = self.labels.get(name)
        if not function:
            raise InterpreterException(f'Label {name} does not exist')
        return function

    def has_label(self, label_name):
        if label_name in self.labels:
            return True
        if self.parent:
            return self.parent.has_label(label_name)
        return False

    def set_label(self, name, instruction):
        if self.has_label(name):
            raise InterpreterException(f'Label named {name} already exists')
        self.functions[name] = instruction
    
    def get_function(self, function_name):
        if self.parent:
            return self.functions.get(function_name, self.parent.get_function(function_name))
        function = self.functions.get(function_name)
        if not function:
            raise InterpreterException(f'Function {function_name} does not exist')
        return function

    def has_function(self, function_name):
        if function_name in self.functions:
            return True
        if self.parent:
            return self.parent.has_function(function_name)
        return False

    def set_function(self, function_name, function):
        if self.has_function(function_name):
            raise InterpreterException(f'Function named {function_name} already exists')
        self.functions[function_name] = function
    
    def __enter__(self):
        return Scope(self.environment, parent=self)
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return exc_type is not None
    
    def clone(self):
        return Scope(self.environment, self.data, self.labels, self.functions, parent=self.parent)

TRANSLATION_LAYER = InterpretedTranslationLayer(TRANSLATORS)

class Interpreter:
    def __init__(self, strict_mode=False):
        self.scope = Scope(self, functions=BUILT_INS)
        self.strict_mode = strict_mode
    
    def load(self, script):
        return self.run(parse(script))
    
    def run(self, tree):
        instructions = TRANSLATION_LAYER.translate(*tree.children)
        scope = self.scope.clone()

        for instruction in instructions:
            instruction(scope)

        return scope