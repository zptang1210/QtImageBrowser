import os
from decord import VideoReader
from decord import cpu

from models.ImageCollectionModel import ImageCollectionModel


class ImageCollectionVideoModel(ImageCollectionModel):
    def __init__(self, path, name):
        super().__init__()
        self.path = path
        self.name = name

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
