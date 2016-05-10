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