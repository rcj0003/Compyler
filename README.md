# Compyler
General purpose compiler/interpreter for Python

## Disclaimers
I know nothing about compilers or interpreters (except for basic knowledge of Backus-Naur Form).

## Does it work?
Yes. although I'm not sure what happens with particularly complex "tokenizer schemas", and if enough recursion will cause problems.

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


The above is certainly an eyesore, but it roughly approximates BNF.

It parses the script you give it out into recursive trees, each with the production name and child elements. These elements will either be a token with a name and string value, or another tree.

After writing productions and successfully parsing out your script, you need to tell Compyler how to translate it into runnable code. A "translation layer" needs to be made, which will parse out tokens and children parse trees into something runnable. The translation layer can compile or interpret to anything with enough knowhow. I choose to map out parse tree data into Python function calls and to box the interpreted data.
