""" Test the zone statistic methods for binning data into custom zones."""

from dataclasses import asdict

import numpy as np
import pytest
from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge

from mplsoccer import Pitch, VerticalPitch
from mplsoccer.heatmap import BinnedStatisticResult, bin_statistic
from mplsoccer.soccer.dimensions import valid, size_varies


def pitch_kwargs(pitch_type):
    """ Extra keyword arguments needed to create a pitch of the given type."""
    if pitch_type in size_varies:
        return {'pitch_length': 105, 'pitch_width': 68}
    return {}


def random_points(pitch, num_points, pad=0.):
    """ Random uniform points on the pitch (padded outside the pitch if pad > 0)."""
    extent = pitch.dim.pitch_extent
    x_pad = (extent[1] - extent[0]) * pad
    y_pad = (extent[3] - extent[2]) * pad
    x = np.random.uniform(low=extent[0] - x_pad, high=extent[1] + x_pad, size=num_points)
    y = np.random.uniform(low=extent[2] - y_pad, high=extent[3] + y_pad, size=num_points)
    return x, y


def legacy_bin_statistic_positional(x, y, values=None, dim=None, positional='full',
                                    statistic='count', normalize=False):
    """ Frozen copy of the original bin_statistic_positional implementation
    (multiple binned_statistic_2d passes) used as the regression reference."""
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


def test_bin_statistic_zones_points():
    """ Test all 10 million points are included in the zone statistics."""
    num_points = 10000000
    for pitch_type in valid:
        pitch = Pitch(pitch_type=pitch_type, **pitch_kwargs(pitch_type))
        x, y = random_points(pitch, num_points)
        regions, names = pitch.positional_zones('full')
        stats = pitch.bin_statistic_zones(x, y, regions, names=names)
        assert stats['statistic'].sum() == num_points


def test_bin_statistic_zones_edge_points():
    """ Test points exactly on the region boundaries are all counted exactly once.
    This includes the 0-1 metricasports coordinate system, whose edges are
    non-terminating binary fractions."""
    for pitch_type in valid:
        pitch = Pitch(pitch_type=pitch_type, **pitch_kwargs(pitch_type))
        regions, _ = pitch.positional_zones('full')
        extent = pitch.dim.pitch_extent
        x_edges = pitch.dim.positional_x
        y_edges = pitch.dim.positional_y
        # points exactly on the x-edges
        x = np.tile(x_edges, 100000)
        y = np.random.uniform(low=extent[2], high=extent[3], size=x.size)
        stats = pitch.bin_statistic_zones(x, y, regions)
        assert stats['statistic'].sum() == x.size
        # points exactly on the y-edges
        y = np.tile(y_edges, 100000)
        x = np.random.uniform(low=extent[0], high=extent[1], size=y.size)
        stats = pitch.bin_statistic_zones(x, y, regions)
        assert stats['statistic'].sum() == y.size
        # corner points exactly on both x and y edges simultaneously
        x_corner, y_corner = np.meshgrid(x_edges, y_edges)
        x = np.tile(x_corner.ravel(), 10000)
        y = np.tile(y_corner.ravel(), 10000)
        stats = pitch.bin_statistic_zones(x, y, regions)
        assert stats['statistic'].sum() == x.size


def test_bin_statistic_positional_regression():
    """ Test the reimplemented bin_statistic_positional reproduces the
    original implementation exactly for all pitch types and options."""
    num_points = 100000
    for vertical in [False, True]:
        pitch_class = VerticalPitch if vertical else Pitch
        for pitch_type in valid:
            pitch = pitch_class(pitch_type=pitch_type, **pitch_kwargs(pitch_type))
            # include points outside the pitch so out-of-range handling is compared too
            x, y = random_points(pitch, num_points, pad=0.1)
            values = np.random.normal(size=num_points)
            for positional in ['full', 'horizontal', 'vertical']:
                for statistic, vals, normalize in [('count', None, False),
                                                   ('count', None, True),
                                                   ('mean', values, False),
                                                   ('sum', values, False)]:
                    old = legacy_bin_statistic_positional(x, y, values=vals, dim=pitch.dim,
                                                          positional=positional,
                                                          statistic=statistic,
                                                          normalize=normalize)
                    new = pitch.bin_statistic_positional(x, y, values=vals,
                                                         positional=positional,
                                                         statistic=statistic,
                                                         normalize=normalize)
                    assert len(old) == len(new)
                    for old_section, new_section in zip(old, new):
                        assert old_section.keys() == new_section.keys()
                        assert np.array_equal(old_section['statistic'],
                                              new_section['statistic'], equal_nan=True)
                        for key in ['x_grid', 'y_grid', 'cx', 'cy']:
                            assert np.array_equal(old_section[key], new_section[key])


