"""`mplsoccer.scatterutils` is a python module containing Matplotlib
generic markers and a function to rotate markers."""

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import matplotlib.markers as mmarkers
import matplotlib.path as mpath
import numpy as np

__all__ = ['scatter_rotation', 'arrowhead_marker']

arrowhead_marker = mpath.Path(np.array([[0., 1.], [-1., -1.], [0., -0.4], [1., -1.], [0., 1.]]),
                              np.array([1, 2, 2, 2, 79], dtype=np.uint8))


def _mscatter(x, y, markers=None, ax=None, **kwargs):
    """ Helper function to allow rotation of scatter points."""
    # based on:
    # https://stackoverflow.com/questions/52303660/iterating-markers-in-plots/52303895#52303895
    scatter_plot = ax.scatter(x, y, **kwargs)
    if markers is not None:
        paths = []
        for marker in markers:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(marker_obj.get_transform())
            paths.append(path)
        scatter_plot.set_paths(paths)
    return scatter_plot


def scatter_rotation(x, y, rotation_degrees, marker=None, ax=None, vertical=False, **kwargs):
    """ Scatter plot with points rotated by rotation_degrees clockwise.

    Parameters
    ----------
    x, y : array-like or scalar.
        Commonly, these parameters are 1D arrays.
    rotation_degrees: array-like or scalar, default None.
        Rotates the marker in degrees, clockwise. 0 degrees is facing the direction of play.
        In a horizontal pitch, 0 degrees is this way →
    marker: MarkerStyle, optional
        The marker style. marker can be either an instance of the class or the
        text shorthand for a particular marker. Defaults to None, in which case it takes
        the value of rcParams["scatter.marker"] (default: 'o') = 'o'.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    vertical : bool, default False
        Rotates the markers correctly for the orientation. If using a vertical setup
        where the x and y-axis are flipped set vertical=True.
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.

    Returns
    -------
    paths : matplotlib.collections.PathCollection
    """
    rotation_degrees = np.ma.ravel(rotation_degrees)
    if x.size != rotation_degrees.size:
        raise ValueError("x and rotation_degrees must be the same size")
    # rotated counterclockwise - this makes it clockwise with zero facing the direction of play
    rotation_degrees = - rotation_degrees
    # if horizontal rotate by 90 degrees so 0 degrees is this way →
    if vertical is False:
        rotation_degrees = rotation_degrees - 90
    markers = []
    for degrees in rotation_degrees:
        marker_style = mmarkers.MarkerStyle(marker=marker)
        marker_style._transform = marker_style.get_transform().rotate_deg(degrees)
        markers.append(marker_style)

    return _mscatter(x, y, markers=markers, ax=ax, **kwargs)
