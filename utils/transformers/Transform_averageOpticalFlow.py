import numpy as np
from utils.transformers.Transform_toOpticalFlowModel import Transform_toOpticalFlowModel

class Transform_averageOpticalFlow(Transform_toOpticalFlowModel):
    command = 'averageOpticalFlow'

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        return None

    def processImageCollection(self, model, args):
        flows = []
        
        for idx in range(model.length()):
            flow = model.getData(idx)
            flows.append(flow)
        floMean = self.averageFlows(flows)
        yield floMean, 'mean_optical_flow'

    def averageFlows(self, flows):
        flows = np.stack(flows, axis=0)
        flow_mean = flows.mean(axis=0)
        return flow_mean 