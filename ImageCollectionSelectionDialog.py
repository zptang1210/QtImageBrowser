import os
from PyQt5 import QtWidgets

class ImageCollectionSelectionDialog(QtWidgets.QDialog):
    availTypes = ('folder', 'video', 'ppm')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
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

    def buttonOKClicked(self):
        self.accept()
    
    def fileDialogButtonClicked(self):
        pass

    def getPath(self):
        return os.path.normpath(self.pathLineEdit.text())

    def getName(self):
        return self.nameLineEdit.text().strip()

    def setName(self, text):
        self.nameLineEdit.setText(text)
    
    def getType(self):
        selectedType = self.typeComboBox.currentText()
        assert selectedType in ImageCollectionSelectionDialog.availTypes
        return selectedType

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionSelectionDialog()
    ans = dialog.exec_()
    print(ans)