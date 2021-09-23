from PyQt5 import QtCore
from utils.TransformCodeParseAndRunThread import TransformCodeParseAndRunThread
from models.ImageCollectionSubModel import ImageCollectionSubModel
from utils.TransformCodeInterpreter import TransformCodeInterpreter
from TransformDialog import TransformDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPixmap, qRgb
from PIL import Image
import numpy as np

class ImageViewerWidget(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle(model.name)
        self.model = model
        self.parent = parent

        self.openedLabelSubWindows = []
        
        self.transformDlg = None
        self.threadpool = QtCore.QThreadPool()

        self.toolbar = QtWidgets.QToolBar()
        # self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.transformAction = QtWidgets.QAction('Transform', self)
        # self.transformAction = QtWidgets.QAction(QIcon('resources/icons/transformIcon.ico'), 'Transform', self)
        self.transformAction.setShortcut('Ctrl+T')
        self.toolbar.addAction(self.transformAction)
        self.transformAction.triggered.connect(self.transformActionTriggered)

        self.labelToolButton = QtWidgets.QToolButton()
        self.labelToolButton.setText('Label ')
        self.labelToolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.maxLabelNum = 3
        assert 1 <= self.maxLabelNum <= 9
        self.labelMenu = QtWidgets.QMenu()
        self.labelToggleActions = {}
        self.labelList = {}
        for i in range(1, self.maxLabelNum+1):
            labelAction = QtWidgets.QAction('label ' + str(i), self)
            labelAction.setShortcut('Ctrl+' + str(i))
            labelAction.setCheckable(True)
            labelAction.toggled.connect(self.labelToggled)
            self.labelToggleActions[i] = labelAction
            self.labelMenu.addAction(labelAction)
            self.labelList[i] = set()
        self.labelMenu.addSeparator()
        self.labelViewActions = {}
        for i in range(1, self.maxLabelNum+1):
            labelAction = QtWidgets.QAction('View images with label ' + str(i), self)
            labelAction.setShortcut('Alt+' + str(i))
            labelAction.triggered.connect((lambda checked, idx=i: self.labelViewActionTriggered(idx)))
            self.labelViewActions[i] = labelAction
            self.labelMenu.addAction(labelAction)        
        self.labelToolButton.setMenu(self.labelMenu)

        self.getPathAction = QtWidgets.QAction('Copy Path', self)
        self.getPathAction.setShortcut('Ctrl+C')
        self.toolbar.addAction(self.getPathAction)
        self.getPathAction.triggered.connect(self.getPathActionTriggered)

        self.toolbar.addWidget(self.labelToolButton)
        
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setMenuBar(self.toolbar)
        self.setLayout(self.mainLayout)

        self.hLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.hLayout)

        # self.image = QImage('a.jpg')

        # image = Image.open('b.jpg')
        # image = np.asarray(image)
        # h, w, c = image.shape
        # self.imageQImage = QImage(image.data, w, h, 3*w, QImage.Format_RGB888)
        # self.imagePixMap = QPixmap(self.imageQImage)

        image_qimg = QImage(500, 500, QImage.Format_RGB888)
        image_qimg.fill(qRgb(255, 255, 255))
        image_pixmap = QPixmap(image_qimg)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setPixmap(image_pixmap)
        
        self.hLayout.addWidget(self.imageLabel)

        self.slider = QtWidgets.QSlider(Qt.Vertical, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.model.length()-1)
        self.slider.setInvertedAppearance(True)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.hLayout.addWidget(self.slider)

        self.extraInfoLabel = QtWidgets.QLabel()
        self.mainLayout.addWidget(self.extraInfoLabel)

        self.slider.setValue(0)
        self.sliderValueChanged(0)


    def sliderValueChanged(self, value):
        image_np, image_name = self.model.get(value)

        h, w, c = image_np.shape
        image_qimg = QImage(image_np.data.tobytes(), w, h, 3*w, QImage.Format_RGB888)
        image_pixmap = QPixmap(image_qimg)
        self.imageLabel.setPixmap(image_pixmap)

        self.extraInfoLabel.setText(f'{image_name}')

        for i in range(1, self.maxLabelNum+1):
            if value in self.labelList[i]:
                self.labelToggleActions[i].setChecked(True)
            else:
                self.labelToggleActions[i].setChecked(False)

    def transformActionTriggered(self):
        if self.transformDlg is None:
            self.transformDlg = TransformDialog(self)

        if self.transformDlg.exec_():
            newCollectionName = self.transformDlg.nameLineEdit.text().strip()
            code = self.transformDlg.transformCode.toPlainText()

            TransformCodeParseAndRunThread.parseAndRun(code, self.model, newCollectionName, self.threadpool, self.transformFinishedCallback)
        else:
            self.transformDlg = None
            return

    def transformFinishedCallback(self, newModel):
        if newModel is not None:
            flag = self.parent.parent.createAndAddNewImageCollection(newModel.path, newModel.name + '_temp', type='folder', parentModel=self.model)
            if flag:
                QtWidgets.QMessageBox.information(self, 'Info', f'The new image collection {newModel.name} has been opened.', QtWidgets.QMessageBox.Ok)
            self.transformDlg = None     
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Failed to run the commands!', QtWidgets.QMessageBox.Ok)
            self.transformAction.trigger()


    def getCurrentImgIdx(self):
        return self.slider.value()

    def getPathActionTriggered(self):
        currentIdx = self.getCurrentImgIdx()
        path = self.model.getImgInfo(currentIdx)['path']
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(path)

    def labelToggled(self):
        currentIdx = self.getCurrentImgIdx()
        for i in range(1, self.maxLabelNum+1):
            if self.labelToggleActions[i].isChecked():
                self.labelList[i].add(currentIdx)
            else:
                self.labelList[i].discard(currentIdx)
        # print(self.labelList)

    def labelViewActionTriggered(self, idx):
        if len(self.labelList[idx]) == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Empty image collection.', QtWidgets.QMessageBox.Ok)
            return

        subModel = ImageCollectionSubModel('label_' + str(idx), list(self.labelList[idx]), self.model)
        import ImageLabelViewerSubWindow
        labelWindow = ImageLabelViewerSubWindow.ImageLabelViewerSubWindow(subModel, self)
        self.openedLabelSubWindows.append(labelWindow)
        self.parent.parent.mdiArea.addSubWindow(labelWindow)
        self.setLabelActionEnabled(False)
        labelWindow.show()

    def setTransformActionEnabled(self, flag):
        self.transformAction.setEnabled(flag)
    
    def setLabelActionEnabled(self, flag):
        for action in self.labelToggleActions.values():
            action.setEnabled(flag)
        for action in self.labelViewActions.values():
            action.setEnabled(flag)       