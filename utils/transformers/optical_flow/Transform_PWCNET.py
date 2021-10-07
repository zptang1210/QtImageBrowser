import numpy as np
import torch
from utils.transformers.optical_flow.Transform_opticalFlowFramework import Transform_opticalFlowFramework
from .thirdparty.pytorch_pwc.run import estimate

class Transform_PWCNET(Transform_opticalFlowFramework):
    command = 'pwcnet'

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        return super().getArgParser()

    def initOpticalFlowAlgorithm(self, model, args):
        pass

    def computeOpticalFlow(self, img1, img2):
        img1 = img1[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) * (1.0 / 255.0)
        img2 = img2[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) * (1.0 / 255.0)

        tensor1 = torch.FloatTensor(np.ascontiguousarray(img1))
        tensor2 = torch.FloatTensor(np.ascontiguousarray(img2))

        outputTensor = estimate(tensor1, tensor2) # channel, height, width

        outputArray = outputTensor.numpy().transpose(1, 2, 0).astype(np.float32)

        return outputArray
        
