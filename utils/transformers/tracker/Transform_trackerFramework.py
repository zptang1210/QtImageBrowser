from abc import abstractmethod
import argparse
from utils.transformers.tracker.Transform_trackerBase import Transform_trackerBase


class Transform_trackerFramework(Transform_trackerBase):

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Base argument parser for tracker')
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

            yield img_np, img_name, bbox

    @abstractmethod
    def initTracker(self, args):
        pass

    @abstractmethod
    def update(self, frame):
        pass