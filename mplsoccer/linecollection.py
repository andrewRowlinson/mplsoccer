""" A module with functions for using LineCollection to create lines.´´."""

import warnings

import numpy as np
from matplotlib import colormaps
from matplotlib import rcParams
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba_array
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerLineCollection

from mplsoccer.cm import create_transparent_cmap
from mplsoccer.utils import validate_ax

__all__ = ['lines']


def lines(xstart, ystart, xend, yend, color=None, n_segments=100, comet=False, transparent=False,
          alpha_start=0.01, alpha_end=1, cmap=None, ax=None, vertical=False,
          reverse_cmap=False, **kwargs):
    """ Plots lines using matplotlib.collections.LineCollection.
    This is a fast way to plot multiple lines without loops.
    Also enables lines that increase in width or opacity by splitting
    the line into n_segments of increasing
    width or opacity as the line progresses.

    Parameters
    ----------
    xstart, ystart, xend, yend: array-like or scalar.
        Commonly, these parameters are 1D arrays.
        These should be the start and end coordinates of the lines.
    color : A matplotlib color or sequence of colors, defaults to None.
        Defaults to None. In that case the marker color is determined
        by the value rcParams['lines.color']
    n_segments : int, default 100
        If comet=True or transparent=True this is used to split the line
        into n_segments of increasing width/opacity.
    comet : bool default False
        Whether to plot the lines increasing in width.
    transparent : bool, default False
        Whether to plot the lines increasing in opacity.
    linewidth or lw : array-like or scalar, default 5.
        Multiple linewidths not supported for the comet or transparent lines.
    alpha_start: float, default 0.01
        The starting alpha value for transparent lines, between 0 (transparent) and 1 (opaque).
        If transparent = True the line will be drawn to
        linearly increase in opacity between alpha_start and alpha_end.
    alpha_end : float, default 1
        The ending alpha value for transparent lines, between 0 (transparent) and 1 (opaque).
        If transparent = True the line will be drawn to
        linearly increase in opacity between alpha_start and alpha_end.
    cmap : str, default None
        A matplotlib cmap (colormap) name
    vertical : bool, default False
        If the orientation is vertical (True), then the code switches the x and y coordinates.
    reverse_cmap : bool, default False
        Whether to reverse the cmap colors.
        If the pitch is horizontal and the y-axis is inverted then set this to True.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    **kwargs : All other keyword arguments are passed on to matplotlib.collections.LineCollection.

    Returns
    -------
    LineCollection : matplotlib.collections.LineCollection

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> pitch = Pitch()
    >>> fig, ax = pitch.draw()
    >>> pitch.lines(20, 20, 45, 80, comet=True, transparent=True, ax=ax)

    >>> from mplsoccer.linecollection import lines
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> lines([0.1, 0.4], [0.1, 0.5], [0.9, 0.4], [0.8, 0.8], ax=ax)
    """
    validate_ax(ax)
    if not isinstance(comet, bool):
        raise TypeError("Invalid argument: comet should be bool (True or False).")
    if not isinstance(transparent, bool):
        raise TypeError("Invalid argument: transparent should be bool (True or False).")

    if alpha_start < 0 or alpha_start > 1:
        raise TypeError("alpha_start values should be within 0-1 range")
    if alpha_end < 0 or alpha_end > 1:
        raise TypeError("alpha_end values should be within 0-1 range")
    if alpha_start > alpha_end:
        msg = "Alpha start > alpha end. The line will increase in transparency nearer to the end"

        warnings.warn(msg)
    if 'colors' in kwargs:
        warnings.warn("lines method takes 'color' as an argument, 'colors' in ignored")
    if color is not None and cmap is not None:
        raise ValueError("Only use one of color or cmap arguments not both.")
    if 'lw' in kwargs and 'linewidth' in kwargs:
        raise TypeError("lines got multiple values for 'linewidth' argument (linewidth and lw).")

    if 'lw' in kwargs:
        lw = kwargs.pop('lw', 5)
    elif 'linewidth' in kwargs:
        lw = kwargs.pop('linewidth', 5)
    else:
        lw = 5
    xstart = np.ravel(xstart)
    ystart = np.ravel(ystart)
    xend = np.ravel(xend)
    yend = np.ravel(yend)
    lw = np.ravel(lw)
    if (comet or transparent) and lw.size > 1:
        msg = "Multiple linewidths with a comet or transparent line is not implemented."

        raise NotImplementedError(msg)
    if color is None and cmap is None:
        color = rcParams['lines.color']
    if (comet or transparent) and cmap is None and to_rgba_array(color).shape[0] > 1:
        msg = "Multiple colors with a comet or transparent line is not implemented."
        raise NotImplementedError(msg)
    if xstart.size != ystart.size:
        raise ValueError("xstart and ystart must be the same size")
    if xstart.size != xend.size:
        raise ValueError("xstart and xend must be the same size")
    if ystart.size != yend.size:
        raise ValueError("ystart and yend must be the same size")
    if lw.size > 1 and lw.size != xstart.size:
        raise ValueError("lw and xstart must be the same size")
    if lw.size == 1:
        lw = lw[0]
    if vertical:
        ystart, xstart = xstart, ystart
        yend, xend = xend, yend
    if comet:
        lw = np.linspace(1, lw, n_segments)
        handler_first_lw = False
    else:
        handler_first_lw = True
    multi_segment = transparent is not False or comet is not False or cmap is not None
    if transparent:
        cmap = create_transparent_cmap(color, cmap, n_segments, alpha_start, alpha_end)
    if isinstance(cmap, str):
        cmap = colormaps.get_cmap(cmap)
    if cmap is not None:
        handler_cmap = True
        line_collection = _lines_cmap(xstart, ystart, xend, yend, lw=lw, cmap=cmap, ax=ax,
                                      n_segments=n_segments, multi_segment=multi_segment,
                                      reverse_cmap=reverse_cmap, **kwargs)

    else:
        handler_cmap = False
        line_collection = _lines_no_cmap(xstart, ystart, xend, yend, lw=lw, color=color,
                                         ax=ax, n_segments=n_segments,
                                         multi_segment=multi_segment, **kwargs)

    line_collection_handler = HandlerLines(numpoints=n_segments, invert_y=reverse_cmap,
                                           first_lw=handler_first_lw, use_cmap=handler_cmap)

    Legend.update_default_handler_map({LineCollection: line_collection_handler})
    return line_collection


