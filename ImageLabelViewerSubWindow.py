from ImageViewerWidget import ImageViewerWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

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

    def closeEvent(self, event):
        self.parent.setLabelActionEnabled(True)