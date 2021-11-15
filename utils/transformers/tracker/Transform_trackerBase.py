from utils.transformers.Transform_toBboxModel import Transform_toBboxModel


class Transform_trackerBase(Transform_toBboxModel):
    def __init__(self):
        super().__init__()
