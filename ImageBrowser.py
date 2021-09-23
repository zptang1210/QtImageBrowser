import sys
from PyQt5 import QtWidgets
from main.ImageBrowserMainWindow import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()