class InterpretedEnvironment:
    def __init__(self, translation_layer, builtins={}, tree=None):
        self.translation_layer = translation_layer
        self.instructions = []
        self.builtins = builtins
        self.data = {}
        if tree:
            self.compile(tree)
    
    def get_builtin(self, name):
        return self.builtins[name]
    
    def get_data(self, name):
        return self.data[name]
    
    def set_data(self, name, value):
        self.data[name] = value
    
    def compile(self, tree):
        trees = None
        if tree.name == 'root':
            trees = tree.children
        else:
            trees = [tree]
        self.instructions = self.translation_layer.translate(trees)

    def run(self):
        self.data.clear()
        for instruction in self.instructions:
            instruction(self)
    
    def print_data(self):
        print()
        print('===[Environment variables]===')
        print('\n'.join(
            f'{key} = {value.get_value(self)}' for key, value in self.data.items()
        ))
        print('=============================')
        print()