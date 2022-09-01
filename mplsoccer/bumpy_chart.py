"""A Python module for plotting bump chart.

Author: Anmol_Durgapal(@slothfulwave612)
"""

import warnings

import matplotlib.pyplot as plt
# import required packages/modules
import numpy as np
from matplotlib import patches
from matplotlib.path import Path

from mplsoccer.utils import set_labels

# ignore UserWarning
warnings.simplefilter("ignore", UserWarning)

__all__ = ['Bumpy']


class Bumpy:
    """ A class for plotting bump-charts in Matplotlib

    Parameters
    ----------
    background_color : str, default "#1B1B1B"
        The background-color of the plot.
    scatter : bool, default True
        To plot scatter points or not.
        "value" --> scatter point for highlighted attribute.
    scatter_color : str, default "#4F535C"
        Color value for our scatter points.
    line_color : str, default None
        Color value for the connecting lines.
        if None --> takes the same color as scatter_color.
    scatter_points : str, default 'o'
        Type of marker user wants to plot.
    scatter_primary : str, default None
        Type of marker user wants to plot for highlighted attribute.
    scatter_size : float, default 100
        Size of the scatter_points.
    ticklabel_size : float, default 13
        Fontsize of the ticklabel.
    curviness : float, default 0.85
        Value of the curved line.
    rotate_xticks : float, default 0
        Rotation of xticklabels in degrees.
    rotate_yticks : float, default 0
        Rotation of yticklabels.
    show_right : bool, default False
        yticklabels to be shown at the right y-axis or not.
    label_size : float, default 20
        Fontsize of the x and y labels.
    labelpad : float, default 20
        Padding between labels and ticklables.
    alignment_xvalue : float, default 0.035
        Value for alignment of x-label.
    alignment_yvalue : float, default 0.16
        Value for alignment of y-label
    label_color : str, default "#FFFFFF"
        Color value for labels.
    plot_labels : bool, default True
        To plot the labels.
    """

    def __init__(self, background_color="#1B1B1B", scatter=True, scatter_color="#4F535C",
                 line_color=None, scatter_points='o', scatter_primary=None, scatter_size=100,
                 ticklabel_size=13,  curviness=0.85, rotate_xticks=0, rotate_yticks=0,
                 show_right=False, label_size=20, labelpad=20, alignment_xvalue=0.035,
                 alignment_yvalue=0.16, label_color='#F2F2F2', plot_labels=True):
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

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'background_color={self.background_color}, '
                f'scatter={self.scatter}, '
                f'scatter_color={self.scatter_color}, '
                f'scatter_points={self.scatter_points}, '
                f'scatter_size={self.scatter_size}, '
                f'ticklabel_size={self.ticklabel_size}, '
                f'curviness={self.curviness}) '
                f'rotate_xticks={self.rotate_xticks}) '
                f'rotate_yticks={self.rotate_yticks}) '
                f'show_right={self.show_right}) '
                f'label_size={self.label_size}) '
                f'labelpad={self.labelpad}) '
                f'align_xval={self.align_xval}) '
                f'align_yval={self.align_yval}) '
                f'label_color={self.label_color}) '
                f'plot_labels={self.plot_labels}) ')

    def plot(self, x_list, y_list, values, highlight_dict, figsize=(12, 8), lw=2,
             secondary_alpha=1, x_label=None, y_label=None, xlim=None, ylim=None,
             ax=None, upside_down=False, **kwargs):
        """ Function to plot bumpy-chart.

        Parameters
        ----------
        x_list : sequence of float/str
            xticklabel values(serial-wise order from left to right).
        y_list : sequence of float/str
            yticklabel values(serial-wise order from top to bottom).
        values : dict
            Containing key as team-name and value as list of rank for that team.
        highlight_dict : dict
            Containing key as the team-name to be highlighted with their corresponding color.
        figsize : tuple, default (12,8)
            Size of the plot. Defaults to (12,8).
        lw : int, default 2
            Line-width for the lines in the plot.
        secondary_alpha : float, default 1
            Alpha value for non-shaded lines/markers.
        x_label, y_label : str, default None
            x-label and y-label name
        xlim, ylim: tuple, default None
            Limit for x-axis and y-axis respectively.
        ax : axes.Axes object, default None
            axes object on which chart will be plotted.
        upside_down : bool, default False
            To plot chart upside down.
        **kwargs : All other keyword arguments are passed for setting ticklabels and labels.

        Returns
        -------
        If ax=None returns a matplotlib Figure and Axes.
        Else the settings are applied on an existing axis and returns None.
        """
        if ax is None:
            # create subplot
            fig, ax = plt.subplots(figsize=figsize, facecolor=self.background_color)
            ax.set_facecolor(self.background_color)

            return_figax = True
        else:
            return_figax = False

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
                verts = [(i + d, vij + add_value) for i, vij in enumerate(value)
                         for d in (-self.curviness, 0, self.curviness)][1: -1]

            else:
                if len_y % 2 == 0:
                    add_value = 1
                else:
                    add_value = 0

                # y-coordinate to plot scatter points
                y = len_y - np.array(value) + add_value

                # coordinates for bezier curve
                verts = [(i + d, len_y - vij + add_value) for i, vij in enumerate(value)
                         for d in (-self.curviness, 0, self.curviness)][1: -1]

            # plot scatter-points
            if self.scatter != "value":
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
            patch = patches.PathPatch(path, facecolor='none', lw=lw, edgecolor=line_color,
                                      zorder=zorder, alpha=alpha)
            ax.add_patch(patch)

        # plot labels
        if self.plot_labels:
            if upside_down:
                y_list = y_list[::-1]
            self.__add_labels(
                x_list, y_list, ax=ax,
                x_label=x_label, y_label=y_label,
                **kwargs
            )

        # xlim and ylim
        if xlim is not None:
            ax.set(xlim=xlim)
        elif ylim is not None:
            ax.set(ylim=ylim)

        if return_figax:
            return fig, ax
        return None

    def __add_labels(self, x_list, y_list, ax, x_label, y_label, **kwargs):
        """ Function to add labels and titles to the plot.

        Parameters
        ----------
        x_list : sequence of float/str
            xticklabel values(serial-wise order from left to right).
        y_list : sequence of float/str
            yticklabel values(serial-wise order from top to bottom).
        ax : axes.Axes object
            axes object on which chart will be plotted.
        x_label, y_label : str
            x-label and y-label name
        **kwargs : All other keyword arguments are passed on to set ticklabels and labels.
        """
        # remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # get labels for x and y axis
        x_labels = set_labels(ax=ax, label_value=x_list, label_axis='x')
        y_labels = set_labels(ax=ax, label_value=y_list, label_axis='y')

        # set ticklabels
        ax.set_xticklabels(x_labels, fontsize=self.ticklabel_size,
                           rotation=self.rotate_xticks, **kwargs)
        ax.set_yticklabels(y_labels, fontsize=self.ticklabel_size,
                           rotation=self.rotate_yticks, **kwargs)

        # set x and y axis labels
        ax.set_xlabel(
            x_label, fontsize=self.label_size, labelpad=self.labelpad, x=self.align_xval,
            **kwargs
        )
        ax.set_ylabel(
            y_label, fontsize=self.label_size, labelpad=self.labelpad, y=self.align_yval,
            **kwargs
        )
        ax.xaxis.label.set_color(self.label_color)
        ax.yaxis.label.set_color(self.label_color)

        # remove tick marks
        ax.tick_params(axis='both', which='both', length=0, colors=self.label_color)

        if self.show_right:
            ax.tick_params(
                direction='out', axis='y', which='both', labelleft=True, labelright=True,
                right=True, left=True
            )

    # __str__ is the same as __repr__
    __str__ = __repr__
