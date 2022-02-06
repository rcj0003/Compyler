from .exceptions import InterpreterException


class FuncParams:
    def __init__(self, values):
        self.values = values
    
    def get(self, scope):
        return self.values
    
    def set(self, scope, value):
        raise InterpreterException('Cannot set function parameters (read-only)')
    
    def unbox(self, scope):
        return [
            value.unbox(scope)
            for value in self.values
        ]

class Variable:
    def __init__(self, name):
        self.name = name
    
    def get(self, scope):
        return self
    
    def set(self, scope, value):
        scope.set_data(self.name, value)
    
    def unbox(self, scope):
        return scope.get_data(self.name).unbox(scope)

class Literal:
    def __init__(self, value):
        self.value = value

    def get(self, scope):
        return self
    
    def set(self, scope, value):
        raise InterpreterException('Cannot set the value of a literal')

    def unbox(self, scope):
        return self.value

class Float(Literal):
    pass

class String(Literal):
    pass

class Integer(Literal):
    pass

def box(value):
    value_type = type(value)

    if value_type is int:
        return Integer(value)
    elif value_type is str:
        return String(value)
    elif value_type is float:
        return Float(value)
    
    raise Exception(f'Cannot box {value_type} ({value})')