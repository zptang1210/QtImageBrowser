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