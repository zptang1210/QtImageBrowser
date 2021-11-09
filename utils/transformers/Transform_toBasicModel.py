import os
from PIL import Image
from utils.transformers.Transform_base import Transform_base
from models.ImageCollectionFolderModel import ImageCollectionFolderModel

class Transform_toBasicModel(Transform_base):

    def __init__(self):
        super().__init__()

    def generateProcessedModel(self, fileGenerator, savePath, saveName):
        try:
            for img_np, img_name in fileGenerator:
                img_pil = Image.fromarray(img_np)
                img_pil.save(os.path.join(savePath, img_name+'.jpg'))
        except:
            print('Error occurs during generating files for the new model')
            raise

        try:
            newModel = ImageCollectionFolderModel(savePath, saveName)
        except:
            raise
        else:
            return newModel