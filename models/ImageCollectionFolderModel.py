import os
from glob import glob
from PIL import Image
import numpy as np
from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionFolderModel(ImageCollectionModel):
    def __init__(self, path, name, parentModel=None):
        super().__init__()
        self.path = os.path.normpath(path)
        self.name = name
        self.parentModel = parentModel

        self.imgList = glob(os.path.join(self.path, '*.png')) + \
            glob(os.path.join(self.path, '*.jpg')) + \
            glob(os.path.join(self.path, '*.jpeg')) + \
            glob(os.path.join(self.path, '*.tiff')) + \
            glob(os.path.join(self.path, '*.tif')) + \
            glob(os.path.join(self.path, '*.bmp'))

        self.imgList = list(map(os.path.normpath, self.imgList))
        self.imgList = sorted(self.imgList)

    def length(self):
        return len(self.imgList)

    def getImg(self, idx):
        assert idx >= 0 and self.length()
        image_pil = Image.open(self.imgList[idx])
        image_pil = image_pil.convert('RGB')
        image_np = np.asarray(image_pil)

        return image_np

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return os.path.splitext(os.path.basename(self.imgList[idx]))[0]

    def getRootPath(self):
        return os.path.normpath(self.path)

    def getImgInfo(self, idx):
        path = os.path.normpath(self.imgList[idx])
        rootPath = self.getRootPath()
        idx = idx
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath):
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        else:
            return False
        
        for idx in range(modelToSave.length()):
            img_np, name = modelToSave.get(idx)
            img_pil = Image.fromarray(img_np)
            img_pil.save(os.path.join(savePath, name+'.jpg'))
        
        return True
