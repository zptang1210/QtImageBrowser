from PyQt5 import QtWidgets
from utils.RemoteServerManager import remoteServerManager
from configs.availTypesConfig import availTypes

class ImageCollectionSelectionDialog(QtWidgets.QDialog):

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
        self.layout.addWidget(self.typeComboBox, 0, 1, 1, 2)

        self.layout.addWidget(QtWidgets.QLabel('Input name: '), 1, 0, 1, 1)
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.nameLineEdit, 1, 1, 1, 2)

        self.layout.addWidget(QtWidgets.QLabel('Image location: '), 2, 0, 1, 1)
        self.locComboBox = QtWidgets.QComboBox(self)
        self.locationList = ['']
        self.locationList.extend(remoteServerManager.getListOfServers())
        self.locComboBox.addItems(self.locationList)
        self.locComboBox.currentIndexChanged.connect(self.locComboBoxIdxChanged)

        self.layout.addWidget(self.locComboBox, 2, 1, 1, 1)

        self.fileDialogButton = QtWidgets.QPushButton('select')
        self.fileDialogButton.clicked.connect(self.fileDialogButtonClicked)
        self.layout.addWidget(self.fileDialogButton, 2, 2, 1, 1)
        
        self.fileDialogButton.setEnabled(True)
        self.locComboBox.setCurrentIndex(0)

        self.layout.addWidget(QtWidgets.QLabel('Input path: '), 3, 0, 1, 1)
        self.pathLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.pathLineEdit, 3, 1, 1, 2)

        self.layout.addWidget(self.buttonBox, 4, 1, 1, 2)

        self.setLayout(self.layout)

    def locComboBoxIdxChanged(self, idx):
        if idx == 0: # Path is probably for local machine, enable select button (path can also be in the scp format)
            self.fileDialogButton.setEnabled(True)
        else:
            self.fileDialogButton.setEnabled(False)

    def buttonOKClicked(self):
        self.accept()
    
    def fileDialogButtonClicked(self):
        pass

    def getPath(self):
        path = self.pathLineEdit.text()
        return path

    def setPath(self, text): # the path you set must be of full format
        self.pathLineEdit.setText(text)
        self.locComboBox.setCurrentIndex(0)

    def getName(self):
        return self.nameLineEdit.text()

    def setName(self, text):
        self.nameLineEdit.setText(text)
    
    def getType(self):
        selectedType = self.typeComboBox.currentText()
        assert selectedType in availTypes
        return selectedType

    def getLocationIdx(self):
        return self.locComboBox.currentIndex()

    def getLocationName(self):
        return self.locComboBox.currentText()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionSelectionDialog()
    ans = dialog.exec_()
    print(ans)