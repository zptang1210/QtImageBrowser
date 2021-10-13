import cv2
from multiprocessing import Process, Queue
from utils.interactTools.Interact_base import Interact_base

class Interact_selectROI(Interact_base):
    command = 'selectROI'

    def __init__(self):
        super().__init__()

    def selectROI(queue, frame, flag):
        bbox = cv2.selectROI(frame, flag)
        queue.put(bbox)

    def interact(self, model):
        image, _ = model.get(0)
        image_ = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # CAUTIOUS: Now the image browser supports multithreading. This makes the following line fail because opencv only allow window related functions to run on the main thread.
        # Thus you need to use a new process to run window related functions!
        queue = Queue()
        p = Process(target=Interact_selectROI.selectROI, args=(queue, image_, False))
        p.start()
        p.join()
        bbox = queue.get(True)

        if bbox == (0, 0, 0, 0):
            bbox_res = None
        else:
            bbox_res = f'{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}'

        print('bbox', bbox_res)
        return bbox_res
