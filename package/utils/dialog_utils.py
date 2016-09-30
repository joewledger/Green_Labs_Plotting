from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


#Opens a file dialog and gets the filepath selected by the user
def fileDialog():
    fileDialog = QFileDialog()
    file = fileDialog.getOpenFileName()
    return file[0]


#Opens a directory dialog and gets the directory selected by the user
def directoryDialog():
    dialog = QFileDialog()
    directory = dialog.getExistingDirectory()
    return directory


#Opens a message dialog with the provided message in a separate window
def messageDialog(window_title, message):
    msg = QMessageBox()
    msg.setWindowTitle(window_title)
    msg.setText(message)
    msg.exec_()


#Opens a color dialog and gets the color selected by the user
def colorDialog():
    dialog = QColorDialog()
    color = dialog.getColor()
    return color
