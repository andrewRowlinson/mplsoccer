""" Colormap functions."""

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgba

__all__ = ['create_transparent_cmap', 'grass_cmap']


def grass_cmap():
    """ Create a grass colormap.

    Returns
    -------
    cmap : matplotlib.colors.ListedColormap
    """
    color_from = (0.25, 0.44, 0.12, 1)
    color_to = (0.38612245, 0.77142857, 0.3744898, 1.)
    cmap = LinearSegmentedColormap.from_list('grass', [color_from, color_to], N=30)
    cmap = cmap(np.linspace(0, 1, 30))
    cmap = np.concatenate((cmap[:10][::-1], cmap))
    return ListedColormap(cmap, name='grass')


def create_transparent_cmap(color=None, cmap=None, n_segments=100, alpha_start=0.01, alpha_end=1):
    """ Create a colormap where the alpha transparency increases linearly
    from alpha_start to alpha_end.

    Parameters
    ----------
    color : A matplotlib color, default None.
        A matplotlib color. Use either cmap or color, not both.
    cmap : str, default None
        A matplotlib cmap (colormap) name. Use either cmap or color, not both.
    n_segments : int, default 100
        The number of colors in the cmap.
    alpha_start, alpha_end: float, default 0.01, 1
        The starting/ ending alpha values for the cmap transparency.
        Values between 0 (transparent) and 1 (opaque).

    Returns
    -------
    cmap : matplotlib.colors.ListedColormap
    """
    # check one of cmap and color are not None
    if color is None and cmap is None:
        raise ValueError("Missing 1 required argument: color or cmap")
    if color is not None and cmap is not None:
        raise ValueError("Use either cmap or color arguments not both.")

    # cmap as an rgba array (n_segments long)
    if color is not None:
        cmap = to_rgba(color)
        cmap = np.tile(np.array(cmap), (n_segments, 1))
    else:
        if isinstance(cmap, str):
            cmap = colormaps.get_cmap(cmap)
        if not isinstance(cmap, (ListedColormap, LinearSegmentedColormap)):
            raise ValueError("cmap: not a recognised cmap type.")
        cmap = cmap(np.linspace(0, 1, n_segments))

    # amend the alpha channel
    cmap[:, 3] = np.linspace(alpha_start, alpha_end, n_segments)

    return ListedColormap(cmap, name='transparent cmap')
