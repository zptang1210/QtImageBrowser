import numpy as np
import cv2
from utils.transformers.Transform_base import Transform_base


class Transform_trackerBase(Transform_base):
    def __init__(self):
        super().__init__()
    
    def visualizeImgWithBbox(self, frame, bbox, hide_bbox=False):
        frame = np.uint8(frame)
        if not hide_bbox:
            frame = cv2.rectangle(frame,
                                (bbox[0], bbox[1]),
                                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                                (255, 0, 0), 2)

        return frame

    def visualizeBboxInFixedPosition(self, frame, bbox, frame_size, init_bbox, hide_bbox=False):
        x0, y0, w, h = bbox
        bbox_ = np.array([[x0, y0], [x0+w, y0], [x0+w, y0+h], [x0, y0+h]])
        x0, y0, w, h = init_bbox
        init_bbox_ = np.array([[x0, y0], [x0+w, y0], [x0+w, y0+h], [x0, y0+h]])

        ha, status = cv2.findHomography(bbox_, init_bbox_)
        frame_warped = cv2.warpPerspective(frame, ha, (frame_size[1], frame_size[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0)) # frame_size: (H, W)
        
        if not hide_bbox:
            p1 = (int(init_bbox[0]), int(init_bbox[1]))
            p2 = (int(init_bbox[0] + init_bbox[2]), int(init_bbox[1] + init_bbox[3]))
            cv2.rectangle(frame_warped, p1, p2, (255,0,0), 2, 1)

        return frame_warped


    def visualizeBboxInCenterPosition(self, frame, bbox, frame_size, hide_bbox=False):
        _, _, bbox_w, bbox_h = bbox
        frame_h, frame_w = frame_size # frame_size: (H, W)
        center_bbox = (int(frame_w/2 - bbox_w/2), int(frame_h/2 - bbox_h/2), bbox_w, bbox_h)
        frame_warped = self.visualizeBboxInFixedPosition(frame, bbox, frame_size, center_bbox, hide_bbox)
        return frame_warped