def _create_segments(xstart, ystart, xend, yend, n_segments=100, multi_segment=False):
    if multi_segment:
        x = np.linspace(xstart, xend, n_segments + 1)
        y = np.linspace(ystart, yend, n_segments + 1)
        points = np.array([x, y]).T
        points = np.concatenate([points, np.expand_dims(points[:, -1, :], 1)], axis=1)
        points = np.expand_dims(points, 1)
        segments = np.concatenate([points[:, :, :-2, :],
                                   points[:, :, 1:-1, :],
                                   points[:, :, 2:, :]], axis=1)
        segments = np.transpose(segments, (0, 2, 1, 3)).reshape((-1, 3, 2))
    else:
        segments = np.transpose(np.array([[xstart, ystart], [xend, yend]]), (2, 0, 1))
    return segments


def _lines_no_cmap(xstart, ystart, xend, yend, lw=None, color=None, ax=None,
                   n_segments=100, multi_segment=False, **kwargs):
    segments = _create_segments(xstart, ystart, xend, yend,
                                n_segments=n_segments, multi_segment=multi_segment)
    color = to_rgba_array(color)
    if (color.shape[0] > 1) and (color.shape[0] != xstart.size):
        raise ValueError("xstart and color must be the same size")
    line_collection = LineCollection(segments, color=color, linewidth=lw, snap=False, **kwargs)
    line_collection = ax.add_collection(line_collection)
    return line_collection


def _lines_cmap(xstart, ystart, xend, yend, lw=None, cmap=None, ax=None,
                n_segments=100, multi_segment=False, reverse_cmap=False, **kwargs):
    segments = _create_segments(xstart, ystart, xend, yend,
                                n_segments=n_segments, multi_segment=multi_segment)
    if reverse_cmap:
        cmap = cmap.reversed()
    line_collection = LineCollection(segments, cmap=cmap, linewidth=lw, snap=False, **kwargs)
    line_collection = ax.add_collection(line_collection)
    extent = ax.get_ylim()
    pitch_array = np.linspace(extent[0], extent[1], n_segments)
    line_collection.set_array(pitch_array)
    return line_collection


# Amended from
# https://stackoverflow.com/questions/49223702/adding-a-legend-to-a-matplotlib-plot-with-a-multicolored-line?rq=1
class HandlerLines(HandlerLineCollection):
    """Automatically generated by Pitch.lines() to allow use of linecollection in legend.
    """

    def __init__(self, invert_y=False, first_lw=False, use_cmap=False,
                 marker_pad=0.3, numpoints=None, **kw):
        HandlerLineCollection.__init__(self, marker_pad=marker_pad, numpoints=numpoints, **kw)
        self.invert_y = invert_y
        self.first_lw = first_lw
        self.use_cmap = use_cmap

    def create_artists(self, legend, artist, xdescent, ydescent,
                       width, height, fontsize, trans):
        x = np.linspace(0, width, self.get_numpoints(legend) + 1)
        y = np.zeros(self.get_numpoints(legend) + 1) + height / 2. - ydescent
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lw = artist.get_linewidth()
        if self.first_lw:
            lw = lw[0]
        if self.use_cmap:
            cmap = artist.cmap
            if self.invert_y:
                cmap = cmap.reversed()
            line_collection = LineCollection(segments, lw=lw, cmap=cmap,
                                             snap=False, transform=trans)
            line_collection.set_array(x)
        else:
            line_collection = LineCollection(segments, lw=lw, colors=artist.get_colors()[0],
                                             snap=False, transform=trans)
        return [line_collection]
