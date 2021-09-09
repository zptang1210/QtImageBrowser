import os
from models.ImageCollectionFolderModel import ImageCollectionFolderModel
from PyQt5 import QtWidgets

class ImageCollectionSelectionDialog(QtWidgets.QDialog):
    availTypes = ('folder', 'video', 'ppm')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Choose path')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.buttonOKClicked)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QGridLayout()

        self.layout.addWidget(QtWidgets.QLabel('Select type: '), 0, 0, 1, 1)
        self.typeComboBox = QtWidgets.QComboBox(self)
        self.typeComboBox.addItems(ImageCollectionSelectionDialog.availTypes)
        self.layout.addWidget(self.typeComboBox, 0, 1, 1, 2)

        self.layout.addWidget(QtWidgets.QLabel('Input name: '), 1, 0, 1, 1)
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.nameLineEdit, 1, 1, 1, 2)

        self.layout.addWidget(QtWidgets.QLabel('Input path: '), 2, 0, 1, 1)
        self.pathLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.pathLineEdit, 2, 1, 1, 1)
        
        self.fileDialogButton = QtWidgets.QPushButton('Select')
        self.fileDialogButton.clicked.connect(self.fileDialogButtonClicked)
        self.layout.addWidget(self.fileDialogButton, 2, 2, 1, 1)

        self.layout.addWidget(self.buttonBox, 3, 1, 1, 2)

        self.setLayout(self.layout)

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

        if not invalid:
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)

    def getPath(self):
        return self.pathLineEdit.text()

    def getName(self):
        name = self.nameLineEdit.text().strip()
        if name == '':
            return os.path.basename(self.getPath())
        else:
            return name
    
    def getType(self):
        selectedType = self.typeComboBox.currentText()
        assert selectedType in ImageCollectionSelectionDialog.availTypes
        return selectedType


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionSelectionDialog()
    ans = dialog.exec_()
    print(ans)