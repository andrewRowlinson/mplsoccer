""" Test the Standardizer, which transforms points between different coordinate systems."""

import random

import numpy as np

from mplsoccer import Standardizer
from mplsoccer.dimensions import valid, size_varies, create_pitch_dims


def test_standardizer_multiple():
    """Shove 100k points through 1000 pitch transforms (ending at the original) 
    and check the result approximately equal the original values."""
    num_pitches = 1000
    num_points = 100000
    pitch_types = np.random.choice(valid, size=num_pitches)
    pitch_types_shift = np.roll(pitch_types, shift=-1)
    pitch_length = random.randint(a=90, b=115)
    pitch_width = random.randint(a=55, b=75)
    if pitch_types[0] in size_varies:
        dims = create_pitch_dims(pitch_types[0], pitch_width=pitch_width, pitch_length=pitch_length)
    else:
        dims = create_pitch_dims(pitch_types[0])
    x = np.random.uniform(low=dims.pitch_extent[0], high=dims.pitch_extent[1], size=num_points)
    y = np.random.uniform(low=dims.pitch_extent[2], high=dims.pitch_extent[3], size=num_points)
    x_copy = x.copy()
    y_copy = y.copy()
    # test
    kwargs = {'width_from': pitch_width, 'length_from': pitch_length,
              'width_to': pitch_width, 'length_to': pitch_length}
    for i in range(num_pitches):
        pitch_from = pitch_types[i]
        pitch_to = pitch_types_shift[i]
        standard = Standardizer(pitch_from=pitch_from, pitch_to=pitch_to, **kwargs)
        x, y = standard.transform(x, y)

    assert np.isclose(np.abs(x - x_copy).sum(), 0, atol=1e-05)
    assert np.isclose(np.abs(y - y_copy).sum(), 0, atol=1e-05)

    
def test_standardizer_reverse():
    """Shove 100k points through a transform and the reverse and check that
    the original values approximately match the reversed values (1000 times)."""
    num_pitches = 1000
    num_points = 100000
    for i in range(num_pitches):
        # from
        pitch_type_from = np.random.choice(valid)
        length_from = random.randint(a=90, b=115)
        width_from = random.randint(a=55, b=75)
        # to
        pitch_type_to = np.random.choice(valid)
        length_to = random.randint(a=90, b=115)
        width_to = random.randint(a=55, b=75)
        # pitches
        standard = Standardizer(pitch_from=pitch_type_from, pitch_to=pitch_type_to,
                                length_from=length_from, width_from=width_from,
                                length_to=length_to, width_to=width_to,)
        # random points
        x = np.random.uniform(low=standard.dim_from.pitch_extent[0],
                              high=standard.dim_from.pitch_extent[1],
                              size=num_points)
        y = np.random.uniform(low=standard.dim_from.pitch_extent[2],
                              high=standard.dim_from.pitch_extent[3],
                              size=num_points)
        x_std, y_std = standard.transform(x, y)
        x_reverse, y_reverse = standard.transform(x_std, y_std, reverse=True)
        assert np.isclose(np.abs(x - x_reverse).sum(), 0, atol=1e-05)
        assert np.isclose(np.abs(y - y_reverse).sum(), 0, atol=1e-05)
