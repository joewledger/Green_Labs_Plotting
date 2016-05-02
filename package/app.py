import sys
from PyQt5 import QtWidgets
from package.ui import mainwindow

def run():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = mainwindow.Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    app.exec_()