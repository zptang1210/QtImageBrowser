import os
import time
import json
import importlib
import re
import traceback

from utils.SaveImageCollection import SaveImageCollection
from utils.pathUtils import constructServerPath, normalizePath
from utils.RemoteServer import RemoteServer
from models.ImageCollectionCloudModel import ImageCollectionCloudModel
from utils.rsyncWrapper import rsync

def str_to_raw(s):
    raw_map = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
    return r''.join(i if ord(i) > 32 else raw_map.get(ord(i), i) for i in s)

class TransformCodeInterpreter:
    def __init__(self):
        jsonPath = os.path.join('utils', 'transformers', 'registeredTransformers.json')
        with open(jsonPath, 'r') as fin:
            self.registeredModules = json.load(fin)

        jsonPath = os.path.join('utils', 'interactTools', 'registeredInteractCmds.json')
        with open(jsonPath, 'r') as fin:
            self.registeredInteractCmds = json.load(fin)


    def parseAndRun(self, rawCode, model, newCollectionName, rootSavePath=None):
        code, macros = self.parse(rawCode)
        if code is None:
            return None

        code = self.preprocess(model, code, macros)
        if code is None:
            return None

        model = self.run(code, model, newCollectionName, rootSavePath=rootSavePath)
        return model


    def parse(self, rawCode):
        code = []
        macros = []
        lines = rawCode.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            line = line.split()
            command = line[0]
            argsList = line[1:]

            if command == '#define': # macros for the preprocessor
                if len(argsList) < 2: return None, None # invalid #define
                else:
                    macroName = argsList[0]
                    interactiveCmd = argsList[1]
                    macros.append((macroName, interactiveCmd))
            else: # ordinary command
                modulePath, className = self.getModule(command)
                if modulePath is None:
                    print('Unknown command or unregistered command.')
                    return None, None
                else:
                    code.append((command, modulePath, className, argsList))

        if len(code) == 0: return None, None # avoid empty script
        return code, macros


    def preprocess(self, model, code, macros):
        if len(macros) == 0: return code # no macro found

        macroDict = dict()
        for macroName, interactiveCmd in macros:
            macroValue = self.runInteractiveCmd(model, interactiveCmd)
            if macroValue is not None:
                macroDict[macroName] = macroValue
            else:
                return None # invalid value returned from the interactive command
        
        # replace all [macro] appear in args with macroDict[macro]
        newCode = []
        for command, modulePath, className, argsList in code:
            argsStr = ' '.join(argsList)
            for macroName in macroDict.keys():
                argsStr = argsStr.replace(f'[{macroName}]', macroDict[macroName])
            newArgsList = argsStr.split()

            newCode.append((command, modulePath, className, newArgsList))
        return newCode


    def runInteractiveCmd(self, model, cmd):
        modulePath, className = self.registeredInteractCmds.get(cmd, (None, None))
        if modulePath is None: # cannot find the interactive command
            print('Unknown interactive command.')
            return None

        try:
            module = importlib.import_module(modulePath)
            classMeta = getattr(module, className)
            interactiveTool = classMeta()
        except:
            print('Loading interactive tool failed', traceback.format_exc())
            return None

        try:
            result = interactiveTool.run(model)
        except:
            print('Running interactive tool failed.', traceback.format_exc())
        else:
            if result is not None and isinstance(result, str):
                return result
            else:
                return None


    def getModule(self, cmd):
        modulePath, className = self.registeredModules.get(cmd, (None, None))
        return modulePath, className


    def run(self, code, model, newCollectionName, rootSavePath=None):
        if rootSavePath is None:
            rootSavePath = os.path.join('.', 'tmp')
        try:
            rootSavePath = normalizePath(rootSavePath)
        except:
            print('invalid rootSavePath.')
            return None

        modelList = []
        try:
            for i, (command, modulePath, className, argsList) in enumerate(code):
                module = importlib.import_module(modulePath)
                classMeta = getattr(module, className)
                transformer = classMeta()

                saveName = newCollectionName if i == len(code) - 1 else f'{newCollectionName}_step_{i}_{time.time()}'
                model = transformer.run(model, argsList, rootSavePath=rootSavePath, saveName=saveName)
                if model is None:
                    return None
                else:
                    modelList.append(model)
        except:
            print('running script failed.', traceback.format_exc())
            return None

        return modelList


    def getScriptWoMacros(self, rawCode, model):
        parsedCode, macros = self.parse(rawCode)
        if parsedCode is None:
            return None

        codeWoMacros = self.preprocess(model, parsedCode, macros)
        if codeWoMacros is None:
            return None

        newScript = ''
        for (command, modulePath, className, argsList) in codeWoMacros:
            line = f"{command} {' '.join(argsList)}\n"
            newScript += line
        
        return newScript


    def parseAndRunRemotely(self, rawCode, model, newCollectionName, serverConfig):
        server = RemoteServer(serverConfig)
        flag = server.login()
        if not flag:
            return None

        # scriptPath
        randomScriptName = f'script_{time.time()}'
        scriptPath = os.path.join(server.get_processor_path(), 'tmp', 'scripts', randomScriptName+'.txt')
        logPath = os.path.join(server.get_processor_path(), 'log', 'log_'+randomScriptName+'.txt')

        # [GENSCRIPT]
        genscriptCode = f'echo -e "{str_to_raw(rawCode)}" > {scriptPath}'
        print('[GENSCRIPT]', genscriptCode)

        # processorFile
        processorFile = os.path.join(server.get_processor_path(), 'transform_backend.py')

        # model_path and model_type
        # upload the local model to the corresponding server, and use the path on the server to run the script
        # if the model is a cloud model, use localPath instead of the path.
        try:
            modelType = model.sourceModelTypeName

            modelLocalPath = None
            if isinstance(model, ImageCollectionCloudModel):
                if model.loaded:
                    modelLocalPath = model.localPath
            else:
                modelLocalPath = model.path
            
            if modelLocalPath is None: raise ValueError('The model to transform is not loaded.')

            tempModelName = os.path.basename(modelLocalPath) + '_' + str(time.time())
            tempModelServerPath = os.path.join(server.get_processor_path(), 'tmp', tempModelName)
            tempModelServerFullPath = server.get_username() + '@' + server.get_server() + ':' + tempModelServerPath
            flag = SaveImageCollection.upload(modelLocalPath, tempModelServerFullPath, modelType)
            if not flag:
                raise RuntimeError('model uploading failed.')
        except:
            print('model uploading failed.')
            server.logout() # log out from the server
            return None
        else:
            print('model uploading succeeded.')
            modelPath = tempModelServerPath

        # resultName
        resultName = newCollectionName

        # [RUN]
        runCode = f'python {processorFile} --model_path={modelPath} --model_type={modelType} --script_file={scriptPath} --result_name={resultName} | tee {logPath}'
        print('[RUN]', runCode)
        
        # run the generated script on the server
        replace = {'[GENSCRIPT]': genscriptCode, '[RUN]': runCode}
        expectRe = 'transform_finished (\d) (.*)'
        result = server.runTemplateScript(replace, expectRe)
        print('transform result:', result)
        if result is None: # running failed
            server.logout()
            return None

        server.logout() # finished using the server for transformation, log out from the server

        # parse result
        pattern = re.compile(expectRe)
        m = pattern.match(result)
        flag = int(m.group(1).strip())
        logResFilePathOnSrv = m.group(2).strip()

        if flag == 0:
            print('remote server reports failure of running the script.')
            return None

        # download result log file
        logResFileSrvPath = constructServerPath(serverConfig['server'], serverConfig['username'], logResFilePathOnSrv)

        logResFileLocalSaveFolder = os.path.join('.', 'tmp', 'remote_results')
        if not os.path.exists(logResFileLocalSaveFolder): os.makedirs(logResFileLocalSaveFolder)

        flag = rsync(logResFileSrvPath, logResFileLocalSaveFolder)
        if flag == False:
            print('downloading result log file failed.')
            return None

        logResFilePathOnLocal = os.path.join(logResFileLocalSaveFolder, os.path.basename(logResFilePathOnSrv))

        # parse result log file
        newModelInfoList = []

        expectResRe = 'transform_finished (\d) (.*) (.*) (.*)'
        pattern = re.compile(expectResRe)
        try:
            with open(logResFilePathOnLocal, 'r') as fin:
                resNum = int(fin.readline())
                for i in range(resNum):
                    result = fin.readline()

                    m = pattern.match(result)
                    no = int(m.group(1).strip())
                    assert no == i
                    newPath = m.group(2).strip()
                    newName = m.group(3).strip()
                    newTypeName = m.group(4).strip()

                    newServerPath = constructServerPath(serverConfig['server'], serverConfig['username'], newPath)

                    newModelInfoList.append({'path': newServerPath, 'name': newName, 'type': newTypeName})
        except:
            print(f'parsing result log file {logResFilePathOnLocal} failed.')
            return None
            
        # construct cloud models for return
        newModelList = []
        for newModelInfo in newModelInfoList:
            newServerPath, newName, newTypeName = newModelInfo['path'], newModelInfo['name'], newModelInfo['type']
            try:
                # don't preload it to save time since it will be load when opening it to the main window
                newModel = ImageCollectionCloudModel(newServerPath, newName, newTypeName, preload=False)
            except:
                print('error occurs when creating a cloud model:', newServerPath)
                return None
            else:
                newModelList.append(newModel)

        return newModelList
