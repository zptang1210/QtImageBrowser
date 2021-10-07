import flow_vis
from utils.transformers.Transform_base import Transform_base

class Transform_opticalFlowBase(Transform_base):

    def __init__(self):
        super().__init__()

    def flowToImage(self, flo):
        return flow_vis.flow_to_color(flo)
        