from test_schema import schema
from test_translators import TREE_TRANSLATORS, TOKEN_TRANSLATORS

from compyler import InterpretedEnvironment
from compyler.translation import InterpretedTranslationLayer

import time

def output(environment, args):
    print(*args.get_value(environment))

interpreted_builtins = {
    'output': output
}

with open('script.compyler', 'r') as file:
    script = file.read()

translation_layer = InterpretedTranslationLayer(TREE_TRANSLATORS, TOKEN_TRANSLATORS)
env = InterpretedEnvironment(translation_layer, interpreted_builtins)

start = time.time()

tree = schema.parse(script)
parse_time = time.time()
env.compile(tree)
print()
print('========================================')
print(f'Parse time:     {((parse_time - start) * 1000):.1f}ms')
print(f'Translate time: {((time.time() - parse_time) * 1000):.1f}ms')
print('========================================')
print()

env.run()
env.print_data()