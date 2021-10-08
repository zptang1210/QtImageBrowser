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

    def visualizeBboxInFixedPosition(self, frame, bbox, init_frame, init_bbox):
        x0, y0, w, h = bbox
        bbox_ = np.array([[x0, y0], [x0+w, y0], [x0+w, y0+h], [x0, y0+h]])
        x0, y0, w, h = init_bbox
        init_bbox_ = np.array([[x0, y0], [x0+w, y0], [x0+w, y0+h], [x0, y0+h]])

        ha, status = cv2.findHomography(bbox_, init_bbox_)
        frame_warped = cv2.warpPerspective(frame, ha, (init_frame.shape[1], init_frame.shape[0]), borderMode=cv2.BORDER_REPLICATE)
        
        p1 = (int(init_bbox[0]), int(init_bbox[1]))
        p2 = (int(init_bbox[0] + init_bbox[2]), int(init_bbox[1] + init_bbox[3]))
        cv2.rectangle(frame_warped, p1, p2, (255,0,0), 2, 1)

        return frame_warped