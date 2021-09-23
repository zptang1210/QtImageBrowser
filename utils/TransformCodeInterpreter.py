import os
import time
import json
import importlib
import re
from utils.pathUtils import normalizePath
from utils.RemoteServer import RemoteServer
from utils.strToRaw import str_to_raw
from models.ImageCollectionCloudModel import ImageCollectionCloudModel

class TransformCodeInterpreter:
    def __init__(self):
        jsonPath = os.path.join('utils', 'transformers', 'registeredTransformers.json')
        with open(jsonPath, 'r') as fin:
            self.registeredModules = json.load(fin)

        with open('./configs/serverConfigs/registeredServerConfig.json', 'r') as fin:
            self.serverConfig = json.load(fin)

    def parseAndRun(self, rawCode, model, newCollectionName, rootSavePath=None):
        code = self.parse(rawCode)
        if code is not None:
            model = self.run(code, model, newCollectionName, rootSavePath=rootSavePath)
            return model
        else:
            return None

    def parse(self, rawCode):
        code = []
        lines = rawCode.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            line = line.split()
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

    def run(self, code, model, newCollectionName, rootSavePath=None):
        if rootSavePath is None:
            rootSavePath = os.path.join('.', 'tmp')
        rootSavePath = normalizePath(rootSavePath)

        if len(code) == 0: return None # avoid empty script

        for i, (modulePath, className, argsList) in enumerate(code):
            module = importlib.import_module(modulePath)
            classMeta = getattr(module, className)
            transformer = classMeta()

            saveName = newCollectionName if i == len(code) - 1 else None
            model = transformer.run(model, argsList, rootSavePath=rootSavePath, saveName=saveName)
            if model is None:
                return None
        
        return model

    def parseAndRunRemotely(self, rawCode, model, newCollectionName):
        server = RemoteServer(self.serverConfig['config_file'])
        flag = server.login()
        if not flag:
            return None
        randomScriptName = f'script_{time.time()}.txt'
        scriptPath = os.path.join(server.get_processor_path(), 'tmp', 'scripts', randomScriptName)

        genscriptCode = f'echo -e "{str_to_raw(rawCode)}" > {scriptPath}'
        print('[GENSCRIPT]', genscriptCode)

        processorFile = os.path.join(server.get_processor_path(), 'transform_backend.py')
        modelPath = model.getRootPath().split(':')[1]
        modelType = model.type
        resultName = newCollectionName
        runCode = f'python {processorFile} --model_path={modelPath} --model_type={modelType} --script_file={scriptPath} --result_name={resultName}'
        print('[RUN]', runCode)

        replace = {'[GENSCRIPT]': genscriptCode, '[RUN]': runCode}
        expectRe = 'transform_finished (\d) (.*) (.*)'
        result = server.runTemplateScript(replace, expectRe)
        print('transform result:', result)
        if result is None:
            return None

        pattern = re.compile(expectRe)
        m = pattern.match(result)
        flag = int(m.group(1).strip())
        newPath = m.group(2).strip()
        newName = m.group(3).strip()
        
        newServerPath = f'{server.get_username()}@{server.get_server()}:{newPath}'
        
        if flag == 0:
            return None
        else:
            newModel = ImageCollectionCloudModel(newServerPath, newName, 'folder', preload=False)
            return newModel
