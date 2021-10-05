import os, shutil
import time
import traceback
from abc import abstractmethod
from utils.pathUtils import normalizePath
from PIL import Image
from models.ImageCollectionFolderModel import ImageCollectionFolderModel

class Transform_base:
    command = None

    def __init__(self):
        self.argParser = None

    @abstractmethod
    def getArgParser(self):
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
            for img_np, img_name in self.processImageCollection(model, self.args):
                img_pil = Image.fromarray(img_np)
                img_pil.save(os.path.join(savePath, img_name+'.jpg'))
        except ValueError as e:
            print('Error occured during running transformation due to unknown arguments.')
            print(e, '\n', traceback.format_exc())
            shutil.rmtree(savePath)
            return None
        except Exception as e:
            print('Unknown error occured during running transformation.')
            print(e, '\n', traceback.format_exc())
            shutil.rmtree(savePath)
            return None
        
        try:
            newModel = ImageCollectionFolderModel(savePath, saveName)
        except:
            print('Failed to create a new model to hold results.')
            return None
        else:
            return newModel 

    @classmethod
    def getCommand(cls):
        return cls.command