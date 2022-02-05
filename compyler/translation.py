class BaseTranslationLayer:
    def translate(self, tree):
        pass

class TreeInstructions:
    def __init__(self, instructions):
        self.instructions = instructions
    
    def __call__(self, environment):
        for instruction in self.instructions:
            instruction(environment)

class InterpretedTranslationLayer(BaseTranslationLayer):
    def __init__(self, tree_translators, token_translators):
        self._tree_translators = {translator.tree_name: translator for translator in tree_translators}
        self._token_translators = {translator.token_name: translator for translator in token_translators}
    
    def translate(self, trees):
        instructions = []
        
        for tree in trees:
            instruction = self._tree_translators[tree.name].translate(tree, self)
            instructions.append(instruction)
        
        return instructions
    
    def translate_token(self, token):
        return self._token_translators[token.name].translate(token)
