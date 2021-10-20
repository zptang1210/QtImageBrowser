import sys
from PyQt5 import QtWidgets
from main.ImageBrowserMainWindow import MainWindow

if __name__ == '__main__':
    if not (sys.platform.startswith('linux') or sys.platform == 'darwin'):
        print('Unsupported operating system!')
        sys.exit(0)
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()