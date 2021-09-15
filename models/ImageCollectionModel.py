from abc import abstractmethod


class ImageCollectionModel:
    def __init__(self):
        pass

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

    def get(self, idx):
        img = self.getImg(idx)
        name = self.getImgName(idx)
        return img, name

    @staticmethod
    def saveModel(modelToSave, savePath):
        pass
