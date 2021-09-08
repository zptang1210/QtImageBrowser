from PyQt5.QtCore import Qt
from ImageViewerSubWIndow import ImageViewerSubWindow
from ImageViewerWidget import ImageViewerWidget
import sys, os
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
        if not path:
            return
        name = os.path.basename(path)

        # trying to create a new data model for the image collection to opoen
        flag = self.createNewImageCollectionModel(path, name, type='folder')
        if flag:
            # insert a new item into QListWidget
            if self.imageCollectionModels[path].length() > 0:
                self.addCollectionItem(path, name)
            else:
                QtWidgets.QMessageBox.information(self, 'Info', 'There is no image in this image collection.', QtWidgets.QMessageBox.Ok)
                self.imageCollectionModels.pop(path)
        else:
            QtWidgets.QMessageBox.information(self, 'Info', 'This image collection has already been opened.', QtWidgets.QMessageBox.Ok)


    def createNewImageCollectionModel(self, path, name, type='folder'):
        assert type in ('folder', 'txt', 'ppm')
        if path not in self.imageCollectionModels.keys():
            model = ImageCollectionFolderModel(path, name)
            self.imageCollectionModels[path] = model
            return True
        else:
            return False


    def addCollectionItem(self, path, name):
        item = QtWidgets.QListWidgetItem()
        item.setText(name)
        item.setToolTip(path)
        item.path = path
        item.name = name
        self.listWidget.addItem(item)


    def imageCollectionItemDoubleClicked(self):
        item = self.listWidget.selectedItems()[0]
        print(item.path)

        selectedSubWindow = self.imageViewerSubWindows.get(item.path, None)
        if selectedSubWindow:
            self.mdiArea.setActiveSubWindow(selectedSubWindow)
        else:
            model = self.imageCollectionModels[item.path]
            # newSubWindow = QtWidgets.QMdiSubWindow()
            newSubWindow = ImageViewerSubWindow(model, self)
            newSubWindow.setWidget(ImageViewerWidget(model))
            self.mdiArea.addSubWindow(newSubWindow)
            self.imageViewerSubWindows[item.path] = newSubWindow
            newSubWindow.show()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()