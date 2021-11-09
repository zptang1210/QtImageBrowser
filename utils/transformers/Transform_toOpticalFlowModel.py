import os
import utils.opticalFlowUtils as ofUtils
from utils.transformers.Transform_base import Transform_base
from models.ImageCollectionOpticalFlowModel import ImageCollectionOpticalFlowModel

class Transform_toOpticalFlowModel(Transform_base):

    def __init__(self):
        super().__init__()

    def generateProcessedModel(self, fileGenerator, savePath, saveName):
        try:
            for flow, name in fileGenerator:
                ofUtils.write_flow(flow, os.path.join(savePath, name+'.flo'))
        except:
            print('Error occurs during generating files for the new model')
            raise

        try:
            newModel = ImageCollectionOpticalFlowModel(savePath, saveName)
        except:
            print('Error occurs during loading the new model from processed files.')
            raise
        else:
            return newModel