import os
from utils.pathUtils import normalizePath, getPathType, PathType
from models.ImageCollectionDerivedModel import ImageCollectionDerivedModel
from utils.rsyncWrapper import rsync
from configs.availTypesConfig import availTypes
from configs.availTypesConfig import modelClassDict, modelNameDict

class ImageCollectionCloudModel(ImageCollectionDerivedModel):
    DEFAULT_LOCAL_ROOT_PATH = normalizePath(os.path.join('.', 'tmp'))

    def __init__(self, path, name, type, localPath=None, preload=True, parentModel=None):
        super().__init__()
        self.path = path # server path
        assert getPathType(self.path) == PathType.Server
        self.name = name
        self.type = type
        assert self.type in availTypes
        self.parentModel = parentModel

        if localPath is None:
            self.localPath = os.path.join(ImageCollectionCloudModel.DEFAULT_LOCAL_ROOT_PATH, name)
        else:
            self.localPath = localPath
        assert getPathType(self.localPath) == PathType.Local
        self.localPath = normalizePath(self.localPath)

        self.serverAddr = self.path.split(':')[0]
        
        if preload:
            flag = self.load(self.path, self.localPath)
            if flag == False:
                raise RuntimeError('Unable to load the image collection from the server.')

            self.model = self.getModel()
            if self.model is None:
                raise RuntimeError('Unable to create a mapping image model.')
            else:
                self.loaded = True
        else:
            self.loaded = False
            self.model = None

        self.sourceModel = self.model
        self.sourceModelTypeName = modelNameDict[type(self.sourceModel)]


    def load(self, serverPath, localPath):
        if self.type == 'folder' and not serverPath.endswith('/'):
            serverPath = serverPath + '/' # copy all files in the folder to the local path, exluding the folder structure

        flag = rsync(serverPath, localPath)
        if flag: self.loaded = True
        else: self.loaded = False

        return flag


    def getModel(self):
        try:
            modelClass = modelClassDict[self.type]
            model = modelClass(self.localPath, self.name, parentModel=self.parentModel)
        except:
            return None
        else:
            return model
        
    def length(self):
        assert self.loaded
        return self.model.length()

    def getData(self, idx):
        assert self.loaded
        return self.model.getData(idx)
    
    def getImg(self, idx):
        assert self.loaded
        return self.model.getImg(idx)
    
    def getImgName(self, idx):
        assert self.loaded
        return self.model.getImgName(idx)

    def getRootPath(self):
        return self.path

    def getImgInfo(self, idx):
        assert self.loaded
        rootPath = self.getRootPath()
        idx = idx

        if self.type == 'folder':
            imgFileName = os.path.split(self.model.getImgInfo(idx)['path'])[1]
            path = os.path.join(rootPath, imgFileName)
        elif self.type == 'video' or self.type == 'ppm':
            path = rootPath + f':{idx}'
        
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath):
        raise NotImplemented()


    