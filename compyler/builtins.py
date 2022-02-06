from cgi import test


def builtin_print(scope, params):
    print(*params.unbox(scope))

BUILT_INS = {
    'PRINT': builtin_print
}