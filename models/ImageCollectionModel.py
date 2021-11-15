from abc import abstractmethod

class ImageCollectionModel:
    def __init__(self):
        self.path = None # path must pass this check: path == normalizePath(path)
        self.name = None
        # the model which this object computed from, this property is used for the tree view widget for opened model.
        # if parentModel is None, it should be a root model in the widget, otherwise, it should be a child of the root parent model.
        self.parentModel = None
        # the model where this object derive, when the model is a derived model; otherwise, self.
        # e.g. for sub model, sourceModel is the model where all subitems are; for cloud model, sourceModel is the backend model for this wrapper model.
        # for other types, because they are not derived from any other models, we assign self to it, but this property is not recommended to be used in this case.
        self.sourceModel = None
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
