from utils.TransformCodeInterpreter import TransformCodeInterpreter
from TransformDialog import TransformDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap, qRgb
from PIL import Image
import numpy as np

class ImageViewerWidget(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle(model.name)
        self.model = model
        self.parent = parent

        self.parser = TransformCodeInterpreter()

        self.toolbar = QtWidgets.QToolBar()

        self.transformAction = QtWidgets.QAction('Transform', self)
        self.toolbar.addAction(self.transformAction)
        self.transformAction.triggered.connect(self.transformActionTriggered)
        
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
        self.extraInfoLabel.setText(f'{self.model.path}')
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

    def transformActionTriggered(self):
        dlg = TransformDialog(self)
        succeeded = False
        while True:
            if dlg.exec_():
                newCollectionName = dlg.nameLineEdit.text().strip()
                code = dlg.transformCode.toPlainText()

                newModel = self.parser.parseAndRun(code, self.model, newCollectionName)
                if newModel is not None:
                    succeeded = True
                    break
                else:
                    QtWidgets.QMessageBox.warning(self, 'Warning', 'Failed to run the commands!', QtWidgets.QMessageBox.Ok)
            else: 
                break

        if succeeded:
            rootModel = self.model.rootModel if self.model.rootModel else self.model
            flag = self.parent.parent.createAndAddNewImageCollection(newModel.path, newModel.name + ' (temp collection)', type='folder', rootModel=rootModel)
            if flag:
                QtWidgets.QMessageBox.information(self, 'Info', f'The new image collection {newModel.name} has been opened.', QtWidgets.QMessageBox.Ok)