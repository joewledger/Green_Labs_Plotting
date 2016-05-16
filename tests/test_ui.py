from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from package.ui import mainwindow,controllers
import sys
import package.ui.graph_edit_dialog as ged

def test_graph_edit():
    app = QApplication(sys.argv)
    requested_params = ["Title","X Axis","Y Axis"]
    widget = ged.GraphEditWidget(requested_params)
    widget.show()
    app.exec_()