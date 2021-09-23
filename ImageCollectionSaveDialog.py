import os
from utils.isServerPath import isServerPath
from PyQt5 import QtWidgets
from ImageCollectionSelectionDialog import ImageCollectionSelectionDialog
from configs.availTypesConfig import availTypes


class ImageCollectionSaveDialog(ImageCollectionSelectionDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)

    # override
    def fileDialogButtonClicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        if path:
            path = os.path.normpath(path)
            self.pathLineEdit.setText(path)
        else:
            self.pathLineEdit.setText(None)

    # override
    def buttonOKClicked(self):
        name = self.getName()
        selectedType = self.getType()
        if name == '' or ''.join(name.split()) != name or (selectedType == availTypes[2] and not name.endswith('.ppm')) or \
            (selectedType == availTypes[1] and not (name.endswith('.mp4') or name.endswith('.avi'))):
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name.', QtWidgets.QMessageBox.Ok)
        else:
            path = self.getPath()
            if path == '':
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Empty path.', QtWidgets.QMessageBox.Ok)
            elif (not isServerPath(path)) and (not os.path.exists(path)) or (os.path.exists(os.path.join(path, name))):
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)
            else:
                self.accept()