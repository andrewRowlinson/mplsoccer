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
    center_circle_diameter_length: float
    center_circle_diameter_width: float
    backboard_left: float
    backboard_right: float
    backboard_bottom: float
    backboard_top: float
    three_point_left: float
    three_point_right: float
    three_point_bottom: float
    three_point_top: float
    hoop_left: float
    hoop_right: float
    hoop_diameter_length: float
    hoop_diameter_width: float
    restricted_area_diameter_length: float
    restricted_area_diameter_width: float
    three_point_diameter_length: float
    three_point_diameter_width: float
    hash_sideline_left: float
    hash_sideline_right: float
    hash_sideline_bottom: float
    hash_sideline_top: float
    hash_substitution_top: float
    hash_substitution_left: float
    hash_substitution_right: float
    # dimensions that can be calculated in __post_init__
    key_left: Optional[float] = None
    key_right: Optional[float] = None
    key_bottom: Optional[float] = None
    key_top: Optional[float] = None
    arc1_theta1: Optional[float] = None
    arc1_theta2: Optional[float] = None
    arc2_theta1: Optional[float] = None
    arc2_theta2: Optional[float] = None

    def __post_init__(self):
        self.pitch_extent = np.array([self.left, self.right, self.top, self.bottom])
        self.standardized_extent = np.array([0, 28.6512, 0, 15.24])


        self.arc1_theta2 = self.intersection_arc(self.three_point_diameter_length,
                                                 self.three_point_diameter_width,
                                                 self.three_point_left,
                                                 self.center_width,
                                                 self.hoop_left)
        self.arc1_theta1 = 360 - self.arc1_theta2
        self.arc2_theta1 = 180 - self.arc1_theta2
        self.arc2_theta2 = 180 + self.arc1_theta2

@dataclass
class FixedDims(BaseBasketBallDims):
    """ Dataclass holding the dimensions for courts with fixed dimensions: 'nba'."""

def nba_dims():
    """ Create 'nba' dimensions."""
    return FixedDims(left=0., right=100., bottom=100., top=0.,
                     aspect=50/94,
                     width=100., length=100.,
                     pitch_width=50, pitch_length=94,
                     center_circle_diameter_length=12/94*100,
                     center_circle_diameter_width=12/50*100,
                     backboard_left=4/94*100,
                     backboard_right=100-4/94*100,
                     backboard_bottom=50+3/50*100,
                     backboard_top=50-3/50*100,
                     key_width=32, # 16/50*100
                     key_length=19/94*100,
                     key_left=19/94*100,
                     key_right=100-19/94*100,
                     three_point_left=14/94*100,
                     three_point_right=100-14/94*100,
                     three_point_bottom=94, #100-3/50*100,
                     three_point_top=6, # 3/50*100,
                     hoop_left=5.25/94*100,
                     hoop_right=100-5.25/94*100,
                     hoop_diameter_length=0.75*2/94*100,
                     hoop_diameter_width=0.75*2/50*100,
                     restricted_area_diameter_length=4*2/94*100,
                     restricted_area_diameter_width=4*2/50*100,
                     three_point_diameter_length=23.75*2/94*100,
                     three_point_diameter_width=23.75*2/50*100,
                     hash_sideline_left=28/94*100,
                     hash_sideline_right=100-28/94*100,
                     hash_sideline_bottom=94, #100-3/50*100,
                     hash_sideline_top=6, # 3/50*100,
                     hash_substitution_top=-4/50*100,
                     hash_substitution_left=50-4/94*100,
                     hash_substitution_right=50+4/94*100,
                     key_bottom=66, # 50 + key_width/2
                     key_top=34, # 50 - key_width/2
                     center_width=50.,
                     center_length=50.,
                     invert_y=True,
                     origin_center=False,
                     pad_default=10, pad_multiplier=1, aspect_equal=False,
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


