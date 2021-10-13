from abc import abstractmethod

class Interact_base:
    command = None

    def __init__(self):
        pass

    @abstractmethod
    def interact(self, model):
        pass

    def run(self, model):
        result = self.interact(model)
        assert isinstance(result, str)
        return result