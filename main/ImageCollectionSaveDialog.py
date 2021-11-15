import os
from PyQt5 import QtWidgets
from main.ImageCollectionSelectionDialog import ImageCollectionSelectionDialog
from utils.RemoteServerManager import remoteServerManager
from utils.pathUtils import PathType, getPathType, normalizePath
from configs.availTypesConfig import TypeProperty, ModelType, availTypes, FileType

class ImageCollectionSaveDialog(ImageCollectionSelectionDialog):
    
    def __init__(self, modelToSaveTypeName=None, parent=None):
        super().__init__(parent)

        # add types to combobox
        # if we save basic types, available types are basic types
        # if we save compound types, available types are basic types and the same type as the model
        if modelToSaveTypeName is None:
            self.typeComboBox.addItems(availTypes)
        else:
            for typeName in availTypes:
                if TypeProperty[typeName]['modelType'] == ModelType.basic:
                    self.typeComboBox.addItem(typeName)
                elif TypeProperty[typeName]['modelType'] == ModelType.compound:
                    if typeName == modelToSaveTypeName:
                        self.typeComboBox.addItem(typeName)
                else:
                    raise ValueError('Unexpected model type to save.')

    # override
    def fileDialogButtonClicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        if path:
            path = normalizePath(path)
            self.setPath(path)
        else:
            self.setPath(None)

    # override
    def buttonOKClicked(self):
        # check name
        name = self.getName().strip()
        selectedType = self.getType()

        if name == '' or ''.join(name.split()) != name:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name (e.g. it is empty or it contains spaces).', QtWidgets.QMessageBox.Ok)
            return

        for typeName in TypeProperty.keys():
            if selectedType == typeName and TypeProperty[typeName]['fileType'] ==FileType.file:
                nameWithValidExt = False
                for extName in TypeProperty[typeName]['extension']:
                    if name.endswith(extName):
                        nameWithValidExt = True
                        break
                
                if nameWithValidExt == False:
                    QtWidgets.QMessageBox.warning(self, 'Warning', 'The extension is incorrect or missing.', QtWidgets.QMessageBox.Ok)
                    return

        self.setName(name) # set normalized name

        # check path
        path = self.getPath().strip()
        if path == '':
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Empty path.', QtWidgets.QMessageBox.Ok)
            return
        if getPathType(path) == PathType.Invalid:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)
            return             

        # expand the path to incorporate the server addr if selected location is a server
        if self.getLocationIdx() != 0:
            if getPathType(path) == PathType.Server:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'When opening a full path on the cloud, please select image location as empty.', QtWidgets.QMessageBox.Ok)
                return 
            else:
                addr = remoteServerManager.getServerAddr(self.getLocationName())
                path = addr + ':' + path

        if getPathType(path) == PathType.Local: # local path
            valid = False
            if self.getType() == 'folder' and os.path.exists(os.path.join(path)):
                valid = True

            if self.getType() != 'folder' and not os.path.exists(os.path.join(path, name)):
                valid = True

            if not valid:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path.', QtWidgets.QMessageBox.Ok)
                return

        self.setPath(path)

        self.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionSaveDialog()
    ans = dialog.exec_()
    print(ans, dialog.getPath(), dialog.getName())