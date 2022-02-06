from compyler import Interpreter, load_script
from compyler.builtins import BUILT_INS


script = load_script('script.compyler', False)
script.save('compiled.json', 4)

interpreter = Interpreter(BUILT_INS, strict_mode=False)
scope = interpreter.run(script)

while True:
    pass