import time, random
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from utils.RemoteServerManager import remoteServerManager

class TransformDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Transform')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.buttonOkClicked)
        self.buttonBox.rejected.connect(self.reject)


        self.layout = QtWidgets.QGridLayout()

        self.layout.addWidget(QtWidgets.QLabel('New collection name: '), 0, 0)
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.nameLineEdit, 0 , 1)

        self.layout.addWidget(QtWidgets.QLabel('Command:'), 1, 0)
        self.transformCode = QtWidgets.QPlainTextEdit(self)
        self.layout.addWidget(self.transformCode, 1, 1)

        self.layout.addWidget(QtWidgets.QLabel('Running on:'), 2, 0)
        self.locComboBox = QtWidgets.QComboBox(self)
        self.locationList = ['local']
        self.locationList.extend(remoteServerManager.getListOfServersAllowingProcessing())
        self.locComboBox.addItems(self.locationList)
        self.layout.addWidget(self.locComboBox, 2, 1)

        self.layout.addWidget(self.buttonBox, 3, 1)

        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setLayout(self.layout)

    def buttonOkClicked(self):
        name = self.getName().strip()
        code = self.getCode().strip()

        if len(name) == 0: # use a random string as the name
            name = time.ctime().replace(' ', '_') + '-' + str(random.randint(0, 10000))

        if ''.join(name.split()) == name and len(code) != 0: # no blank character or script
            self.setName(name)
            self.setCode(code) # normalize name and code
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name or script!', QtWidgets.QMessageBox.Ok)

    def getName(self):
        return self.nameLineEdit.text()
    
    def getCode(self):
        return self.transformCode.toPlainText()

    def setName(self, name):
        self.nameLineEdit.setText(name)

    def setCode(self, code):
        self.transformCode.setPlainText(code)

    def getSelectedProcessingServer(self):
        selected = self.locComboBox.currentText()
        if selected == 'local': # return None if selected is the local machine.
            return None
        else:
            return selected

    def resetNameAndCode(self):
        self.resetName()
        self.resetCode()

    def resetName(self):
        self.setName(None)

    def resetCode(self):
        self.setCode(None)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = TransformDialog()
    ans = dialog.exec_()
    print(ans, dialog.getName(), dialog.getCode())