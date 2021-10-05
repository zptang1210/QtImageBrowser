import os
from PyQt5 import QtWidgets
from main.ImageCollectionSelectionDialog import ImageCollectionSelectionDialog
from utils.RemoteServerManager import remoteServerManager
from utils.pathUtils import PathType, getPathType, normalizePath

class ImageCollectionSaveDialog(ImageCollectionSelectionDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)

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
        if name == '' or ''.join(name.split()) != name or (selectedType == 'ppm' and not name.endswith('.ppm')) or \
            (selectedType == 'video' and not (name.endswith('.mp4') or name.endswith('.avi'))):
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name or the extension is missing.', QtWidgets.QMessageBox.Ok)
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