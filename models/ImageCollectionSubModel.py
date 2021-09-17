import os
from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionSubModel(ImageCollectionModel):
    def __init__(self, name, subItemIndexes, parentModel):
        super().__init__()
        self.parentModel = parentModel
        self.path = None
        self.name = name

        self.subItemIndexes = subItemIndexes

    def length(self):
        return len(self.subItemIndexes)
    
    def getImg(self, idx):
        assert idx >= 0 and idx < self.length()
        return self.parentModel.getImg(self.subItemIndexes[idx])

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return self.parentModel.getImgName(self.subItemIndexes[idx])

    def getRootPath(self):
        raise NotImplemented()

    def getImgInfo(self, idx):
        return self.parentModel.getImgInfo(self.subItemIndexes[idx])

    @staticmethod
    def saveModel(modelToSave, savePath):
        raise NotImplemented()