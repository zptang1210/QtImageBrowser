import numpy as np
import flow_vis
from utils.transformers.Transform_toOpticalFlowModel import Transform_toOpticalFlowModel

class Transform_opticalFlowBase(Transform_toOpticalFlowModel):

    def __init__(self):
        super().__init__()
