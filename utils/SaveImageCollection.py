import os
from PyQt5 import QtCore
from utils.pathUtils import getPathType, PathType
from utils.rsyncWrapper import rsync
from configs.availTypesConfig import availTypes
from configs.availTypesConfig import modelClassDict

class SaveSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(bool)

class SaveImageCollection(QtCore.QRunnable):
    def __init__(self, modelToSave, savePath, targetType):
        super().__init__()
        self.modelToSave = modelToSave
        self.savePath = savePath
        assert targetType in availTypes
        self.targetType = targetType

        self.signals = SaveSignals()
    
    @QtCore.pyqtSlot()
    def run(self):
        # check if the path is to the server, if yes, save model to a temp place and then upload it.
        # If modelToSave is a cloud type, and the path is also a cloud path, copy directly on the server side.
        if getPathType(self.savePath) == PathType.Local:
            flag = modelClassDict[self.targetType].saveModel(self.modelToSave, self.savePath)
            self.signals.finished.emit(flag)
        elif getPathType(self.savePath) == PathType.Server:
            saveName = os.path.basename(self.savePath.split(':')[1])
            tmp_savePath = os.path.join('.', 'tmp', saveName)
            flag = modelClassDict[self.targetType].saveModel(self.modelToSave, tmp_savePath)
            if not flag:
                self.signals.finished.emit(flag)
            else:
                flag_upload = SaveImageCollection.upload(tmp_savePath, self.savePath, self.targetType)
                self.signals.finished.emit(flag_upload)
        else:
            self.signals.finished.emit(False)

    @staticmethod
    def upload(localPath, serverPath, fileType):
        if fileType == 'folder' and not localPath.endswith('/'):
            localPath = localPath + '/'

        return rsync(localPath, serverPath)

    @staticmethod
    def save(modelToSave, savePath, targetType, threadpool, callback):
        saveThread = SaveImageCollection(modelToSave, savePath, targetType)
        saveThread.signals.finished.connect(callback)
        threadpool.start(saveThread)