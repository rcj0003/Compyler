from compyler import Interpreter, load_script


script = load_script('script.compyler')
script.save('compiled.json')

interpreter = Interpreter(strict_mode=False)
scope = interpreter.run(script)

while True:
    pass