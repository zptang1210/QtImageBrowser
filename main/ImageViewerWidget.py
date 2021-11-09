from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPixmap, qRgb
from models.ImageCollectionDerivedModel import ImageCollectionDerivedModel
from utils.TransformCodeParseAndRunThread import TransformCodeParseAndRunThread
from models.ImageCollectionSubModel import ImageCollectionSubModel
from main.TransformDialog import TransformDialog
from utils.PresetManager import PresetManager
from configs.availTypesConfig import modelNameDict

class ImageViewerWidget(QtWidgets.QWidget):
    maxLabelNum = 3


    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle(model.name)
        self.model = model
        self.parent = parent

        self.maxLabelNum = ImageViewerWidget.maxLabelNum
        self.scale = 100

        self.openedLabelSubWindows = []
        
        self.transformDlg = TransformDialog(self)
        self.threadpool = QtCore.QThreadPool()

        self.toolbar = QtWidgets.QToolBar()
        # self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.constructToolBar()

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setMenuBar(self.toolbar)
        self.setLayout(self.mainLayout)

        # Image viewer
        self.hLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.hLayout)

        # # Image Label
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
        # self.imageLabel.setScaledContents(True)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setPixmap(image_pixmap)
        
        self.hLayout.addWidget(self.imageLabel)

        # Slider
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


    def constructToolBar(self):
        # construct tool bar
        # Navigate menu
        self.navigateButton = QtWidgets.QToolButton()
        self.navigateButton.setText('Navigate')
        self.navigateButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.navigateMenu = QtWidgets.QMenu()

        self.goBackAction = QtWidgets.QAction('Go to previous image', self)
        self.goBackAction.setShortcut('Up')
        self.goBackAction.triggered.connect((lambda checked, signal='previous': self.goToActionTriggered(signal)))

        self.goForthAction = QtWidgets.QAction('Go to next image', self)
        self.goForthAction.setShortcut('Down')
        self.goForthAction.triggered.connect((lambda checked, signal='next': self.goToActionTriggered(signal)))

        self.goToAction = QtWidgets.QAction('Go to...', self)
        self.goToAction.triggered.connect((lambda checked, signal='goto': self.goToActionTriggered(signal)))

        self.navigateMenu.addAction(self.goBackAction)
        self.navigateMenu.addAction(self.goForthAction)
        self.navigateMenu.addAction(self.goToAction)

        self.navigateButton.setMenu(self.navigateMenu)
        self.toolbar.addWidget(self.navigateButton)

        # Transform
        self.transformAction = QtWidgets.QAction('Transform script', self)
        # self.transformAction = QtWidgets.QAction(QIcon('resources/icons/transformIcon.ico'), 'Transform', self)
        self.transformAction.setShortcut('Ctrl+T')
        self.transformAction.triggered.connect(self.transformActionTriggered)

        # Presets
        self.presetManager = PresetManager(self.presetActionTriggered)
        self.transformToolButton = QtWidgets.QToolButton()
        self.transformToolButton.setText('Transform')
        self.transformToolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.presetMenu = QtWidgets.QMenu()
        self.presetManager.generatePresetMenu(self.presetMenu, self.presetManager.presetList)
        self.presetMenu.addSeparator()
        self.presetMenu.addAction(self.transformAction)
        self.transformToolButton.setMenu(self.presetMenu)
        self.toolbar.addWidget(self.transformToolButton)

        # Label
        self.labelToolButton = QtWidgets.QToolButton()
        self.labelToolButton.setText('Label ')
        self.labelToolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

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
        self.toolbar.addWidget(self.labelToolButton)

        # Scale
        self.scaleToolButton = QtWidgets.QToolButton()
        self.scaleToolButton.setText('Scale ')
        self.scaleToolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.scaleMenu = QtWidgets.QMenu()
        self.zoominAction = QtWidgets.QAction('Zoom in', self)
        self.zoominAction.setShortcut('=')
        self.zoominAction.triggered.connect((lambda checked, signal='+': self.scaleActionTriggered(signal)))
        self.zoomoutAction = QtWidgets.QAction('Zoom out', self)
        self.zoomoutAction.setShortcut('-')
        self.zoomoutAction.triggered.connect((lambda checked, signal='-': self.scaleActionTriggered(signal)))
        self.originalScaleAction = QtWidgets.QAction('Reset to original scale', self)
        self.originalScaleAction.setShortcut('r')
        self.originalScaleAction.triggered.connect((lambda checked, signal='r': self.scaleActionTriggered(signal)))
        self.scaleMenu.addAction(self.zoominAction)
        self.scaleMenu.addAction(self.zoomoutAction)
        self.scaleMenu.addAction(self.originalScaleAction)

        self.scaleToolButton.setMenu(self.scaleMenu)
        self.toolbar.addWidget(self.scaleToolButton)

        # Copy path
        self.getPathAction = QtWidgets.QAction('Copy Path', self)
        self.getPathAction.setShortcut('Ctrl+C')
        self.toolbar.addAction(self.getPathAction)
        self.getPathAction.triggered.connect(self.getPathActionTriggered)

    def goToActionTriggered(self, key):
        if key == 'previous':
            value = self.slider.value() - 1
        elif key == 'next':
            value = self.slider.value() + 1
        elif key == 'goto':
            idx_str, ok = QtWidgets.QInputDialog.getText(None, "Go to a sepecific image", f"Index (0-{self.model.length()-1}):")
            if not ok:
                return
            else:
                try:
                    value = int(idx_str)
                except:
                    print('invalid input of index.')
                    return

        if value >= 0 and value < self.model.length():
            self.slider.setValue(value)

    def sliderValueChanged(self, value):
        if not (value >= 0 and value < self.model.length()):
            return

        image_np, image_name = self.model.get(value)

        h, w, c = image_np.shape
        image_qimg = QImage(image_np.data.tobytes(), w, h, 3*w, QImage.Format_RGB888)
        image_pixmap = QPixmap(image_qimg)
        if self.scale != 100:
            scaled_w = w * (self.scale / 100)
            scaled_h = h * (self.scale / 100)
            image_pixmap = image_pixmap.scaled(scaled_w, scaled_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.imageLabel.setPixmap(image_pixmap)

        if self.scale == 100:
            self.extraInfoLabel.setText(f'{image_name}')
        else:
            self.extraInfoLabel.setText(f'{image_name} ({self.scale}%)')

        for i in range(1, self.maxLabelNum+1):
            if value in self.labelList[i]:
                self.labelToggleActions[i].setChecked(True)
            else:
                self.labelToggleActions[i].setChecked(False)

    def transformActionTriggered(self):
        self.transformDlg.resetName()
        if self.transformDlg.exec_():
            newCollectionName = self.transformDlg.getName()
            code = self.transformDlg.getCode()
            processingSrv = self.transformDlg.getSelectedProcessingServer()
            self.transformDlg.resetName()

            TransformCodeParseAndRunThread.parseAndRun(code, self.model, newCollectionName, processingSrv, self.threadpool, self.transformFinishedCallback)
        else:
            self.transformDlg.resetNameAndCode()

    def transformFinishedCallback(self, newModel):
        if newModel is not None:
            # get model type # TODO: can be extracted to a function
            if isinstance(newModel, ImageCollectionDerivedModel):
                newModelTypeName = modelNameDict[type(newModel.sourceModel)]
            else:
                newModelTypeName = modelNameDict[type(newModel)]

            flag = self.parent.parent.createAndAddNewImageCollection(newModel.path, newModel.name + '_temp', type=newModelTypeName, parentModel=self.model)
            if flag:
                QtWidgets.QMessageBox.information(self, 'Info', f'The new image collection {newModel.name} has been opened.', QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Failed to run the commands!', QtWidgets.QMessageBox.Ok)
            
        self.transformDlg.resetNameAndCode()

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
        from main import ImageLabelViewerSubWindow
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

    def scaleActionTriggered(self, signal):
        if signal == '+':
            self.scale += 10
        elif signal == '-':
            self.scale -= 10
        elif signal == 'r':
            self.scale = 100
        else:
            raise ValueError('Invalid argument for scaleActionTriggered')

        if self.scale == 200:
            self.zoominAction.setEnabled(False)
        elif self.scale == 10:
            self.zoomoutAction.setEnabled(False)
        else:
            self.zoominAction.setEnabled(True)
            self.zoomoutAction.setEnabled(True)

        assert 10 <= self.scale <= 200

        self.sliderValueChanged(self.slider.value())

    def presetActionTriggered(self, fileName):
        # print('selected preset:', fileName)
        script = self.presetManager.getPreset(fileName)

        self.transformDlg.resetNameAndCode()
        self.transformDlg.setCode(script)

        if self.transformDlg.exec_():
            newCollectionName = self.transformDlg.getName()
            code = self.transformDlg.getCode()
            processingSrv = self.transformDlg.getSelectedProcessingServer()
            self.transformDlg.resetName()

            TransformCodeParseAndRunThread.parseAndRun(code, self.model, newCollectionName, processingSrv, self.threadpool, self.transformFinishedCallback)
        else:
            self.transformDlg.resetNameAndCode()
