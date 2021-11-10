from abc import abstractmethod

class ImageCollectionModel:
    def __init__(self):
        self.path = None # path must pass this check: path == normalizePath(path)
        self.name = None
        self.parentModel = None
        self.sourceModel = None # the model where this object derive ,when the model is derived model; otherwise, self.
        self.sourceModelTypeName = None

    @abstractmethod
    def length(self):
        pass

    @abstractmethod
    def getRootPath(self):
        pass

    @abstractmethod
    def getData(self, idx):
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
