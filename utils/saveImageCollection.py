import os
from models.ImageCollectionPPMModel import ImageCollectionPPMModel
from models.ImageCollectionVideoModel import ImageCollectionVideoModel
from models.ImageCollectionFolderModel import ImageCollectionFolderModel


def saveImageCollection(modelToSave, savePath, targetType):
    assert targetType in ('folder', 'video', 'ppm')
    modelClassDict = {'folder': ImageCollectionFolderModel, 'video': ImageCollectionVideoModel,'ppm': ImageCollectionPPMModel}
    flag = modelClassDict[targetType].saveModel(modelToSave, savePath)
    return flag