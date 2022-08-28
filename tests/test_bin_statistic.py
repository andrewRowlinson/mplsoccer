""" Test the bin statistic methods for binning data on the pitch."""

import numpy as np
import pandas as pd

from mplsoccer import Pitch
from mplsoccer.dimensions import valid, size_varies


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
