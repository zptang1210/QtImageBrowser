import os
from models.ImageCollectionModel import ImageCollectionModel
from utils.rsyncWrapper import rsync
from configs.availTypesConfig import availTypes
from configs.availTypesConfig import modelClassDict

class ImageCollectionCloudModel(ImageCollectionModel):
    DEFAULT_LOCAL_ROOT_PATH = os.path.normpath(os.path.join('.', 'tmp'))

    def __init__(self, path, name, type, localPath=None, preload=True, parentModel=None):
        super().__init__()
        self.path = path
        self.name = name
        self.type = type
        assert self.type in availTypes
        self.parentModel = parentModel

        if localPath is None:
            self.localPath = os.path.join(ImageCollectionCloudModel.DEFAULT_LOCAL_ROOT_PATH, name)
        else:
            self.localPath = localPath
        self.localPath = os.path.normpath(self.localPath)

        self.serverAddr = self.path.split(':')[0]
        
        if preload:
            flag = self.load(self.path, self.localPath)
            self.loaded = True
            if flag == False:
                raise RuntimeError('Unable to load the image collection from the server.')
        
            self.model = self.getModel()
        else:
            self.loaded = False
            self.model = None


    def load(self, serverPath, localPath):
        if self.type == 'folder' and not serverPath.endswith('/'):
            serverPath = serverPath + '/' # copy all files in the folder to the local path, exluding the folder structure

        cmd = f'rsync -a --delete {serverPath} {localPath}'      #rsync -av --delete xxx@gypsum.cs.umass.edu:~/testData /Users/xxx/Desktop/tmp
        flag = rsync(cmd)
        if flag: self.loaded = True
        else: self.loaded = False

        return flag


    def getModel(self):
        modelClass = modelClassDict[self.type]
        model = modelClass(self.localPath, self.name, parentModel=self.parentModel)
        return model
        
    def length(self):
        assert self.loaded
        return self.model.length()
    
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


if __name__ == '__main__':
    model = ImageCollectionCloudModel('zhipengtang@gypsum.cs.umass.edu:~/testData/batch_00002_0', 'testData')
    