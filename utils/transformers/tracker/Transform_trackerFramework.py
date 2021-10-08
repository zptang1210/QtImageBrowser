from abc import abstractmethod
import argparse
from utils.transformers.tracker.Transform_trackerBase import Transform_trackerBase


class Transform_trackerFramework(Transform_trackerBase):

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Base argument parser for tracker')
        parser.add_argument('--vis', type=str, default='img', help='the visualization method (img/bboxonly/bboxfixed).')
        parser.add_argument('--bbox', nargs='+', type=int, help='the coordinates of the initial bounding box.')
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
                yield self.visualizeImgWithBbox(img_np, bbox), img_name
            elif args.vis == 'bboxonly':
                raise NotImplemented()
            elif args.vis == 'bboxfixed':
                yield self.visualizeImgWithBbox(img_np, bbox, model.getImg(0), args.bbox)
            else:
                raise ValueError('invalid vis argument.')

    @abstractmethod
    def initTracker(self, args):
        pass

    @abstractmethod
    def update(self, frame):
        pass