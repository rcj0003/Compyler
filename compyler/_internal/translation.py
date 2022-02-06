class BaseTranslationLayer:
    def translate(self, *children):
        return []

class InterpretedTranslationLayer(BaseTranslationLayer):
    def __init__(self, translators):
        self._translators = translators
    
    def translate(self, *children):
        instructions = []
        
        for child in children:
            instruction = self._translators[child.name](child, self)
            if type(instruction) is list:
                instructions.extend(instruction)
            else:
                instructions.append(instruction)
        
        return instructions