def test_float_noise_edges():
    """ Test regions with edges perturbed by one ulp give identical results
    after edge canonicalisation."""
    num_points = 100000
    for pitch_type in ['statsbomb', 'metricasports']:
        pitch = Pitch(pitch_type=pitch_type, **pitch_kwargs(pitch_type))
        x, y = random_points(pitch, num_points)
        regions, _ = pitch.positional_zones('full')
        regions = np.asarray(regions, dtype=float)
        noisy = regions.copy()
        noisy[::2] = np.nextafter(noisy[::2], np.inf)
        noisy[1::2] = np.nextafter(noisy[1::2], -np.inf)
        stats = pitch.bin_statistic_zones(x, y, regions)
        stats_noisy = pitch.bin_statistic_zones(x, y, noisy)
        assert np.array_equal(stats['statistic'], stats_noisy['statistic'])
        assert np.array_equal(stats['binnumber'], stats_noisy['binnumber'])


def test_statistic_parity():
    """ Test mean/ median per zone match a direct per-zone numpy computation
    via binnumber masks (no mean-of-means error on merged zones)."""
    num_points = 100000
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points)
    values = np.random.normal(size=num_points)
    # thirds in the defensive half plus halfspace-style splits in the attacking half
    regions = [(0, 40, 0, 80), (40, 80, 0, 80),
               (80, 120, 0, 18), (80, 120, 18, 62), (80, 120, 62, 80)]
    for statistic, func in [('mean', np.mean), ('median', np.median), ('std', np.std)]:
        stats = pitch.bin_statistic_zones(x, y, regions, values=values, statistic=statistic)
        direct = np.array([func(values[stats['binnumber'] == k]) for k in range(len(regions))])
        assert np.allclose(stats['statistic'], direct)


def test_label_heatmap_zones():
    """ Test label_heatmap works on the zone statistics dictionary unchanged."""
    num_points = 1000
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        x, y = random_points(pitch, num_points)
        regions, names = pitch.positional_zones('full')
        stats = pitch.bin_statistic_zones(x, y, regions, names=names)
        annotations = pitch.label_heatmap(stats, ax=ax, str_format='{:.0f}')
        assert len(annotations) == len(regions)
        positions = np.array([annotation.get_position() for annotation in annotations])
        if pitch.vertical:
            assert np.array_equal(positions, np.c_[stats['cy'], stats['cx']])
        else:
            assert np.array_equal(positions, np.c_[stats['cx'], stats['cy']])


def test_heatmap_zones_collection():
    """ Test heatmap_zones plots one PatchCollection with the statistic as its array."""
    num_points = 1000
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        x, y = random_points(pitch, num_points)
        regions, _ = pitch.positional_zones('full')
        stats = pitch.bin_statistic_zones(x, y, regions)
        collection = pitch.heatmap_zones(stats, ax=ax, vmin=0, vmax=100, cmap='hot')
        assert isinstance(collection, PatchCollection)
        assert np.array_equal(collection.get_array(), stats['statistic'])
        assert collection.get_clim() == (0, 100)
        # the collection is clipped to the pitch boundaries (like hexbin/ kdeplot).
        # matplotlib stores a rectangle clip path as a clip box (in display space)
        assert collection.clipbox is not None
        corners = ax.transData.transform(
            np.array([[pitch.visible_pitch[0], pitch.visible_pitch[2]],
                      [pitch.visible_pitch[1], pitch.visible_pitch[3]]]))
        assert np.allclose(np.sort(collection.clipbox.get_points(), axis=0),
                           np.sort(corners, axis=0))
    # a zone statistics dictionary is patches not grids so heatmap must fail loudly
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    with pytest.raises(KeyError):
        pitch.heatmap(stats, ax=ax)


def test_validation_overlap():
    """ Test overlapping regions raise an error naming both regions."""
    pitch = Pitch(pitch_type='statsbomb')
    regions = [(0, 60, 0, 80), (50, 120, 0, 80)]
    with pytest.raises(ValueError, match='regions 0 and 1 overlap'):
        pitch.bin_statistic_zones([60.], [40.], regions)


def test_validation_gap():
    """ Test regions that do not tile the pitch raise an error with a location."""
    pitch = Pitch(pitch_type='statsbomb')
    regions = [(0, 60, 0, 80), (70, 120, 0, 80)]
    with pytest.raises(ValueError, match='gap around x=65, y=40'):
        pitch.bin_statistic_zones([60.], [40.], regions)


def test_validation_bad_rectangle():
    """ Test rectangles with x1 <= x0 or y1 <= y0 raise an error naming the region."""
    pitch = Pitch(pitch_type='statsbomb')
    with pytest.raises(ValueError, match='region 1 is invalid'):
        pitch.bin_statistic_zones([60.], [40.], [(0, 60, 0, 80), (120, 60, 0, 80)])


