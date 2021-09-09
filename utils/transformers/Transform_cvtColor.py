import argparse
import numpy as np
from PIL import Image
from utils.transformers.Transform_base import Transform_base


class Transform_cvtColor(Transform_base):
    command = 'cvtColor'

    def __init__(self):
        super().__init__()

    def getArgParser(self):
        parser = argparse.ArgumentParser(description='Argument parser for cvtColor')
        parser.add_argument('target', type=str, help='The target color (grey/color).')
        return parser

    def processImageCollection(self, model, args):
        targetColor = args.target
        if targetColor not in ('grey', 'color'):
            raise ValueError('target arg is invalid.')
        else:
            mode_pil = 'RGB' if targetColor == 'color' else 'L'

        imgNum = model.length()
        for i in range(imgNum):
            img_np, img_name = model.get(i) # TODO: get a copy
            img_pil = Image.fromarray(img_np)
            img_pil = img_pil.convert(mode_pil)

            yield np.asarray(img_pil), img_name
