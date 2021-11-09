import numpy as np
from scipy import stats
import cv2
from utils.transformers.Transform_toBasicModel import Transform_toBasicModel



class Transform_modeSubtract(Transform_toBasicModel):
    command = 'mode'

    def __init__(self):
        super().__init__()
        self.mode = None

    def getArgParser(self):
        return None

    def processImageCollection(self, model, args):

        imgNum = model.length()
        if self.mode == None:
            imgs = []
            for i in range(imgNum):
                img_np, img_name = model.get(i) 
                imgs.append(img_np.copy())

            imgs = np.array(imgs)
            self.mode = self.create_mode(imgs)
            imgs = []


        for i in range(imgNum):
            img_np, img_name = model.get(i) 
            img = cv2.subtract(self.mode, img_np)
            yield img, img_name

    def create_mode(self, imgs):
        m =  stats.mode(imgs, axis=0)[0][0]
        return  m
        