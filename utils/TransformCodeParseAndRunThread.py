from models.ImageCollectionCloudModel import ImageCollectionCloudModel
from utils.RemoteServerManager import remoteServerManager
from utils.TransformCodeInterpreter import TransformCodeInterpreter
from models.ImageCollectionModel import ImageCollectionModel
from PyQt5 import QtCore

class TransformSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(ImageCollectionModel)
    failed = QtCore.pyqtSignal()


class TransformCodeParseAndRunThread(QtCore.QRunnable):
    def __init__(self, rawScript, model, newCollectionName, serverConfig):
        super().__init__()
        self.script = rawScript
        self.model = model
        self.newCollectionName = newCollectionName
        self.serverConfig = serverConfig

        self.parser = TransformCodeInterpreter()
        self.signals = TransformSignals()

    @QtCore.pyqtSlot()
    def run(self):
        if self.serverConfig is not None:
            newScript = self.parser.getScriptWoMacros(self.script, self.model)
            if newScript is not None:
                newModel = self.parser.parseAndRunRemotely(newScript, self.model, self.newCollectionName, self.serverConfig)
            else:
                self.signals.failed.emit() # invalid code
                return
        else:
            newModel = self.parser.parseAndRun(self.script, self.model, self.newCollectionName)
            
        if newModel is not None:
            self.signals.finished.emit(newModel)
        else:
            self.signals.failed.emit()

    @staticmethod
    def parseAndRun(rawScript, model, newCollectionName, serverName, threadpool, callback):
        if serverName is not None: # non-local machine
            serverConfig = remoteServerManager.getConfig(serverName)
        else:
            serverConfig = None
        parseAndRunThread = TransformCodeParseAndRunThread(rawScript, model, newCollectionName, serverConfig)
        parseAndRunThread.signals.finished.connect(callback)
        parseAndRunThread.signals.failed.connect(lambda: callback(None))

        threadpool.start(parseAndRunThread)


