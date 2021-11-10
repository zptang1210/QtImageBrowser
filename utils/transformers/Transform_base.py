import os, shutil
import time
import traceback
from abc import abstractmethod
from utils.pathUtils import normalizePath

class Transform_base:
    command = None

    def __init__(self):
        self.argParser = None

    @abstractmethod
    def getArgParser(self):
        pass

    @abstractmethod
    def generateProcessedModel(fileGenerator, savePath, saveName):
        pass

    @abstractmethod
    def processImageCollection(self, model, args):
        pass

    def run(self, model, argsList, rootSavePath, saveName=None):
        if saveName is None: saveName = 'tmp_' + str(time.time())
        try:
            savePath = normalizePath(os.path.join(rootSavePath, saveName))
        except:
            print('invalid rootSavePath.')
            return None

        try:
            self.argParser = self.getArgParser()
            if self.argParser is None:
                self.args = None
            else:
                self.args = self.argParser.parse_args(argsList)
        except Exception as e:
            print('Error occured during parsing.')
            print(e, '\n', traceback.format_exc())
            return None

        try:
            if os.path.exists(savePath):
                # shutil.rmtree(savePath) # should avoid this since it may replace existing opened files
                print('Path already exists...')
                return None
            else: os.makedirs(savePath)

            newModel = self.generateProcessedModel(self.processImageCollection(model, self.args), savePath, saveName)
        except ValueError as e:
            print('Error occured during running transformation probably due to unknown arguments.')
            print(e, '\n', traceback.format_exc())
            shutil.rmtree(savePath)
            return None
        except Exception as e:
            print('Unknown error occured during running transformation and creating a new model.')
            print(e, '\n', traceback.format_exc())
            shutil.rmtree(savePath)
            return None
        else:
            return newModel 

    @classmethod
    def getCommand(cls):
        return cls.command