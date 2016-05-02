from package.utils import fileUtils
from functools import partial

def setup_controllers(ui):
    ui.file_select.clicked.connect(partial(recieve_file_selection, ui=ui))
    ui.select_save_loc.clicked.connect(partial(recieve_save_loc_selection,ui=ui))


def recieve_file_selection(ui):
    file = fileUtils.fileDialog()
    ui.file_display.setText(file)

def recieve_save_loc_selection(ui):
    save_loc = fileUtils.directoryDialog()
    ui.display_save_loc.setText(save_loc)