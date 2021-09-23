from ImageViewerWidget import ImageViewerWidget
from PyQt5 import QtWidgets

class ImageLabelViewerSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model = model
        self.setWidget(ImageViewerWidget(model, self))
        self.widget().setTransformActionEnabled(False)
        self.widget().setLabelActionEnabled(False)
        
        self.saveAction = QtWidgets.QAction('Save', self.widget())
        self.widget().toolbar.addAction(self.saveAction)
        self.saveAction.triggered.connect(self.saveLabelActionTriggered)

    def closeEvent(self, event):
        self.parent.setLabelActionEnabled(True)
        self.parent.openedLabelSubWindows.remove(self)

    def saveLabelActionTriggered(self):
        self.parent.parent.parent.saveAndOpenCollection(self.model)