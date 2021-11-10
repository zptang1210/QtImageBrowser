import os
from PyQt5 import QtCore, QtWidgets
from main.ImageBrowserWindow import Ui_MainWindow
from main.ImageViewerSubWindow import ImageViewerSubWindow
from main.ImageCollectionSaveDialog import ImageCollectionSaveDialog
from main.ImageCollectionOpenDialog import ImageCollectionOpenDialog
from models.ImageCollectionCloudModel import ImageCollectionCloudModel
from utils.SaveImageCollection import SaveImageCollection
from utils.pathUtils import getPathType, normalizePath, PathType
from configs.availTypesConfig import availTypes, modelClassDict, modelNameDict

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.threadpool = QtCore.QThreadPool()
        
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
            if self.imageCollectionModels[model.path].length() > 0:
                self.addCollectionItem(model)
                return True
            else:
                QtWidgets.QMessageBox.information(self, 'Info', 'There is no image in this image collection.', QtWidgets.QMessageBox.Ok)
                self.imageCollectionModels.pop(model.path)
                return False
        else:
            QtWidgets.QMessageBox.information(self, 'Info', 'Error occurs during openning the image collection. (e.g. this image collection has already been opened.)', QtWidgets.QMessageBox.Ok)
            return False


    def createNewImageCollectionModel(self, path, name, type, parentModel=None):
        assert type in availTypes

        if path not in self.imageCollectionModels.keys():
            try:
                if getPathType(path) == PathType.Server:
                    model = ImageCollectionCloudModel(path, name, type, parentModel=parentModel)
                elif getPathType(path) == PathType.Local:
                    modelClass = modelClassDict[type]
                    model = modelClass(path, name, parentModel=parentModel)
                else:
                    raise ValueError('invalid path.')
            except:
                return False, None
            else:
                self.imageCollectionModels[model.path] = model
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
            modelToSave = self.imageCollectionModels[item.path]
            self.saveAndOpenCollection(modelToSave)
        

    def saveAndOpenCollection(self, modelToSave):
        modelToSaveTypeName = modelToSave.sourceModelTypeName
        diag = ImageCollectionSaveDialog(modelToSaveTypeName=modelToSaveTypeName, parent=self)
        if diag.exec_():
            path = diag.getPath()
            name = diag.getName()
            savePath = normalizePath(os.path.join(path, name))
            targetType = diag.getType()
            
            callback = lambda flag: self.saveFinishedCallback(savePath, name, targetType, flag)
            SaveImageCollection.save(modelToSave, savePath, targetType, self.threadpool, callback)

    
    def saveFinishedCallback(self, savePath, name, targetType, flag):
        if flag:
            QtWidgets.QMessageBox.information(self, 'Information', 'Image collection saved.', QtWidgets.QMessageBox.Ok)
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
                if subItem.path in self.imageViewerSubWindows:
                    self.imageViewerSubWindows[subItem.path].removeAffiliatedWindows()
                    self.mdiArea.removeSubWindow(self.imageViewerSubWindows[subItem.path])
                    self.imageViewerSubWindows.pop(subItem.path)
                
            self.imageViewerSubWindows[item.path].removeAffiliatedWindows()
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
