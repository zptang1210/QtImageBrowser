import os
from glob import glob
import numpy as np
import cv2
from utils.pathUtils import normalizePath
from models.ImageCollectionCompoundModel import ImageCollectionCompoundModel

class ImageCollectionBboxModel(ImageCollectionCompoundModel):
    def __init__(self, path, name, parentModel=None):
        super().__init__()
        assert path == normalizePath(path)
        self.path = path
        self.name = name
        self.parentModel = parentModel
        self.sourceModel = self
        self.sourceModelTypeName = 'bbox'

        self.imgList = glob(os.path.join(self.path, '*.png')) + \
            glob(os.path.join(self.path, '*.jpg')) + \
            glob(os.path.join(self.path, '*.jpeg')) + \
            glob(os.path.join(self.path, '*.tiff')) + \
            glob(os.path.join(self.path, '*.tif')) + \
            glob(os.path.join(self.path, '*.bmp'))

        self.imgList = list(map(normalizePath, self.imgList))
        self.imgList = sorted(self.imgList)

        self.bboxes = dict()
        try:
            with open(os.path.join(path, 'bboxes.txt'), 'r') as fin:
                for line in fin:
                    res = line.split()
                    assert len(res) == 5
                    img_name = res[0]
                    # (x, y) is the left corner, where x is for width, y is for height. w and h are width and height, respectively.
                    x, y, w, h = int(res[1]), int(res[2]), int(res[3]), int(res[4]) 

                    assert img_name in list(map(os.path.basename, self.imgList))
                    self.bboxes[img_name] = (x, y, w, h)
        except:
            print('Error occurs during loading bbox information.')
            raise

        try:
            for imgPath in self.imgList:
                assert os.path.basename(imgPath) in self.bboxes.keys()
        except:
            print('Bboxes don\'t match images')
            raise

    def length(self):
        return len(self.imgList)

    def readImg(self, imgPath):
        image_np = cv2.imread(imgPath, cv2.IMREAD_COLOR)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        return image_np

    def getImg(self, idx):
        assert idx >= 0 and idx < self.length()
        image_np = self.readImg(self.imgList[idx])
        # image_np = np.uint8(image_np) # TODO: I believe this line is not necessary, but need more test before del it.
        bbox = self.bboxes[os.path.basename(self.imgList[idx])]
        image_np = cv2.rectangle(image_np,
                                (bbox[0], bbox[1]),
                                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                                (255, 0, 0), 2)

        return image_np

    def getData(self, idx):
        return self.readImg(self.imgList[idx]), self.bboxes[os.path.basename(self.imgList[idx])]

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return os.path.splitext(os.path.basename(self.imgList[idx]))[0]

    def getRootPath(self):
        return self.path

    def getImgInfo(self, idx):
        path = self.imgList[idx]
        rootPath = self.getRootPath()
        idx = idx
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath):
        modelToSaveTypeName = modelToSave.sourceModelTypeName
        if modelToSaveTypeName != 'bbox':
            return False

        if not os.path.exists(savePath):
            os.makedirs(savePath)
        else:
            return False

        try:
            with open(os.path.join(savePath, 'bboxes.txt'), 'w') as fout:
                for idx in range(modelToSave.length()):
                    img_np, bbox = modelToSave.getData(idx)
                    img_name = modelToSave.getImgName(idx)
                    
                    cv2.imwrite(os.path.join(savePath, img_name+'.jpg'), cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
                    fout.write(f'{img_name}.jpg {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n')
        except:
            print('Error occurs during saving images and bboxes.')
            # return False
            raise
        else:
            return True
