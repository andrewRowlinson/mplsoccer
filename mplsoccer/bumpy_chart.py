"""
A Python module for plotting radar-chart.

Authors: Anmol_Durgapal(@slothfulwave612)
"""

# import required packages/modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import warnings

from mplsoccer.utils import set_labels

# ignore UserWarning
warnings.simplefilter("ignore", UserWarning)

__all__ = ['Bumpy']


class Bumpy:
    """
    contains methods to make bumpy-charts.
    """

    def __init__(
        self, background_color="#1B1B1B", scatter=True, scatter_color="#4F535C", line_color=None,
        scatter_points='o', scatter_primary=None, scatter_size=100, ticklabel_size=13, 
        curviness=0.85, rotate_xticks=0, rotate_yticks=0, show_right=False, label_size=20, labelpad=20, 
        horizontalalignment_x='left', horizontalalignment_y='right', alignment_xvalue=0.035, 
        alignment_yvalue=0.16, label_color='#F2F2F2', plot_labels=True
    ):
        """
        Function to initialize the object of the class.

        Args:
            background_color (str, optional): background color for the plot. Defaults to "#1B1B1B".
            scatter (bool/str, optional): to plot scatter points or not. Defaults to True.
                                          "value" --> scatter point for highlighted attribute.
            scatter_color (str, optional): color value for our scatter points. Defaults to "#4F535C".
            line_color (str, optional): color value for the connecting lines. Defaults to None.
                                        if None --> takes the same color as scatter_color.
            scatter_points (str, optional): type of marker user wants to plot. Defaults to 'o'.
            scatter_primary (str, optional): type of marker user wants to plot for highlighted attribute. Defaults to None.
            scatter_size (float, optional): size of the scatter_points. Defaults to 100.
            ticklabel_size (float, optional): fontsize of the ticklabel. Defaults to 13.
            curviness (float, optional): value of the curved line. Defaults to 0.85.
            rotate_xticks (int, optional): rotation of xticklabels in degrees. Defaults to 0.
            rotate_yticks (int, optional): rotation of yticklabels. Defaults to 0.
            show_right (bool, optional): yticklabels to be shown at the right y-axis or not. Defaults to False.
            label_size (int, optional): fontsize of the x and y labels. Defaults to 20.
            labelpad (int, optional): padding between labels and ticklables. Defaults to 20.
            alignment_xvalue (float, optional): value for alignment of x-label. Defaults to 0.035.
            alignment_yvalue (float, optional): value for alignment of y-label. Defaults to 0.16.
            label_color (str, optional): color value for labels. Defaults to '#FFFFFF'.
            plot_labels (bool, optional): to plot the labels. Defaults to True.
        """
        self.background_color = background_color
        self.scatter = scatter
        self.scatter_color = scatter_color
        self.scatter_points = scatter_points
        self.scatter_size = scatter_size
        self.ticklabel_size = ticklabel_size
        self.curviness = curviness
        self.rotate_xticks = rotate_xticks
        self.rotate_yticks = rotate_yticks
        self.show_right = show_right
        self.label_size = label_size
        self.labelpad = labelpad
        self.align_xval = alignment_xvalue
        self.align_yval = alignment_yvalue
        self.label_color = label_color
        self.plot_labels = plot_labels

        if line_color is None:
            self.line_color = scatter_color
        else:
            self.line_color = line_color

        if scatter_primary is None:
            self.scatter_primary = self.scatter_points
        else:
            self.scatter_primary = scatter_primary

    def plot(
        self, x_list, y_list, values, highlight_dict, figsize=(12,8), lw=2,
        secondary_alpha=1, x_label=None, y_label=None, xlim=None, ylim=None, 
        figax=None, upside_down=False, fontproperties=None
        ):
        """
        Function to plot bumpy-chart.

        Args:
            x_list (list): xticklabel values(serial-wise order from left to right).
            y_list (list): yticklabel values(serial-wise order from top to bottom).
            values (dict): containing key as team-name and value as list of rank for that team.
            highlight_dict (dict): containing key as the team-name to be highlighted with their corresponding color.
            figsize (tuple, optional): size of the plot. Defaults to (12,8).
            lw (int, optional): line-width for the lines in the plot. Defaults to 2.
            secondary_alpha (float, optional): alpha value for non-shaded lines/markers. Default to 1.
            x_label (str, optional): x-label-name. Defaults to None.
            y_label (str, optional): y-label-name. Defaults to None.
            xlim (tuple, optional): limit for x axis value. Defaults to None.
            ylim (tuple, optional): limit for y axis value. Defaults to None.
            figax (tuple, optional): figure and axis object. Defaults to None.
            upside_down (bool, optional): to plot chart upside down. Defaults to False.
            fontproperties (fontmanage, optional): fontproperties for labels and ticks. Defaults to None.

        Returns:
            matplotlib.figure.Figure: figure object.
            axes.Axes: axes object.
        """
        if figax:
            fig, ax = figax
        else:
            # create subplot
            fig, ax = plt.subplots(figsize=figsize, facecolor=self.background_color)
            ax.set_facecolor(self.background_color)

        # length of values dict
        len_y = len(y_list)

        # iterate thorugh the dictionary and plot the chart
        for key, value in values.items():
            
            # find value in highlight_dict
            if highlight_dict.get(key):
                line_color = highlight_dict[key]     # fetch the required color
                color = line_color
                zorder = 3
                alpha = 1
                marker = self.scatter_primary
            else:
                color = self.scatter_color
                line_color = self.line_color
                zorder = 2
                alpha = secondary_alpha
                marker = self.scatter_points

            # to plot upside down bumpy chart
            if upside_down:
                if len_y % 2 == 0:
                    add_value = 0
                else:
                    add_value = 1

                # y-coordinate to plot scatter points
                y = np.array(value) + add_value

                # coordinates for bezier curve
                verts = [(i + d, vij + add_value) for i, vij in enumerate(value) for d in (-self.curviness, 0, self.curviness)][1: -1]
            
            else:
                if len_y % 2 == 0:
                    add_value = 1
                else:
                    add_value = 0
                
                # y-coordinate to plot scatter points
                y = len_y - np.array(value) + add_value

                # coordinates for bezier curve
                verts = [(i + d, len_y - vij + add_value) for i, vij in enumerate(value) for d in (-self.curviness, 0, self.curviness)][1: -1]

            # plot scatter-points
            if self.scatter == True:
                ax.scatter(
                    np.arange(len(value)), y, 
                    marker=marker, 
                    color=color,
                    s=self.scatter_size,
                    alpha=alpha,
                    zorder=zorder
                )
            elif self.scatter == "value" and highlight_dict.get(key):
                ax.scatter(
                    np.arange(len(value)), y, 
                    marker=marker, 
                    color=color,
                    s=self.scatter_size,
                    zorder=zorder
                )

            # create bezier curves 
            codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
            path = Path(verts, codes)
            patch = patches.PathPatch(path, facecolor='none', lw=lw, edgecolor=line_color, zorder=zorder, alpha=alpha)
            ax.add_patch(patch)

        # plot labels 
        if self.plot_labels == True:
            if upside_down == True:
                y_list = y_list[::-1]
            fig, ax = self.add_labels(
                x_list, y_list, highlight_dict, figax=(fig, ax), 
                x_label=x_label, y_label=y_label, 
                fontproperties=fontproperties
            )

        # xlim and ylim
        if xlim != None:
            ax.set(xlim=xlim)
        elif ylim != None:
            ax.set(ylim=ylim)

        return fig, ax

    def add_labels(
        self, x_list, y_list, highlight_dict, 
        figax, x_label, y_label, fontproperties=None
    ):
        """
        Function to add labels and titles to the plot.

        Args:
            x_list (list): xticklabel values(serial-wise order from left to right).
            y_list (list): yticklabel values(serial-wise order from top to bottom).
            highlight_dict (dict): containing key as the team-name to be highlighted with their corresponding color.
            figax (tuple): containing figure and axis object.
            x_label (str): x-label-name.
            y_label (str): y-label-name.
            fontproperties (fontmanage, optional): fontproperties for labels and ticks. Defaults to None.

        Returns:
            matplotlib.figure.Figure: figure object.
            axes.Axes: axis object.
        """        
        
        # fetch figure and axis object
        fig, ax = figax[0], figax[1]

        # remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # get labels for x and y axis
        x_labels = set_labels(ax=ax, label_value=x_list, label_axis='x')
        y_labels = set_labels(ax=ax, label_value=y_list, label_axis='y')

        # set ticklabels
        ax.set_xticklabels(x_labels, fontsize=self.ticklabel_size, rotation=self.rotate_xticks, fontproperties=fontproperties)
        ax.set_yticklabels(y_labels, fontsize=self.ticklabel_size, rotation=self.rotate_yticks, fontproperties=fontproperties)

        # set x and y axis labels
        ax.set_xlabel(
            x_label, fontsize=self.label_size, labelpad=self.labelpad, x=self.align_xval,
            fontproperties=fontproperties
        )
        ax.set_ylabel(
            y_label, fontsize=self.label_size, labelpad=self.labelpad, y=self.align_yval,
            fontproperties=fontproperties
        )
        ax.xaxis.label.set_color(self.label_color)
        ax.yaxis.label.set_color(self.label_color)

        # remove tick marks
        ax.tick_params(axis='both', which='both', length=0, colors=self.label_color)

        if self.show_right == True:
            ax.tick_params(direction='out', axis='y', which='both', labelleft=True, labelright=True,
                    right=True, left=True)

        return fig, ax
    
    def __repr__(self):        
        return f"""{self.__class__.__name__}(background_color='{self.background_color}', scatter_color='{self.scatter_color}', 
                   scatter_points='{self.scatter_points}', scatter_size={self.scatter_size},
                   ticklabel_size={self.ticklabel_size}, curviness={self.curviness}, 
                   rotate_xticks={self.rotate_xticks}, rotate_y_ticks={self.rotate_yticks},
                   show_right={self.show_right}, label_size={self.label_size}, labelpad={self.labelpad},
                   self.alignment_xvalue={self.align_xval}, self.alignment_yvalue={self.align_yval}, 
                   label_color={self.label_color}, plot_labels={self.plot_labels}),
                   line_color={self.line_color}, scatter_primary={self.scatter_primary}"""

    # __str__ is the same as __repr__
    __str__ = __repr__
