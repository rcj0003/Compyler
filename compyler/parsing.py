from ._internal.tokenization import TokenizerSchemaBuilder, TokenizerBuilder
import re

schema = TokenizerSchemaBuilder()\
    .complex_rule('BODY')\
        .rule(
            TokenizerBuilder('BODY')
                .lookup_rule('INSTRUCTION')
                .lookup_rule('BODY')
                .build()
        )\
        .rule(
            TokenizerBuilder('BODY')
                .lookup_rule('INSTRUCTION')
                .regex_rule(';')
                .lookup_rule('BODY')
                .build()
        )\
        .lookup_rule('INSTRUCTION')\
        .next(first_group=True)\
    .complex_rule('INSTRUCTION')\
        .lookup_rule('STRICT_ASSIGN')\
        .lookup_rule('ASSIGN')\
        .lookup_rule('FUNC_CALL')\
        .next(first_group=True)\
    .complex_rule('STRICT_ASSIGN')\
        .regex_rule('VAR\\s+', flags=[re.IGNORECASE])\
        .lookup_rule('ASSIGN')\
        .next()\
    .complex_rule('ASSIGN')\
        .lookup_rule('VAR_NAME')\
        .regex_rule('=')\
        .lookup_rule('EXPRESSION')\
        .next()\
    .complex_rule('FUNC_CALL')\
        .rule(
            TokenizerBuilder('FUNC_CALL')\
                .lookup_rule('KEY_WORD')\
                .lookup_rule('FUNC_PARAMS')\
                .build()\
        )\
        .lookup_rule('KEY_WORD')\
        .next(first_group=True)\
    .complex_rule('FUNC_PARAMS')\
        .rule(
            TokenizerBuilder('FUNC_PARAMS')\
                .lookup_rule('EXPRESSION')\
                .regex_rule('\\,')\
                .lookup_rule('FUNC_PARAMS')\
                .build()\
        )\
        .lookup_rule('EXPRESSION')\
        .next(first_group=True)\
    .complex_rule('EXPRESSION')\
        .rule(
            TokenizerBuilder('EXPRESSION')
                .regex_rule('\\(')
                .lookup_rule('EXPRESSION')
                .regex_rule('\\)')
                .lookup_rule('OPERATOR')
                .lookup_rule('EXPRESSION')
                .build()
        )\
        .rule(
            TokenizerBuilder('EXPRESSION')
                .regex_rule('\\(')
                .lookup_rule('EXPRESSION')
                .regex_rule('\\)')
                .lookup_rule('EXPRESSION')
                .build()
        )\
        .rule(
            TokenizerBuilder('EXPRESSION')
                .regex_rule('\\(')
                .lookup_rule('EXPRESSION')
                .regex_rule('\\)')
                .build()
        )\
        .rule(
            TokenizerBuilder('EXPRESSION')
                .lookup_rule('VAR')
                .lookup_rule('OPERATOR')
                .lookup_rule('EXPRESSION')
                .build()
        )\
        .lookup_rule('VAR')\
        .next(first_group=True)\
    .complex_rule('VAR')\
        .lookup_rule('VAR_NAME')\
        .lookup_rule('LITERAL')\
        .next(first_group=True)\
    .complex_rule('VAR_NAME')\
        .rule(
            TokenizerBuilder('VAR_NAME')
                .lookup_rule('KEY_WORD')
                .lookup_rule('DATA_TYPE')
                .build()
        )\
        .lookup_rule('KEY_WORD')\
        .next(first_group=True)\
    .complex_rule('LITERAL')\
        .lookup_rule('STR_LITERAL')\
        .lookup_rule('FLOAT_LITERAL')\
        .lookup_rule('INT_LITERAL')\
        .next(first_group=True)\
    .regex_rule('STR_LITERAL', '".*?"(?<!\\\\")')\
    .regex_rule('FLOAT_LITERAL', '\\d+\\.\\d+')\
    .regex_rule('INT_LITERAL', '\\d+')\
    .regex_rule('KEY_WORD', '[A-Z_][A-Z0-9_]{0,31}', flags=[re.IGNORECASE])\
    .complex_rule('DATA_TYPE')\
        .lookup_rule('STR_TYPE')\
        .lookup_rule('INT_TYPE')\
        .lookup_rule('FLOAT_TYPE')\
        .next(first_group=True)\
    .regex_rule('STR_TYPE', '\\$')\
    .regex_rule('INT_TYPE', '\\%')\
    .regex_rule('FLOAT_TYPE', '\\#')\
    .complex_rule('OPERATOR')\
        .lookup_rule('MULT_OP')\
        .lookup_rule('DIV_OP')\
        .lookup_rule('ADD_OP')\
        .lookup_rule('SUB_OP')\
        .next(first_group=True)\
    .regex_rule('MULT_OP', '\\*')\
    .regex_rule('DIV_OP', '/')\
    .regex_rule('ADD_OP', '\\+')\
    .regex_rule('SUB_OP', '\\-')\
    .build()