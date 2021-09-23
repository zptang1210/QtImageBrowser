import os
from PyQt5 import QtCore
from utils.isServerPath import isServerPath
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
        # TODO: check if the path is to the server, if yes, save model to a temp place and then upload it.
        # If modelToSave is a cloud type, and the path is also a cloud path, copy directly on the server side.
        if not isServerPath(self.savePath):
            flag = modelClassDict[self.targetType].saveModel(self.modelToSave, self.savePath)
            self.signals.finished.emit(flag)
        else:
            saveName = os.path.basename(self.savePath.split(':')[1])
            tmp_savePath = os.path.join('.', 'tmp', saveName)
            flag = modelClassDict[self.targetType].saveModel(self.modelToSave, tmp_savePath)
            if not flag:
                self.signals.finished.emit(flag)
            else:
                flag_upload = self.upload(tmp_savePath, self.savePath)
                self.signals.finished.emit(flag_upload)

    def upload(self, localPath, serverPath):
        if self.targetType == 'folder' and not localPath.endswith('/'):
            localPath = localPath + '/'

        cmd = f'rsync -a --delete {localPath} {serverPath}'
        return rsync(cmd)

    @staticmethod
    def save(modelToSave, savePath, targetType, threadpool, callback):
        saveThread = SaveImageCollection(modelToSave, savePath, targetType)
        saveThread.signals.finished.connect(callback)
        threadpool.start(saveThread)