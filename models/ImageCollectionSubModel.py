from models.ImageCollectionDerivedModel import ImageCollectionDerivedModel
from configs.availTypesConfig import modelNameDict

class ImageCollectionSubModel(ImageCollectionDerivedModel):
    def __init__(self, name, subItemIndexes, srcModel):
        super().__init__()
        self.sourceModel = srcModel
        self.sourceModelTypeName = modelNameDict[type(self.sourceModel)]

        self.parentModel = None # this property should not be used since we don't add sub models to the tree view widget
        self.path = None
        self.name = name

        self.subItemIndexes = subItemIndexes

    def length(self):
        return len(self.subItemIndexes)

    def getData(self, idx):
        assert idx >=0 and idx < self.length()
        return self.sourceModel.getData(self.subItemIndexes[idx])
    
    def getImg(self, idx):
        assert idx >= 0 and idx < self.length()
        return self.sourceModel.getImg(self.subItemIndexes[idx])

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return self.sourceModel.getImgName(self.subItemIndexes[idx])

    def getRootPath(self):
        raise NotImplemented()

    def getImgInfo(self, idx):
        return self.sourceModel.getImgInfo(self.subItemIndexes[idx])

    @staticmethod
    def saveModel(modelToSave, savePath):
        raise NotImplemented()