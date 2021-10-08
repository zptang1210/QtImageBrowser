import numpy as np
import cv2
from utils.transformers.Transform_base import Transform_base


class Transform_trackerBase(Transform_base):
    def __init__(self):
        super().__init__()
    
    def visualizeImgWithBbox(self, frame, bbox):
        frame = np.uint8(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.rectangle(frame,
                              (bbox[0], bbox[1]),
                              (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                              (255, 0, 0), 2)

        return frame        