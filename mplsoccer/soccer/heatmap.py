""" A module with functions for binning data into 2d bins and plotting heatmaps."""

from ..heatmap import bin_statistic_zones, heatmap_zones


def positional_zones(dim, positional='full'):
    """ The Juego de Posición (positional play) zone layout.

    Returns the rectangles and names for use with bin_statistic_zones/
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
    zones : list of tuple
        A list of (x0, x1, y0, y1) rectangles in pitch coordinates that tile the pitch.
    names : list of str
        A name for each zone in the same order as the zones.
        Rows and columns are numbered from the top left of a horizontal pitch.
        The names are the same for VerticalPitch so the zones keep their
        names when you switch orientation.

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2)
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> zones, names = pitch.positional_zones()
    >>> stats = pitch.bin_statistic_zones(x, y, zones, names=names)
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
        zones = []
        names = []
        for col in range(6):
            zones.append((px[col], px[col + 1], band_top[0], band_top[1]))
            names.append(f'top-{col + 1}')
        for col in range(6):
            zones.append((px[col], px[col + 1], band_bottom[0], band_bottom[1]))
            names.append(f'bottom-{col + 1}')
        middle_columns = [(px[1], px[3]), (px[3], px[5])]
        for row, (y0, y1) in enumerate(middle_bands):
            for col, (x0, x1) in enumerate(middle_columns):
                zones.append((x0, x1, y0, y1))
                names.append(f'middle-{row + 1}-{col + 1}')
        zones.append((px[0], px[1], py[1], py[4]))
        names.append('penalty-left')
        zones.append((px[5], px[6], py[1], py[4]))
        names.append('penalty-right')
    elif positional == 'horizontal':
        bands = [(py[i], py[i + 1]) for i in range(5)]
        if not dim.invert_y:
            bands = bands[::-1]
        zones = [(px[0], px[6], y0, y1) for y0, y1 in bands]
        names = [f'horizontal-{row + 1}' for row in range(5)]
    elif positional == 'vertical':
        zones = [(px[col], px[col + 1], py[0], py[5]) for col in range(6)]
        names = [f'vertical-{col + 1}' for col in range(6)]
    else:
        raise ValueError("positional must be one of 'full', 'vertical' or 'horizontal'")
    return zones, names


def bin_statistic_positional(x, y, values=None, dim=None, positional='full',
                             statistic='count', normalize=False):
    """ Calculates binned statistics for the Juego de Posición (positional play) zones.

    A shortcut for bin_statistic_zones with the positional_zones layout.

    Parameters
    ----------
    x, y, values : array-like or scalar.
        Commonly, these parameters are 1D arrays.
        If the statistic is 'count' then values are ignored.
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    positional : str
        One of 'full', 'horizontal' or 'vertical' for the respective layouts.
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean'
        or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic.html
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.

    Returns
    -------
    zone_statistic : dict.
        The same dictionary as bin_statistic_zones: the keys are
        'statistic' (a flat array of the calculated statistic per zone),
        'count' (the number of points in each zone), 'patches' (one
        matplotlib.patches.Rectangle per zone), 'cx' and 'cy' (the zone centres),
        'binnumber' (the zone identifier per point, -1 if outside the pitch),
        'inside' (whether each point is inside the pitch),
        'area' (the zone areas) and 'names' (the zone names).

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
    zones, names = positional_zones(dim, positional=positional)
    return bin_statistic_zones(x, y, zones, dim=dim, values=values,
                               statistic=statistic, normalize=normalize, names=names)


def heatmap_positional(stats, ax=None, vertical=False, **kwargs):
    """ Plots the Juego de Posición zones as a single
    matplotlib.collections.PatchCollection.

    The same as heatmap_zones.

    Parameters
    ----------
    stats : dict.
        This should be calculated via bin_statistic_positional().
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    vertical : bool, default False
        If the orientation is vertical (True), then the code switches the x and y coordinates.
    **kwargs : All other keyword arguments are passed on to
        matplotlib.collections.PatchCollection, except vmin/ vmax
        which set the color limits of the collection.

    Returns
    -------
    collection : matplotlib.collections.PatchCollection

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
    return heatmap_zones(stats, ax=ax, vertical=vertical, **kwargs)
