class Generic_Bar_Plotter(Plotter):

    def __init__(self):
        Plotter.__init__(self)

    def single_bar_plot(self,axes,values,errors=None,title=None,title_fontsize=12,x_ticks=None,x_tick_fontsize=12,
                        x_label=None,y_label=None,color="blue",rotation="horizontal"):

        min_y,max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        margin = .05
        width = ind[1] / 2

        if(errors):
            axes.bar(ind,values,width,align="center",color=color,yerr=errors,error_kw=dict(ecolor='black'))
        else:
            axes.bar(ind,values,width,align="center",color=color)

        axes.set_xlim([-width,ind[-1] + width])
        axes.set_xticks(ind)

        if(x_ticks): axes.set_xticklabels(x_ticks,rotation=rotation,fontsize=x_tick_fontsize)
        if(x_label): axes.set_xlabel(x_label)
        if(y_label): axes.set_ylabel(y_label)
        if(title): axes.set_title(title,fontsize=title_fontsize)
        axes.set_aspect(1)

    #Values and errors expect a list of tuples, of which each tuple contains two values (one for each of the twin bars)
    #bar_labels expects a tuple containing two strings
    def twin_bar_plot(self,axes,values,errors=None,title=None,title_fontsize=12,x_ticks=None,x_ticks_fontsize=12,rotation="horizontal",
                      x_label=None,y_label=None,bar_labels=None,colors=("blue","red")):
        
        min_y,max_y = self.get_min_max_values(values)
        ind = np.arange(len(values)) * (max_y / len(values))
        margin = .05
        width = ind[1] / 4

        kwarg_list = self.get_twin_bar_kwarg_list(values,errors,colors)

        rect1 = axes.bar(ind,self.unpack_tuples(values,0),width,**kwarg_list[0])
        rect2 = axes.bar(ind + width,self.unpack_tuples(values,1),width,**kwarg_list[1])

        axes.set_xticks(ind + width / 2)

        if(x_ticks): axes.set_xticklabels(x_ticks,rotation=rotation,fontsize=x_ticks_fontsize)
        if(x_label): axes.set_xlabel(x_label)
        if(y_label): axes.set_ylabel(y_label)
        if(title): axes.set_title(title,fontsize=title_fontsize)
        if(bar_labels): axes.legend((rect1[0], rect2[0]), bar_labels)
        axes.set_aspect(1)


    def twin_bar_plot_two_scales(self,axes,values,errors=None,title=None,title_fontsize=12,x_ticks=None,x_ticks_fontsize=12,rotation="horizontal",
                                  x_label=None,y_labels=None,bar_labels=None,colors=("blue","red")):

        axes2 = axes.twinx()
        n = len(values)
        ind = np.arange(n)
        width = .35

        kwarg_list = self.get_twin_bar_kwarg_list(values,errors,colors)
        print(kwarg_list[1]["yerr"])

        rect1 = axes.bar(ind,self.unpack_tuples(values,0),width,**kwarg_list[0])
        rect2 = axes2.bar(ind + width,self.unpack_tuples(values,1),width,**kwarg_list[1])

        axes.set_ylim(bottom=0)
        axes2.set_ylim(bottom=0)

        if(x_ticks):
            axes.set_xticks(ind + width / 2)
            axes.set_xticklabels(x_ticks,rotation=rotation,fontsize=x_ticks_fontsize)
        if(x_label): axes.set_xlabel(x_label)
        if(y_labels): 
            axes.set_ylabel(y_labels[0])
            axes2.set_ylabel(y_labels[1])
        if(title): axes.set_title(title)


    def get_twin_bar_kwarg_list(self,values,errors,colors):
        kwarg_list = [dict(align="center",color=colors[x],error_kw=dict(ecolor='black')) for x in range(0,2)]
        if(errors):
            for x in range(0,2):
                kwarg_list[x]["yerr"] = self.unpack_tuples(errors,x)
        return kwarg_list

    def unpack_tuples(self,array,index):
        return [x[index] for x in array]


    #Returns a tuple containing the highest and lowest numbers in a list of values
    #Can handle two cases: a list of floats, or a list of tuples of floats
    def get_min_max_values(self,values):
        if(all(type(x) in [float,np.float64] for x in values)):
            return min(values),max(values)
        elif(all(type(x) == tuple for x in values)):
            tuple_op = lambda l,op : op([op(item) for item in values])
            return tuple_op(values,min),tuple_op(values,max)