""" Test the bin statistic methods for binning data on the pitch."""

import numpy as np
import pandas as pd

from mplsoccer import Pitch
from mplsoccer.soccer.dimensions import valid, size_varies


def test_bin_statistic_points():
    """ Test all 10 million points are included in the stats"""
    num_points = 10000000
    for pitch_type in valid:
        if pitch_type in size_varies:
            kwargs = {'pitch_length': 105, 'pitch_width': 68}
        else:
            kwargs = {}
        pitch = Pitch(pitch_type=pitch_type, label=True, axis=True, **kwargs)
        x = np.random.uniform(low=pitch.dim.pitch_extent[0], high=pitch.dim.pitch_extent[1],
                              size=num_points)
        y = np.random.uniform(low=pitch.dim.pitch_extent[2], high=pitch.dim.pitch_extent[3],
                              size=num_points)
        stats = pitch.bin_statistic(x, y)
        assert stats["statistic"].sum() == num_points
        

def test_binnumber_correct():
    """ Test that the bin numbers match the statistic grid."""
    num_points = 10000000
    for pitch_type in valid:
        if pitch_type in size_varies:
            kwargs = {'pitch_length': 105, 'pitch_width': 68}
        else:
            kwargs = {}
        pitch = Pitch(pitch_type=pitch_type, label=True, axis=True, **kwargs)
        x = np.random.uniform(low=pitch.dim.pitch_extent[0], high=pitch.dim.pitch_extent[1],
                              size=num_points)
        y = np.random.uniform(low=pitch.dim.pitch_extent[2], high=pitch.dim.pitch_extent[3],
                              size=num_points)
        stats = pitch.bin_statistic(x, y, bins=(5, 4))
        df = pd.DataFrame(stats['binnumber'].T)
        df.columns = ['x', 'y']
        df = df.value_counts().reset_index(name='bin_counts')

        bin_stats = np.zeros((4, 5))  # note that statistic is transposed
        bin_stats[df['y'], df['x']] = df['bin_counts']
        assert (bin_stats == stats['statistic']).mean() == 1
        

def test_bin_statistic_explicit_asymmetric_edges():
    """ Test explicit non-uniform bin edges attach the statistics to the
    correct bands for all pitch types. Inverted-y pitches previously binned
    the flipped data against unflipped user edges, so the statistics were
    attached to the wrong y bands (uniform integer bins were unaffected)."""
    num_points = 100000
    rng = np.random.default_rng(42)
    for pitch_type in valid:
        if pitch_type in size_varies:
            kwargs = {'pitch_length': 105, 'pitch_width': 68}
        else:
            kwargs = {}
        pitch = Pitch(pitch_type=pitch_type, **kwargs)
        xmin, xmax, ymin, ymax = pitch.dim.pitch_extent
        x = rng.uniform(low=xmin, high=xmax, size=num_points)
        y = rng.uniform(low=ymin, high=ymax, size=num_points)
        x_edges = np.concatenate([[xmin], np.sort(rng.uniform(xmin, xmax, 3)), [xmax]])
        y_edges = np.concatenate([[ymin], np.sort(rng.uniform(ymin, ymax, 2)), [ymax]])
        stats = pitch.bin_statistic(x, y, bins=(x_edges, y_edges))
        # independent reference via digitize in original pitch coordinates
        # (random points never sit exactly on the edges). Statistic row 0 is
        # the top of the pitch as displayed, so for inverted-y pitches it is
        # the band with the smallest y values
        col = np.digitize(x, x_edges) - 1
        band = np.digitize(y, y_edges) - 1
        num_y = len(y_edges) - 1
        row = band if pitch.dim.invert_y else num_y - 1 - band
        expected = np.zeros((num_y, len(x_edges) - 1))
        np.add.at(expected, (row, col), 1)
        assert np.array_equal(stats['statistic'], expected)
        assert np.array_equal(stats['binnumber'][0], col)
        assert np.array_equal(stats['binnumber'][1], row)


def test_bin_statistic_sonar_explicit_asymmetric_edges():
    """ Test explicit non-uniform y bin edges attach the sonar statistics
    to the correct bands on an inverted-y pitch."""
    pitch = Pitch(pitch_type='statsbomb')
    x_edges = np.array([0., 120.])
    y_edges = np.array([0., 10., 80.])
    x = np.full(100, 60.)
    y = np.full(100, 50.)  # all points in the y band [10, 80]
    angle = np.zeros(100)
    stats = pitch.bin_statistic_sonar(x, y, angle, bins=(x_edges, y_edges, 4),
                                      center=False)
    # row 0 is the [0, 10] band displayed at the top of the statsbomb pitch
    assert stats['statistic'][0, 0].sum() == 0
    assert stats['statistic'][1, 0].sum() == 100


def test_bin_statistic_positional_points():
    """ Test all 10 million points are included in the stats"""
    num_points = 10000000
    for pitch_type in valid:
        if pitch_type in size_varies:
            kwargs = {'pitch_length': 105, 'pitch_width': 68}
        else:
            kwargs = {}
        pitch = Pitch(pitch_type=pitch_type, label=True, axis=True, **kwargs)
        x = np.random.uniform(low=pitch.dim.pitch_extent[0], high=pitch.dim.pitch_extent[1],
                              size=num_points)
        y = np.random.uniform(low=pitch.dim.pitch_extent[2], high=pitch.dim.pitch_extent[3],
                              size=num_points)
        stats = pitch.bin_statistic_positional(x, y)
        assert np.array([stat["statistic"].sum() for stat in stats]).sum() == num_points

        
def test_bin_statistic_positional_yedge():
    """ Test all 8 million points (1 million * 8 edges) are included in the stats"""
    for pitch_type in valid:
        if pitch_type in size_varies:
            kwargs = {'pitch_length': 105, 'pitch_width': 68}
        else:
            kwargs = {}
        pitch = Pitch(pitch_type=pitch_type, label=True, axis=True, **kwargs)
        y = np.tile(pitch.dim.y_markings_sorted, 1000000)
        x = np.random.uniform(low=pitch.dim.pitch_extent[0], high=pitch.dim.pitch_extent[1],
                              size=y.size)
        stats = pitch.bin_statistic_positional(x, y)
        assert np.array([stat["statistic"].sum() for stat in stats]).sum() == 8000000
        

def test_bin_statistic_positional_xedge():
    """ Test all 9 million points (1 million * 9 edges) are included in the stats"""
    for pitch_type in valid:
        if pitch_type in size_varies:
            kwargs = {'pitch_length': 105, 'pitch_width': 68}
        else:
            kwargs = {}
        pitch = Pitch(pitch_type=pitch_type, label=True, axis=True, **kwargs)
        x = np.tile(pitch.dim.x_markings_sorted, 1000000)
        y = np.random.uniform(low=pitch.dim.pitch_extent[2], high=pitch.dim.pitch_extent[3],
                              size=x.size)
        stats = pitch.bin_statistic_positional(x, y)
        assert np.array([stat["statistic"].sum() for stat in stats]).sum() == 9000000
