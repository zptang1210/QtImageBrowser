import cv2
from abc import abstractmethod
import argparse
import numpy as np
from PIL import Image
from utils.transformers.Transform_base import Transform_base


class Transform_trackerBase(Transform_base):

    def __init__(self):
        super().__init__()

    # def getArgParser(self):
    #     parser = argparse.ArgumentParser(description='Argument parser for cvtColor')
    #     parser.add_argument('target', type=str, help='The target color (grey/color).')
    #     return parser

    def processImageCollection(self, model, args):
        print("processImageCollection")
        self.init(args)

        past_bbox = args.bbox
        for i in range(model.length()):
            img_np, img_name = model.get(i)
            bbox = self.update(img_np)
            if bbox is not None:
                past_bbox = bbox
            else:
                bbox = past_bbox
            yield self.visualize(img_np, bbox), img_name

        # targetColor = args.target
        # if targetColor not in ('grey', 'color'):
        #     raise ValueError('target arg is invalid.')
        # else:
        #     mode_pil = 'RGB' if targetColor == 'color' else 'L'
        #
        # imgNum = model.length()
        # for i in range(imgNum):
        #     img_np, img_name = model.get(i) # TODO: get a copy
        #     img_pil = Image.fromarray(img_np)
        #     img_pil = img_pil.convert(mode_pil)
        #
        #     yield np.asarray(img_pil), img_name

    def visualize(self, frame, bbox):
        frame = np.uint8(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.rectangle(frame,
                              (bbox[0], bbox[1]),
                              (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                              (255, 0, 0), 2)

        return frame

    @abstractmethod
    def init(self, args):
        pass

    @abstractmethod
    def update(self, frame):
        pass