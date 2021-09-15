import os
import cv2
from decord import VideoReader
from decord import cpu

from models.ImageCollectionModel import ImageCollectionModel


class ImageCollectionVideoModel(ImageCollectionModel):
    def __init__(self, path, name, rootModel=None):
        super().__init__()
        self.path = path
        self.name = name
        self.rootModel = rootModel

        self.vr = VideoReader(self.path, ctx=cpu(0))

    def length(self):
        return len(self.vr)

    def getImg(self, idx):
        assert idx >= 0 and idx < self.length()
        frame = self.vr[idx].asnumpy()
        return frame

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return 'frame_' + ('%06d' % idx)

    def getRootPath(self):
        return os.path.dirname(self.path)

    @staticmethod
    def saveModel(modelToSave, savePath, fps=30):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        img_size = modelToSave.getImg(0).shape
        size = img_size[:2]
        out = cv2.VideoWriter(savePath, fourcc, fps, (size[1], size[0]))
        try:
            for idx in range(modelToSave.length()):
                img_np = modelToSave.getImg(idx)
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                out.write(img_np)
        except:
            return False
        finally:
            out.release()
            
        return True