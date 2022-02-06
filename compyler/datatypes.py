from .exceptions import InterpreterException


class FuncParams:
    def __init__(self, values):
        self.values = values
    
    def get(self, scope):
        return self.values
    
    def set(self, scope, value):
        raise InterpreterException('Cannot set function parameters (read-only)')
    
    def unbox(self, scope):
        flattened = []

        for value in self.values:
            unboxed = value.unbox(scope)
            if type(unboxed) == list:
                flattened.extend(unboxed)
            else:
                flattened.append(unboxed)

        return flattened

class Expression:
    def __init__(self, lhs, rhs, operator):
        self.lhs, self.rhs = lhs, rhs
        self.operator = operator
    
    def get(self, scope):
        return box(self.unbox(scope))
    
    def set(self, scope, value):
        raise InterpreterException('Cannot set the value of an expression')
    
    def unbox(self, scope):
        lhs, rhs = self.lhs.unbox(scope), self.rhs.unbox(scope)

        try:
            if self.operator == 'ADD_OP':
                return lhs + rhs
            elif self.operator == 'SUB_OP':
                return lhs - rhs
            elif self.operator == 'MULT_OP':
                return lhs * rhs
            elif self.operator == 'DIV_OP':
                return lhs / rhs
        except:
            raise InterpreterException(f'Failed {self.operator} operation with {lhs} and {rhs}')
        
        raise InterpreterException(f'Unrecognized operator {self.operator}')

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