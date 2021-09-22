from models.ImageCollectionCloudModel import ImageCollectionCloudModel
import os
import time
import json
import importlib
import re
from utils.RemoteServer import RemoteServer
from pexpect import pxssh
from getpass import getpass

class TransformCodeInterpreter:
    def __init__(self):
        jsonPath = os.path.join(os.path.dirname(__file__), 'transformers', 'registeredTransformers.json')
        with open(jsonPath) as fin:
            self.registeredModules = json.load(fin)

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
        if len(code) == 0: return None
        if rootSavePath is None:
            # rootSavePath = os.path.join(model.getRootPath(), 'transform')
            rootSavePath = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'tmp'))
        for i, (modulePath, className, argsList) in enumerate(code):
            module = importlib.import_module(modulePath)
            classMeta = getattr(module, className)
            transformer = classMeta()

            saveName = newCollectionName if i == len(code) - 1 else None
            model = transformer.run(model, argsList, rootSavePath=rootSavePath, saveName=saveName)
            if model is None:
                return None
        
        return model

    def parseAndRunRemotely(self, rawCode, model, newCollectionName, rootSavePath=None):
        server = RemoteServer('./utils/serverConfigs/gypsum.json')
        flag = server.login()
        if not flag:
            return None
        randomScriptName = f'script_{time.time()}.txt'
        scriptPath = os.path.join(server.get_processor_path(), 'tmp', 'scripts', randomScriptName)

        genscriptCode = f'echo -e "{self.str_to_raw(rawCode)}" > {scriptPath}'
        print('[GENSCRIPT]', genscriptCode)

        processorFile = os.path.join(server.get_processor_path(), 'transform.py')
        modelPath = model.getRootPath().split(':')[1]
        modelType = model.type
        resultName = newCollectionName
        runCode = f'python {processorFile} --model_path={modelPath} --model_type={modelType} --script_file={scriptPath} --result_name={resultName}'
        print('[RUN]', runCode)

        replace = {'[GENSCRIPT]': genscriptCode, '[RUN]': runCode}
        expectRe = 'transform_finished (\d) (.*) (.*)'
        result = server.runTemplateScript(replace, expectRe)
        print(result)

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

    def str_to_raw(self, s):
        raw_map = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
        return r''.join(i if ord(i) > 32 else raw_map.get(ord(i), i) for i in s)