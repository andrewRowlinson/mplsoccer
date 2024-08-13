""" A module with functions for binning data into 2d bins and plotting heatmaps.´´."""

from dataclasses import dataclass, asdict
from functools import partial

import numpy as np
from scipy.stats import binned_statistic_2d, binned_statistic_dd, circmean
from matplotlib.projections.polar import PolarAxes
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize
from typing import Optional

from mplsoccer.utils import validate_ax


@dataclass
class BinnedStatisticResult:
    """ Dataclass for the bin_statistic results."""
    statistic: np.ndarray
    x_grid: np.ndarray
    y_grid: np.ndarray
    cx: np.ndarray
    cy: np.ndarray
    binnumber: Optional[np.ndarray] = None
    inside: Optional[np.ndarray] = None
    angle_grid: Optional[np.ndarray] = None
    angle_widths: Optional[np.ndarray] = None


def _nan_safe(statistic):
    """ Make the statistic nan safe"""
    if statistic == 'mean':
        statistic = np.nanmean
    elif statistic == 'std':
        statistic = np.nanstd
    elif statistic == 'median':
        statistic = np.nanmedian
    elif statistic == 'sum':
        statistic = np.nansum
    elif statistic == 'min':
        statistic = np.nanmin
    elif statistic == 'max':
        statistic = np.nanmax
    elif statistic == 'circmean':
        statistic = partial(circmean, nan_policy='omit')
    else:
        statistic = statistic
    return statistic


