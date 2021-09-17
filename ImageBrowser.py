import sys, os
from models.ImageCollectionFolderModel import ImageCollectionFolderModel
from models.ImageCollectionVideoModel import ImageCollectionVideoModel
from models.ImageCollectionPPMModel import ImageCollectionPPMModel
from ImageBrowserWindow import Ui_MainWindow
from ImageViewerSubWindow import ImageViewerSubWindow
from utils.saveImageCollection import saveImageCollection
from ImageCollectionSaveDialog import ImageCollectionSaveDialog
from ImageCollectionOpenDialog import ImageCollectionOpenDialog
from PyQt5 import QtWidgets

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        
        self.imageCollectionModels = {}
        self.openCollectionButton.clicked.connect(self.openCollectionButtonClicked)

        self.imageViewerSubWindows = {}
        self.treeWidget.itemDoubleClicked.connect(self.imageCollectionItemDoubleClicked)

        self.saveCollectionButton.clicked.connect(self.saveCollectionButtonClicked)

        self.closeCollectionButton.clicked.connect(self.closeCollectionButtonClicked)


    def openCollectionButtonClicked(self):
        diag = ImageCollectionOpenDialog(self)
        if diag.exec_():
            path = diag.getPath()
            name = diag.getName()

            # trying to create a new data model for the image collection to open and add item to the QListWidget
            self.createAndAddNewImageCollection(path, name, type=diag.getType())


    def createAndAddNewImageCollection(self, path, name, type, parentModel=None):
        flag, model = self.createNewImageCollectionModel(path, name, type, parentModel=parentModel)
        if flag:
            # insert a new item into QListWidget
            if self.imageCollectionModels[path].length() > 0:
                self.addCollectionItem(model)
                return True
            else:
                QtWidgets.QMessageBox.information(self, 'Info', 'There is no image in this image collection.', QtWidgets.QMessageBox.Ok)
                self.imageCollectionModels.pop(path)
                return False
        else:
            QtWidgets.QMessageBox.information(self, 'Info', 'This image collection has already been opened.', QtWidgets.QMessageBox.Ok)
            return False


    def createNewImageCollectionModel(self, path, name, type, parentModel=None):
        assert type in ('folder', 'video', 'ppm')
        modelClassDict = {'folder': ImageCollectionFolderModel, 'video': ImageCollectionVideoModel,'ppm': ImageCollectionPPMModel}
        if path not in self.imageCollectionModels.keys():
            modelClass = modelClassDict[type]
            model = modelClass(path, name, parentModel=parentModel)
            self.imageCollectionModels[path] = model
            return True, model
        else:
            return False, None


    def addCollectionItem(self, model):
        path = model.path
        name = model.name
        if model.isRootModel(): # this model is a root model, insert it into the top level of the widget
            item = QtWidgets.QTreeWidgetItem(self.treeWidget)
            item.setText(0, name)
            item.setToolTip(0, path)
            item.path = path
            item.name = name
            self.treeWidget.addTopLevelItem(item)
            self.treeWidget.setCurrentItem(item)
        else: # this model is not a root model, add this model as a child of the root model
            rootModel = model.getRootModel()
            rootItem = None
            for idx in range(self.treeWidget.topLevelItemCount()):
                item = self.treeWidget.topLevelItem(idx)
                if item.path == rootModel.path:
                    rootItem = item
            assert rootItem is not None

            item = QtWidgets.QTreeWidgetItem(rootItem)
            item.setText(0, name)
            item.setToolTip(0, path)
            item.path = path
            item.name = name

            self.treeWidget.expandItem(rootItem)
            self.treeWidget.setCurrentItem(item)


    def imageCollectionItemDoubleClicked(self):
        item = self.treeWidget.selectedItems()[0]

        selectedSubWindow = self.imageViewerSubWindows.get(item.path, None)
        if selectedSubWindow:
            self.mdiArea.setActiveSubWindow(selectedSubWindow)
        else:
            model = self.imageCollectionModels[item.path]
            newSubWindow = ImageViewerSubWindow(model, self)
            self.mdiArea.addSubWindow(newSubWindow)
            self.imageViewerSubWindows[item.path] = newSubWindow
            newSubWindow.show()

    
    def saveCollectionButtonClicked(self):
        items = self.treeWidget.selectedItems()
        if len(items) == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select an image collection to save.', QtWidgets.QMessageBox.Ok)
            return
        else:
            item = items[0]
        
        diag = ImageCollectionSaveDialog(self)
        if diag.exec_():
            path = diag.getPath()
            name = diag.getName()
            savePath = os.path.join(path, name)
            targetType = diag.getType()

            modelToSave = self.imageCollectionModels[item.path]
            flag = saveImageCollection(modelToSave, savePath, targetType)
            if flag:
                self.createAndAddNewImageCollection(savePath, name, targetType)
            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Error occurs during saving.', QtWidgets.QMessageBox.Ok)

    
    def closeCollectionButtonClicked(self):
        item = self.treeWidget.selectedItems()
        if not item: return
        item = item[0]
        parent = item.parent()

        if item.path in self.imageViewerSubWindows.keys():
            for idx in range(item.childCount()):
                subItem = item.child(idx)
                self.mdiArea.removeSubWindow(self.imageViewerSubWindows[subItem.path])
                self.imageViewerSubWindows.pop(subItem.path)
                
            self.mdiArea.removeSubWindow(self.imageViewerSubWindows[item.path])
            self.imageViewerSubWindows.pop(item.path)

        for idx in range(item.childCount()):
            subItem = item.child(idx)
            self.imageCollectionModels.pop(subItem.path)
        item.takeChildren()
        
        self.imageCollectionModels.pop(item.path)
        if parent:
            parent.removeChild(item)
        else:
            self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(item))
        del item




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()