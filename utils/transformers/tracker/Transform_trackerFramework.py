from abc import abstractmethod
import argparse
from utils.transformers.tracker.Transform_trackerBase import Transform_trackerBase


class Transform_trackerFramework(Transform_trackerBase):

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Base argument parser for tracker')
        parser.add_argument('--vis', type=str, default='img', help='the visualization method (img/bboxfixed).')
        parser.add_argument('--bbox', nargs='+', type=int, help='the coordinates of the initial bounding box.')
        parser.add_argument('--hide_bbox', type=bool, default=False, help='hide the bbox in the output images.')
        return parser

    def processImageCollection(self, model, args):
        self.initTracker(args)

        past_bbox = args.bbox
        for i in range(model.length()):
            img_np, img_name = model.get(i)
            bbox = self.update(img_np)
            if bbox is not None:
                past_bbox = bbox
            else:
                bbox = past_bbox
            # yield self.visualize(img_np, bbox, args.bbox, args.vis), img_name

            if args.vis == 'img':
                yield self.visualizeImgWithBbox(img_np, bbox, hide_bbox=args.hide_bbox), img_name
            elif args.vis == 'bboxfixed':
                first_img_size = model.getImg(0).shape # H, W, C
                yield self.visualizeBboxInFixedPosition(img_np, bbox, first_img_size[:2], args.bbox, hide_bbox=args.hide_bbox), img_name
            elif args.vis == 'bboxcenterized':
                first_img_size = model.getImg(0).shape # H, W, C
                yield self.visualizeBboxInCenterPosition(img_np, bbox, first_img_size[:2], hide_bbox=args.hide_bbox), img_name                
            else:
                raise ValueError('invalid vis argument.')

    @abstractmethod
    def initTracker(self, args):
        pass

    @abstractmethod
    def update(self, frame):
        pass