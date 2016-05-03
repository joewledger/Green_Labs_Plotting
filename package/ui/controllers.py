from package.utils import fileUtils
from package.plotting import plotting as plt
from functools import partial

def setup_controllers(app,ui):
    ui.file_select.clicked.connect(partial(recieve_file_selection, app = app, ui=ui))
    ui.select_save_loc.clicked.connect(partial(recieve_save_loc_selection,app = app,ui=ui))
    ui.generate_graphs.clicked.connect(partial(recieve_generate_graphs,app=app,ui=ui))
    ui.view_previous.clicked.connect(partial(recieve_view_previous,app=app,ui=ui))
    ui.view_next.clicked.connect(partial(recieve_view_next,app=app,ui=ui))


def recieve_file_selection(app,ui):
    file = fileUtils.fileDialog()
    ui.file_display.setText(file)
    app.working_file = file

def recieve_save_loc_selection(app,ui):
    save_loc = fileUtils.directoryDialog()
    ui.display_save_loc.setText(save_loc)
    app.save_loc = save_loc

def recieve_generate_graphs(app,ui):
    #app.hobo_data_container.import_datafile(app.working_file)
    num_graphs = plt.determine_num_graphs(app.hobo_data_container)
    app.curr_graph = 1
    app.graph_count = num_graphs
    set_graph_count(app,ui)
    
def recieve_view_previous(app,ui):
    if(app.curr_graph in range(2,app.graph_count + 1)):
        app.curr_graph -= 1
        set_graph_count(app,ui)

def recieve_view_next(app,ui):
    if(app.curr_graph in range(1,app.graph_count)):
        app.curr_graph += 1
        set_graph_count(app,ui)

def set_graph_count(app,ui):
    ui.graph_count.setText("%d/%d" % (app.curr_graph,app.graph_count))