import os
import json
import importlib

class TransformCodeInterpreter:
    def __init__(self):
        jsonPath = os.path.join(os.path.dirname(__file__), 'transformers', 'registeredTransformers.json')
        with open(jsonPath) as fin:
            self.registeredModules = json.load(fin)

    def parseAndRun(self, rawCode, model, newCollectionName):
        code = self.parse(rawCode)
        if code is not None:
            model = self.run(code, model, newCollectionName)
            return model
        else:
            return None

    def parse(self, rawCode):
        code = []
        lines = rawCode.split('\n')
        for line in lines:
            line = line.strip().split(' ')
            command = line[0]
            argsList = line[1:]

            modulePath, className = self.getModule(command)
            if modulePath is None:
                print('Unknown command or unregistered command.')
                return None
            else:
                code.append((modulePath, className, argsList))

        return code

    def getModule(self, cmd):
        modulePath, className = self.registeredModules.get(cmd, (None, None))
        return modulePath, className

    def run(self, code, model, newCollectionName):
        for i, (modulePath, className, argsList) in enumerate(code):
            module = importlib.import_module(modulePath)
            classMeta = getattr(module, className)
            transformer = classMeta()

            saveName = newCollectionName if i == len(code) - 1 else None
            model = transformer.run(model, argsList, saveName=saveName)
        
        return model

