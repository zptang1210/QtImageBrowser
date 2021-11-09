import cv2
from utils.transformers.optical_flow.Transform_opticalFlowFramework import Transform_opticalFlowFramework


class Transform_Farneback(Transform_opticalFlowFramework):
    command = 'farneback'

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        return super().getArgParser()

    def initOpticalFlowAlgorithm(self, model, args):
        return
    
    def computeOpticalFlow(self, img1, img1_name, img2, img2_name):
        img1_grey = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        img2_grey = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
        flow = cv2.calcOpticalFlowFarneback(img1_grey, img2_grey, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        return flow, img1_name