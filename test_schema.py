from compyler.tokenization import TokenizerSchemaBuilder, TokenizerBuilder
import re


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

if __name__ == '__main__':
    script = '''
    var stringVariable = "this is a string";
    var integerVariable = 5;
    var floatVariable = 2.2;
    call output "Here are the defined variables";
    call output stringVariable, floatVariable, integerVariable;
    '''
    tree = schema.parse(script)

    import json
    with open('compiled.json', 'w') as file:
        file.write(json.dumps(tree.as_json(), indent=4))