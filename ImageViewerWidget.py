from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QRgba64, qRgb
from PIL import Image
import numpy as np

class ImageViewerWidget(QtWidgets.QWidget):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle(model.name)
        self.model = model
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

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
        
        self.layout.addWidget(self.imageLabel)

        self.slider = QtWidgets.QSlider(Qt.Vertical, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.model.length()-1)
        self.slider.setInvertedAppearance(True)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.layout.addWidget(self.slider)

        self.slider.setValue(0)
        self.sliderValueChanged(0)


    def sliderValueChanged(self, value):
        image_np = self.model.get(value)

        h, w, c = image_np.shape
        image_qimg = QImage(image_np.data, w, h, 3*w, QImage.Format_RGB888)
        image_pixmap = QPixmap(image_qimg)
        self.imageLabel.setPixmap(image_pixmap)
