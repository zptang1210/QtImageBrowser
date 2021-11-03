from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionBasicModel(ImageCollectionModel):
    def __init__(self):
        super().__init__()

    def getData(self, idx):
        return self.getImg(idx)
