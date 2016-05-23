
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import package.utils.param_utils as param_utils
import package.utils.dialog_utils as dialog_utils

class GraphEditWidget(QtWidgets.QWidget):

    #requested_params and default_values are param_utils.Parameter_Collection objects
    def __init__(self,default_parameters,current_parameters,communication):

        super().__init__()
        self.resize(350,200)

        self.default_parameters = default_parameters
        self.current_parameters = current_parameters
        self.communication = communication

        #Maps param_expectation a list of selectors
        self.param_expectation_to_selector = {}
        self.selector_to_color_display = {}
        self.selector_to_stored_color = {}

        self.label_list = []
        self.selector_list = []

        self.layout = QtWidgets.QGridLayout(self)
        self.add_header_labels()

        #Create and add Selector labels,selectors, and color display widgets to the layout
        self.create_selection_widgets()
        self.add_selection_widgets_to_layout()

        self.add_apply_button()
        self.add_revert_button()
        self.add_done_button()
        self.setWindowTitle("Graph Options")


    def num_fields(self):
        return len(self.selector_list) + 1

    def create_selection_widgets(self):
        for expectation in self.default_parameters:

            label_text = lambda index : "%s %d" % (expectation.param_name,index + 1) if len(expectation) > 1 else expectation.param_name

            labels = [QtWidgets.QLabel(label_text(i),self) for i in range(0,len(expectation))]
            selectors = [self.get_selector(expectation) for x in range(0,len(expectation))]

            self.label_list.extend(labels)
            self.selector_list.extend(selectors)
            self.param_expectation_to_selector[expectation] = selectors

            if(expectation.get_type() == QtGui.QColor):
                for i,selector in enumerate(selectors):
                    color = self.get_default_value(expectation,i)
                    color_display = self.create_color_display_widget(color)
                    self.selector_to_color_display[selector] = color_display
                    self.selector_to_stored_color[selector] = color
                    selector.clicked.connect(self.receive_select_color)

    def get_selector(self,expectation):
        _type = expectation.get_type()
        if(_type == str):
            return QtWidgets.QLineEdit(self)
        elif(_type == QtGui.QColor):
            button = QtWidgets.QPushButton(self)
            button.setText("Choose Color")
            return button

    def add_selection_widgets_to_layout(self):
        for i,selector in enumerate(self.selector_list):
            row = i + 1

            label = self.label_list[i]
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.layout.addWidget(label,row,0)

            if(type(selector) == QtWidgets.QLineEdit):
                self.layout.addWidget(selector,row,1,1,3)
            elif(type(selector) == QtWidgets.QPushButton):
                self.layout.addWidget(selector,row,1,1,2)
                color_display = self.selector_to_color_display[selector]
                self.layout.addWidget(color_display,row,3)


    def create_color_display_widget(self,color):
        widget = QtWidgets.QWidget(self)
        self.change_widget_color(widget,color)
        return widget

    def get_default_value(self,expectation,index=0):
        value = self.default_parameters[expectation]
        return (value[index] if type(value) == list else value)

    def get_current_value(self,expectation,index=0):
        value = self.current_parameters[expectation]
        return (value[index] if type(value) == list else value)

    def receive_select_color(self):
        selector = self.sender()
        color_display_widget = self.selector_to_color_display[selector]
        color = dialog_utils.colorDialog()
        self.selector_to_stored_color[selector] = color
        self.change_widget_color(color_display_widget,color)

    def change_widget_color(self,widget,new_color):
        palette = QtGui.QPalette()
        palette.setColor(widget.backgroundRole(),new_color)
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)

    def add_header_labels(self):
        font = QtGui.QFont()
        font.setBold(True)
        header_labels = [QtWidgets.QLabel("Graph Property",self),QtWidgets.QLabel("New Value",self)]
        for i,l in enumerate(header_labels):
            l.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            l.setMaximumHeight(20)
            l.setFont(font)
            self.layout.addWidget(l,0,i * 2)

    def add_apply_button(self):
        apply_button = QtWidgets.QPushButton(self)
        apply_button.setText("Apply Changes")
        apply_button.setMinimumWidth(100)
        apply_button.clicked.connect(self.apply_changes)
        self.layout.addWidget(apply_button,self.num_fields(),0,1,2)

    def add_revert_button(self):
        revert_button = QtWidgets.QPushButton(self)
        revert_button.setText("Revert to Defaults")
        revert_button.clicked.connect(self.revert_to_default)
        self.layout.addWidget(revert_button,self.num_fields(),2,1,2)

    def add_done_button(self):
        done_button = QtWidgets.QPushButton(self)
        done_button.setText("Done")
        done_button.clicked.connect(self.done)
        self.layout.addWidget(done_button,self.num_fields() + 1, 0,1,4)

    def get_change_dictionary(self):

        text = lambda selector : selector.text() if selector.text() != "" else None
        color = lambda selector : self.selector_to_stored_color[selector]
        text_or_color = lambda exp, selector: text(selector) if exp.get_type() == str else color(selector)

        change_dictionary = {}

        for exp in self.param_expectation_to_selector:
            changes = [text_or_color(exp,selector) for selector in self.param_expectation_to_selector[exp] if(text_or_color(exp,selector))]
            if(len(changes) > 0):
                change_dictionary[exp] = (changes[0] if len(changes) == 1 else changes) 
        return change_dictionary


    def apply_changes(self):
        change_dictionary = self.get_change_dictionary()
        self.current_parameters.update_values(change_dictionary)
        self.communication.signal.emit(self.current_parameters)

    def revert_to_default(self):

        for exp in self.param_expectation_to_selector:
            for i,selector in enumerate(self.param_expectation_to_selector[exp]):
                if(exp.get_type() == str):
                    selector.setText("")
                elif(exp.get_type() == QtGui.QColor):
                    default_color = self.get_default_value(exp,index=i)
                    color_display = self.selector_to_color_display[selector]
                    self.change_widget_color(color_display,default_color)
                    self.selector_to_stored_color[selector] = default_color

        self.communication.signal.emit(self.default_parameters)

    def done(self):
        if(self.unsaved_changes()):
            if(self.prompt_discard_unsaved_changes()):
                return
        self.close()

    def unsaved_changes(self):
        change_dictionary = self.get_change_dictionary()
        changed = lambda exp : change_dictionary[exp] != self.current_parameters[exp]
        return any(changed(exp) for exp in change_dictionary.keys())

    def prompt_discard_unsaved_changes(self):
        msg = "There are unsaved changes to the current graph. Do you want to discard them?"
        reply = QMessageBox.question(self,'Message', 
                msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.No:
            return True
        return False