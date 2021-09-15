import os
from PyQt5 import QtWidgets
from ImageCollectionSelectionDialog import ImageCollectionSelectionDialog

class ImageCollectionOpenDialog(ImageCollectionSelectionDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    # override
    def fileDialogButtonClicked(self):
        selectedType = self.typeComboBox.currentText()
        if selectedType == ImageCollectionSelectionDialog.availTypes[0]:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        elif selectedType == ImageCollectionSelectionDialog.availTypes[1]:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'Videos (*.mp4 *.avi)')
        elif selectedType == ImageCollectionSelectionDialog.availTypes[2]:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'PPM Image (*.ppm)')
        else:
            path = None

        if path:
            self.pathLineEdit.setText(path)
        else:
            self.pathLineEdit.setText(None)

    # override
    def buttonOKClicked(self):
        selectedType = self.typeComboBox.currentText()
        path = self.getPath()

        invalid = False
        if selectedType == ImageCollectionSelectionDialog.availTypes[0]:
            if not os.path.exists(path):
                invalid = True
        elif selectedType == ImageCollectionSelectionDialog.availTypes[1]:
            if (not os.path.exists(path)) or (os.path.splitext(path)[1].lower() not in ('.mp4', '.avi')):
                invalid = True
        elif selectedType == ImageCollectionSelectionDialog.availTypes[2]:
            if (not os.path.exists(path)) or (os.path.splitext(path)[1].lower() != '.ppm'):
                invalid = True
        else:
            invalid = True

        name = self.getName()
        if name == '':
            self.setName(os.path.basename(self.getPath()))

        if not invalid:
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionOpenDialog()
    ans = dialog.exec_()
    print(ans)