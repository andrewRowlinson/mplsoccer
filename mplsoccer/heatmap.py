""" A module with functions for binning data into 2d bins and plotting heatmaps."""

from dataclasses import dataclass, asdict
from functools import partial
from typing import Optional

import numpy as np
from scipy.stats import binned_statistic, binned_statistic_2d, binned_statistic_dd, circmean
from matplotlib.projections.polar import PolarAxes
from matplotlib import colormaps
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize
from matplotlib.patches import Rectangle
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from .utils import validate_ax


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


@dataclass
class ZoneStatisticResult:
    """ Dataclass for the zone statistic results."""
    statistic: np.ndarray
    count: np.ndarray
    patches: Optional[list]
    cx: Optional[np.ndarray]
    cy: Optional[np.ndarray]
    binnumber: np.ndarray
    inside: np.ndarray
    area: Optional[np.ndarray] = None
    names: Optional[list] = None
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


def _center_angles(angle, angle_bins, center):
    """ The width of the first angle segment and, if centering the sonars,
    the angles shifted by half that width so the first segment is centered
    around zero. Explicit segment edges must be radians spanning 0 to 2*pi."""
    if isinstance(angle_bins, int):
        first_width = 2 * np.pi / angle_bins
    else:
        if not np.isclose(np.min(angle_bins), 0) or not np.isclose(np.max(angle_bins),
                                                                   2 * np.pi):
            raise ValueError('bin angles should be radians between 0 and 2 pi')
        first_width = np.sort(angle_bins)[1]
    if center:
        angle = np.mod(angle + first_width / 2, 2 * np.pi)
    return angle, first_width


