
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import package.utils.dialog_utils as dialog_utils

"""
This module defines and creates a GraphEditWidget, which uses the parameter expectation objects
for the current plot to allow for editing of the plot. The widget is dynamically created in that different
parameters will be editable depending on the Plotter type used for the current Canvas.
"""
class GraphEditWidget(QtWidgets.QWidget):

    #requested_params and default_values are param_utils.Parameter_Collection objects
    def __init__(self, default_parameters, current_parameters, communication):

        super().__init__()
        self.resize(350, 200)

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

    #Creates selection widgets based on parameter expectations
    def create_selection_widgets(self):
        for expectation in self.default_parameters:

            label_text = lambda index: "%s %d" % (expectation.param_name, index + 1) if len(expectation) > 1 else expectation.param_name

            labels = [QtWidgets.QLabel(label_text(i), self) for i in range(0, len(expectation))]
            selectors = [self.get_selector(expectation) for x in range(0, len(expectation))]

            self.label_list.extend(labels)
            self.selector_list.extend(selectors)
            self.param_expectation_to_selector[expectation] = selectors

            #If the expectation type is a QColor, then we create color display widgets
            #for each of the selectors built from the expectation and connect them to recieve_select_color
            if(expectation.get_type() == QtGui.QColor):
                for i, selector in enumerate(selectors):
                    color = self.get_default_value(expectation, i)
                    color_display = self.create_color_display_widget(color)
                    self.selector_to_color_display[selector] = color_display
                    self.selector_to_stored_color[selector] = color
                    selector.clicked.connect(self.receive_select_color)

    #Builds a selector for a given parameter expectation
    #A selector for Parameter Expectations that want a string will be a QLineEdit
    #A selector for Parameter Expectations that want a color will be a QPushButton
    def get_selector(self, expectation):
        _type = expectation.get_type()
        if(_type == str):
            return QtWidgets.QLineEdit(self)
        elif(_type == QtGui.QColor):
            button = QtWidgets.QPushButton(self)
            button.setText("Choose Color")
            return button

    #Adds the selection widgets to the layout (from self.selector_list)
    #Calling this method assumes that self.create_selection_widgets() has already been called
    def add_selection_widgets_to_layout(self):
        for i, selector in enumerate(self.selector_list):
            row = i + 1

            label = self.label_list[i]
            label.setAlignment(QtCore.Qt.AlignHCenter)
            self.layout.addWidget(label, row, 0)

            if(type(selector) == QtWidgets.QLineEdit):
                self.layout.addWidget(selector, row, 1, 1, 3)
            elif(type(selector) == QtWidgets.QPushButton):
                self.layout.addWidget(selector, row, 1, 1, 2)
                color_display = self.selector_to_color_display[selector]
                self.layout.addWidget(color_display, row, 3)

    #Returns a color display widget for displaying colors in the application
    def create_color_display_widget(self, color):
        widget = QtWidgets.QWidget(self)
        self.change_widget_color(widget, color)
        return widget

    #Gets the default value of an expectation
    #If the expectation is a list, gets the default value at a given index
    def get_default_value(self, expectation, index=0):
        value = self.default_parameters[expectation]
        return (value[index] if type(value) == list else value)

    #Gets the current value for a given parameter expectation
    #If the expectation is a list, gets the default value at a given index
    def get_current_value(self, expectation, index=0):
        value = self.current_parameters[expectation]
        return (value[index] if type(value) == list else value)

    #Listener for the select color buttons
    def receive_select_color(self):
        selector = self.sender()
        color_display_widget = self.selector_to_color_display[selector]
        color = dialog_utils.colorDialog()
        self.selector_to_stored_color[selector] = color
        self.change_widget_color(color_display_widget, color)

    #Changes the widget background color
    def change_widget_color(self, widget, new_color):
        palette = QtGui.QPalette()
        palette.setColor(widget.backgroundRole(), new_color)
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)

    #Add header labels to the widget
    def add_header_labels(self):
        font = QtGui.QFont()
        font.setBold(True)
        header_labels = [QtWidgets.QLabel("Graph Property", self), QtWidgets.QLabel("New Value", self)]
        for i, l in enumerate(header_labels):
            l.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            l.setMaximumHeight(20)
            l.setFont(font)
            self.layout.addWidget(l, 0, i * 2)

    #Adds the apply button to the widget and connects it to the listener apply_changes()
    def add_apply_button(self):
        apply_button = QtWidgets.QPushButton(self)
        apply_button.setText("Apply Changes")
        apply_button.setMinimumWidth(100)
        apply_button.clicked.connect(self.apply_changes)
        self.layout.addWidget(apply_button, self.num_fields(), 0, 1, 2)

    #Adds the revert button to the widget
    def add_revert_button(self):
        revert_button = QtWidgets.QPushButton(self)
        revert_button.setText("Revert to Defaults")
        revert_button.clicked.connect(self.revert_to_default)
        self.layout.addWidget(revert_button, self.num_fields(), 2, 1, 2)

    #Adds the done button to the widget
    def add_done_button(self):
        done_button = QtWidgets.QPushButton(self)
        done_button.setText("Done")
        done_button.clicked.connect(self.done)
        self.layout.addWidget(done_button, self.num_fields() + 1, 0, 1, 4)

    #Returns a dictionary mapping parameter expectations to values if the values have changed.
    def get_change_dictionary(self):

        text = lambda selector: selector.text() if selector.text() != "" else None
        color = lambda selector: self.selector_to_stored_color[selector]
        text_or_color = lambda exp, selector: text(selector) if exp.get_type() == str else color(selector)

        change_dictionary = {}

        for exp in self.param_expectation_to_selector:
            changes = [text_or_color(exp, selector) for selector in self.param_expectation_to_selector[exp] if(text_or_color(exp, selector))]
            if(len(changes) > 0):
                change_dictionary[exp] = (changes[0] if len(changes) == 1 else changes)
        return change_dictionary

    #Applies the changes by sending a signal with the change directory back to the MainControllers
    def apply_changes(self):
        change_dictionary = self.get_change_dictionary()
        self.current_parameters.update_values(change_dictionary)
        self.communication.signal.emit(self.current_parameters)

    #Reverts the changes to their default values by sending a signal
    #with the self.default_parameters back to the MainControllers
    #Also sets the text selectors to blank and any color display widgets back to their default color
    def revert_to_default(self):
        for exp in self.param_expectation_to_selector:
            for i, selector in enumerate(self.param_expectation_to_selector[exp]):
                if(exp.get_type() == str):
                    selector.setText("")
                elif(exp.get_type() == QtGui.QColor):
                    default_color = self.get_default_value(exp, index=i)
                    color_display = self.selector_to_color_display[selector]
                    self.change_widget_color(color_display, default_color)
                    self.selector_to_stored_color[selector] = default_color

        self.communication.signal.emit(self.default_parameters)

    #Checks if there are unsaved changes, and if there are prompts the user to see if they really want to quit
    #If they do, closes the GraphEditWidget
    def done(self):
        if(self.unsaved_changes()):
            if(self.prompt_discard_unsaved_changes()):
                return
        self.close()

    #Checks to see if there are any unsaved changes by comparing the change dictionary against the current parameters
    def unsaved_changes(self):
        change_dictionary = self.get_change_dictionary()
        changed = lambda exp: change_dictionary[exp] != self.current_parameters[exp]
        return any(changed(exp) for exp in change_dictionary.keys())

    #Prompts the user and asks if they want to discard unsaved changes
    def prompt_discard_unsaved_changes(self):
        msg = "There are unsaved changes to the current graph. Do you want to discard them?"
        return QMessageBox.question(self, 'Message', msg, QMessageBox.Yes, QMessageBox.No) == QMessageBox.No
