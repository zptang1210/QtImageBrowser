from abc import abstractmethod
import argparse
from utils.transformers.optical_flow.Transform_opticalFlowBase import Transform_opticalFlowBase


class Transform_opticalFlowFramework(Transform_opticalFlowBase):

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Base argument parser for optical flow')
        return parser

    def processImageCollection(self, model, args):
        self.initOpticalFlowAlgorithm(model, args)

        imgNum = model.length()
        assert imgNum > 2
        for i in range(imgNum-1):
            img1, img1_name = model.get(i)
            img2, img2_name = model.get(i+1)
            print(f'- processing {i}/{imgNum-1} - {img1_name} -> {img2_name}')

            flow, flow_name = self.computeOpticalFlow(img1, img1_name, img2, img2_name)
            yield flow, flow_name       

    @abstractmethod
    def initOpticalFlowAlgorithm(self, model, args):
        pass

    @abstractmethod
    def computeOpticalFlow(self, img1, img1_name, img2, img2_name):
        return None, None

