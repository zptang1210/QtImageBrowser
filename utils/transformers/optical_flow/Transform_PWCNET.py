import numpy as np
import torch
from utils.transformers.Transform_base import Transform_base
import flow_vis
from .thirdparty.pytorch_pwc.run import estimate

class Transform_PWCNET(Transform_base):
    command = 'pwcnet'

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        None

    def processImageCollection(self, model, args):
        imgNum = model.length()
        assert imgNum > 0

        for i in range(imgNum-1):
            print(f'- processing {i}/{imgNum-1}')

            firstImg, firstImgName = model.get(i)
            secondImg, _ = model.get(i+1)

            firstImg = firstImg[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) * (1.0 / 255.0)
            secondImg = secondImg[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) * (1.0 / 255.0)

            firstTensor = torch.FloatTensor(np.ascontiguousarray(firstImg))
            secondTensor = torch.FloatTensor(np.ascontiguousarray(secondImg))

            outputTensor = estimate(firstTensor, secondTensor) # channel, height, width

            outputArray = outputTensor.numpy().transpose(1, 2, 0).astype(np.float32)
            
            vis = flow_vis.flow_to_color(outputArray)

            yield vis, firstImgName



