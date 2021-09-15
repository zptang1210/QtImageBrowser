import os
from models.ImageCollectionModel import ImageCollectionModel
from utils import PPMProcessor

class ImageCollectionPPMModel(ImageCollectionModel):
    def __init__(self, path, name):
        super().__init__()
        self.path = path
        self.name = name

        self.imgList = PPMProcessor.readSuperPPM(self.path)

    def length(self):
        return len(self.imgList)

    def getImg(self, idx):
        assert idx >= 0 and idx < len(self.imgList)
        image_np = self.imgList[idx]

        return image_np

    def getImgName(self, idx):
        assert idx >= 0 and idx < len(self.imgList)
        return ('%06d' % idx)

    def getRootPath(self):
        return os.path.dirname(self.path)

    @staticmethod
    def saveModel(modelToSave, savePath, numPerRow=10):
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