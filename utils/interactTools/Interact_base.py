from abc import abstractmethod
from multiprocessing import Process, Queue

class Interact_base:
    command = None

    def __init__(self):
        pass

    @abstractmethod
    def interact(self, model):
        pass

    def interactSubProcess(self, model, queue):
        result = self.interact(model)
        queue.put(result)

    def run(self, model):
        queue = Queue()
        p = Process(target=self.interactSubProcess, args=(model, queue))
        p.start()
        p.join()
        result = queue.get(True)
        return result