def test_validation_outside_extent():
    """ Test rectangles outside the pitch extent raise an error naming the region."""
    pitch = Pitch(pitch_type='statsbomb')
    with pytest.raises(ValueError, match='region 1 x-edges are outside the pitch extent'):
        pitch.bin_statistic_zones([60.], [40.], [(0, 60, 0, 80), (60, 130, 0, 80)])


def test_ordering_preserved():
    """ Test zone k statistics match region k for a deliberately shuffled region list."""
    num_points = 100000
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points)
    regions, _ = pitch.positional_zones('full')
    regions = np.asarray(regions, dtype=float)
    rng = np.random.default_rng(42)
    shuffled = regions[rng.permutation(len(regions))]
    stats = pitch.bin_statistic_zones(x, y, shuffled)
    for k, (x0, x1, y0, y1) in enumerate(shuffled):
        # direct count with edge semantics irrelevant: no points sit exactly on edges
        direct = ((x >= x0) & (x < x1) & (y >= y0) & (y < y1)).sum()
        assert stats['statistic'][k] == direct
        assert stats['patches'][k].get_x() == x0
        assert stats['patches'][k].get_y() == y0


def test_zone_statistic_from_binnumber():
    """ Test the escape hatch: a hand-built polar binnumber matches a
    direct computation, and feeding bin_statistic_zones' own binnumber
    back through reproduces its statistics."""
    num_points = 100000
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points)
    values = np.random.normal(size=num_points)
    # polar wedges around the goal at (120, 40): four 45 degree segments facing the pitch
    angle = np.arctan2(y - 40, x - 120)
    edges = np.linspace(np.pi / 2, 3 * np.pi / 2, 5)
    binnumber = np.digitize(np.mod(angle, 2 * np.pi), edges) - 1
    binnumber[(binnumber < 0) | (binnumber > 3)] = -1
    patches = [Wedge((120, 40), 130, 90 + 45 * i, 135 + 45 * i) for i in range(4)]
    cx = 120 + 65 * np.cos(np.radians([112.5, 157.5, 202.5, 247.5]))
    cy = 40 + 65 * np.sin(np.radians([112.5, 157.5, 202.5, 247.5]))
    stats = pitch.zone_statistic_from_binnumber(binnumber, values=values, statistic='mean',
                                                patches=patches, cx=cx, cy=cy)
    inside = binnumber >= 0
    assert np.array_equal(stats['count'], np.bincount(binnumber[inside], minlength=4))
    direct = np.array([values[binnumber == k].mean() for k in range(4)])
    assert np.allclose(stats['statistic'], direct)
    assert np.array_equal(stats['cx'], cx)
    assert np.array_equal(stats['cy'], cy)
    # round trip: the zones binnumber reproduces the zones statistics
    regions, _ = pitch.positional_zones('full')
    zone_stats = pitch.bin_statistic_zones(x, y, regions)
    round_trip = pitch.zone_statistic_from_binnumber(zone_stats['binnumber'],
                                                     patches=zone_stats['patches'])
    assert np.array_equal(round_trip['statistic'], zone_stats['statistic'])
    assert np.array_equal(round_trip['count'], zone_stats['count'])


def test_binnumber_validation():
    """ Test the escape hatch validates the binnumber."""
    pitch = Pitch(pitch_type='statsbomb')
    with pytest.raises(TypeError, match='integers'):
        pitch.zone_statistic_from_binnumber(np.array([0.5, 1.5]))
    with pytest.raises(ValueError, match='>= -1'):
        pitch.zone_statistic_from_binnumber(np.array([-2, 0]))
    with pytest.raises(ValueError, match='patches'):
        pitch.zone_statistic_from_binnumber(np.array([0, 5]),
                                            patches=[None] * 2)


def test_consistency():
    """ Test the count key equals a bincount of the inside binnumbers and
    inside equals binnumber >= 0, whatever the requested statistic."""
    num_points = 100000
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points, pad=0.1)
    values = np.random.normal(size=num_points)
    regions, _ = pitch.positional_zones('full')
    for statistic, vals in [('count', None), ('mean', values)]:
        stats = pitch.bin_statistic_zones(x, y, regions, values=vals, statistic=statistic)
        assert np.array_equal(stats['inside'], stats['binnumber'] >= 0)
        assert np.array_equal(stats['count'],
                              np.bincount(stats['binnumber'][stats['inside']],
                                          minlength=len(regions)))


def test_normalize():
    """ Test the normalized statistic sums to one."""
    num_points = 100000
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points)
    regions, _ = pitch.positional_zones('full')
    stats = pitch.bin_statistic_zones(x, y, regions, normalize=True)
    assert np.isclose(stats['statistic'].sum(), 1)
