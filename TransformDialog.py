from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

class TransformDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Transform')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


        self.layout = QtWidgets.QGridLayout()

        self.layout.addWidget(QtWidgets.QLabel('New collection name: '), 0, 0)
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.nameLineEdit, 0 , 1)

        self.layout.addWidget(QtWidgets.QLabel('Command:'), 1, 0)
        self.transformCode = QtWidgets.QPlainTextEdit(self)
        self.layout.addWidget(self.transformCode, 1, 1)

        self.layout.addWidget(self.buttonBox, 2, 1)

        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setLayout(self.layout)
