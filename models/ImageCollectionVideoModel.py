import os
import cv2
from decord import VideoReader
from decord import cpu

from models.ImageCollectionModel import ImageCollectionModel


class ImageCollectionVideoModel(ImageCollectionModel):
    def __init__(self, path, name, parentModel=None):
        super().__init__()
        self.path = os.path.normpath(path)
        self.name = name
        self.parentModel = parentModel

        try:
            self.vr = VideoReader(self.path, ctx=cpu(0))
        except:
            raise RuntimeError('Unable to load the video file.')

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
        return os.path.normpath(os.path.dirname(self.path))

    def getImgInfo(self, idx):
        path = os.path.normpath(self.path) + f':{idx}'
        rootPath = self.getRootPath()
        idx = idx
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath, fps=30):
        if os.path.exists(savePath): return False

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