import os
from glob import glob
from models.ImageCollectionDerivedModel import ImageCollectionDerivedModel
import utils.opticalFlowUtils as ofUtils
from utils.pathUtils import normalizePath
from models.ImageCollectionCompoundModel import ImageCollectionCompoundModel

class ImageCollectionOpticalFlowModel(ImageCollectionCompoundModel):
    def __init__(self, path, name, parentModel=None):
        super().__init__()
        assert path == normalizePath(path)
        self.path = path
        self.name = name
        self.parentModel = parentModel
        self.sourceModel = self
        self.sourceModelTypeName = 'opticalFlow'

        self.ofList = glob(os.path.join(self.path, '*.flo'))
        self.ofList = list(map(normalizePath, self.ofList))
        self.ofList = sorted(self.ofList)

    def length(self):
        return len(self.ofList)

    def getImg(self, idx):
        assert idx >= 0 and idx < self.length()
        flow = ofUtils.read_flow(self.ofList[idx])
        img = ofUtils.flow_to_image(flow)
        return img

    def getData(self, idx):
        assert idx >= 0 and idx < self.length()
        flow = ofUtils.read_flow(self.ofList[idx])
        return flow

    def getImgName(self, idx):
        assert idx >= 0 and idx < self.length()
        return os.path.splitext(os.path.basename(self.ofList[idx]))[0]

    def getRootPath(self):
        return self.path

    def getImgInfo(self, idx):
        path = self.ofList[idx]
        rootPath = self.getRootPath()
        idx = idx
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath):
        modelToSaveTypeName = modelToSave.sourceModelTypeName
        if modelToSaveTypeName != 'opticalFlow':
            return False

        if not os.path.exists(savePath):
            os.makedirs(savePath)
        else:
            return False

        try:
            for idx in range(modelToSave.length()):
                flow = modelToSave.getData(idx)
                name = modelToSave.getImgName(idx)
                ofUtils.write_flow(flow, os.path.join(savePath, name+'.flo'))
        except:
            print('error happens during saving the model to optical flow files.')
            return False

        return True