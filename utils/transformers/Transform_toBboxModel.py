import os
import cv2
from utils.transformers.Transform_base import Transform_base
from models.ImageCollectionBboxModel import ImageCollectionBboxModel

class Transform_toBboxModel(Transform_base):

    def __init__(self):
        super().__init__()

    def generateProcessedModel(self, fileGenerator, savePath, saveName):
        try:
            with open(os.path.join(savePath, 'bboxes.txt'), 'w') as fout:
                for img_np, img_name, bbox in fileGenerator:
                    cv2.imwrite(os.path.join(savePath, img_name+'.jpg'), cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
                    fout.write(f'{img_name}.jpg {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n')
        except:
            print('Error occurs during generating files for the new model')
            raise

        try:
            newModel = ImageCollectionBboxModel(savePath, saveName)
        except:
            print('Error occurs during loading the new model from processed files.')
            raise
        else:
            return newModel