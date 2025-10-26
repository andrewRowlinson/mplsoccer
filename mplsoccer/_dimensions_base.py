""" Base pitch dimensions common to many sports."""

from dataclasses import dataclass, KW_ONLY
from typing import Optional

import numpy as np


@dataclass
class BaseDims:
    """ Base dataclass to hold pitch dimensions."""
    pitch_width: float
    pitch_length: float
    invert_y: bool
    origin_center: bool
    pad_default: float
    pad_multiplier: float
    aspect_equal: bool

    # dimensions that can be calculated in __post_init__
    _: KW_ONLY
    left: Optional[float] = None
    right: Optional[float] = None
    bottom: Optional[float] = None
    top: Optional[float] = None
    aspect: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    center_width: Optional[float] = None
    center_length: Optional[float] = None
    pitch_extent: Optional[np.array] = None
    standardized_extent: Optional[np.array] = None

    @staticmethod
    def intersection_arc(diameter_length, diameter_width, center_x, center_y, line_x):
        radius_length = diameter_length / 2
        radius_width = diameter_width / 2
        intersection = center_y - ((radius_width * radius_length *
                                  (radius_length ** 2 -
                                   (center_x - line_x) ** 2) ** 0.5) /
                                 radius_length ** 2)
        arc_intersection = (line_x, intersection)
        center_xy = (center_x, center_y)
        adjacent = arc_intersection[0] - center_xy[0]
        opposite = arc_intersection[1] - center_xy[1]
        return abs(np.degrees(np.arctan(opposite / adjacent)))
