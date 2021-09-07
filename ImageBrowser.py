import sys
from PyQt5 import QtWidgets, uic
from ImageBrowserWindow import Ui_MainWindow
from models.ImageCollectionFolderModel import ImageCollectionFolderModel

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.imageCollectionModels = {}
        self.openCollectionButton.clicked.connect(self.openCollectionButtonClicked)

        self.imageViewerSubWindows = {}
        self.listWidget.itemDoubleClicked.connect(self.imageCollectionItemDoubleClicked)

    def openCollectionButtonClicked(self):
        # path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'PPM Image (*.ppm)')
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        print(path)

        if path not in self.imageCollectionModels.keys():
            self.addCollectionItem(path, type='folder')
        else:
            print('already opened.')

    def addCollectionItem(self, path, type='folder'):
        assert type in ('folder', 'txt', 'ppm')

        # insert new 
        item = QtWidgets.QListWidgetItem()
        item.setText(path)
        item.path = path
        self.listWidget.addItem(item)

        model = ImageCollectionFolderModel(path)
        self.imageCollectionModels[path] = model

    def imageCollectionItemDoubleClicked(self):
        item = self.listWidget.selectedItems()[0]
        print(item.path)

        selectedSubWindow = self.imageViewerSubWindows.get(item.path, None)
        if selectedSubWindow:
            self.mdiArea.setActiveSubWindow(selectedSubWindow)
        else:
            newSubWindow = QtWidgets.QMdiSubWindow()
            newSubWindow.setWidget(QtWidgets.QLabel(item.path))
            self.mdiArea.addSubWindow(newSubWindow)
            self.imageViewerSubWindows[item.path] = newSubWindow
            newSubWindow.show()
            


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()