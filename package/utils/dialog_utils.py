from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def fileDialog():
	fileDialog = QFileDialog()
	file = fileDialog.getOpenFileName()
	return file[0]

def directoryDialog():
	dialog = QFileDialog()
	directory = dialog.getExistingDirectory()
	return directory

def messageDialog(window_title,message):
    msg = QMessageBox()
    msg.setWindowTitle(window_title)
    msg.setText(message)
    msg.exec_()

def colorDialog():
	dialog = QColorDialog()
	color = dialog.getColor()
	return color