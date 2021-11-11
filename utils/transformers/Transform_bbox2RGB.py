import argparse
import numpy as np
import cv2
from utils.transformers.Transform_toBasicModel import Transform_toBasicModel

class Transform_bbox2RGB(Transform_toBasicModel):
    command = 'bbox2RGB'

    def __init__(self):
        super().__init__()


    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Argument parser for bbox2RGB')
        parser.add_argument('--mode', type=str, default='default', help='the visualization method (default/bboxfixed/bboxcentralized).')
        parser.add_argument('--hide_bbox', type=bool, default=False, help='hide the bbox in the output images.')
        return parser


    def processImageCollection(self, model, args):
        assert model.sourceModelTypeName == 'bbox'
        if args.mode not in ('default', 'bboxfixed', 'bboxcentralized'):
            raise ValueError('mode arg is invalid.')

        for i in range(model.length()):
            raw_img_np, bbox = model.getData(i)
            img_name = model.getImgName(i)
        
            if args.mode == 'default':
                yield model.getImg(i), img_name
            elif args.mode == 'bboxfixed':
                first_img_size = ((model.getData(0))[0]).shape # H, W, C
                init_bbox = (model.getData(0))[1]
                yield self.visualizeBboxInFixedPosition(raw_img_np, bbox, first_img_size[:2], init_bbox, hide_bbox=args.hide_bbox), img_name
            elif args.mode == 'bboxcentralized':
                first_img_size = ((model.getData(0))[0]).shape # H, W, C
                yield self.visualizeBboxInCenterPosition(raw_img_np, bbox, first_img_size[:2], hide_bbox=args.hide_bbox), img_name


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
