from utils.RemoteServerManager import remoteServerManager
from utils.TransformCodeInterpreter import TransformCodeInterpreter
from models.ImageCollectionModel import ImageCollectionModel
from PyQt5 import QtCore

class TransformSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)
    failed = QtCore.pyqtSignal()


class TransformCodeParseAndRunThread(QtCore.QRunnable):
    def __init__(self, rawScript, model, newCollectionName, outputIntermediateResults, serverConfig):
        super().__init__()
        self.script = rawScript
        self.model = model
        self.newCollectionName = newCollectionName
        self.outputIntermediateResults = outputIntermediateResults
        self.serverConfig = serverConfig

        self.parser = TransformCodeInterpreter()
        self.signals = TransformSignals()

    @QtCore.pyqtSlot()
    def run(self):
        # send the script and the input to transformation core.
        if self.serverConfig is not None:
            newScript = self.parser.getScriptWoMacros(self.script, self.model)
            if newScript is not None:
                newModelList = self.parser.parseAndRunRemotely(newScript, self.model, self.newCollectionName, self.serverConfig)
            else:
                self.signals.failed.emit() # invalid code
                return
        else:
            newModelList = self.parser.parseAndRun(self.script, self.model, self.newCollectionName)

        # none newModelList, running script failed
        if newModelList is None:
            self.signals.failed.emit()
            return 
        else:
            # empty result list, this is a strange behavior
            if len(newModelList) < 1:
                print('no model is output. Potential bug here.')
                self.signals.failed.emit() 
                return

            # if only the final result is needed, throw out all intermediate results and keep the last model in the list
            if self.outputIntermediateResults == False:
                newModelList = newModelList[-1:]
            
            # send the results to the callback function
            self.signals.finished.emit(newModelList)

    @staticmethod
    def parseAndRun(rawScript, model, newCollectionName, outputIntermediateResults, serverName, threadpool, callback):
        if serverName is not None: # non-local machine
            serverConfig = remoteServerManager.getConfig(serverName)
        else:
            serverConfig = None
        parseAndRunThread = TransformCodeParseAndRunThread(rawScript, model, newCollectionName, outputIntermediateResults, serverConfig)
        parseAndRunThread.signals.finished.connect(callback)
        parseAndRunThread.signals.failed.connect(lambda: callback(None))

        threadpool.start(parseAndRunThread)


