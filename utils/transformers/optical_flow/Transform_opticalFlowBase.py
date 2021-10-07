import numpy as np
import flow_vis
from utils.transformers.Transform_base import Transform_base

class Transform_opticalFlowBase(Transform_base):

    def __init__(self):
        super().__init__()

    def flowToImage(self, flow):
        return flow_vis.flow_to_color(flow)
    
    def averageFlows(self, flows):
        flows = np.stack(flows, axis=0)
        flow_mean = flows.mean(axis=0)
        return flow_mean