import os
import time
import cv2
from utils.interactTools.Interact_base import Interact_base

class Interact_selectROI(Interact_base):
    command = 'selectROI'

    def __init__(self):
        super().__init__()

    def interact(self, model):
        image, _ = model.get(0)
        temp_root_path = os.path.abspath(os.path.join('.', 'tmp', 'interactToolTmp'))
        if not os.path.exists(temp_root_path):
            os.makedirs(temp_root_path)

        randn_str = str(time.time())
        temp_image_name = 'selectROI_' + randn_str + '.jpg'

        temp_image_path = os.path.join(temp_root_path, temp_image_name)
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(temp_image_path, image_bgr)

        temp_output_name = 'selectROI_' + randn_str + '.txt'
        temp_output_path = os.path.join(temp_root_path, temp_output_name)

        selectROI_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selectROI.py')
        # Notice Qt cannot work with opencv's GUI functions together, so we have to use a separate python interpreter for cv2.selectROI
        os.system(' '.join(['python', selectROI_path, temp_image_path, temp_output_path]))

        with open(temp_output_path, 'r') as fin:
            bbox = fin.read().strip()
        print('bbox', bbox)

        os.remove(temp_output_path)
        os.remove(temp_image_path)

        return bbox
