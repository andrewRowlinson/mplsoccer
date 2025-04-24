""" mplsoccer basketball dimensions"""

from dataclasses import dataclass
from typing import Optional, Dict

import numpy as np

from .._dimensions_base import BaseDims

valid = ['nba']
size_varies = []


@dataclass
class BaseBasketBallDims(BaseDims):
    """ Base dataclass to hold court dimensions."""
    key_width: float
    key_length: float
    # dimensions that can be calculated in __post_init__
    key_left: Optional[float] = None
    key_right: Optional[float] = None
    key_bottom: Optional[float] = None
    key_top: Optional[float] = None

    def __post_init__(self):
        self.pitch_extent = np.array([self.left, self.right, self.top, self.bottom])
        self.standardized_extent = np.array([0, 28.6512, 0, 15.24])

@dataclass
class FixedDims(BaseBasketBallDims):
    """ Dataclass holding the dimensions for courts with fixed dimensions: 'nba'."""

def nba_dims():
    """ Create 'nba' dimensions."""
    return FixedDims(left=0., right=100., bottom=100., top=0., aspect=50/94,
                     width=100., length=100., pitch_width=15.24, pitch_length=28.6512,
                     key_width=32,
                     key_length=19/94*100,
                     key_left=19/94*100,
                     key_right=100-19/94*100,
                     key_bottom=34,
                     key_top=66,
                     center_width=50., center_length=50.,
                     invert_y=True, origin_center=False,
                     pad_default=4, pad_multiplier=1, aspect_equal=False,
                     )

def create_pitch_dims(pitch_type):
    """ Create pitch dimensions.

    Parameters
    ----------
    pitch_type : str
        The pitch type used in the plot. The supported pitch types are: 'nba'.

    Returns
    -------
    dataclass
        A dataclass holding the pitch dimensions.
    """
    return nba_dims()


