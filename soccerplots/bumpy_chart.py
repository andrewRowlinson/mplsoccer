"""
__author__: Anmol_Durgapal(@slothfulwave612)

A Python module for plotting bumpy-charts.
"""

## import required packages/modules
import collections
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import warnings

from . import utils

## ignore UserWarning
warnings.simplefilter("ignore", UserWarning)

class Bumpy:    
    """
    contains methods to make bumpy-charts.
    """

    def __init__(
        self, background_color="#1B1B1B", scatter_color="#4F535C", scatter_points='o', scatter_size=100,
        ticklabel_size=13, fontfamily="Liberation Serif", curviness=0.85,
        rotate_xticks=0, rotate_yticks=0, show_right=False, label_size=20, labelpad=20, horizontalalignment_x='left',
        horizontalalignment_y='right', alignment_xvalue=0.035, alignment_yvalue=0.16, label_color='#FFFFFF', 
        plot_labels=True
    ):
        """
        Function to initialize the object of the class.

        Args:
            background_color (str, optional): background color for the plot. Defaults to "#1B1B1B".
            scatter_color (str, optional): color value for our scater points. Defaults to "#4F535C".
            scatter_points (str, optional): type of scatter point user wants to plot. Defaults to 'o'.
            scatter_size (float, optional): size of the scatter_points. Defaults to 100.
            ticklabel_size (float, optional): fontsize of the ticklabel. Defaults to 13.
            fontfamily (str, optional): fontfamily available in matplotlib. Defaults to "Liberation Serif".
            curviness (float, optional): value of the curved line. Defaults to 0.85.
            rotate_xticks (int, optional): rotation of xticklabels in degrees. Defaults to 0.
            rotate_yticks (int, optional): rotation of yticklabels. Defaults to 0.
            show_right (bool, optional): yticklabels to be shown at the right y-axis or not. Defaults to False.
            label_size (int, optional): fontsize of the x and y labels. Defaults to 20.
            labelpad (int, optional): padding between labels and ticklables. Defaults to 20.
            horizontalalignment_x (str, optional): alignment for the x-label. Defaults to 'left'.
            horizontalalignment_y (str, optional): alignment for the y-label. Defaults to 'right'.
            alignment_xvalue (float, optional): value for alignment of x-label. Defaults to 0.035.
            alignment_yvalue (float, optional): value for alignment of y-label. Defaults to 0.16.
            label_color (str, optional): color value for labels. Defaults to '#FFFFFF'.
            plot_labels (bool, optional): to plot the labels. Defaults to True.
        """        
        self.background_color = background_color
        self.scatter_color = scatter_color
        self.scatter_points = scatter_points
        self.scatter_size = scatter_size
        self.ticklabel_size = ticklabel_size
        self.fontfamily = fontfamily
        self.curviness = curviness
        self.rotate_xticks = rotate_xticks
        self.rotate_yticks = rotate_yticks
        self.show_right = show_right
        self.label_size = label_size
        self.labelpad = labelpad
        self.horz_xalign = horizontalalignment_x
        self.horz_yalign = horizontalalignment_y
        self.align_xval = alignment_xvalue
        self.align_yval = alignment_yvalue
        self.label_color = label_color
        self.plot_labels = plot_labels
    
    def plot(
        self, x_list, y_list, values, highlight_dict, filename=None, dpi=300, figsize=(12,8), lw=2, show=True, 
        x_label=None, y_label=None, title=None, title_dict=None, xy=None, title_color="#FFFFFF", title_size=25, 
        endnote=None, xy_end=None, end_color="#808080", end_size=15, image=None, image_coord=None, alpha=1, 
        interpolation="none", xlim=None, ylim=None, figax=None, **kwargs
        ):
        """
        Function to plot bumpy-chart.

        Args:
            x_list (list): xticklabel values(serial-wise order from left to right).
            y_list (list): yticklabel values(serial-wise order from top to bottom).
            values (dict): containing key as team-name and value as list of rank for that team.
            highlight_dict (dict): containing key as the team-name to be highlighted with their corresponding color.
            filename (str, optional): the name of the file per which plot will be saved. Defaults to None.
            dpi (int, optional): dots per inch value. Defaults to 300.
            figsize (tuple, optional): size of the plot. Defaults to (12,8).
            lw (int, optional): line-width for the lines in the plot. Defaults to 2.
            show (bool, optional): whether to display the plot or not. Defaults to True.
            x_label (str, optional): x-label-name. Defaults to None.
            y_label (str, optional): y-label-name. Defaults to None.
            title (str, optional): the title of the plot. Defaults to None.
            title_dict (dict, optional): extra information about title. Defaults to None.
            xy (tuple, optional): x and y coordinate for the title. Defaults to None.
            title_color (str, optional): color value for title. Defaults to "#FFFFFF".
            title_size (float, optional): size of the title. Defaults to 25.
            endnote (str, optional): the endnote of the plot. Defaults to None.
            xy_end (tuple, optional): x and y coordinate for endnote. Defaults to None.
            end_color (str, optional): color value for the endnote. Defaults to "#808080".
            end_size (float, optional): size of endnote. Defaults to 15.
            image (str, optional): path of the image to be added. Defaults to None.
            image_coord (list, optional): containing left, bottom, width, height for image. Defaults to None.
            alpha (float, optional): the alpha value for the image. Defaults to 1.
            interpolation (str, optional): interpolation for the image. Defaults to "none".
            xlim (tuple, optional): limit for x axis value. Defaults to None.
            ylim (tuple, optional): limit for y axis value. Defaults to None.
            figax (tuple, optional): figure and axis object. Defaults to None.

        Returns:
            matplotlib.figure.Figure: figure object.
            axes.Axes: axes object.
        """        
        
        ## assert conditions
        assert(type(x_list) == list), "x_list argument should be a list"
        assert(type(y_list) == list), "y_list argument should be a list"
        assert(type(values) == dict), "values argument should be dictionary"
        assert(type(highlight_dict) == dict), "highlight_dict should be a dictionary"

        if figax:
            fig, ax = figax
        else:
            ## create subplot
            fig, ax = plt.subplots(figsize=figsize, facecolor=self.background_color)
            ax.set_facecolor(self.background_color)

        ## length of values dict
        len_y = len(y_list)

        ## set title coordinates
        if title != None and xy == None:
            xy = [0, len(values) + 1.3]

        ## set endnode coordinates
        if endnote != None and xy_end == None:
            xy_end = [len(x_list) + 1.3, -3]

        ## iterate thorugh the dictionary and plot the chart
        for key, value in values.items():
            
            ## find value in highlight_dict
            if highlight_dict.get(key):
                color = highlight_dict[key]     ## fetch the required color
                zorder = 3
            else:
                color = self.scatter_color      
                zorder = 2

            ## if string get index
            if type(value[0]) == str:
                ## init an empty list
                index_value = []

                ## fetch the index
                for i in value:
                    index_value.append(y_list.index(i) + 1)

            else:
                index_value = value

            ## plot scatter-points
            ax.scatter(
                np.arange(len(value)), len_y - np.array(index_value) + 1, 
                marker=self.scatter_points, 
                color=color,
                s=self.scatter_size,
                zorder=zorder
            )

            ## create bezier curves 
            verts = [(i + d, len_y - vij + 1) for i, vij in enumerate(index_value) for d in  (-self.curviness, 0, self.curviness)][1: -1]
            codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
            path = Path(verts, codes)
            patch = patches.PathPatch(path, facecolor='none', lw=lw, edgecolor=color, zorder=zorder)
            ax.add_patch(patch)

        ## plot labels 
        if self.plot_labels == True:
            fig, ax = self.__add_labels(x_list, y_list, highlight_dict, figax=(fig, ax), x_label=x_label, y_label=y_label)
        
        ## plot title
        if title != None and title_dict != None:
            ax = utils.plot_text(xy[0], xy[1], title, title_dict, ax, color_rest=title_color, fontsize=title_size, ha="left", va="baseline")

        ## plot endnote
        if endnote != None:
            ax.text(xy_end[0], xy_end[1], endnote, fontdict=dict(color=end_color), 
                    ha='right', va='center', fontsize=end_size
            )

        ## add image
        if image != None and image_coord != None:
            fig = utils.add_image(image, fig, image_coord[0], image_coord[1], image_coord[2], image_coord[3], alpha=alpha, interpolation=interpolation)

        ## xlim and ylim
        if xlim != None:
            ax.set(xlim=xlim)
        elif ylim != None:
            ax.set(ylim=ylim)

        if filename != None:
            ## save the file
            fig.savefig(filename, dpi=dpi, bbox_inches='tight')

        if show == 'True':
            ## to show plot
            plt.show()

        return fig, ax

    def __add_labels(self, x_list, y_list, highlight_dict, figax, x_label, y_label):
        """
        Function to add labels and titles to the plot.

        Args:
            x_list (list): xticklabel values(serial-wise order from left to right).
            y_list (list): yticklabel values(serial-wise order from top to bottom).
            highlight_dict (dict): containing key as the team-name to be highlighted with their corresponding color.
            figax (tuple): containing figure and axis object.
            x_label (str): x-label-name.
            y_label (str): y-label-name.

        Returns:
            matplotlib.figure.Figure: figure object.
            axes.Axes: axis object.
        """        
        
        ## fetch figure and axis object
        fig, ax = figax[0], figax[1]

        ## remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        ## get labels for x and y axis
        x_labels = utils.set_labels(ax=ax, label_value=x_list, label_axis='x')
        y_labels = utils.set_labels(ax=ax, label_value=y_list, label_axis='y')

        ## set ticklabels
        ax.set_xticklabels(x_labels, fontfamily=self.fontfamily, fontsize=self.ticklabel_size, rotation=self.rotate_xticks)
        ax.set_yticklabels(y_labels, fontfamily=self.fontfamily, fontsize=self.ticklabel_size, rotation=self.rotate_yticks)

        ## set x and y axis labels
        ax.set_xlabel(x_label, fontfamily=self.fontfamily, fontsize=self.label_size, labelpad=self.labelpad, 
                       horizontalalignment=self.horz_xalign, x=self.align_xval)
        ax.set_ylabel(y_label, fontfamily=self.fontfamily, fontsize=self.label_size, labelpad=self.labelpad, 
                       horizontalalignment=self.horz_yalign, y=self.align_yval)
        ax.xaxis.label.set_color(self.label_color)
        ax.yaxis.label.set_color(self.label_color)

        ## remove tick marks
        ax.tick_params(axis='both', which='both', length=0, colors=self.label_color)

        if self.show_right == True:
            ax.tick_params(direction='out', axis='y', which='both', labelleft=True, labelright=True,
                    right=True, left=True)

        return fig, ax
    
    def __repr__(self):        
        return f"""{self.__class__.__name__}(background_color='{self.background_color}', scatter_color='{self.scatter_color}', 
                   scatter_points='{self.scatter_points}', scatter_size={self.scatter_size},
                   ticklabel_size={self.ticklabel_size}, fontfamily='{self.fontfamily}', curviness={self.curviness}, 
                   rotate_xticks={self.rotate_xticks}, rotate_y_ticks={self.rotate_yticks},
                   show_right={self.show_right}, label_size={self.label_size}, labelpad={self.labelpad}, 
                   self.horizontalalignment_x={self.horz_xalign}, self.horizontalalignment_y={self.horz_yalign}, 
                   self.alignment_xvalue={self.align_xval}, self.alignment_yvalue={self.align_yval}, 
                   label_color={self.label_color}, plot_labels={self.plot_labels})"""

    ## __str__ is the same as __repr__
    __str__ = __repr__