import os
from PyQt5 import QtWidgets
from main.ImageCollectionSelectionDialog import ImageCollectionSelectionDialog
from utils.RemoteServerManager import remoteServerManager
from utils.pathUtils import getPathType, normalizePath, PathType

class ImageCollectionOpenDialog(ImageCollectionSelectionDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

    # override
    def fileDialogButtonClicked(self):
        selectedType = self.typeComboBox.currentText()
        if selectedType == 'folder':
            path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Image Folder', '')
        elif selectedType == 'video':
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'Videos (*.mp4 *.avi)')
        elif selectedType == 'ppm':
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'PPM Image (*.ppm)')
        else:
            path = None
            raise ValueError('invalid selected type.')

        if path:
            path = normalizePath(path)
            self.setPath(path)
        else:
            self.setPath(None)

    # override
    def buttonOKClicked(self):
        selectedType = self.typeComboBox.currentText()
        path = self.getPath().strip()

        if getPathType(path) == PathType.Invalid:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path format!', QtWidgets.QMessageBox.Ok)
            return                 

        # expand the path to the normalized form
        # if the path is local and the selected location is also local, convert it to absolute path
        # if the path is local but the selected location is a server, convert it to the scp format
        if self.getLocationIdx() == 0:
            path = normalizePath(path)
        else:
            if getPathType(path) == PathType.Server:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'When opening a full path on the cloud, please select image location as empty.', QtWidgets.QMessageBox.Ok)
                return 
            elif getPathType(path) == PathType.Local:
                addr = remoteServerManager.getServerAddr(self.getLocationName())
                path = addr + ':' + path           

        # detect if path is valid.
        # If the path is on local machine, detect if the path exists and its extension.
        # if the path is of the server format, detect its extension only.
        invalid = False
        
        if selectedType == 'folder':
            if not self.isValidPath(path):
                invalid = True
        elif selectedType == 'video':
            if (not self.isValidPath(path)) or (os.path.splitext(path)[1].lower() not in ('.mp4', '.avi')):
                invalid = True
        elif selectedType == 'ppm':
            if (not self.isValidPath(path)) or (os.path.splitext(path)[1].lower() != '.ppm'):
                invalid = True
        else:
            invalid = True
            raise ValueError('Invalid selected type.')

        if invalid == True:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid path (check path existence and its extension).', QtWidgets.QMessageBox.Ok)
            return 
        
        self.setPath(path)

        # detect if name is valid
        name = self.getName().strip()
        if name == '':
            self.setName(os.path.basename(path))
        elif ''.join(name.split()) != name: # contains space char
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid name (probably because contains space character).', QtWidgets.QMessageBox.Ok)
            return 
        else:
            self.setName(name) # normalize the name

        self.accept()

    def isValidPath(self, path):
        if getPathType(path) == PathType.Server:
            return True
        elif getPathType(path) == PathType.Local:
            return os.path.exists(path)
        else:
            return False


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = ImageCollectionOpenDialog()
    ans = dialog.exec_()
    print(ans, dialog.getPath(), dialog.getName())