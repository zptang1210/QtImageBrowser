import os
from utils.pathUtils import normalizePath
from models.ImageCollectionModel import ImageCollectionModel
from utils import PPMProcessor

class ImageCollectionPPMModel(ImageCollectionModel):
    def __init__(self, path, name, parentModel=None):
        super().__init__()
        assert path == normalizePath(path)
        self.path = path
        self.name = name
        self.parentModel = parentModel

        try:
            self.imgList = PPMProcessor.readSuperPPM(self.path)
        except:
            raise RuntimeError('Unable to load the ppm file.')

    def length(self):
        return len(self.imgList)

    def getImg(self, idx):
        assert idx >= 0 and idx < self.length()
        image_np = self.imgList[idx]

        return image_np

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return ('%06d' % idx)

    def getRootPath(self):
        return normalizePath(os.path.dirname(self.path))

    def getImgInfo(self, idx):
        path = self.path + f':{idx}'
        rootPath = self.getRootPath()
        idx = idx
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath, numPerRow=10):
        if os.path.exists(savePath): return False 

        img_list = []
        for idx in range(modelToSave.length()):
            img_np = modelToSave.getImg(idx)
            img_list.append(img_np)

        img_shape = img_list[0].shape
        for img_np in img_list:
            if img_np.shape != img_shape:
                return False
        
        PPMProcessor.writeSuperPPM(img_list, savePath, numPerRow=numPerRow)
        return True