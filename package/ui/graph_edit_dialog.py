
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QtWidget

class GraphEditWidget(QtWidgets.QWidget):

    def __init__(self,requested_params,default_values,communication):

        super().__init__()
        self.resize(350,200)

        self.requested_params = requested_params
        self.default_values = default_values
        self.current_values = default_values
        self.communication = communication

        layout = QtWidgets.QGridLayout(self)

        header_labels = [QtWidgets.QLabel("Graph Property",self),QtWidgets.QLabel("New Value",self)]
        for l in header_labels:
            l.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            l.setMaximumHeight(20)

        layout.addWidget(header_labels[0],0,0)
        layout.addWidget(header_labels[1],0,1)


        self.param_name_to_line_edit = {}

        for i,param_name in enumerate(requested_params):
            self.param_name_to_line_edit[param_name] = QtWidgets.QLineEdit(self)
            label = QtWidgets.QLabel(param_name,self)
            label.setAlignment(QtCore.Qt.AlignHCenter)
            layout.addWidget(label,i + 1,0)
            layout.addWidget(self.param_name_to_line_edit[param_name],i + 1,1)

        num_fields = lambda s : len(s.param_name_to_line_edit) + 1


        apply_button = QtWidgets.QPushButton(self)
        apply_button.setText("Apply Changes")
        apply_button.setMinimumWidth(100)
        apply_button.clicked.connect(self.apply_changes)
        layout.addWidget(apply_button,num_fields(self),0)

        revert_button = QtWidgets.QPushButton(self)
        revert_button.setText("Revert to Defaults")
        revert_button.clicked.connect(self.revert_to_default)
        layout.addWidget(revert_button,num_fields(self),1)

        done_button = QtWidgets.QPushButton(self)
        done_button.setText("Done")
        done_button.clicked.connect(self.done)
        layout.addWidget(done_button,num_fields(self) + 1, 0,1,2)

        self.setWindowTitle("Graph Options")

    def apply_changes(self):
        change_dictionary = {name : self.param_name_to_line_edit[name].text() for name in self.param_name_to_line_edit}
        self.current_values = change_dictionary
        self.communication.signal.emit(change_dictionary)

    def revert_to_default(self):
        self.communication.signal.emit(self.default_values)

    def done(self):
        if(self.unsaved_changes()):
            if(self.prompt_discard_unsaved_changes()):
                return
        self.close()

    def unsaved_changes(self):
        field_blank = lambda field_name : self.param_name_to_line_edit[field_name].text() == ""
        field_changed = lambda field_name : not self.param_name_to_line_edit[field_name].text() == self.current_values[field_name]
        return any(not field_blank(f) and field_changed(f) for f in list(self.param_name_to_line_edit.keys()))

    def prompt_discard_unsaved_changes(self):
        msg = "There are unsaved changes to the current graph. Do you want to discard them?"
        reply = QMessageBox.question(self,'Message', 
                msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.No:
            return True
        return False