def _flip_y_bin_edges(bins, bottom):
    """ Flip explicit y bin-edges into the flipped binning space used for
    inverted-y pitches (where the data is binned as bottom - y).

    Returns the bins to give to scipy and the original ascending y-edges
    (None if the y bins are a number of bins rather than explicit edges).
    Uniform edges (from an integer number of bins) need no flipping because
    they are symmetric about the pitch midline."""
    try:
        num = len(bins)
    except TypeError:
        return bins, None  # a single number of bins for both dimensions
    if num == 2:  # (nx, ny), (x_edges, y_edges) or a mix
        x_bins, y_bins = bins
        if np.iterable(y_bins):
            y_edges = np.asarray(y_bins, dtype=float)
            return (x_bins, (bottom - y_edges)[::-1]), y_edges
        return bins, None
    # otherwise bins is a single array of edges for both dimensions
    edges = np.asarray(bins, dtype=float)
    return (edges, (bottom - edges)[::-1]), edges


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
    y_edge_original = None
    if standardized:
        pitch_range = np.array([dim.standardized_extent[0:2],
                                dim.standardized_extent[2:]])
    elif dim.invert_y:
        pitch_range = [[dim.left, dim.right], [dim.top, dim.bottom]]
        y = dim.bottom - y
        # explicit y-edges must be flipped with the data; the original edges
        # are restored after binning for building the grids/ centers
        bins, y_edge_original = _flip_y_bin_edges(bins, dim.bottom)
    else:
        pitch_range = [[dim.left, dim.right], [dim.bottom, dim.top]]
    statistic, x_edge, y_edge, binnumber = binned_statistic_2d(x, y, values, statistic=statistic,
                                                               bins=bins, range=pitch_range,
                                                               expand_binnumbers=True)
    if y_edge_original is not None:
        y_edge = y_edge_original

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
        or starts at zero (False). Centering shifts the angles by half the
        width of the first segment.
    Returns
    -------
    bin_statistic : dict.
        The keys are 'statistic' (the calculated statistic),
        'x_grid', 'y_grid' and 'angle_grid' (the bin's edges),
        'angle_widths' (the angle bin widths), 'cx' and 'cy' (the bin centers),
        'binnumber' (the bin indices each point belongs to)
        and 'inside' (whether the point is inside the pitch).
        'binnumber' is a (3, N) array (x, y and angle) that represents the bin
        in which the observation falls, and is -1 for a dimension if the
        observation falls outside the pitch/ angle range. The binnumber are zero
        indexed and start from the top and left handside of the pitch.
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
    angle, first_width = _center_angles(angle, bins[2], center)

    y_edge_original = None
    if standardized:
        pitch_range = np.array([dim.standardized_extent[0:2],
                                dim.standardized_extent[2:],
                                [0, 2 * np.pi]])
    else:
        if dim.invert_y:
            pitch_range = [[dim.left, dim.right], [dim.top, dim.bottom], [0, 2 * np.pi]]
            y = dim.bottom - y  # for inverted axis flip the coordinates
            # explicit y-edges must be flipped with the data; the original edges
            # are restored after binning for building the grids/ centers
            (x_bins, y_bins), y_edge_original = _flip_y_bin_edges(bins[:2], dim.bottom)
            bins = (x_bins, y_bins, bins[2])
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
    if y_edge_original is not None:
        y_edge = y_edge_original
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


def _merge_close_edges(edges, atol):
    """ Sort and deduplicate edges, merging values that differ only by
    float noise into a single shared edge value (sometimes called vertex
    welding or snap rounding). Each edge is compared against the last kept
    edge, so a run of closely spaced edges never collapses into one value
    wider than the tolerance."""
    edges = np.sort(np.unique(np.asarray(edges, dtype=float)))
    keep = [edges[0]]
    for edge in edges[1:]:
        if not np.isclose(edge, keep[-1], rtol=0, atol=atol):
            keep.append(edge)
    return np.array(keep)


def _snap_to_edges(values, edges):
    """ Snap each value to the nearest merged edge. The order of values is preserved."""
    return edges[np.abs(values[:, None] - edges[None, :]).argmin(axis=1)]


def _validate_zones(zones, extent, atol):
    """ Validate that the zones exactly tile the extent.

    Region edges that differ only by float noise are merged into a single
    shared edge and the zone coordinates are snapped to the merged edges.
    The merged edges define the fine grid: every distinct x-edge crossed
    with every distinct y-edge, the finest grid that all the zones
    line up with.
    Returns the snapped zones, the fine-grid x/y edges, and the
    fine-cell to zone mapping (ny, nx).
    The zone order is the order the zones were supplied in; it is never reordered.
    """
    zones = np.asarray(zones, dtype=float)
    if zones.ndim != 2 or zones.shape[1] != 4:
        raise ValueError('zones must be a sequence of (x0, x1, y0, y1) rectangles')
    xmin, xmax, ymin, ymax = extent
    bad = np.where((zones[:, 1] <= zones[:, 0]) | (zones[:, 3] <= zones[:, 2]))[0]
    if bad.size:
        raise ValueError(f'zone {bad[0]} is invalid: zones must have x1 > x0 and y1 > y0')
    bad = np.where((zones[:, 0] < xmin - atol) | (zones[:, 1] > xmax + atol))[0]
    if bad.size:
        raise ValueError(f'zone {bad[0]} x-edges are outside the pitch extent {extent}')
    bad = np.where((zones[:, 2] < ymin - atol) | (zones[:, 3] > ymax + atol))[0]
    if bad.size:
        raise ValueError(f'zone {bad[0]} y-edges are outside the pitch extent {extent}')
    x_edges = _merge_close_edges(np.concatenate([zones[:, 0], zones[:, 1],
                                                 [xmin, xmax]]), atol)
    y_edges = _merge_close_edges(np.concatenate([zones[:, 2], zones[:, 3],
                                                 [ymin, ymax]]), atol)
    snapped = zones.copy()
    snapped[:, 0] = _snap_to_edges(zones[:, 0], x_edges)
    snapped[:, 1] = _snap_to_edges(zones[:, 1], x_edges)
    snapped[:, 2] = _snap_to_edges(zones[:, 2], y_edges)
    snapped[:, 3] = _snap_to_edges(zones[:, 3], y_edges)
    # map each fine-grid cell to a zone by testing the cell centre against each zone.
    # centres never sit on edges so strict inequalities are safe
    fine_x = 0.5 * (x_edges[:-1] + x_edges[1:])
    fine_y = 0.5 * (y_edges[:-1] + y_edges[1:])
    fine_x_grid, fine_y_grid = np.meshgrid(fine_x, fine_y)
    cell_zone = np.full(fine_x_grid.shape, -1, dtype=int)
    for i, (x0, x1, y0, y1) in enumerate(snapped):
        mask = ((fine_x_grid > x0) & (fine_x_grid < x1) &
                (fine_y_grid > y0) & (fine_y_grid < y1))
        clash = mask & (cell_zone != -1)
        if clash.any():
            raise ValueError(f'zones {cell_zone[clash].ravel()[0]} and {i} overlap')
        cell_zone[mask] = i
    if (cell_zone == -1).any():
        gap_y_index, gap_x_index = np.argwhere(cell_zone == -1)[0]
        raise ValueError('zones do not tile the pitch: gap around '
                         f'x={fine_x[gap_x_index]:.6g}, y={fine_y[gap_y_index]:.6g}. '
                         'If the edges around the gap are meant to coincide, '
                         'increase edge_tol.')
    return snapped, x_edges, y_edges, cell_zone


def _patch_centroid(patch):
    """ Best-effort centroid of a patch from its path vertices."""
    path = patch.get_path().transformed(patch.get_patch_transform())
    if path.codes is not None:
        vertices = path.vertices[path.codes != Path.CLOSEPOLY]
    else:
        vertices = path.vertices
    return vertices.mean(axis=0)


def zone_statistic_from_binnumber(binnumber, values=None, statistic='count',
                                  patches=None, cx=None, cy=None,
                                  names=None, area=None, normalize=False):
    """ Calculates zone statistics from per-point zone identifiers.

    This is the second half of bin_statistic_zones exposed publicly:
    you supply the zone each point belongs to (the binnumber), computed however
    you like (e.g. polar wedges via numpy.arctan2/ numpy.digitize), and it
    computes the statistic and count per zone and assembles the zone
    statistics dictionary for plotting with heatmap_zones.

    Parameters
    ----------
    binnumber : array-like of int
        The zone identifier for each point. Use -1 for points outside the zones.
        Zone identifiers are zero indexed and correspond to the order
        of the patches/ names.
    values : array-like or scalar, default None
        The values on which to calculate the statistic.
        If the statistic is 'count' then values are ignored.
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean'
        or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic.html
    patches : list of matplotlib.patches.Patch, default None
        One patch per zone in pitch coordinates for plotting with heatmap_zones.
        If None, the number of zones is inferred from binnumber.max() + 1.
    cx, cy : array-like, default None
        The centre of each zone in pitch coordinates, used to place labels
        (label_heatmap). Supply them for curved patches: the fallback is the
        centroid of the patch vertices, which can sit outside a Wedge.
    names : list of str, default None
        An optional name for each zone.
    area : array-like, default None
        An optional area for each zone (e.g. for normalising by area).
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.

    Returns
    -------
    zone_statistic : dict.
        The keys are 'statistic' (a flat array of the calculated statistic per zone),
        'count' (the number of points in each zone, always populated),
        'patches' (one matplotlib patch per zone), 'cx' and 'cy' (the zone centres),
        'binnumber' (the zone identifier per point, -1 if outside the zones),
        'inside' (whether each point is inside the zones),
        'area' (the zone areas) and 'names' (the zone names).

    Examples
    --------
    >>> import numpy as np
    >>> from mplsoccer import Pitch
    >>> pitch = Pitch()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> binnumber = (x > 60).astype(int)  # two zones: own half (0) and opposition half (1)
    >>> stats = pitch.zone_statistic_from_binnumber(binnumber)
    """
    binnumber = np.ravel(np.asarray(binnumber))
    if binnumber.size and not np.issubdtype(binnumber.dtype, np.integer):
        raise TypeError('binnumber must be an array of integers (-1 for points outside the zones)')
    if binnumber.size and binnumber.min() < -1:
        raise ValueError('binnumber must be >= -1 (-1 for points outside the zones)')
    if patches is not None:
        num_zones = len(patches)
        if binnumber.size and binnumber.max() >= num_zones:
            raise ValueError(f'binnumber contains zone {binnumber.max()} but there '
                             f'are only {num_zones} patches')
    elif binnumber.size and binnumber.max() >= 0:
        num_zones = int(binnumber.max()) + 1
    else:
        raise ValueError('cannot infer the number of zones: supply patches or a '
                         'binnumber with at least one point inside the zones')
    statistic = _nan_safe(statistic)
    if (values is None) & (statistic != 'count'):
        raise ValueError('values on which to calculate the statistic are missing')
    if values is None:
        values = np.zeros(binnumber.shape)  # ignored by the 'count' statistic
    values = np.ravel(values)
    if values.size != binnumber.size:
        raise ValueError('binnumber and values must be the same size')
    inside = binnumber >= 0
    stat, _, _ = binned_statistic(binnumber[inside], values[inside], statistic=statistic,
                                  bins=num_zones, range=(-0.5, num_zones - 0.5))
    count = np.bincount(binnumber[inside], minlength=num_zones)
    if normalize:
        stat = stat / np.nansum(stat)
    if patches is not None and (cx is None or cy is None):
        centroids = np.array([_patch_centroid(patch) for patch in patches])
        if cx is None:
            cx = centroids[:, 0]
        if cy is None:
            cy = centroids[:, 1]
    if cx is not None:
        cx = np.ravel(cx).astype(float)
    if cy is not None:
        cy = np.ravel(cy).astype(float)
    if area is not None:
        area = np.ravel(area).astype(float)
    return asdict(ZoneStatisticResult(stat, count, patches, cx, cy,
                                      binnumber=binnumber, inside=inside,
                                      area=area, names=names))


def bin_statistic_zones(x, y, zones, dim=None, values=None, statistic='count',
                        normalize=False, standardized=False, names=None, edge_tol=None):
    """ Calculates statistics for zones: any tiling of the pitch by
    axis-aligned rectangles.

    Unlike bin_statistic, the zones do not have to form a regular grid:
    rectangles can span multiple rows/ columns of other rectangles
    (e.g. the Juego de Posición layout) as long as together they exactly
    tile the pitch with no gaps or overlaps. The results are flat arrays with
    one value per zone. Zone k always corresponds to zones[k]/ names[k]
    as supplied; the zones are never reordered, so you can safely join the
    results back to a dataframe, e.g. df['zone'] = stats['binnumber'].

    Parameters
    ----------
    x, y : array-like or scalar.
        Commonly, these parameters are 1D arrays.
    zones : array-like of shape (num_zones, 4)
        A sequence of (x0, x1, y0, y1) rectangles in pitch coordinates
        (x0 < x1 and y0 < y1) that together exactly tile the pitch.
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    values : array-like or scalar, default None
        The values on which to calculate the statistic.
        If the statistic is 'count' then values are ignored.
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean'
        or a user-defined function. The statistic is computed on the points
        in each zone, so mean and median are exact for merged zones. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic.html
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.
    standardized : bool, default False
        Whether the x, y and zone values have been standardized to the
        'uefa' pitch coordinates (105m x 68m)
    names : list of str, default None
        An optional name for each zone (in the same order as zones).
    edge_tol : float, default None
        The absolute tolerance for merging zone edges that differ only by
        floating point noise into one shared edge. The default None uses
        a scale-aware tolerance of max(abs(pitch extent)) * 1e-9.

    Returns
    -------
    zone_statistic : dict.
        The keys are 'statistic' (a flat array of the calculated statistic per zone),
        'count' (the number of points in each zone, always populated),
        'patches' (one matplotlib.patches.Rectangle per zone), 'cx' and 'cy'
        (the zone centres), 'binnumber' (the zone identifier per point,
        -1 if outside the pitch), 'inside' (whether each point is inside the pitch),
        'area' (the zone areas) and 'names' (the zone names).

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> import numpy as np
    >>> pitch = Pitch(line_zorder=2)
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> zones = [(0, 60, 0, 80), (60, 120, 0, 40), (60, 120, 40, 80)]
    >>> stats = pitch.bin_statistic_zones(x, y, zones)
    >>> pc = pitch.heatmap_zones(stats, edgecolors='black', cmap='hot', ax=ax)
    """
    x = np.ravel(x).astype(float)
    y = np.ravel(y).astype(float)
    if x.size != y.size:
        raise ValueError('x and y must be the same size')
    statistic = _nan_safe(statistic)
    if (values is None) & (statistic != 'count'):
        raise ValueError('values on which to calculate the statistic are missing')
    if standardized:
        extent = np.asarray(dim.standardized_extent, dtype=float)
    else:
        extent = np.asarray(dim.pitch_extent, dtype=float)
    if edge_tol is None:
        edge_tol = np.abs(extent).max() * 1e-9
    snapped, x_edges, y_edges, cell_zone = _validate_zones(zones, extent, edge_tol)
    # mirror bin_statistic: for inverted-y pitches flip the point coordinates and
    # the fine-grid edges so points on shared edges bin identically to bin_statistic
    if dim.invert_y and not standardized:
        y = dim.bottom - y
        y_bin_edges = (dim.bottom - y_edges)[::-1]
        cell_zone_binning = cell_zone[::-1]
    else:
        y_bin_edges = y_edges
        cell_zone_binning = cell_zone
    _, _, _, fine_binnumber = binned_statistic_2d(x, y, x, statistic='count',
                                                  bins=[x_edges, y_bin_edges],
                                                  expand_binnumbers=True)
    num_x = len(x_edges) - 1
    num_y = len(y_bin_edges) - 1
    inside = ((fine_binnumber[0] >= 1) & (fine_binnumber[0] <= num_x) &
              (fine_binnumber[1] >= 1) & (fine_binnumber[1] <= num_y))
    binnumber = np.full(x.size, -1, dtype=int)
    binnumber[inside] = cell_zone_binning[fine_binnumber[1][inside] - 1,
                                          fine_binnumber[0][inside] - 1]
    patches = [Rectangle((x0, y0), x1 - x0, y1 - y0) for x0, x1, y0, y1 in snapped]
    return zone_statistic_from_binnumber(binnumber, values=values, statistic=statistic,
                                         patches=patches,
                                         cx=0.5 * (snapped[:, 0] + snapped[:, 1]),
                                         cy=0.5 * (snapped[:, 2] + snapped[:, 3]),
                                         names=names,
                                         area=((snapped[:, 1] - snapped[:, 0]) *
                                               (snapped[:, 3] - snapped[:, 2])),
                                         normalize=normalize)


def heatmap_zones(stats, ax=None, vertical=False, **kwargs):
    """ Plots zone statistics as a single matplotlib.collections.PatchCollection.

    Because the zones are one artist, cmap/ norm/ vmin/ vmax apply across
    all zones and fig.colorbar(pc) works without any syncing.
    The stats dictionary only requires the keys 'patches' and 'statistic'
    so you can also plot dictionaries from zone_statistic_from_binnumber
    with your own patches (e.g. matplotlib.patches.Wedge).
    The Pitch/ VerticalPitch heatmap_zones methods additionally clip the
    collection to the pitch boundaries (like hexbin and kdeplot), so patches
    that extend past the pitch edges are snapped to the pitch.

    Parameters
    ----------
    stats : dict.
        This should be calculated via bin_statistic_zones()
        or zone_statistic_from_binnumber().
        The 'patches' (one patch per zone in pitch coordinates) and
        'statistic' (a flat array of values per zone) keys are used for plotting.
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
    >>> pitch = Pitch(line_zorder=2)
    >>> fig, ax = pitch.draw()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> y = np.random.uniform(low=0, high=80, size=100)
    >>> zones = [(0, 60, 0, 80), (60, 120, 0, 40), (60, 120, 40, 80)]
    >>> stats = pitch.bin_statistic_zones(x, y, zones)
    >>> pc = pitch.heatmap_zones(stats, edgecolors='black', cmap='hot', ax=ax)
    """
    validate_ax(ax)
    vmin = kwargs.pop('vmin', None)
    vmax = kwargs.pop('vmax', None)
    collection = PatchCollection(stats['patches'], **kwargs)
    collection.set_array(np.asarray(stats['statistic'], dtype=float))
    collection.set_clim(vmin, vmax)
    if vertical:
        # the patches are authored in pitch coordinates; swap the x and y
        # coordinates of the whole collection with an affine transform
        swap = Affine2D(np.array([[0., 1., 0.], [1., 0., 0.], [0., 0., 1.]]))
        collection.set_transform(swap + ax.transData)
    ax.add_collection(collection)
    return collection


def zone_sonar_from_binnumber(binnumber, angle, values=None, statistic='count',
                              angle_bins=10, patches=None, cx=None, cy=None,
                              names=None, area=None, normalize=False, center=True):
    """ Calculates sonar statistics (zone by angle segment) from per-point
    zone identifiers.

    This is the sonar equivalent of zone_statistic_from_binnumber:
    you supply the zone each point belongs to (the binnumber), computed
    however you like, and it bins the angles within each zone for plotting
    with sonar_zones. The angle wrap-around at 2 pi is your responsibility:
    shift the angles with numpy.mod so a segment does not straddle
    the 0/ 2 pi boundary (or use the default center=True behaviour).

    Parameters
    ----------
    binnumber : array-like of int
        The zone identifier for each point. Use -1 for points outside the zones.
        Zone identifiers are zero indexed and correspond to the order
        of the patches/ names.
    angle : array-like or scalar.
        The angle for each point in radians between 0 and 2*pi.
    values : array-like or scalar, default None
        The values on which to calculate the statistic.
        If the statistic is 'count' then values are ignored.
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean'
        or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html
    angle_bins : int or array_like, default 10
        The number of angle segments, or the segment edges in
        radians between 0 and 2*pi.
    patches : list of matplotlib.patches.Patch, default None
        One patch per zone in pitch coordinates for plotting with heatmap_zones.
        If None, the number of zones is inferred from binnumber.max() + 1.
    cx, cy : array-like, default None
        The centres for each zone in pitch coordinates where the
        sonars are placed by sonar_zones. If None, they fall back to a
        best-effort centroid of the patch path vertices.
    names : list of str, default None
        An optional name for each zone.
    area : array-like, default None
        An optional area for each zone.
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.
    center : bool, default True
        Whether to center the sonars so the first segment is centered around zero (True)
        or starts at zero (False). Centering shifts the angles by half the
        width of the first segment.

    Returns
    -------
    zone_sonar : dict.
        The keys are 'statistic' (the calculated statistic with one row per zone
        and one column per angle segment), 'count' (the total number of points in
        each zone), 'patches', 'cx' and 'cy' (the zone centres),
        'binnumber' (the zone identifier per point, -1 if outside the zones),
        'inside' (whether each point is inside the zones), 'area', 'names',
        'angle_grid' (the segment start angles) and
        'angle_widths' (the segment widths).

    Examples
    --------
    >>> import numpy as np
    >>> from mplsoccer import Pitch
    >>> pitch = Pitch()
    >>> x = np.random.uniform(low=0, high=120, size=100)
    >>> angle = np.random.uniform(low=0, high=2 * np.pi, size=100)
    >>> binnumber = (x > 60).astype(int)  # two zones: own half (0) and opposition half (1)
    >>> stats = pitch.zone_sonar_from_binnumber(binnumber, angle, angle_bins=4)
    """
    result = zone_statistic_from_binnumber(binnumber, patches=patches, cx=cx, cy=cy,
                                           names=names, area=area)
    binnumber = result['binnumber']
    num_zones = result['count'].size
    angle = np.ravel(angle)
    if angle.size != binnumber.size:
        raise ValueError('binnumber and angle must be the same size')
    statistic = _nan_safe(statistic)
    if (values is None) & (statistic != 'count'):
        raise ValueError('values on which to calculate the statistic are missing')
    if values is None:
        values = np.zeros(binnumber.shape)  # ignored by the 'count' statistic
    values = np.ravel(values)
    if values.size != binnumber.size:
        raise ValueError('binnumber and values must be the same size')
    angle, first_width = _center_angles(angle, angle_bins, center)
    inside = result['inside']
    stat, _, angle_edge, _ = binned_statistic_2d(binnumber[inside], angle[inside],
                                                 values[inside], statistic=statistic,
                                                 bins=[num_zones, angle_bins],
                                                 range=[[-0.5, num_zones - 0.5],
                                                        [0, 2 * np.pi]])
    if normalize:
        stat = stat / np.nansum(stat)
    if center:
        angle_edge = angle_edge - first_width / 2
    result['statistic'] = stat
    result['angle_widths'] = np.diff(angle_edge)
    # remove the last edge as only the segment start locations are needed
    result['angle_grid'] = angle_edge[:-1]
    return result


def bin_statistic_sonar_zones(x, y, angle, zones, dim=None, values=None,
                              statistic='count', angle_bins=10, normalize=False,
                              standardized=False, names=None, edge_tol=None,
                              center=True):
    """ Calculates sonar statistics (angle segments per zone) for zones:
    any tiling of the pitch by axis-aligned rectangles.

    This is the sonar equivalent of bin_statistic_zones: each point is
    assigned to a zone and the angles are binned within each zone.
    Unlike bin_statistic_sonar, the zones do not have to form a regular grid,
    e.g. the Juego de Posición layout from positional_zones.
    Plot the results with sonar_zones.

    Parameters
    ----------
    x, y, angle : array-like or scalar.
        Commonly, these parameters are 1D arrays. The angle is in radians
        between 0 and 2*pi.
    zones : array-like of shape (num_zones, 4)
        A sequence of (x0, x1, y0, y1) rectangles in pitch coordinates
        (x0 < x1 and y0 < y1) that together exactly tile the pitch.
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    values : array-like or scalar, default None
        The values on which to calculate the statistic.
        If the statistic is 'count' then values are ignored.
    statistic : string or callable, optional
        The statistic to compute (default is 'count').
        The following statistics are available: 'count' (default),
        'mean', 'std', 'median', 'sum', 'min', 'max', 'circmean'
        or a user-defined function. See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html
    angle_bins : int or array_like, default 10
        The number of angle segments, or the segment edges in
        radians between 0 and 2*pi.
    normalize : bool, default False
        Whether to normalize the statistic by dividing by the total.
    standardized : bool, default False
        Whether the x, y and zone values have been standardized to the
        'uefa' pitch coordinates (105m x 68m)
    names : list of str, default None
        An optional name for each zone (in the same order as zones).
    edge_tol : float, default None
        The absolute tolerance for merging zone edges that differ only by
        floating point noise into one shared edge. The default None uses
        a scale-aware tolerance of max(abs(pitch extent)) * 1e-9.
    center : bool, default True
        Whether to center the sonars so the first segment is centered around zero (True)
        or starts at zero (False). Centering shifts the angles by half the
        width of the first segment.

    Returns
    -------
    zone_sonar : dict.
        The keys are 'statistic' (the calculated statistic with one row per zone
        and one column per angle segment), 'count' (the total number of points in
        each zone), 'patches' (one matplotlib.patches.Rectangle per zone),
        'cx' and 'cy' (the zone centres), 'binnumber' (the zone identifier
        per point, -1 if outside the pitch), 'inside' (whether each point is
        inside the pitch), 'area', 'names', 'angle_grid' (the segment start
        angles) and 'angle_widths' (the segment widths).

    Examples
    --------
    >>> from mplsoccer import Pitch, Sbopen
    >>> parser = Sbopen()
    >>> df = parser.event(69251)[0]
    >>> df = df[(df.type_name == 'Pass') &
    ...         (df.outcome_name.isnull())].copy()
    >>> pitch = Pitch()
    >>> angle, distance = pitch.calculate_angle_and_distance(df.x, df.y,
    ...                                                      df.end_x, df.end_y)
    >>> zones, names = pitch.positional_zones('full')
    >>> bs = pitch.bin_statistic_sonar_zones(df.x, df.y, angle, zones,
    ...                                      angle_bins=4)
    >>> fig, ax = pitch.draw(figsize=(8, 5.5))
    >>> axs = pitch.sonar_zones(bs, width=10, fc='cornflowerblue', ec='black', ax=ax)
    """
    x = np.ravel(x)
    angle = np.ravel(angle)
    if x.size != angle.size:
        raise ValueError('x and angle must be the same size')
    zone_stats = bin_statistic_zones(x, y, zones, dim=dim, standardized=standardized,
                                     names=names, edge_tol=edge_tol)
    return zone_sonar_from_binnumber(zone_stats['binnumber'], angle, values=values,
                                     statistic=statistic, angle_bins=angle_bins,
                                     patches=zone_stats['patches'],
                                     cx=zone_stats['cx'], cy=zone_stats['cy'],
                                     names=names, area=zone_stats['area'],
                                     normalize=normalize, center=center)


def _reflect_zones(zones, center, low_col, high_col):
    """ Reflect the rectangles about a mirror line on one axis."""
    reflected = zones.copy()
    reflected[:, low_col] = 2 * center - zones[:, high_col]
    reflected[:, high_col] = 2 * center - zones[:, low_col]
    return reflected


def mirror_zones(zones, dim=None, names=None, axis='x', suffixes=None):
    """ Complete a zone layout by reflecting it about the middle of the pitch.

    Zone layouts are often symmetric, so you can define the zones for one
    half (or one quarter) of the pitch and mirror them to cover the whole
    pitch. Zones that straddle a mirror line symmetrically (e.g. a middle
    third) are only reflected about the other axis (or kept once), rather
    than duplicated on top of themselves. Zones that straddle a mirror line
    asymmetrically raise a ValueError as their reflection would overlap them.

    The returned zones start with the supplied zones unchanged (zone k
    keeps its index), followed by the reflected zones (for axis='both' the
    x-reflections, then the y-reflections, then the reflections about both
    axes), each in the same relative order as the supplied zones.
    Overlaps (e.g. mirroring a layout that already covers the whole pitch)
    are not detected here; they raise when the layout is used with
    bin_statistic_zones.

    Parameters
    ----------
    zones : array-like of shape (num_zones, 4)
        A sequence of (x0, x1, y0, y1) rectangles in pitch coordinates
        (x0 < x1 and y0 < y1).
    dim : mplsoccer pitch dimensions
        One of FixedDims, MetricasportsDims, VariableCenterDims, or CustomDims.
        Automatically populated when using Pitch/ VerticalPitch class
    names : list of str, default None
        An optional name for each zone (in the same order as zones).
    axis : str, default 'x'
        The reflection axis. 'x' reflects about the halfway line,
        'y' reflects about the y midline running from goal to goal and
        'both' reflects about both (e.g. to complete a quarter-pitch layout).
    suffixes : tuple of str, default None
        The suffixes added to the zone names, one per copy of the layout:
        (supplied, mirrored) for axis='x'/'y', or
        (supplied, x-mirrored, y-mirrored, xy-mirrored) for axis='both'.
        The default None uses ('', '-mirror') and
        ('', '-mirror-x', '-mirror-y', '-mirror-xy') respectively.
        Zones that produce no reflections because they straddle the mirror
        line(s) symmetrically are not given a suffix.

    Returns
    -------
    zones : list of tuple
        The supplied (x0, x1, y0, y1) rectangles followed by the reflected rectangles.
    names : list of str or None
        A name for each zone, or None if names was None.

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> pitch = Pitch()  # statsbomb dimensions: the halfway line is x=60
    >>> zones = [(80, 120, 0, 80), (40, 80, 0, 80)]
    >>> names = ['final-third', 'middle-third']
    >>> zones, names = pitch.mirror_zones(zones, names, suffixes=('-att', '-def'))
    >>> names  # the middle third straddles halfway symmetrically so is kept once
    ['final-third-att', 'middle-third', 'final-third-def']
    """
    zones = np.asarray(zones, dtype=float)
    if zones.ndim != 2 or zones.shape[1] != 4:
        raise ValueError('zones must be a sequence of (x0, x1, y0, y1) rectangles')
    bad = np.where((zones[:, 1] <= zones[:, 0]) | (zones[:, 3] <= zones[:, 2]))[0]
    if bad.size:
        raise ValueError(f'zone {bad[0]} is invalid: zones must have x1 > x0 and y1 > y0')
    if names is not None and len(names) != len(zones):
        raise ValueError('names must be the same length as zones')
    if axis not in ('x', 'y', 'both'):
        raise ValueError("axis must be one of 'x', 'y' or 'both'")
    mirror_x = axis in ('x', 'both')
    mirror_y = axis in ('y', 'both')
    if suffixes is None:
        suffixes = (('', '-mirror-x', '-mirror-y', '-mirror-xy') if axis == 'both'
                    else ('', '-mirror'))
    if len(suffixes) != 2 + 2 * (axis == 'both'):
        raise ValueError('suffixes must have one suffix per copy of the layout: '
                         "two for axis='x'/'y' or four for axis='both'")
    tol = np.abs(np.asarray(dim.pitch_extent, dtype=float)).max() * 1e-9

    def reflect(low_col, high_col, center, line_name):
        """ Reflected zones, whether each zone maps onto itself (symmetric),
        and raise for zones straddling the mirror line asymmetrically."""
        reflected = _reflect_zones(zones, center, low_col, high_col)
        symmetric = (np.isclose(reflected[:, low_col], zones[:, low_col],
                                rtol=0, atol=tol) &
                     np.isclose(reflected[:, high_col], zones[:, high_col],
                                rtol=0, atol=tol))
        straddle = ((zones[:, low_col] < center - tol) &
                    (zones[:, high_col] > center + tol) & ~symmetric)
        if straddle.any():
            raise ValueError(f'zone {np.where(straddle)[0][0]} straddles the '
                             f'{line_name} asymmetrically so its reflection '
                             'would overlap it')
        return reflected, symmetric

    x_center = (dim.left + dim.right) / 2
    y_center = (dim.bottom + dim.top) / 2
    x_symmetric = np.ones(len(zones), dtype=bool)
    y_symmetric = np.ones(len(zones), dtype=bool)
    # each copy of the layout is (zones, mask of the zones included in the copy)
    copies = [(zones, np.ones(len(zones), dtype=bool))]
    if mirror_x:
        reflected_x, x_symmetric = reflect(0, 1, x_center, "halfway line (axis='x')")
        copies.append((reflected_x, ~x_symmetric))
    if mirror_y:
        reflected_y, y_symmetric = reflect(2, 3, y_center, "y midline (axis='y')")
        copies.append((reflected_y, ~y_symmetric))
    if mirror_x and mirror_y:
        reflected_xy = _reflect_zones(reflected_x, y_center, 2, 3)
        copies.append((reflected_xy, ~x_symmetric & ~y_symmetric))

    out_zones = [tuple(float(value) for value in zone)
                   for copy, mask in copies for zone in copy[mask]]
    if names is None:
        return out_zones, None
    no_suffix = x_symmetric & y_symmetric  # zones producing no reflections at all
    out_names = []
    for suffix, (_, mask) in zip(suffixes, copies):
        out_names += [name if no_suffix[i] else name + suffix
                      for i, name in enumerate(names) if mask[i]]
    return out_zones, out_names


def _sonar(lengths, colors, angle_grid, angle_widths,
           cmap=None, vmin=None, vmax=None, rmin=0, rmax=None,
           sonar_alpha=1, sonar_facecolor='None',
           axis=False, label=False, ax=None, **kwargs):
    """ Plot a single sonar (polar bar chart) from 1d arrays of
    segment lengths and optional segment color values."""
    if not isinstance(ax, PolarAxes):
        raise TypeError('The ax argument must be of type matplotlib.projections.polar.PolarAxes.')
    ax.patch.set_alpha(sonar_alpha)
    ax.grid(axis)
    ax.spines['polar'].set_visible(axis)
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
        norm = Normalize(vmin=vmin, vmax=vmax)
        color = cmap(norm(colors))
        return ax.bar(angle_grid,
                      np.nan_to_num(lengths),
                      width=angle_widths,
                      color=color,
                      align='edge',
                      **kwargs)
    return ax.bar(angle_grid,
                  np.nan_to_num(lengths),
                  width=angle_widths,
                  align='edge',
                  **kwargs)


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
    cmap : str or matplotlib.colors.Colormap, default None
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
        raise ValueError(f"stats_length['statistic'] {stats_length['statistic'].shape} "
                         'should have three dimensions. '
                         'Try creating the statistics again using bin_statistic_sonar.')
    if stats_color is not None and cmap is None:
        raise ValueError("You must supply a cmap for varying the color using stats_color.")
    if stats_color is None and cmap is not None:
        raise ValueError("You must supply a stats_color for varying the color using a cmap.")
    if stats_color is not None and stats_color['statistic'].shape != stats_length['statistic'].shape:
        raise ValueError(f"stats_color['statistic'] {stats_color['statistic'].shape} "
                         f"and stats_length['statistic'] {stats_length['statistic'].shape} are different shapes. "
                         'Try creating the statistics again using bin_statistic_sonar '
                         'with the same bins argument.')
    if rmax is None:
        rmax = np.nanmax(stats_length['statistic'])
    colors = None
    if stats_color is not None:
        if vmin is None:
            vmin = np.nanmin(stats_color['statistic'])
        if vmax is None:
            vmax = np.nanmax(stats_color['statistic'])
        colors = stats_color['statistic'][yindex, xindex, :]
    return _sonar(stats_length['statistic'][yindex, xindex, :], colors,
                  stats_length['angle_grid'], stats_length['angle_widths'],
                  cmap=cmap, vmin=vmin, vmax=vmax, rmin=rmin, rmax=rmax,
                  sonar_alpha=sonar_alpha, sonar_facecolor=sonar_facecolor,
                  axis=axis, label=label, ax=ax, **kwargs)
