import cv2
from utils.interactTools.Interact_base import Interact_base

class Interact_selectROI(Interact_base):
    command = 'selectROI'

    def __init__(self):
        super().__init__()

    def interact(self, model):
        image, _ = model.get(0)
        image_ = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        bbox = cv2.selectROI(image_, False)
        if bbox == (0, 0, 0, 0):
            bbox_res = None
        else:
            bbox_res = f'{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}'

        print('bbox', bbox_res)
        return bbox_res
