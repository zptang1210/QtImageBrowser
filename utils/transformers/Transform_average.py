import numpy as np
from utils.transformers.Transform_base import Transform_base

class Transform_average(Transform_base):
    command = 'average'

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        return None

    def processImageCollection(self, model, args):
        imgs = []
        imgNum = model.length()
        for i in range(imgNum):
            img_np, _ = model.get(i)
            imgs.append(img_np)
        imgs = np.stack(imgs, axis=0)
        img_mean = imgs.mean(axis=0).astype(np.uint8)
        
        yield img_mean, 'mean'
