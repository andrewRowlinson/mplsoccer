""" A module with functions for binning data into 2d bins and plotting heatmaps.´´."""

from dataclasses import asdict

import numpy as np

from ..utils import validate_ax
from ..heatmap import BinnedStatisticResult, bin_statistic,  heatmap


def bin_statistic_positional(x, y, values=None, dim=None, positional='full',
                             statistic='count', normalize=False):
    """ Calculates binned statistics for the Juego de posición (position game) concept.
    It uses scipy.stats.binned_statistic_2d.

    Parameters
    ----------
    x, y, values : array-like or scalar.
        Commonly, these parameters are 1D arrays.
        If the statistic is 'count' then values are ignored.
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    positional : str
        One of 'full', 'horizontal' or 'vertical' for the respective heatmaps.
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html.
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.

    Returns
    -------
    bin_statistic : A list of dictionaries.
        The dictionary keys are 'statistic' (the calculated statistic),
        'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2, pitch_color='black')
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> stats = pitch.bin_statistic_positional(x, y)
    >>> pitch.heatmap_positional(stats, edgecolors='black', cmap='hot', ax=ax)
    """

    # I tried several ways of creating positional bins. It's hard to do this because
    # of points on the edges of bins. You have to be sure they are
    # only counted once consistently. I tried doing this by adding or subtracting a
    # small value near the edges, but it didn't work for all cases
    # I settled on this idea, which is to create binned statistics with an additional row,
    # column either side (unless the side of the pitch) so that the scipy
    # binned_statistic_2d functions handles the edges
    if positional == 'full':
        # top and bottom row - we create a grid with three rows and then
        # ignore the middle row when slicing
        xedge1 = dim.positional_x
        yedge1 = dim.positional_y[[0, 1, 4, 5]]
        bin_statistic1 = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                                       bins=(xedge1, yedge1))
        result1 = asdict(BinnedStatisticResult(bin_statistic1['statistic'][:1, :],
                                               bin_statistic1['x_grid'][:2, :],
                                               bin_statistic1['y_grid'][:2, :],
                                               bin_statistic1['cx'][0, :],
                                               bin_statistic1['cy'][0, :]))
        result2 = asdict(BinnedStatisticResult(bin_statistic1['statistic'][2:, :],
                                         bin_statistic1['x_grid'][2:, :],
                                         bin_statistic1['y_grid'][2:, :],
                                         bin_statistic1['cx'][2, :],
                                         bin_statistic1['cy'][2, :]))

        # middle of the pitch
        xedge3 = dim.positional_x[[0, 1, 3, 5, 6]]
        yedge3 = dim.positional_y
        bin_statistic3 = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                                       bins=(xedge3, yedge3))
        result3 = asdict(BinnedStatisticResult(bin_statistic3['statistic'][1:-1, 1:-1],
                                               bin_statistic3['x_grid'][1:-1:, 1:-1],
                                               bin_statistic3['y_grid'][1:-1, 1:-1],
                                               bin_statistic3['cx'][1:-1, 1:-1],
                                               bin_statistic3['cy'][1:-1, 1:-1]))

        # penalty areas
        xedge4 = dim.positional_x[[0, 1, 2, 5, 6]]
        yedge4 = dim.positional_y[[0, 1, 4, 5]]
        bin_statistic4 = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                                       bins=(xedge4, yedge4))
        result4 = asdict(BinnedStatisticResult(bin_statistic4['statistic'][1:-1, :1],
                                               bin_statistic4['x_grid'][1:-1, 0:2],
                                               bin_statistic4['y_grid'][1:-1, 0:2],
                                               bin_statistic4['cx'][1:-1, :1],
                                               bin_statistic4['cy'][1:-1, :1]))
        result5 = asdict(BinnedStatisticResult(bin_statistic4['statistic'][1:-1, -1:],
                                               bin_statistic4['x_grid'][1:-1, -2:],
                                               bin_statistic4['y_grid'][1:-1, -2:],
                                               bin_statistic4['cx'][1:-1, -1:],
                                               bin_statistic4['cy'][1:-1, -1:]))

        stats = [result1, result2, result3, result4, result5]

    elif positional == 'horizontal':
        xedge = dim.positional_x[[0, 6]]
        yedge = dim.positional_y
        stats = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                              bins=(xedge, yedge))
        stats = [stats]

    elif positional == 'vertical':
        xedge = dim.positional_x
        yedge = dim.positional_y[[0, 5]]
        stats = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                              bins=(xedge, yedge))
        stats = [stats]
    else:
        raise ValueError("positional must be one of 'full', 'vertical' or 'horizontal'")

    if normalize:
        total = np.array([stat['statistic'].sum() for stat in stats]).sum()
        for stat in stats:
            stat['statistic'] = stat['statistic'] / total

    return stats


def heatmap_positional(stats, ax=None, vertical=False, **kwargs):
    """ Plots several heatmaps for the different Juegos de posición areas.

    Parameters
    ----------
    stats : A list of dictionaries.
        This should be calculated via bin_statistic_positional().
        The dictionary keys are 'statistic' (the calculated statistic),
        'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    vertical : bool, default False
        If the orientation is vertical (True), then the code switches the x and y coordinates.

    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.pcolormesh.

    Returns
    -------
    mesh : matplotlib.collections.QuadMesh

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2, pitch_color='black')
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> stats = pitch.bin_statistic_positional(x, y)
    >>> pitch.heatmap_positional(stats, edgecolors='black', cmap='hot', ax=ax)
    """
    validate_ax(ax)
    # make vmin/vmax nan safe with np.nanmax/ np.nanmin
    vmax = kwargs.pop('vmax', np.nanmax([np.nanmax(stat['statistic']) for stat in stats]))
    vmin = kwargs.pop('vmin', np.nanmin([np.nanmin(stat['statistic']) for stat in stats]))

    mesh_list = []
    for bin_stat in stats:
        mesh = heatmap(bin_stat, vmin=vmin, vmax=vmax, ax=ax, vertical=vertical, **kwargs)
        mesh_list.append(mesh)

    return mesh_list
