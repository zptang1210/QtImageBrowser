import os
from glob import glob
from PIL import Image
import numpy as np
from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionFolderModel(ImageCollectionModel):
    def __init__(self, path, name):
        super().__init__()
        self.path = path
        self.name = name

        self.imgList = glob(os.path.join(self.path, '*.png')) + \
            glob(os.path.join(self.path, '*.jpg')) + \
            glob(os.path.join(self.path, '*.jpeg')) + \
            glob(os.path.join(self.path, '*.tiff')) + \
            glob(os.path.join(self.path, '*.tif')) + \
            glob(os.path.join(self.path, '*.bmp'))

    def length(self):
        return len(self.imgList)

    def getImg(self, idx):
        assert idx >= 0 and idx < len(self.imgList)
        image_pil = Image.open(self.imgList[idx])
        image_pil = image_pil.convert('RGB')
        image_np = np.asarray(image_pil)

        return image_np

    def getImgName(self, idx):
        assert idx >= 0 and idx < len(self.imgList)
        return os.path.splitext(os.path.basename(self.imgList[idx]))[0]

    def getRootPath(self):
        return self.path