import os
from glob import glob
from PIL import Image
import numpy as np
from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionFolderModel(ImageCollectionModel):
    def __init__(self, path, name, rootModel=None):
        super().__init__()
        self.path = path
        self.name = name
        self.rootModel = rootModel

        self.imgList = glob(os.path.join(self.path, '*.png')) + \
            glob(os.path.join(self.path, '*.jpg')) + \
            glob(os.path.join(self.path, '*.jpeg')) + \
            glob(os.path.join(self.path, '*.tiff')) + \
            glob(os.path.join(self.path, '*.tif')) + \
            glob(os.path.join(self.path, '*.bmp'))

        self.imgList = sorted(self.imgList)

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

    def getImgPath(self, idx):
        return self.imgList[idx]

    @staticmethod
    def saveModel(modelToSave, savePath):
        if not os.path.exists(savePath):
            os.makedirs(savePath) 
        
        for idx in range(modelToSave.length()):
            img_np, name = modelToSave.get(idx)
            img_pil = Image.fromarray(img_np)
            img_pil.save(os.path.join(savePath, name+'.jpg'))
        
        return True
