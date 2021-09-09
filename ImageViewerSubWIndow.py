from ImageViewerWidget import ImageViewerWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

class ImageViewerSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model = model
        self.setWidget(ImageViewerWidget(model, self))

    def closeEvent(self, event):
        self.parent.imageViewerSubWindows.pop(self.model.path)