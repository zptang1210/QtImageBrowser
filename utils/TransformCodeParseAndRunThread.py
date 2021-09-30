from models.ImageCollectionCloudModel import ImageCollectionCloudModel
from utils.TransformCodeInterpreter import TransformCodeInterpreter
from models.ImageCollectionModel import ImageCollectionModel
from PyQt5 import QtCore

class TransformSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(ImageCollectionModel)
    failed = QtCore.pyqtSignal()


class TransformCodeParseAndRunThread(QtCore.QRunnable):
    def __init__(self, rawScript, model, newCollectionName):
        super().__init__()
        self.script = rawScript
        self.model = model
        self.newCollectionName = newCollectionName

        self.parser = TransformCodeInterpreter()
        self.signals = TransformSignals()

    @QtCore.pyqtSlot()
    def run(self):
        if isinstance(self.model, ImageCollectionCloudModel):
            newScript = self.parser.getScriptWoMacros(self.script, self.model)
            if newScript is not None:
                newModel = self.parser.parseAndRunRemotely(newScript, self.model, self.newCollectionName)
            else:
                self.signals.failed.emit() # invalid code
                return
        else:
            newModel = self.parser.parseAndRun(self.script, self.model, self.newCollectionName)
            
        if newModel:
            self.signals.finished.emit(newModel)
        else:
            self.signals.failed.emit()

    @staticmethod
    def parseAndRun(rawScript, model, newCollectionName, threadpool, callback):
        parseAndRunThread = TransformCodeParseAndRunThread(rawScript, model, newCollectionName)
        parseAndRunThread.signals.finished.connect(callback)
        parseAndRunThread.signals.failed.connect(lambda: callback(None))

        threadpool.start(parseAndRunThread)


