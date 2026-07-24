""" A module with functions for binning data into 2d bins and plotting heatmaps.´´."""

from dataclasses import asdict

import numpy as np

from ..utils import validate_ax
from ..heatmap import BinnedStatisticResult, bin_statistic, bin_statistic_zones, heatmap


def positional_zones(dim, positional='full'):
    """ The Juego de posición (position game) zone layout as data.

    Returns the rectangles and names for feeding to bin_statistic_zones/
    heatmap_zones. This is an alternative to bin_statistic_positional/
    heatmap_positional with a single flat result and one plotting artist,
    so a colorbar and vmin/ vmax work without any syncing.

    Parameters
    ----------
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    positional : str, default 'full'
        One of 'full', 'horizontal' or 'vertical' for the respective layouts.

    Returns
    -------
    regions : list of tuple
        A list of (x0, x1, y0, y1) rectangles in pitch coordinates that tile the pitch.
    names : list of str
        A name for each zone in the same order as the regions.
        Rows and columns are numbered from the top left of the pitch as displayed.

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2)
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> regions, names = pitch.positional_zones()
    >>> stats = pitch.bin_statistic_zones(x, y, regions, names=names)
    >>> pc = pitch.heatmap_zones(stats, cmap='hot', edgecolors='black', ax=ax)
    """
    px = dim.positional_x
    py = dim.positional_y
    # the y-edges are ascending; for inverted-y pitches the smallest values are
    # displayed at the top of the pitch. Zones are ordered from the top of the
    # pitch as displayed so they match the legacy bin_statistic_positional sections
    if dim.invert_y:
        band_top = (py[0], py[1])
        band_bottom = (py[4], py[5])
        middle_bands = [(py[1], py[2]), (py[2], py[3]), (py[3], py[4])]
    else:
        band_top = (py[4], py[5])
        band_bottom = (py[0], py[1])
        middle_bands = [(py[3], py[4]), (py[2], py[3]), (py[1], py[2])]

    if positional == 'full':
        regions = []
        names = []
        for col in range(6):
            regions.append((px[col], px[col + 1], band_top[0], band_top[1]))
            names.append(f'top-{col + 1}')
        for col in range(6):
            regions.append((px[col], px[col + 1], band_bottom[0], band_bottom[1]))
            names.append(f'bottom-{col + 1}')
        middle_columns = [(px[1], px[3]), (px[3], px[5])]
        for row, (y0, y1) in enumerate(middle_bands):
            for col, (x0, x1) in enumerate(middle_columns):
                regions.append((x0, x1, y0, y1))
                names.append(f'middle-{row + 1}-{col + 1}')
        regions.append((px[0], px[1], py[1], py[4]))
        names.append('penalty-left')
        regions.append((px[5], px[6], py[1], py[4]))
        names.append('penalty-right')
    elif positional == 'horizontal':
        bands = [(py[i], py[i + 1]) for i in range(5)]
        if not dim.invert_y:
            bands = bands[::-1]
        regions = [(px[0], px[6], y0, y1) for y0, y1 in bands]
        names = [f'horizontal-{row + 1}' for row in range(5)]
    elif positional == 'vertical':
        regions = [(px[col], px[col + 1], py[0], py[5]) for col in range(6)]
        names = [f'vertical-{col + 1}' for col in range(6)]
    else:
        raise ValueError("positional must be one of 'full', 'vertical' or 'horizontal'")
    return regions, names


def _positional_grids(dim, x_edge, y_edge):
    """ Reproduce bin_statistic's grid and bin-centre construction for explicit edges."""
    x_grid, y_grid = np.meshgrid(x_edge, y_edge)
    cx, cy = np.meshgrid(x_edge[:-1] + 0.5 * np.diff(x_edge),
                         y_edge[:-1] + 0.5 * np.diff(y_edge))
    if not dim.invert_y:
        y_grid = np.flip(y_grid, axis=0)
        cy = np.flip(cy, axis=0)
    return x_grid, y_grid, cx, cy


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

    if positional == 'full':
        # the zones machinery bins the 20 zones in one pass (top row, bottom row,
        # middle grid, and the merged penalty-area columns). The flat results are
        # then reshaped back into the legacy list of five section dictionaries,
        # with the grids and centres rebuilt exactly as bin_statistic builds them
        regions, _ = positional_zones(dim, positional='full')
        zone_stats = bin_statistic_zones(x, y, regions, dim=dim, values=values,
                                         statistic=statistic)
        flat = zone_stats['statistic']

        # top and bottom rows
        x_grid1, y_grid1, cx1, cy1 = _positional_grids(dim, dim.positional_x,
                                                       dim.positional_y[[0, 1, 4, 5]])
        result1 = asdict(BinnedStatisticResult(flat[0:6].reshape(1, 6),
                                               x_grid1[:2, :],
                                               y_grid1[:2, :],
                                               cx1[0, :],
                                               cy1[0, :]))
        result2 = asdict(BinnedStatisticResult(flat[6:12].reshape(1, 6),
                                               x_grid1[2:, :],
                                               y_grid1[2:, :],
                                               cx1[2, :],
                                               cy1[2, :]))

        # middle of the pitch
        x_grid3, y_grid3, cx3, cy3 = _positional_grids(dim, dim.positional_x[[0, 1, 3, 5, 6]],
                                                       dim.positional_y)
        result3 = asdict(BinnedStatisticResult(flat[12:18].reshape(3, 2),
                                               x_grid3[1:-1, 1:-1],
                                               y_grid3[1:-1, 1:-1],
                                               cx3[1:-1, 1:-1],
                                               cy3[1:-1, 1:-1]))

        # penalty areas
        x_grid4, y_grid4, cx4, cy4 = _positional_grids(dim, dim.positional_x[[0, 1, 2, 5, 6]],
                                                       dim.positional_y[[0, 1, 4, 5]])
        result4 = asdict(BinnedStatisticResult(flat[18:19].reshape(1, 1),
                                               x_grid4[1:-1, 0:2],
                                               y_grid4[1:-1, 0:2],
                                               cx4[1:-1, :1],
                                               cy4[1:-1, :1]))
        result5 = asdict(BinnedStatisticResult(flat[19:20].reshape(1, 1),
                                               x_grid4[1:-1, -2:],
                                               y_grid4[1:-1, -2:],
                                               cx4[1:-1, -1:],
                                               cy4[1:-1, -1:]))

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
