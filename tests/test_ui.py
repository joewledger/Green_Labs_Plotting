from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import PyQt5.QtGui as QtGui
from package.ui import mainwindow,controllers
from package.utils import param_utils
import sys
import package.ui.graph_edit_dialog as ged
from collections import *
from copy import copy,deepcopy


class Communicate_Parameter_Collection(QObject):
    signal = pyqtSignal(param_utils.Parameter_Collection)

def test_graph_edit():
    app = QApplication(sys.argv)

    title_param = param_utils.Parameter_Expectation("Title",param_utils.Param_Type_Wrapper(str))
    x_label_param = param_utils.Parameter_Expectation("X-Axis Label", param_utils.Param_Type_Wrapper(str))
    color_param = param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(type(QtGui.QColor()),is_list=True,length=2))
    #color2_param = param_utils.Parameter_Expectation("Color", param_utils.Param_Type_Wrapper(type(QtGui.QColor())))


    printf = lambda x : print(x)

    comm = Communicate_Parameter_Collection()

    comm.signal.connect(printf)

    default_parameters = param_utils.Parameter_Collection(OrderedDict([(title_param, "Equipment Open/Closed Patterns"),
                                                              (x_label_param, "Status"),
                                                              (color_param, [QtGui.QColor(Qt.blue),QtGui.QColor(Qt.red)])]))

    curr_parameters = param_utils.Parameter_Collection(OrderedDict([(title_param, "Equipment Open/Closed Patterns"),
                                                              (x_label_param, "Status"),
                                                              (color_param, [QtGui.QColor(Qt.blue),QtGui.QColor(Qt.red)])]))


    widget = ged.GraphEditWidget(default_parameters,curr_parameters,comm)
    widget.show()
    app.exec_()

def test_imports():
    from PyQt5.QtGui import QColor

    print(type(QColor()))