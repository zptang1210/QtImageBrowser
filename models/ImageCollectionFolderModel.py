from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionFolderModel(ImageCollectionModel):
    def __init__(self, folderPath):
        super().__init__()