def bin_statistic(x, y, values=None, dim=None, statistic='count',
                  bins=(5, 4), normalize=False, standardized=False):
    """ Calculates binned statistics using scipy.stats.binned_statistic_2d.

    This method automatically sets the range, changes the scipy defaults,
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
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean' or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html
    bins : int or [int, int] or array_like or [array, array], optional
        The bin specification.
          * the number of bins for the two dimensions (nx = ny = bins),
          * the number of bins in each dimension (nx, ny = bins),
          * the bin edges for the two dimensions (x_edge = y_edge = bins),
          * the bin edges in each dimension (x_edge, y_edge = bins).
            If the bin edges are specified, the number of bins will be,
            (nx = len(x_edge)-1, ny = len(y_edge)-1).
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.
    standardized : bool, default False
        Whether the x, y values have been standardized to the
        'uefa' pitch coordinates (105m x 68m)

    Returns
    -------
    bin_statistic : dict.
        The keys are 'statistic' (the calculated statistic),
        'x_grid' and 'y_grid (the bin's edges), cx and cy (the bin centers)
        and 'binnumber' (the bin indices each point belongs to).
        'binnumber' is a (2, N) array that represents the bin in which the observation falls
        if the observations falls outside the pitch the value is -1 for the dimension. The
        binnumber are zero indexed and start from the top and left handside of the pitch.

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
    statistic = _nan_safe(statistic)
    if (values is None) & (statistic == 'count'):
        values = x
    if (values is None) & (statistic != 'count'):
        raise ValueError("values on which to calculate the statistic are missing")
    if standardized:
        pitch_range = [[0, 105], [0, 68]]
    elif dim.invert_y:
        pitch_range = [[dim.left, dim.right], [dim.top, dim.bottom]]
        y = dim.bottom - y
    else:
        pitch_range = [[dim.left, dim.right], [dim.bottom, dim.top]]
    statistic, x_edge, y_edge, binnumber = binned_statistic_2d(x, y, values, statistic=statistic,
                                                               bins=bins, range=pitch_range,
                                                               expand_binnumbers=True)

    statistic = np.flip(statistic.T, axis=0)
    if statistic.ndim == 3:
        num_y, num_x, _ = statistic.shape
    else:
        num_y, num_x = statistic.shape
    if normalize:
        statistic = statistic / statistic.sum()
    binnumber[1, :] = num_y - binnumber[1, :] + 1
    x_grid, y_grid = np.meshgrid(x_edge, y_edge)
    cx, cy = np.meshgrid(x_edge[:-1] + 0.5 * np.diff(x_edge), y_edge[:-1] + 0.5 * np.diff(y_edge))

    if not dim.invert_y or standardized is not False:
        y_grid = np.flip(y_grid, axis=0)
        cy = np.flip(cy, axis=0)

    # if outside the pitch set the bin number to minus one
    # else zero index the results by removing one
    mask_x_out = np.logical_or(binnumber[0, :] == 0,
                               binnumber[0, :] == num_x + 1)
    binnumber[0, mask_x_out] = -1
    binnumber[0, ~mask_x_out] = binnumber[0, ~mask_x_out] - 1

    mask_y_out = np.logical_or(binnumber[1, :] == 0,
                               binnumber[1, :] == num_y + 1)
    binnumber[1, mask_y_out] = -1
    binnumber[1, ~mask_y_out] = binnumber[1, ~mask_y_out] - 1
    inside = np.logical_and(~mask_x_out, ~mask_y_out)
    return asdict(BinnedStatisticResult(statistic, x_grid, y_grid,
                                        cx, cy, binnumber=binnumber,
                                        inside=inside))


def bin_statistic_sonar(x, y, angle, values=None, dim=None, statistic='count',
                        bins=(5, 4, 10), normalize=False, standardized=False, center=True):
    """ Calculates binned statistics using scipy.stats.binned_statistic_dd.
    This method automatically sets the range, changes the scipy defaults,
    and outputs the grids and centers for plotting.
    The default statistic has been changed to count instead of mean.
    The default bins have been set to (5, 4, 10).
    Parameters
    ----------
    x, y, angle, values : array-like or scalar.
        Commonly, these parameters are 1D arrays.
        If the statistic is 'count' then values are ignored. The angle is in radians
        between 0 and 2*pi.
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean' or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html
    bins : int or [int, int, int] or array_like or [array, array, array], optional
        The bin specification.
          * A sequence of arrays describing the bin edges along each dimension.
          * The number of bins for each dimension (nx, ny, nangle = bins).
          * The number of bins for all dimensions (nx = ny = nangle … = bins).
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.
    standardized : bool, default False
        Whether the x, y values have been standardized to the
        'uefa' pitch coordinates (105m x 68m)
    center : bool, default True
        Whether to center the sonars so the first segment is centered around zero (True)
        or starts at zero (False)
    Returns
    -------
    bin_statistic : BinnedStatisticResultSonar dataclass
        The attributes are statistic (the calculated statistic),
        x_grid, y_grid, angle_grid (the bin's edges), angle_widths (the angle bin width),
        cx and cy (the bin centers), binnumber (the bin indices each point belongs to)
        and inside (whether the point is inside the pitch).
        binnumber is a (2, N) array that represents the bin in which the observation
        falls if the observations falls outside the pitch the value is -1 for the dimension. The
        binnumber are zero indexed and start from the top and left handside of the pitch.
    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2, pitch_color='black')
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> angle = np.random.uniform(low=0, high=2*np.pi, size=100)
    >>> stats = pitch.bin_statistic_sonar(x, y, angle)
    """
    x = np.ravel(x)
    y = np.ravel(y)
    angle = np.ravel(angle)
    if x.size != y.size:
        raise ValueError("x and y must be the same size")
    if x.size != angle.size:
        raise ValueError("x and angle must be the same size")
    statistic = _nan_safe(statistic)
    if (values is None) & (statistic != 'count'):
        raise ValueError("values on which to calculate the statistic are missing")

    if isinstance(bins, int):
        bins = (bins, bins, bins)
    if not len(bins) == 3:
        raise ValueError("bins should be either an int, [int, int, int] or [array, array, array]")
    if isinstance(bins[2], int):
        first_width = 2 * np.pi / bins[2]
    else:
        if not np.isclose(np.min(bins[2]), 0) or not np.isclose(np.max(bins[2]), 2 * np.pi):
            raise ValueError("bin angles should be radians between 0 and 2 pi")
        first_width = np.sort(bins[2])[1]

    if center:
        angle = np.mod(angle + first_width / 2, 2 * np.pi)

    if standardized:
        pitch_range = [[0, 105], [0, 68], [0, 2 * np.pi]]
    else:
        if dim.invert_y:
            pitch_range = [[dim.left, dim.right], [dim.top, dim.bottom], [0, 2 * np.pi]]
            y = dim.bottom - y  # for inverted axis flip the coordinates
        else:
            pitch_range = [[dim.left, dim.right], [dim.bottom, dim.top], [0, 2 * np.pi]]

    (statistic, bin_edges,
     binnumber) = binned_statistic_dd([x, y, angle], values, statistic=statistic,
                                      bins=bins, range=pitch_range,
                                      expand_binnumbers=True)
    statistic = np.transpose(statistic, axes=(1, 0, 2))
    num_y, num_x, num_angle = statistic.shape
    if dim.invert_y and standardized is False:
        binnumber[1] = num_y - binnumber[1] + 1  # equivalent to flipping
        statistic = np.flip(statistic, axis=0)

    if normalize:
        statistic = statistic / statistic.sum()

    x_edge, y_edge, angle_grid = bin_edges
    if center:
        angle_grid = angle_grid - first_width / 2
    angle_widths = np.diff(angle_grid)

    x_grid, y_grid = np.meshgrid(x_edge, y_edge)
    cx, cy = np.meshgrid(x_edge[:-1] + 0.5 * np.diff(x_edge),
                         y_edge[:-1] + 0.5 * np.diff(y_edge))

    # if outside the pitch/ range set the bin number to minus one
    # else zero index the results by removing one
    mask_x_out = np.logical_or(binnumber[0] == 0,
                               binnumber[0] == num_x + 1)
    mask_y_out = np.logical_or(binnumber[1] == 0,
                               binnumber[1] == num_y + 1)
    mask_angle_out = np.logical_or(binnumber[2] == 0,
                                   binnumber[2] == num_angle + 1)
    binnumber[0, mask_x_out] = -1
    binnumber[0, ~mask_x_out] = binnumber[0, ~mask_x_out] - 1
    binnumber[1, mask_y_out] = -1
    binnumber[1, ~mask_y_out] = binnumber[1, ~mask_y_out] - 1
    binnumber[2, mask_angle_out] = -1
    binnumber[2, ~mask_angle_out] = binnumber[2, ~mask_angle_out] - 1

    # remove last edge as not needed for sonars
    # we only need the start locations for each segment
    angle_grid = angle_grid[:-1]

    inside = np.logical_and(~mask_x_out, ~mask_y_out)
    stats = asdict(BinnedStatisticResult(statistic, x_grid, y_grid,
                                         cx, cy, binnumber=binnumber,
                                         inside=inside, angle_grid=angle_grid,
                                         angle_widths=angle_widths))
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
        return ax.pcolormesh(stats['y_grid'], stats['x_grid'], stats['statistic'], **kwargs)
    return ax.pcolormesh(stats['x_grid'], stats['y_grid'], stats['statistic'], **kwargs)


def sonar(stats_length, xindex=0, yindex=0,
          stats_color=None, cmap=None, vmin=None, vmax=None,
          rmin=0, rmax=None,
          sonar_alpha=1, sonar_facecolor='None',
          axis=False, label=False,
          ax=None,
          **kwargs):
    """ Plot a polar bar chart on an existing Polar axes.

    Parameters
    ----------
    stats_length : dict
        This should be calculated via bin_statistic_sonar().
        It controls the length of the bars.
    xindex, yindex : int, default 0
        Which grid cell of the binned statistics to plot. The default
        plots grid cell x = 0, y = 0.
    stats_color : dict, default None
        This should be calculated via bin_statistic_sonar().
        It controls the color of the bars via a cmap. The vmin/vmax
        arguments will set the boundaries for the cmap.
        If stats_color is None then the color of the bars is controlled
        by 'color', 'fc', or 'facecolor' arguments.
    cmap : str or matplotlib.colros.Colormap, default None
        Controls the color of the bars via stats_color.
    vmin, vmax : float, default None
        The cmap is mapped linearly to the range vmin to vmax, so that values
        equal to or less than vmin are given the first color in the cmap
        and values equal to or greater than vmax are given the last color
        in the cmap. The default of None sets the values to the minimum value of
        stats_color['statistic'] and the maximum value of stats_color['statistic'].
    rmin, rmax : float, default 0 and None
        The radial axis limits. The default rmax of None sets the values to the maximum
        of stats_length['statistic'].
    sonar_alpha : float, default 1
        The alpha/ transparency of the sonar axes patch.
    sonar_facecolor : any Matplotlib color, default 'None'
        The facecolor of the sonar axes. The default 'None' makes the axes transparent.
    axis : bool, default False
        Whether to set the axis spines to visible.
    label : bool, default False
        Whether to include the axis labels.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
        This should be an instance of matplotlib.projections.polar.PolarAxes
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.bar.

    Examples
    --------
    >>> from mplsoccer import Pitch, Sbopen
    >>> parser = Sbopen()
    >>> df = parser.event(69251)[0]
    >>> df = df[(df.type_name == 'Pass') &
    ...         (df.outcome_name.isnull()) &
    ...         (df.player_id == 5503)].copy()
    >>> pitch = Pitch()
    >>> angle, distance = pitch.calculate_angle_and_distance(df.x, df.y,
    ...                                                      df.end_x, df.end_y)
    >>> bs = pitch.bin_statistic_sonar(df.x, df.y, angle, 
    ...                                bins=(1, 1, 4), center=True)
    >>> fig, ax = pitch.draw(figsize=(8, 5.5))
    >>> ax_inset = pitch.inset_axes(x=60, y=40, width=40, polar=True, ax=ax)
    >>> bars = pitch.sonar(bs, fc='cornflowerblue', ec='black', ax=ax_inset)
    """
    if stats_length['statistic'].ndim != 3:
        raise ValueError(f"stats_color['statistic'] {stats_color['statistic'].shape} "
                         f"should have three dimensions. "
                         'Try creating the statistics again using bin_statistic_sonar.')
    if not isinstance(ax, PolarAxes):
        raise TypeError('The ax argument must be of type matplotlib.projections.polar.PolarAxes.')
    if stats_color is not None and cmap is None:
        raise ValueError("You must supply a cmap for varying the color using stats_color.")
    if stats_color is None and cmap is not None:
        raise ValueError("You must supply a stats_color for varying the color using a cmap.")
    if stats_color is not None and stats_color['statistic'].shape != stats_length['statistic'].shape:
        raise ValueError(f"stats_color['statistic'] {stats_color['statistic'].shape} "
                         f"and stats_length['statistic'] {stats_length['statistic'].shape} are different shapes. "
                         'Try creating the statistics again using bin_statistic_sonar '
                         'with the same bins argument.')
    ax.patch.set_alpha(sonar_alpha)
    ax.grid(axis)
    ax.spines['polar'].set_visible(axis)
    if rmax is None:
        rmax = np.nanmax(stats_length['statistic'])
    ax.set_rlim(rmin, rmax)
    ax.set_facecolor(sonar_facecolor)
    if label is False:
        ax.set_yticklabels([])
        ax.set_xticklabels([])

    kwargs.pop('align', None)
    # set colors for the cmap
    if cmap is not None:
        kwargs.pop('color', None)
        kwargs.pop('fc', None)
        kwargs.pop('facecolor', None)
        if isinstance(cmap, str):
            cmap = colormaps.get_cmap(cmap)
        if not isinstance(cmap, (ListedColormap, LinearSegmentedColormap)):
            raise ValueError("cmap: not a recognised cmap type.")
        if vmin is None:
            vmin = np.nanmin(stats_color['statistic'])
        if vmax is None:
            vmax = np.nanmax(stats_color['statistic'])
        norm = Normalize(vmin=vmin, vmax=vmax)
        norm_stats_color = norm(stats_color['statistic'][yindex, xindex, :])
        color = cmap(norm_stats_color)
        return ax.bar(stats_length['angle_grid'],
                      np.nan_to_num(stats_length['statistic'])[yindex, xindex, :],
                      width=stats_length['angle_widths'],
                      color=color,
                      align='edge',
                      **kwargs)
    return ax.bar(stats_length['angle_grid'],
                  np.nan_to_num(stats_length['statistic'])[yindex, xindex, :],
                  width=stats_length['angle_widths'],
                  align='edge',
                  **kwargs)


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
