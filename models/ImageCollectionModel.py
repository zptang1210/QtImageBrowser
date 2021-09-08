from abc import abstractmethod


class ImageCollectionModel:
    def __init__(self):
        pass

    @abstractmethod
    def length(self):
        pass

    @abstractmethod
    def get(self, idx):
        pass