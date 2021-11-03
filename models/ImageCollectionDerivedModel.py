from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionDerivedModel(ImageCollectionModel):
    def __init__(self):
        super().__init__()
        self.sourceModel = None # the model where this object derive
