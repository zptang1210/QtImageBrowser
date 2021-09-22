import os
from PyQt5 import QtWidgets
from ImageCollectionSelectionDialog import ImageCollectionSelectionDialog


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
        if name == '' or ''.join(name.split()) != name or (selectedType == ImageCollectionSelectionDialog.availTypes[2] and not name.endswith('.ppm')) or \
            (selectedType == ImageCollectionSelectionDialog.availTypes[1] and not (name.endswith('.mp4') or name.endswith('.avi'))):
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name.', QtWidgets.QMessageBox.Ok)
        else:
            path = self.getPath()
            if (path == '') or (os.path.exists(path)):
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)
            else:
                self.accept()