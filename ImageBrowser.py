import sys, os
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, uic
from ImageBrowserWindow import Ui_MainWindow
from ImageViewerSubWIndow import ImageViewerSubWindow
from ImageViewerWidget import ImageViewerWidget
from models.ImageCollectionFolderModel import ImageCollectionFolderModel
from models.ImageCollectionPPMModel import ImageCollectionPPMModel
from ImageCollectionSelectionDialog import ImageCollectionSelectionDialog

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        
        self.imageCollectionModels = {}
        self.openCollectionButton.clicked.connect(self.openCollectionButtonClicked)

        self.imageViewerSubWindows = {}
        self.listWidget.itemDoubleClicked.connect(self.imageCollectionItemDoubleClicked)

        self.closeCollectionButton.clicked.connect(self.closeCollectionButtonClicked)


    def openCollectionButtonClicked(self):
        diag = ImageCollectionSelectionDialog(self)
        if diag.exec_():
            path = diag.getPath()
            name = diag.getName()

            # trying to create a new data model for the image collection to open and add item to the QListWidget
            self.createAndAddNewImageCollection(path, name, type=diag.getType())


    def createAndAddNewImageCollection(self, path, name, type):
        flag = self.createNewImageCollectionModel(path, name, type)
        if flag:
            # insert a new item into QListWidget
            if self.imageCollectionModels[path].length() > 0:
                self.addCollectionItem(path, name)
            else:
                QtWidgets.QMessageBox.information(self, 'Info', 'There is no image in this image collection.', QtWidgets.QMessageBox.Ok)
                self.imageCollectionModels.pop(path)
        else:
            QtWidgets.QMessageBox.information(self, 'Info', 'This image collection has already been opened.', QtWidgets.QMessageBox.Ok)


    def createNewImageCollectionModel(self, path, name, type):
        assert type in ('folder', 'video', 'ppm')
        modelClassDict = {'folder': ImageCollectionFolderModel, 'ppm': ImageCollectionPPMModel} # TODO: video model
        if path not in self.imageCollectionModels.keys():
            modelClass = modelClassDict[type]
            model = modelClass(path, name)
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
            newSubWindow = ImageViewerSubWindow(model, self)
            self.mdiArea.addSubWindow(newSubWindow)
            self.imageViewerSubWindows[item.path] = newSubWindow
            newSubWindow.show()

    
    def closeCollectionButtonClicked(self):
        item = self.listWidget.selectedItems()
        if not item: return
        item = item[0]

        if item.path in self.imageViewerSubWindows.keys():
            self.mdiArea.removeSubWindow(self.imageViewerSubWindows[item.path])
            self.imageViewerSubWindows.pop(item.path)

        itemTodel = self.listWidget.takeItem(self.listWidget.row(item))
        del itemTodel
        self.imageCollectionModels.pop(item.path)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()