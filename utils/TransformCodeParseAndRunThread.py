from models.ImageCollectionCloudModel import ImageCollectionCloudModel
from utils.TransformCodeInterpreter import TransformCodeInterpreter
from models.ImageCollectionModel import ImageCollectionModel
from PyQt5 import QtCore

class TransformSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(ImageCollectionModel)
    failed = QtCore.pyqtSignal()


class TransformCodeParseAndRunThread(QtCore.QRunnable):
    def __init__(self, rawCode, model, newCollectionName):
        super().__init__()
        self.code = rawCode
        self.model = model
        self.newCollectionName = newCollectionName

        self.parser = TransformCodeInterpreter()
        self.signals = TransformSignals()

    @QtCore.pyqtSlot()
    def run(self):
        if isinstance(self.model, ImageCollectionCloudModel):
            newModel = self.parser.parseAndRunRemotely(self.code, self.model, self.newCollectionName)
        else:
            newModel = self.parser.parseAndRun(self.code, self.model, self.newCollectionName)
            
        if newModel:
            self.signals.finished.emit(newModel)
        else:
            self.signals.failed.emit()

    @staticmethod
    def parseAndRun(rawCode, model, newCollectionName, threadpool, callback):
        parseAndRunThread = TransformCodeParseAndRunThread(rawCode, model, newCollectionName)
        parseAndRunThread.signals.finished.connect(callback)
        parseAndRunThread.signals.failed.connect(lambda: callback(None))

        threadpool.start(parseAndRunThread)


