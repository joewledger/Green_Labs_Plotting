import numpy as np


class Generic_Pie_Plotter():

    def single_pie_chart_plot(self, axes, values, title=None, title_fontsize=12, labels=None, labels_fontsize=8, autopct='%1.1f%%',
                              colors=["green", "red", "yellow", "blue"], startangle=90, autoadjust=True):

        pie_kwargs = dict(labels=labels, colors=colors, startangle=startangle)
        if(autopct):
            patches, texts, autotexts = axes.pie(values, autopct=autopct, **pie_kwargs)
        else:
            patches, texts = axes.pie(values, **pie_kwargs)

        if(autoadjust):
            adjust_kwargs = dict(labels_fontsize=labels_fontsize)
            self.adjust_texts(values, patches, texts, **adjust_kwargs)
            if(autopct):
                self.adjust_autotexts(values, patches, autotexts)

        axes.set_aspect(1)
        if(title):
            axes.set_title(title, fontsize=title_fontsize)

    def quad_pie_chart_plot(self, axes, values, title=None, title_fontsize=12, labels=None, labels_fontsize=8, autopct='%1.1f%%',
                            colors=["green", "red", "yellow", "blue"], autorotate=False):
        return None

    def adjust_texts(self, values, patches, texts, labels_fontsize=8, text_height=1.1,
                     text_adjust=8, min_percent_visible=.01, width_threshold=10):

        for value, patch, text in zip(*[values, patches, texts]):
            text.set_fontsize(labels_fontsize)

            if(not self.patch_wide_enough(patch, width_threshold)):
                text.set_position(self.get_new_patch_position(patch, text_height, text_adjust))

            text.set_visible(value > min_percent_visible)

    def adjust_autotexts(self, values, patches, autotexts, labels_fontsize=8, text_height=.5,
                         text_adjust=8, min_percent_visible=.01, width_threshold=10):

        for value, patch, autotext in zip(*[values, patches, autotexts]):
            autotext.set_fontsize(labels_fontsize)
            autotext.set_visible(value > min_percent_visible)
            if(not self.patch_wide_enough(patch, width_threshold)):
                autotext.set_position(self.get_new_patch_position(patch, text_height, text_adjust))

    def get_patch_angle(self, patch):
        return (patch.theta2 + patch.theta1) / 2

    def get_new_patch_position(self, patch, new_height, adjust):
        angle = lambda p: self.get_patch_angle(p)
        new_x = lambda p, height, adjust: p.r * height * np.cos((angle(p) - adjust) * np.pi / 180)
        new_y = lambda p, height, adjust: p.r * height * np.sin((angle(p) - adjust) * np.pi / 180)
        return (new_x(patch, new_height, adjust), new_y(patch, new_height, adjust))

    def patch_wide_enough(self, patch, threshold):
        return (patch.theta2 - patch.theta1) > threshold


class Generic_Bar_Plotter():

    def single_bar_plot(self, axes, values, errors=None, title=None, title_fontsize=12, x_ticks=None, x_tick_fontsize=12,
                        x_label=None, y_label=None, color="blue", rotation="horizontal"):

        min_y, max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        width = ind[1] / 2

        kwargs = dict(align="center", color=color)
        if(errors):
            kwargs.update(dict(yerr=errors, error_kw=dict(ecolor='black')))

        axes.bar(ind, values, width, **kwargs)

        axes.set_xlim([-width, ind[-1] + width])
        axes.set_xticks(ind)

        if(x_ticks):
            axes.set_xticklabels(x_ticks, rotation=rotation,
                                 fontsize=x_tick_fontsize)
        if(x_label):
            axes.set_xlabel(x_label)
        if(y_label):
            axes.set_ylabel(y_label)
        if(title):
            axes.set_title(title, fontsize=title_fontsize)
        axes.set_aspect(1)

    # Values and errors expect a list of tuples, of which each tuple contains two values (one for each of the twin bars)
    # bar_labels expects a tuple containing two strings
    def twin_bar_plot(self, axes, values, errors=None, title=None, title_fontsize=12, x_ticks=None, x_ticks_fontsize=12, rotation="horizontal",
                      x_label=None, y_label=None, bar_labels=None, colors=("blue", "red")):

        min_y, max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        width = ind[1] / 4

        kwarg_list = self.get_twin_bar_kwarg_list(values, errors, colors)

        rect1 = axes.bar(ind, self.unpack_tuples(values, 0), width, **kwarg_list[0])
        rect2 = axes.bar(ind + width, self.unpack_tuples(values, 1), width, **kwarg_list[1])

        axes.set_xticks(ind + width / 2)

        if(x_ticks):
            axes.set_xticklabels(x_ticks, rotation=rotation,
                                 fontsize=x_ticks_fontsize)
        if(x_label):
            axes.set_xlabel(x_label)
        if(y_label):
            axes.set_ylabel(y_label)
        if(title):
            axes.set_title(title, fontsize=title_fontsize)
        if(bar_labels):
            axes.legend((rect1[0], rect2[0]), bar_labels)
        axes.set_aspect(1)

    def twin_bar_plot_two_scales(self, axes, values, errors=None, title=None, title_fontsize=12, x_ticks=None, x_ticks_fontsize=12,
                                 rotation="horizontal", x_label=None, y_labels=None, bar_labels=None, colors=("blue", "red")):

        axes2 = axes.twinx()
        n = len(values)
        ind = np.arange(n)
        width = .35

        kwarg_list = self.get_twin_bar_kwarg_list(values, errors, colors)

        axes.bar(ind, self.unpack_tuples(values, 0), width, **kwarg_list[0])
        axes2.bar(ind + width, self.unpack_tuples(values, 1), width, **kwarg_list[1])

        axes.set_ylim(bottom=0)
        axes2.set_ylim(bottom=0)

        if(x_ticks):
            axes.set_xticks(ind + width / 2)
            axes.set_xticklabels(x_ticks, rotation=rotation, fontsize=x_ticks_fontsize)
        if(x_label):
            axes.set_xlabel(x_label)
        if(y_labels):
            axes.set_ylabel(y_labels[0])
            axes2.set_ylabel(y_labels[1])
        if(title):
            axes.set_title(title)

    def get_twin_bar_kwarg_list(self, values, errors, colors):
        kwarg_list = [dict(align="center", color=colors[x],
                           error_kw=dict(ecolor='black')) for x in range(0, 2)]
        if(errors):
            for x in range(0, 2):
                kwarg_list[x]["yerr"] = self.unpack_tuples(errors, x)
        return kwarg_list

    def unpack_tuples(self, array, index):
        return [x[index] for x in array]

    # Returns a tuple containing the highest and lowest numbers in a list of values
    # Can handle two cases: a list of floats, or a list of tuples of floats
    def get_min_max_values(self, values):
        if(all(type(x) in [float, np.float64] for x in values)):
            return min(values), max(values)
        elif(all(type(x) == tuple for x in values)):
            tuple_op = lambda l, op: op([op(item) for item in values])
            return tuple_op(values, min), tuple_op(values, max)
