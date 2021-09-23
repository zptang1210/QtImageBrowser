from ImageViewerWidget import ImageViewerWidget
from PyQt5 import QtWidgets

class ImageViewerSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model = model
        self.widget = ImageViewerWidget(model, self)
        self.setWidget(self.widget)

    def closeEvent(self, event):
        self.removeAffiliatedWindows()
        print('before', self.parent.imageViewerSubWindows, self.model.path)
        self.parent.imageViewerSubWindows.pop(self.model.path)
        print('after', self.parent.imageViewerSubWindows)

    def removeAffiliatedWindows(self):
        for win in self.widget.openedLabelSubWindows:
            self.parent.mdiArea.removeSubWindow(win)
        self.widget.openedLabelSubWindows = []