import os
from PyQt5 import QtWidgets
from main.ImageCollectionSelectionDialog import ImageCollectionSelectionDialog
from utils.pathUtils import isServerPath, normalizePath

class ImageCollectionSaveDialog(ImageCollectionSelectionDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)

    # override
    def fileDialogButtonClicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        if path:
            path = normalizePath(path)
            self.pathLineEdit.setText(path)
        else:
            self.pathLineEdit.setText(None)

    # override
    def buttonOKClicked(self):
        name = self.getName()
        selectedType = self.getType()
        if name == '' or ''.join(name.split()) != name or (selectedType == 'ppm' and not name.endswith('.ppm')) or \
            (selectedType == 'video' and not (name.endswith('.mp4') or name.endswith('.avi'))):
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name.', QtWidgets.QMessageBox.Ok)
        else:
            path = self.getPath()
            if path == '':
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Empty path.', QtWidgets.QMessageBox.Ok)
            elif (not isServerPath(path)) and (not os.path.exists(path)) or (os.path.exists(os.path.join(path, name))):
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)
            else:
                self.accept()