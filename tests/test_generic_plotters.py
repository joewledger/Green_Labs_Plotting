from package.plotting import generic_plotters as gen_plt
import matplotlib.pyplot as plt
from nose.tools import nottest


@nottest
def generic_test_dummy_data(data, plotting_function, **kwargs):

    fig = plt.figure()
    axes = fig.add_subplot(111)

    plotting_function(axes, data, **kwargs)

    plt.show()


def test_single_pie_chart():

    values = [.12, .35, .33, .20]
    pie_plt = gen_plt.Generic_Pie_Plotter()

    kwargs = dict(labels=["Test %d" % d for d in range(1, 5)], title="Example Title")

    generic_test_dummy_data(values, pie_plt.single_pie_chart_plot, **kwargs)

    pass


def test_get_min_max_values():

    bar_plotter = gen_plt.Generic_Bar_Plotter()

    data = [(.56, .43), (.75, .25), (.82, .35)]
    assert(bar_plotter.get_min_max_values(data) == (.25, .82))

    data2 = [.45, .67, .54]
    assert(bar_plotter.get_min_max_values(data2) == (.45, .67))


def test_twin_bar_plot_two_scales():
    data = [(.56, .43), (.75, .25), (.82, .35), (.26, .89)]
    errors = [(.1, .05), (.12, .17), (.23, .32), (.45, .37)]
    y_labels = ["Label 1", "Label 2"]
    bar_plotter = gen_plt.Generic_Bar_Plotter()
    kwargs = dict(title="Example", errors=errors, x_ticks=[1, 2, 3, 4], y_labels=y_labels, x_label="Time")

    generic_test_dummy_data(data, bar_plotter.twin_bar_plot_two_scales, **kwargs)


def test_twin_bar_plot():

    data = [(.56, .43), (.75, .25), (.82, .35)]
    errors = [(.1, .05), (.12, .17), (.23, .32)]
    bar_plotter = gen_plt.Generic_Bar_Plotter()
    kwargs = dict(title="Example", colors=("blue", "red"), errors=errors, x_ticks=["Label 1", "Label 2", "Label 3"],
                  x_label="Time", y_label="Value", bar_labels=("Bar 1", "Bar 2"))

    generic_test_dummy_data(data, bar_plotter.twin_bar_plot, **kwargs)


def test_single_bar_plots():

    data = [75.4, 76.3, 78.2, 74.9]
    bar_plotter = gen_plt.Generic_Bar_Plotter()
    kwargs = dict(x_ticks=["A", "B", "C", "D"])
    generic_test_dummy_data(data, bar_plotter.single_bar_plot, **kwargs)
