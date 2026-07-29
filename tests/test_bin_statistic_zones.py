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
    after the edges are merged."""
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


def test_point_on_merged_edge():
    """ Test a point exactly on a shared edge bins consistently with
    bin_statistic when the regions state the edge with float noise
    (region 0 ends at 60, region 1 starts one ulp above 60)."""
    pitch = Pitch(pitch_type='statsbomb')
    regions = [(0., 60., 0., 80.), (np.nextafter(60., np.inf), 120., 0., 80.)]
    x = np.array([60., 30., 90.])
    y = np.array([40., 40., 40.])
    stats = pitch.bin_statistic_zones(x, y, regions)
    # scipy's convention: a point on an internal edge belongs to the right-hand bin
    assert np.array_equal(stats['binnumber'], [1, 0, 1])
    assert np.array_equal(stats['statistic'], [1., 2.])
    grid = pitch.bin_statistic(x, y, bins=(2, 1))
    assert np.array_equal(grid['statistic'], [[1., 2.]])


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


def test_bin_statistic_sonar_zones():
    """ Test the zone sonar statistics match a direct per-zone/ per-segment
    computation via binnumber masks and digitized angles."""
    num_points = 100000
    num_angle = 8
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points)
    angle = np.random.uniform(low=0, high=2 * np.pi, size=num_points)
    values = np.random.normal(size=num_points)
    regions, names = pitch.positional_zones('full')
    stats = pitch.bin_statistic_sonar_zones(x, y, angle, regions, names=names,
                                            angle_bins=num_angle, center=True)
    assert stats['statistic'].shape == (len(regions), num_angle)
    assert stats['statistic'].sum() == num_points
    assert np.array_equal(stats['count'], stats['statistic'].sum(axis=1))
    first_width = 2 * np.pi / num_angle
    shifted = np.mod(angle + first_width / 2, 2 * np.pi)
    segment = np.clip(np.digitize(shifted, np.linspace(0, 2 * np.pi, num_angle + 1)) - 1,
                      0, num_angle - 1)
    direct = np.zeros((len(regions), num_angle))
    np.add.at(direct, (stats['binnumber'], segment), 1)
    assert np.array_equal(stats['statistic'], direct)
    # the mean statistic per zone/ segment matches a direct computation
    stats_mean = pitch.bin_statistic_sonar_zones(x, y, angle, regions, values=values,
                                                 statistic='mean', angle_bins=num_angle)
    mask = (stats['binnumber'] == 5) & (segment == 3)
    assert np.isclose(stats_mean['statistic'][5, 3], values[mask].mean())


def test_bin_statistic_sonar_zones_grid_equivalence():
    """ Test the zone sonars reproduce bin_statistic_sonar when the zones
    form the same regular grid, for both center options."""
    num_points = 100000
    for pitch_type in ['statsbomb', 'uefa']:
        pitch = Pitch(pitch_type=pitch_type)
        x, y = random_points(pitch, num_points)
        angle = np.random.uniform(low=0, high=2 * np.pi, size=num_points)
        xmin, xmax, ymin, ymax = pitch.dim.pitch_extent
        x_edges = np.linspace(xmin, xmax, 5)
        y_edges = np.linspace(ymin, ymax, 4)
        # zone order matches the sonar raster: unlike bin_statistic, the sonar
        # statistic rows are ordered by ascending y for both pitch orientations
        # (they pair with the unflipped cy centres)
        regions = [(x_edges[j], x_edges[j + 1], y_edges[i], y_edges[i + 1])
                   for i in range(3) for j in range(4)]
        for center in [True, False]:
            grid = pitch.bin_statistic_sonar(x, y, angle, bins=(4, 3, 6), center=center)
            zones = pitch.bin_statistic_sonar_zones(x, y, angle, regions,
                                                    angle_bins=6, center=center)
            assert np.array_equal(grid['statistic'].reshape(-1, 6), zones['statistic'])
            assert np.array_equal(grid['angle_grid'], zones['angle_grid'])
            assert np.array_equal(grid['angle_widths'], zones['angle_widths'])


def test_zone_sonar_from_binnumber():
    """ Test the sonar escape hatch: feeding bin_statistic_sonar_zones' own
    binnumber back through zone_sonar_from_binnumber reproduces its statistics."""
    num_points = 10000
    pitch = Pitch(pitch_type='statsbomb')
    x, y = random_points(pitch, num_points)
    angle = np.random.uniform(low=0, high=2 * np.pi, size=num_points)
    regions, _ = pitch.positional_zones('full')
    stats = pitch.bin_statistic_sonar_zones(x, y, angle, regions, angle_bins=6)
    round_trip = pitch.zone_sonar_from_binnumber(stats['binnumber'], angle, angle_bins=6,
                                                 patches=stats['patches'],
                                                 cx=stats['cx'], cy=stats['cy'])
    assert np.array_equal(round_trip['statistic'], stats['statistic'])
    assert np.array_equal(round_trip['count'], stats['count'])
    assert np.array_equal(round_trip['angle_grid'], stats['angle_grid'])


def test_sonar_zones_plotting():
    """ Test sonar_zones places one polar inset per zone with the bar heights
    matching the statistic, on both pitch orientations."""
    num_points = 10000
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        x, y = random_points(pitch, num_points)
        angle = np.random.uniform(low=0, high=2 * np.pi, size=num_points)
        regions, _ = pitch.positional_zones('full')
        stats = pitch.bin_statistic_sonar_zones(x, y, angle, regions, angle_bins=6)
        axs = pitch.sonar_zones(stats, width=10, ax=ax)
        assert axs.shape == (len(regions),)
        for zone, ax_inset in enumerate(axs):
            heights = [patch.get_height() for patch in ax_inset.patches]
            assert np.allclose(heights, np.nan_to_num(stats['statistic'][zone]))
    # zones with no points are excluded when exclude_zeros is True
    stats['statistic'][3, :] = 0
    fig, ax = pitch.draw()
    axs = pitch.sonar_zones(stats, width=10, ax=ax)
    assert axs[3] is None
    # a zone statistics dict has two dimensions so sonar_grid must fail loudly
    with pytest.raises(ValueError, match='three dimensions'):
        pitch.sonar_grid(stats, width=10, ax=ax)
    with pytest.raises(ValueError, match='different shapes'):
        wrong = pitch.bin_statistic_sonar_zones(x, y, angle, regions, angle_bins=4)
        pitch.sonar_zones(stats, stats_color=wrong, cmap='viridis', width=10, ax=ax)


def test_mirror_zones():
    """ Test mirroring completes a layout, keeps symmetric straddlers once,
    preserves the supplied zone order and produces a valid tiling."""
    pitch = Pitch(pitch_type='statsbomb')
    regions = [(80, 120, 0, 40), (80, 120, 40, 80), (40, 80, 0, 80)]
    names = ['right', 'left', 'middle']
    out_regions, out_names = pitch.mirror_zones(regions, names, suffixes=('-att', '-def'))
    assert out_regions == [(80., 120., 0., 40.), (80., 120., 40., 80.), (40., 80., 0., 80.),
                           (0., 40., 0., 40.), (0., 40., 40., 80.)]
    assert out_names == ['right-att', 'left-att', 'middle', 'right-def', 'left-def']
    # the completed layout passes the strict binning validation
    x, y = random_points(pitch, 10000)
    stats = pitch.bin_statistic_zones(x, y, out_regions, names=out_names)
    assert stats['statistic'].sum() == 10000
    # names=None returns None names; axis='y' reflects about the y midline
    out_regions, out_names = pitch.mirror_zones([(0, 120, 0, 18)], axis='y')
    assert out_regions == [(0., 120., 0., 18.), (0., 120., 62., 80.)]
    assert out_names is None
    with pytest.raises(ValueError, match='region 0 straddles the halfway line'):
        pitch.mirror_zones([(40, 90, 0, 80)])
    with pytest.raises(ValueError, match='straddles the y midline'):
        pitch.mirror_zones([(0, 120, 10, 60)], axis='both')
    with pytest.raises(ValueError, match='region 1 is invalid'):
        pitch.mirror_zones([(80, 120, 0, 80), (80, 40, 0, 80)])


def test_mirror_zones_both():
    """ Test axis='both' completes a quarter-pitch layout, reflecting in x,
    y and both, with per-axis symmetry handled per zone."""
    pitch = Pitch(pitch_type='statsbomb')
    # a quarter-pitch layout plus a zone that is symmetric in x only
    regions = [(60, 90, 40, 80), (90, 120, 40, 80), (40, 80, 40, 80)]
    names = ['near', 'far', 'mid']
    out_regions, out_names = pitch.mirror_zones(regions, names, axis='both')
    # copies ordered: supplied, x-mirrored, y-mirrored, xy-mirrored;
    # 'mid' is x-symmetric so it only produces a y reflection
    assert out_names == ['near', 'far', 'mid',
                         'near-mirror-x', 'far-mirror-x',
                         'near-mirror-y', 'far-mirror-y', 'mid-mirror-y',
                         'near-mirror-xy', 'far-mirror-xy']
    assert out_regions[3] == (30., 60., 40., 80.)   # near-mirror-x
    assert out_regions[7] == (40., 80., 0., 40.)    # mid-mirror-y
    assert out_regions[8] == (30., 60., 0., 40.)    # near-mirror-xy
    # the quarter layout without the overlapping mid zone tiles the pitch
    quarter_regions, _ = pitch.mirror_zones([(60, 90, 40, 80), (90, 120, 40, 80)],
                                            axis='both')
    x, y = random_points(pitch, 10000)
    stats = pitch.bin_statistic_zones(x, y, quarter_regions)
    assert stats['statistic'].sum() == 10000
    # a fully symmetric zone is kept once with no suffix
    out_regions, out_names = pitch.mirror_zones([(40, 80, 0, 80), (80, 120, 0, 30)],
                                                ['mid', 'corner'], axis='both')
    assert out_names == ['mid', 'corner', 'corner-mirror-x',
                         'corner-mirror-y', 'corner-mirror-xy']
    with pytest.raises(ValueError, match='suffixes must have one suffix per copy'):
        pitch.mirror_zones(regions, names, axis='both', suffixes=('', '-mirror'))


def test_draw_zones():
    """ Test the zone preview draws invalid layouts without raising,
    labels the zones and cycles the face colors."""
    regions = [(0, 60, 0, 80), (50, 120, 0, 50)]  # overlapping, with a gap
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb')
        fig, ax = pitch.draw()
        collection, annotations = pitch.draw_zones(regions, ['big', 'low'], ax=ax)
        assert isinstance(collection, PatchCollection)
        assert [annotation.get_text() for annotation in annotations] == ['0: big', '1: low']
        assert all(annotation.get_clip_on() for annotation in annotations)
        # indices only when no names are given; no labels when label=False
        fig, ax = pitch.draw()
        _, annotations = pitch.draw_zones(regions, ax=ax)
        assert [annotation.get_text() for annotation in annotations] == ['0', '1']
        _, annotations = pitch.draw_zones(regions, label=False, ax=ax)
        assert annotations == []
    # the default is a single face color; a sequence gives per-zone colors.
    # the zones and labels draw above pitch lines (zorder 3 by default)
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = pitch.draw()
    collection, annotations = pitch.draw_zones(regions, ax=ax)
    assert len(collection.get_facecolor()) == 1
    assert collection.get_zorder() == 3
    assert all(annotation.get_zorder() == 3 for annotation in annotations)
    collection, _ = pitch.draw_zones(regions, facecolor=['red', 'blue'], zorder=4, ax=ax)
    facecolors = collection.get_facecolor()
    assert len(facecolors) == 2
    assert not np.array_equal(facecolors[0], facecolors[1])
    assert collection.get_zorder() == 4


def test_draw_zones_overlaps_darker():
    """ Test overlapping zones render darker than single zones and gaps
    show the background (the visual diagnostics of the preview)."""
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    regions = [(0, 60, 0, 80), (50, 120, 0, 50)]  # overlap x 50-60, gap x 60-120 y 50-80
    pitch.draw_zones(regions, facecolor='blue', label=False, ax=ax)
    fig.canvas.draw()
    buffer = np.asarray(fig.canvas.buffer_rgba())
    height = buffer.shape[0]

    def red_channel(x, y):
        pixel_x, pixel_y = ax.transData.transform((x, y))
        return buffer[int(height - pixel_y), int(pixel_x), 0]

    single = red_channel(20, 70)
    overlap = red_channel(55, 25)
    gap = red_channel(100, 70)
    assert overlap < single < gap


def test_sonar_grid_unchanged():
    """ Test sonar_grid still returns a grid of polar insets with bar heights
    matching the statistic (regression for the shared _sonar_insets refactor)."""
    num_points = 10000
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    x, y = random_points(pitch, num_points)
    angle = np.random.uniform(low=0, high=2 * np.pi, size=num_points)
    stats = pitch.bin_statistic_sonar(x, y, angle, bins=(3, 2, 5))
    axs = pitch.sonar_grid(stats, width=15, ax=ax)
    assert axs.shape == (2, 3)
    for yindex in range(2):
        for xindex in range(3):
            heights = [patch.get_height() for patch in axs[yindex, xindex].patches]
            assert np.allclose(heights, np.nan_to_num(stats['statistic'][yindex, xindex]))
