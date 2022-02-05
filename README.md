# Compyler
General purpose compiler/interpreter for Python

## Disclaimers
I know nothing about compilers or interpreters (except for basic knowledge of Backus-Naur Form). I bashed my head against my keyboard for a couple of hours and this was born.

## Does it work?
Yes, but I'm not sure how well. The test "schema" seems to run fast. There is likely some unnecessary nesting, so I'm not sure how large programs would be handled.

## How does it work?
With lots of recursion... It basically brute forces the script you the `TokenizerSchema`, and if it can't fit at least part of one of the "rules"/productions (more like pseudo-productions), then it'll start over from the last place it was able to parse. It won't go back further than that; if it can't continue to tokenize, it'll throw a `TokenizeException`, basically a syntax or compiler error.

Here's what it looks like in practice with Compyler.
```python
schema = TokenizerSchemaBuilder()\
    .complex_rule('BODY')\
        .rule(
            TokenizerBuilder('BODY')\
                .lookup_rule('INSTRUCTION')\
                .regex_rule(';')
                .lookup_rule('BODY')
                .build()
        )\
        .rule(
            TokenizerBuilder('BODY')\
                .lookup_rule('INSTRUCTION')\
                .regex_rule(';')
                .build()
        )\
        .next(first_group=True)\
    .complex_rule('INSTRUCTION')\
        .lookup_rule('ASSIGNMENT')\
        .lookup_rule('FUNCTION')\
        .next(first_group=True)\
    .complex_rule('FUNCTION')\
        .rule(
            TokenizerBuilder('FUNCTION')\
                .regex_rule('CALL\\s+', flags=[re.IGNORECASE])\
                .lookup_rule('KEYWORD')\
                .lookup_rule('ARRAY')\
                .build()
        )\
        .rule(
            TokenizerBuilder('FUNCTION')\
                .regex_rule('CALL\\s+', flags=[re.IGNORECASE])\
                .lookup_rule('KEYWORD')\
                .build()
        )\
        .next(first_group=True)\
    .complex_rule('ARRAY')\
        .rule(
            TokenizerBuilder('ARRAY')\
                .lookup_rule('EXPRESSION')\
                .regex_rule(',')\
                .lookup_rule('ARRAY')\
                .build()
        )\
        .lookup_rule('EXPRESSION')\
        .next(first_group=True)\
    .complex_rule('ASSIGNMENT')\
        .regex_rule('VAR\\s+', flags=[re.IGNORECASE])\
        .lookup_rule('KEYWORD')\
        .regex_rule('=')\
        .lookup_rule('EXPRESSION')\
        .next(first_group=False)\
    .complex_rule('EXPRESSION')\
        .rule(
            TokenizerBuilder('EXPRESSION')\
                .lookup_rule('MATHEMATICS')\
                .lookup_rule('OPERATOR')
                .lookup_rule('EXPRESSION')\
                .build()
        )\
        .lookup_rule('MATHEMATICS')\
        .next(first_group=True)\
    .complex_rule('MATHEMATICS')\
        .rule(
            TokenizerBuilder('MATHEMATICS')\
                .lookup_rule('VARIABLE')\
                .lookup_rule('OPERATOR')
                .lookup_rule('MATHEMATICS')\
                .build()
        )\
        .rule(
            TokenizerBuilder('MATHEMATICS')\
                .regex_rule('\\(')
                .lookup_rule('MATHEMATICS')\
                .regex_rule('\\)')\
                .build()
        )\
        .lookup_rule('VARIABLE')\
        .next(first_group=True)\
    .complex_rule('VARIABLE')\
        .lookup_rule('KEYWORD')\
        .lookup_rule('LITERAL')\
        .next(first_group=True)\
    .regex_rule('KEYWORD', '[A-Z][A-Z0-9_]{0,31}', flags=[re.IGNORECASE])\
    .complex_rule('LITERAL')\
        .lookup_rule('STRING_LITERAL')\
        .lookup_rule('DECIMAL_LITERAL')\
        .lookup_rule('INTEGER_LITERAL')\
        .next(first_group=True)\
    .regex_rule('STRING_LITERAL', '".*"(?<!\\\\")')\
    .regex_rule('DECIMAL_LITERAL', '\\d\\.\\d')\
    .regex_rule('INTEGER_LITERAL', '\\d')\
    .regex_rule('OPERATOR', '[+-]')\
    .build()
```

I won't really begin to explain the syntax above, but BODY, INSTRUCTION, FUNCTION, and ASSIGNMENT roughly translate to these BNF productions:
```
<BODY> ::= <INSTRUCTION>; <BODY> |
     <INSTRUCTION>;
<INSTRUCTION> ::= <ASSIGNMENT> | <
     <FUNCTION>
<FUNCTION> ::= CALL <KEYWORD> <ARRAY> |
     CALL <KEYWORD>
<ASSIGNMENT> ::= VAR <KEYWORD> = <EXPRESSION>
```

It parses the script you give it out into recursive trees, each with the production name, the subtokens associated with it, and its child trees.

Then, a "translation layer" needs to be made, which will parse out the root tree into "instructions", a list of functions to call. After writing productions and successfully parsing out your script, you need to tell Compyler how to translate it into runnable code.
```python
from compyler import InterpretedEnvironment
from compyler.translation import InterpretedTranslationLayer


class SetEnvironmentValue:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self, environment):
        environment.set_data(self.name, self.value)

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

class Literal:
    def __init__(self, value):
        self.value = value

    def get_value(self, environment):
        return self.value

    def set_value(self, environment, value):
        raise Exception('Cannot set the value of an expression')

class DecimalTranslator:
    token_name = 'DECIMAL_LITERAL'

    def translate(self, token):
        return Literal(float(token.value))

script = 'var test = 5.0;'
interpreted_builtins = {}
translation_layer = InterpretedTranslationLayer(tree_translators=[AssignmentTranslator()], token_translators=[DecimalTranslator()])
env = InterpretedEnvironment(translation_layer, interpreted_builtins)
tree = schema.parse(script)
env.compile(tree)
env.run()
# Outputs:
#
# === [Environment Variables] ===
# test = 5.0
# ===
#
env.print_data()
```
