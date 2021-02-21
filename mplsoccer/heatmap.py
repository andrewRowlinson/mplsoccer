""" A module with functions for binning data into 2d bins and plotting heatmaps.´´."""

from collections import namedtuple

import numpy as np
from scipy.stats import binned_statistic_2d

from mplsoccer.utils import validate_ax

_BinnedStatisticResult = namedtuple('BinnedStatisticResult',
                                    ('statistic', 'x_grid', 'y_grid', 'cx', 'cy'))


def bin_statistic(x, y, values=None, dim=None, statistic='count', bins=(5, 4), standardized=False):
    """ Calculates binned statistics using scipy.stats.binned_statistic_2d.

    This method automatically sets the range, changes some of the scipy defaults,
    and outputs the grids and centers for plotting.

    The default statistic has been changed to count instead of mean.
    The default bins have been set to (5,4).

    Parameters
    ----------
    x, y, values : array-like or scalar.
        Commonly, these parameters are 1D arrays.
        If the statistic is 'count' then values are ignored.
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html
    bins : int or [int, int] or array_like or [array, array], optional
        The bin specification.
          * the number of bins for the two dimensions (nx = ny = bins),
          * the number of bins in each dimension (nx, ny = bins),
          * the bin edges for the two dimensions (x_edge = y_edge = bins),
          * the bin edges in each dimension (x_edge, y_edge = bins).
            If the bin edges are specified, the number of bins will be,
            (nx = len(x_edge)-1, ny = len(y_edge)-1).
    standardized : bool, default False
        Whether the x, y values have been standardized to the
        'uefa' pitch coordinates (105m x 68m)

    Returns
    -------
    bin_statistic : dict.
        The keys are 'statistic' (the calculated statistic),
        'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2, pitch_color='black')
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> stats = pitch.bin_statistic(x, y)
    >>> pitch.heatmap(stats, edgecolors='black', cmap='hot', ax=ax)
    """
    x = np.ravel(x)
    y = np.ravel(y)
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    if values is not None:
        values = np.ravel(values)
    if (values is None) & (statistic == 'count'):
        values = x
    if (values is None) & (statistic != 'count'):
        raise ValueError("values on which to calculate the statistic are missing")
    if values.size != x.size:
        raise ValueError("x and values must be the same size")

    if standardized:
        pitch_range = [[0, 105], [0, 68]]
    else:
        if dim.invert_y:
            pitch_range = [[dim.left, dim.right], [dim.top, dim.bottom]]
            y = dim.bottom - y  # for inverted axis flip the coordinates
        else:
            pitch_range = [[dim.left, dim.right], [dim.bottom, dim.top]]

    statistic, x_edge, y_edge, _ = binned_statistic_2d(x, y, values, statistic=statistic,
                                                       bins=bins, range=pitch_range)

    statistic = statistic.T
    # this ensures that all the heatmaps are created consistently at the heatmap edges
    # i.e. grid cells are created from the bottom to the top of the pitch, where the top edge
    # always belongs to the cell above. First the raw coordinates have been flipped above
    # then the statistic is flipped back here
    if dim.invert_y and standardized is False:
        statistic = np.flip(statistic, axis=0)

    x_grid, y_grid = np.meshgrid(x_edge, y_edge)

    cx, cy = np.meshgrid(x_edge[:-1] + 0.5 * np.diff(x_edge),
                         y_edge[:-1] + 0.5 * np.diff(y_edge))

    stats = _BinnedStatisticResult(statistic, x_grid, y_grid, cx, cy)._asdict()

    return stats


def heatmap(stats, ax=None, vertical=False, **kwargs):
    """ Utility wrapper around matplotlib.axes.Axes.pcolormesh
    which automatically flips the x_grid and y_grid coordinates if the pitch is vertical.

    See: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html

    Parameters
    ----------
    stats : dict.
        This should be calculated via bin_statistic().
        The keys are 'statistic' (the calculated statistic),
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
    >>> stats = pitch.bin_statistic(x, y)
    >>> pitch.heatmap(stats, edgecolors='black', cmap='hot', ax=ax)
    """
    validate_ax(ax)
    if vertical:
        mesh = ax.pcolormesh(stats['y_grid'], stats['x_grid'], stats['statistic'], **kwargs)
    else:
        mesh = ax.pcolormesh(stats['x_grid'], stats['y_grid'], stats['statistic'], **kwargs)

    return mesh


