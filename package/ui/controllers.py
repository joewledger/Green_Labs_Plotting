from package.utils import fileUtils
from functools import partial

def setup_controllers(app,ui):
    ui.file_select.clicked.connect(partial(recieve_file_selection, app = app, ui=ui))
    ui.select_save_loc.clicked.connect(partial(recieve_save_loc_selection,app = app,ui=ui))
    ui.generate_graphs.clicked.connect(partial(recieve_generate_graphs,app=app,ui=ui))


def recieve_file_selection(app,ui):
    file = fileUtils.fileDialog()
    ui.file_display.setText(file)
    app.working_file = file

def recieve_save_loc_selection(app,ui):
    save_loc = fileUtils.directoryDialog()
    ui.display_save_loc.setText(save_loc)
    app.save_loc = save_loc

def recieve_generate_graphs(app,ui):
    ui.file_display.setText(app.save_loc)
    ui.display_save_loc.setText(app.working_file)