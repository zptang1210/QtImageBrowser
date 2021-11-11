from enum import Enum
from models.ImageCollectionBboxModel import ImageCollectionBboxModel
from models.ImageCollectionOpticalFlowModel import ImageCollectionOpticalFlowModel
from models.ImageCollectionPPMModel import ImageCollectionPPMModel
from models.ImageCollectionVideoModel import ImageCollectionVideoModel
from models.ImageCollectionFolderModel import ImageCollectionFolderModel

FileType = Enum('FileType', ('folder', 'file'))
ModelType = Enum('modelType', ('basic', 'compound'))

availTypes = ('folder', 'video', 'ppm', 'opticalFlow', 'bbox')
TypeProperty = {'folder': {'fileType': FileType.folder, 'extension': None, 'modelType': ModelType.basic, 'fileDlgHint': ''},
                'video': {'fileType': FileType.file, 'extension': ['.mp4', '.avi'], 'modelType': ModelType.basic, 'fileDlgHint': 'Videos (*.mp4 *.avi)'},
                'ppm': {'fileType': FileType.file, 'extension': ['.ppm'], 'modelType': ModelType.basic, 'fileDlgHint': 'PPM Image (*.ppm)'},
                'opticalFlow': {'fileType': FileType.folder, 'extension': None, 'modelType': ModelType.compound, 'fileDlgHint': ''}, 
                'bbox': {'fileType': FileType.folder, 'extension': None, 'modelType': ModelType.compound, 'fileDlgHint': ''}
               }
modelClassDict = {'folder': ImageCollectionFolderModel, 'video': ImageCollectionVideoModel, 'ppm': ImageCollectionPPMModel,
                  'opticalFlow': ImageCollectionOpticalFlowModel, 'bbox': ImageCollectionBboxModel}
modelNameDict = {modelCls: name for name, modelCls in modelClassDict.items()}