def bin_statistic_positional(x, y, values=None, dim=None, positional='full', statistic='count'):
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
        xedge = dim.positional_x
        yedge = dim.positional_y[[0, 1, 4, 5]]
        bin_statistic1 = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                                       bins=(xedge, yedge))
        stat1 = bin_statistic1['statistic']
        x_grid1 = bin_statistic1['x_grid']
        y_grid1 = bin_statistic1['y_grid']
        cx1 = bin_statistic1['cx']
        cy1 = bin_statistic1['cy']
        # slicing second row
        stat2 = stat1[2, :].reshape(1, -1).copy()
        x_grid2 = x_grid1[2:, :].copy()
        y_grid2 = y_grid1[2:, :].copy()
        cx2 = cx1[2, :].copy()
        cy2 = cy1[2, :].copy()
        # slice first row
        stat1 = stat1[0, :].reshape(1, -1).copy()
        x_grid1 = x_grid1[:2, :].copy()
        y_grid1 = y_grid1[:2, :].copy()
        cx1 = cx1[0, :].copy()
        cy1 = cy1[0, :].copy()

        # middle of pitch
        xedge = dim.positional_x[[0, 1, 3, 5, 6]]
        yedge = dim.positional_y
        bin_statistic3 = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                                       bins=(xedge, yedge))
        stat3 = bin_statistic3['statistic']
        x_grid3 = bin_statistic3['x_grid']
        y_grid3 = bin_statistic3['y_grid']
        cx3 = bin_statistic3['cx']
        cy3 = bin_statistic3['cy']
        stat3 = stat3[1:-1, 1:-1]
        x_grid3 = x_grid3[1:-1:, 1:-1].copy()
        y_grid3 = y_grid3[1:-1, 1:-1].copy()
        cx3 = cx3[1:-1, 1:-1].copy()
        cy3 = cy3[1:-1, 1:-1].copy()

        # penalty areas
        xedge = dim.positional_x[[0, 1, 2, 5, 6]]
        yedge = dim.positional_y[[0, 1, 4, 5]]
        bin_statistic4 = bin_statistic(x, y, values, dim=dim, statistic=statistic,
                                       bins=(xedge, yedge))
        stat4 = bin_statistic4['statistic']
        x_grid4 = bin_statistic4['x_grid']
        y_grid4 = bin_statistic4['y_grid']
        cx4 = bin_statistic4['cx']
        cy4 = bin_statistic4['cy']
        # slicing each penalty box
        stat5 = stat4[1:-1, -1:]
        stat4 = stat4[1:-1, :1]
        y_grid5 = y_grid4[1:-1, -2:]
        y_grid4 = y_grid4[1:-1, 0:2]
        x_grid5 = x_grid4[1:-1, -2:]
        x_grid4 = x_grid4[1:-1, 0:2]
        cx5 = cx4[1:-1, -1:]
        cx4 = cx4[1:-1, :1]
        cy5 = cy4[1:-1, -1:]
        cy4 = cy4[1:-1, :1]

        result1 = _BinnedStatisticResult(stat1, x_grid1, y_grid1, cx1, cy1)._asdict()
        result2 = _BinnedStatisticResult(stat2, x_grid2, y_grid2, cx2, cy2)._asdict()
        result3 = _BinnedStatisticResult(stat3, x_grid3, y_grid3, cx3, cy3)._asdict()
        result4 = _BinnedStatisticResult(stat4, x_grid4, y_grid4, cx4, cy4)._asdict()
        result5 = _BinnedStatisticResult(stat5, x_grid5, y_grid5, cx5, cy5)._asdict()

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
    vmax = kwargs.pop('vmax', np.array([stat['statistic'].max() for stat in stats]).max())
    vmin = kwargs.pop('vmin', np.array([stat['statistic'].min() for stat in stats]).min())

    mesh_list = []
    for bin_stat in stats:
        mesh = heatmap(bin_stat, vmin=vmin, vmax=vmax, ax=ax, vertical=vertical, **kwargs)
        mesh_list.append(mesh)

    return mesh_list
