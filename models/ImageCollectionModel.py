from abc import abstractmethod


class ImageCollectionModel:
    def __init__(self):
        self.path = None
        self.name = None
        self.parentModel = None

    @abstractmethod
    def length(self):
        pass

    @abstractmethod
    def getRootPath(self):
        pass

    @abstractmethod
    def getImg(self, idx):
        pass

    @abstractmethod
    def getImgName(self, idx):
        pass

    @abstractmethod
    def getImgInfo(self, idx):
        pass

    def get(self, idx):
        img = self.getImg(idx)
        name = self.getImgName(idx)
        return img, name

    def getRootModel(self):
        if self.parentModel is None:
            return self
        else:
            return self.parentModel.getRootModel()

    def isRootModel(self):
        return self.parentModel is None

    @staticmethod
    def saveModel(modelToSave, savePath):
        pass
