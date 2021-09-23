import os
from PyQt5 import QtWidgets
from main.ImageCollectionSelectionDialog import ImageCollectionSelectionDialog
from utils.pathUtils import isServerPath, normalizePath

class ImageCollectionOpenDialog(ImageCollectionSelectionDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    # override
    def fileDialogButtonClicked(self):
        selectedType = self.typeComboBox.currentText()
        if selectedType == 'folder':
            path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        elif selectedType == 'video':
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'Videos (*.mp4 *.avi)')
        elif selectedType == 'ppm':
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'PPM Image (*.ppm)')
        else:
            path = None
            raise ValueError('invalid selected type.')

        if path:
            path = normalizePath(path)
            self.pathLineEdit.setText(path)
        else:
            self.pathLineEdit.setText(None)

    # override
    def buttonOKClicked(self):
        selectedType = self.typeComboBox.currentText()
        path = self.getPath()

        invalid = False
        if selectedType == 'folder':
            if not self.pathExists(path):
                invalid = True
        elif selectedType == 'video':
            if (not self.pathExists(path)) or (os.path.splitext(path)[1].lower() not in ('.mp4', '.avi')):
                invalid = True
        elif selectedType == 'ppm':
            if (not self.pathExists(path)) or (os.path.splitext(path)[1].lower() != '.ppm'):
                invalid = True
        else:
            invalid = True
            raise ValueError('invalid selected type.')

        name = self.getName()
        if name == '':
            self.setName(os.path.basename(self.getPath()))
        elif ''.join(name.split()) != name: # contains space char
            invalid = True

        if not invalid:
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name or path.', QtWidgets.QMessageBox.Ok)

    def pathExists(self, path):
        if isServerPath(path):
            return True 
        else:
            return os.path.exists(path)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionOpenDialog()
    ans = dialog.exec_()
    print(ans)