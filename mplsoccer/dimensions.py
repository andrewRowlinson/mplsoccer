""" mplsoccer pitch dimensions.

Note that for tracab, uefa, metricasports, custom, and skillcorner the dimensions are in meters
(or centimeters for tracab). Real-life pictures are in actually measured in yards and
the meter conversions for distances (e.g. penalty_area_length) are slightly different,
but for the purposes of the visualisations the differences will be minimal.

Wycout dimensions are sourced from ggsoccer:
https://github.com/Torvaney/ggsoccer/blob/master/R/dimensions.R
Note, the goal width in ggsoccer (12 units) is different from socceraction (10 units)
(https://github.com/ML-KULeuven/socceraction/blob/master/socceraction/spadl/wyscout.py),
I am not sure which is correct, but I have gone for the goal width from ggsoccer (12 units).
In the previous versions of mplsoccer (up to 0.0.21), I used the socceraction goal width (10 units).
I changed it because it matters now for converting coordinates to a common dimension and wanted
to be consistent with ggsoccer.

Map of the pitch dimensions:


(left, top)     ____________________________________________________   (right, top)
               |                         |                         |       ^
               |                         |                         |       |
               |----------               |               ----------|       |              ^
               |         |               |               |         |       |              |
               |----     |               |               |     ----|       |      ^       |
               |    |    |       (center_length,         |     |   |       |      |       |
      ^    ~~~~|    |    |         center_width)         |     |   |~~~~   |width |six_   | penalty_
goal  |    |xxx|    | °  |penalty_       °       penalty_| °   |   |xxx|   |      |yard_  | area_
width |    |xxx|    |    |left           |          right|     |   |xxx|   |      |width  | width
      v    ~~~~|    |    |               |               |     |   |~~~~   |      |       |
               |____|    |               |               |     |___|       |      v       |
               |         |               |               |         |       |              |
               |---------                |               ----------|       |              v
               |                         |                         |       |
               |_________________________|_________________________|       v
(left, bottom)                                                                   (right, bottom)
                <-------------------------------------------------->
                                       length
                                     <-------->
                                   circle_diameter
               <--->
           six_yard_length
            <--><--------->
    goal_length penalty_area_length

Other dimensions:

aspect = This is used to stretch a square dimension pitch (e.g. 1x1 or 100x100)
         to a rectangular pitch shape.
         For wyscout and opta pitches. I use 68/105. For metricasports, it is
         calculated via the specified pitch_length divided by the pitch_width.
invert_y = If true, the origin starts at (left, top)
origin_center = If true, the origin starts at (center length, center width)
"""

from dataclasses import dataclass, InitVar

import numpy as np
from typing import Optional, Dict

from mplsoccer.formations import Formation, PositionLine4, PositionLine5, \
    PositionLine5WithSecondStriker, Coordinate

valid = ['statsbomb', 'tracab', 'opta', 'wyscout', 'uefa',
         'metricasports', 'custom', 'skillcorner', 'secondspectrum',
         'impect']
size_varies = ['tracab', 'metricasports', 'custom', 'skillcorner', 'secondspectrum']


@dataclass
class BaseDims:
    """ Base dataclass to hold pitch dimensions."""
    pitch_width: float
    pitch_length: float
    goal_width: float
    goal_length: float
    six_yard_width: float
    six_yard_length: float
    penalty_area_width: float
    penalty_area_length: float
    circle_diameter: float
    corner_diameter: float
    arc: Optional[float]
    invert_y: bool
    origin_center: bool
    # dimensions that can be calculated in __post_init__
    left: Optional[float] = None
    right: Optional[float] = None
    bottom: Optional[float] = None
    top: Optional[float] = None
    aspect: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    goal_bottom: Optional[float] = None
    goal_top: Optional[float] = None
    six_yard_left: Optional[float] = None
    six_yard_right: Optional[float] = None
    six_yard_bottom: Optional[float] = None
    six_yard_top: Optional[float] = None
    penalty_left: Optional[float] = None
    penalty_right: Optional[float] = None
    penalty_area_left: Optional[float] = None
    penalty_area_right: Optional[float] = None
    penalty_area_bottom: Optional[float] = None
    penalty_area_top: Optional[float] = None
    center_width: Optional[float] = None
    center_length: Optional[float] = None
    # defined in pitch_markings
    x_markings_sorted: Optional[np.array] = None
    y_markings_sorted: Optional[np.array] = None
    pitch_extent: Optional[np.array] = None
    # defined in juego_de_posicion
    positional_x: Optional[np.array] = None
    positional_y: Optional[np.array] = None
    # defined in stripes
    stripe_locations: Optional[np.array] = None
    # These positions do not include an extra line for the second striker line, at the moment
    # the only provider to use this position is StatsBomb for a few formations
    # we use these positions if there is no second striker so there is more
    # space for the visualization
    position_line4: PositionLine4 = None
    position_line5: PositionLine5 = None
    # these are additional positions including space for a second striker line.
    # The attacking midfielders are placed slightly backwards for these positions,
    # and for the five positions variation a second striker (SS) is placed between the
    # atttacking midfielder line and the forwards
    position_line4_with_ss: PositionLine4 = None
    position_line5_with_ss: PositionLine5WithSecondStriker = None
    formations: Dict[str, Dict[str, Coordinate]] = None

    def setup_dims(self):
        """ Run methods for the extra pitch dimensions."""
        self.pitch_markings()
        self.juego_de_posicion()
        self.stripes()
        self.create_positions_five_per_line()
        self.create_positions_four_per_line()
        self.create_positions_five_per_line_ss()
        self.create_positions_four_per_line_ss()
        self.create_formations()

    def pitch_markings(self):
        """ Create sorted pitch dimensions to enable standardization of coordinates.
        and pitch_extent which contains [xmin, xmax, ymin, ymax]."""
        self.x_markings_sorted = np.array([self.left, self.six_yard_left, self.penalty_left,
                                           self.penalty_area_left, self.center_length,
                                           self.penalty_area_right, self.penalty_right,
                                           self.six_yard_right, self.right])

        self.y_markings_sorted = np.array([self.bottom, self.penalty_area_bottom,
                                           self.six_yard_bottom, self.goal_bottom,
                                           self.goal_top, self.six_yard_top,
                                           self.penalty_area_top, self.top])
        if self.invert_y:
            self.y_markings_sorted = np.sort(self.y_markings_sorted)
            self.pitch_extent = np.array([self.left, self.right, self.top, self.bottom])
        else:
            self.pitch_extent = np.array([self.left, self.right, self.bottom, self.top])

    def juego_de_posicion(self):
        """ Create Juego de Posición pitch marking dimensions.
        See: https://spielverlagerung.com/2014/11/26/juego-de-posicion-a-short-explanation/"""
        self.positional_x = np.array([self.left, self.penalty_area_left,
                                      (self.penalty_area_left +
                                       (self.center_length - self.penalty_area_left) / 2.),
                                      self.center_length,
                                      (self.center_length +
                                       (self.penalty_area_right - self.center_length) / 2.),
                                      self.penalty_area_right, self.right])
        # for positional_y remove the goal posts (indices 3 & 4) from the pitch markings
        self.positional_y = self.y_markings_sorted[[0, 1, 2, 5, 6, 7]]

    def stripes(self):
        """ Create stripe dimensions."""
        stripe_pen_area = (self.penalty_area_length - self.six_yard_length) / 2.
        stripe_other = (self.length - 2 * self.six_yard_length - 6 * stripe_pen_area) / 10.
        stripe_locations = ([self.left] + [self.six_yard_length] + [stripe_pen_area] * 3 +
                            [stripe_other] * 10 + [stripe_pen_area] * 3 + [self.six_yard_length])
        self.stripe_locations = np.array(stripe_locations).cumsum()

    def penalty_box_dims(self):
        """ Create the penalty box dimensions. This is used to calculate the dimensions
         inside the penalty boxes for pitches with varying dimensions (width and length varies)."""
        self.penalty_right = self.right - self.penalty_left
        self.penalty_area_left = self.penalty_area_length
        self.penalty_area_right = self.right - self.penalty_area_length
        neg_if_inverted = - 1 / 2 if self.invert_y else 1 / 2
        self.penalty_area_bottom = self.center_width - (neg_if_inverted * self.penalty_area_width)
        self.penalty_area_top = self.center_width + (neg_if_inverted * self.penalty_area_width)
        self.six_yard_bottom = self.center_width - (neg_if_inverted * self.six_yard_width)
        self.six_yard_top = self.center_width + (neg_if_inverted * self.six_yard_width)
        self.goal_bottom = self.center_width - (neg_if_inverted * self.goal_width)
        self.goal_top = self.center_width + (neg_if_inverted * self.goal_width)
        self.six_yard_left = self.six_yard_length
        self.six_yard_right = self.right - self.six_yard_length

    def create_positions_five_per_line(self):
        """ Create player positions, using 5 positions per line (for example, RB, RCB, CB, LCB, LB).

        This can be used to evenly space players when you have 3 or 5 players per line.

        Used to translate a position e.g. CAM to the x,y coordinates."""
        x = np.linspace(self.penalty_left, self.penalty_right, 6)
        y = np.linspace(self.bottom, self.top, 11)[1::2]
        x_half = np.linspace(self.left + self.six_yard_length / 2,
                             self.center_length - self.six_yard_length, 6)
        x_half = np.repeat(np.expand_dims(x_half, axis=0), len(y), axis=0)
        x, y = np.meshgrid(x, y)

        x_flip = np.where(self.origin_center, self.center_length - x, self.right - x)
        x_half_flip = np.where(self.origin_center, self.center_length - x_half, self.right - x_half)
        y_flip = np.where(self.origin_center, self.center_width - y, max(self.top, self.bottom) - y)

        idx = [12, 1, 7, 13, 19, 25, 2, 8, 14, 20, 26, 3, 9, 15, 21, 27, 4, 10, 16, 22, 28, 11, 17,
               23]
        self.position_line5 = PositionLine5(
            *[Coordinate(*c) for c in list(zip(x.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist(),
                                               x_half.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_half_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist()
                                               ))]
        )

    def create_positions_four_per_line(self):
        """ Create player positions, using 4 poistions per line (for example, RB, RCB, LCB, LB).

        This can be used to evenly space players when you have 2 or 4 players per line.

        Used to translate a position e.g. CAM to the x,y coordinates."""
        x = np.linspace(self.penalty_left, self.penalty_right, 6)
        y = np.linspace(self.bottom, self.top, 9)[1:-1]
        x_half = np.linspace(self.left + self.six_yard_length / 2,
                             self.center_length - self.six_yard_length, 6)
        x_half = np.repeat(np.expand_dims(x_half, axis=0), len(y), axis=0)
        x, y = np.meshgrid(x, y)

        x_flip = np.where(self.origin_center, self.center_length - x, self.right - x)
        x_half_flip = np.where(self.origin_center, self.center_length - x_half, self.right - x_half)
        y_flip = np.where(self.origin_center, self.center_width - y, max(self.top, self.bottom) - y)

        idx = [18, 1, 13, 25, 37, 2, 14, 26, 38, 3, 15, 27, 39, 4, 16, 28, 40, 17, 29]
        self.position_line4 = PositionLine4(
            *[Coordinate(*c) for c in list(zip(x.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist(),
                                               x_half.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_half_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist()
                                               ))]
        )

    def create_positions_five_per_line_ss(self):
        """ Create player positions, using 5 positions per line (for example, RB, RCB, CB, LCB, LB).

        This can be used to evenly space players when you have 3 or 5 players per line.

        Used to translate a position e.g. CAM to the x,y coordinates."""
        x = np.linspace(self.penalty_left, self.penalty_right, 7)
        y = np.linspace(self.bottom, self.top, 11)[1::2]
        x_half = np.linspace(self.left + self.six_yard_length / 2,
                             self.center_length - self.six_yard_length, 7)
        x_half = np.repeat(np.expand_dims(x_half, axis=0), len(y), axis=0)
        x, y = np.meshgrid(x, y)

        x_flip = np.where(self.origin_center, self.center_length - x, self.right - x)
        x_half_flip = np.where(self.origin_center, self.center_length - x_half, self.right - x_half)
        y_flip = np.where(self.origin_center, self.center_width - y, max(self.top, self.bottom) - y)

        idx = [14, 1, 8, 15, 22, 29, 2, 9, 16, 23, 30, 3, 10, 17, 24, 31, 4, 11, 18, 25, 32, 13, 20,
               27, 19]
        self.position_line5_with_ss = PositionLine5WithSecondStriker(
            *[Coordinate(*c) for c in list(zip(x.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist(),
                                               x_half.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_half_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist()
                                               ))]
        )

    def create_positions_four_per_line_ss(self):
        """ Create player positions, using 4 poistions per line (for example, RB, RCB, LCB, LB).

        This can be used to evenly space players when you have 2 or 4 players per line.

        Used to translate a position e.g. CAM to the x,y coordinates."""
        x = np.linspace(self.penalty_left, self.penalty_right, 7)
        y = np.linspace(self.bottom, self.top, 9)[1:-1]
        x_half = np.linspace(self.left + self.six_yard_length / 2,
                             self.center_length - self.six_yard_length, 7)
        x_half = np.repeat(np.expand_dims(x_half, axis=0), len(y), axis=0)
        x, y = np.meshgrid(x, y)

        x_flip = np.where(self.origin_center, self.center_length - x, self.right - x)
        x_half_flip = np.where(self.origin_center, self.center_length - x_half, self.right - x_half)
        y_flip = np.where(self.origin_center, self.center_width - y, max(self.top, self.bottom) - y)

        idx = [21, 1, 15, 29, 43, 2, 16, 30, 44, 3, 17, 31, 45, 4, 18, 32, 46, 20, 34]
        self.position_line4_with_ss = PositionLine4(
            *[Coordinate(*c) for c in list(zip(x.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist(),
                                               x_half.ravel()[idx].tolist(),
                                               y.ravel()[idx].tolist(),
                                               x_half_flip.ravel()[idx].tolist(),
                                               y_flip.ravel()[idx].tolist()
                                               ))]
        )

    def create_formations(self):
        """ Create formations from the player positions."""
        formations = Formation(self.position_line4, self.position_line5,
                               self.position_line4_with_ss,
                               self.position_line5_with_ss)
        self.formations = formations.formations


@dataclass
class FixedDims(BaseDims):
    """ Dataclass holding the dimensions for pitches with fixed dimensions:
     'opta', 'wyscout', 'statsbomb' and 'uefa'."""

    def __post_init__(self):
        self.setup_dims()


@dataclass
class VariableCenterDims(BaseDims):
    """ Dataclass holding the dimensions for pitches where the origin is the center of the pitch:
    'tracab', 'skillcorner', 'impect', and 'secondspectrum'."""
    penalty_spot_distance: InitVar[float] = None

    def __post_init__(self, penalty_spot_distance):
        self.left = - self.pitch_length / 2
        self.right = - self.left
        self.bottom = - self.pitch_width / 2
        self.top = - self.bottom
        self.width = self.pitch_width
        self.length = self.pitch_length
        self.six_yard_left = self.left + self.six_yard_length
        self.six_yard_right = - self.six_yard_left
        self.penalty_left = self.left + penalty_spot_distance
        self.penalty_right = self.right - penalty_spot_distance
        self.penalty_area_left = self.left + self.penalty_area_length
        self.penalty_area_right = - self.penalty_area_left
        self.setup_dims()


@dataclass
class CustomDims(BaseDims):
    """ Dataclass holding the dimension for the custom pitch.
    This is a pitch where the dimensions (width/length) vary and the origin is (left, bottom)."""
    penalty_spot_distance: InitVar[float] = None

    def __post_init__(self, penalty_spot_distance):
        self.top = self.pitch_width
        self.right = self.pitch_length
        self.center_width = self.pitch_width / 2
        self.center_length = self.pitch_length / 2
        self.penalty_left = penalty_spot_distance
        self.penalty_box_dims()
        self.setup_dims()


@dataclass
class MetricasportsDims(BaseDims):
    """ Dataclass holding the dimensions for the 'metricasports' pitch."""
    penalty_spot_distance: InitVar[float] = None

    def __post_init__(self, penalty_spot_distance):
        self.aspect = self.pitch_width / self.pitch_length
        self.six_yard_width = round(self.six_yard_width / self.pitch_width, 4)
        self.six_yard_length = round(self.six_yard_length / self.pitch_length, 4)
        self.penalty_area_width = round(self.penalty_area_width / self.pitch_width, 4)
        self.penalty_area_length = round(self.penalty_area_length / self.pitch_length, 4)
        self.goal_length = round(self.goal_length / self.pitch_length, 4)
        self.goal_width = round(self.goal_width / self.pitch_width, 4)
        self.penalty_left = round(penalty_spot_distance / self.pitch_length, 4)
        self.penalty_box_dims()
        self.setup_dims()


def opta_dims():
    """ Create 'opta' dimensions."""
    return FixedDims(left=0., right=100., bottom=0., top=100., aspect=68 / 105,
                     width=100., length=100., pitch_width=68., pitch_length=105.,
                     goal_width=9.6, goal_length=1.9, goal_bottom=45.2, goal_top=54.8,
                     six_yard_width=26.4, six_yard_length=5.8, six_yard_left=5.8,
                     six_yard_right=94.2, six_yard_bottom=36.8, six_yard_top=63.2,
                     penalty_left=11.5, penalty_right=88.5,
                     penalty_area_width=57.8, penalty_area_length=17.0, penalty_area_left=17.,
                     penalty_area_right=83., penalty_area_bottom=21.1, penalty_area_top=78.9,
                     center_width=50., center_length=50., circle_diameter=17.68,
                     corner_diameter=1.94, arc=None, invert_y=False, origin_center=False)


def wyscout_dims():
    """ Create 'wyscout' dimensions."""
    return FixedDims(left=0., right=100., bottom=100., top=0., aspect=68 / 105,
                     width=100., length=100., pitch_width=68., pitch_length=105.,
                     goal_width=12., goal_length=1.9, goal_bottom=56., goal_top=44.,
                     six_yard_width=26., six_yard_length=6., six_yard_left=6.,
                     six_yard_right=94., six_yard_bottom=63., six_yard_top=37.,
                     penalty_left=10., penalty_right=90.,
                     penalty_area_width=62., penalty_area_length=16., penalty_area_left=16.,
                     penalty_area_right=84., penalty_area_bottom=81., penalty_area_top=19.,
                     center_width=50., center_length=50., circle_diameter=17.68,
                     corner_diameter=1.94, arc=None, invert_y=True, origin_center=False)


def uefa_dims():
    """ Create 'uefa dimensions."""
    return FixedDims(left=0., right=105., top=68., bottom=0., aspect=1.,
                     width=68., length=105., pitch_width=68., pitch_length=105.,
                     goal_width=7.32, goal_length=2., goal_bottom=30.34, goal_top=37.66,
                     six_yard_width=18.32, six_yard_length=5.5, six_yard_left=5.5,
                     six_yard_right=99.5, six_yard_bottom=24.84, six_yard_top=43.16,
                     penalty_left=11., penalty_right=94.,
                     penalty_area_width=40.32, penalty_area_length=16.5, penalty_area_left=16.5,
                     penalty_area_right=88.5, penalty_area_bottom=13.84, penalty_area_top=54.16,
                     center_width=34., center_length=52.5, circle_diameter=18.3, corner_diameter=2.,
                     arc=53.05, invert_y=False, origin_center=False)


def statsbomb_dims():
    """ Create 'statsbomb dimensions."""
    return FixedDims(left=0., right=120., bottom=80., top=0., aspect=1.,
                     width=80., length=120., pitch_width=80., pitch_length=120.,
                     goal_width=8., goal_length=2.4, goal_bottom=44., goal_top=36.,
                     six_yard_width=20., six_yard_length=6., six_yard_left=6.,
                     six_yard_right=114., six_yard_bottom=50., six_yard_top=30.,
                     penalty_left=12., penalty_right=108.,
                     penalty_area_width=44., penalty_area_length=18., penalty_area_left=18.,
                     penalty_area_right=102., penalty_area_bottom=62., penalty_area_top=18.,
                     center_width=40., center_length=60., circle_diameter=20.,
                     corner_diameter=2.186, arc=53.05, invert_y=True, origin_center=False)


def metricasports_dims(pitch_width, pitch_length):
    """ Create 'metricasports' dimensions."""
    return MetricasportsDims(top=0., bottom=1., left=0., right=1.,
                             pitch_width=pitch_width, pitch_length=pitch_length,
                             width=1., center_width=0.5, length=1., center_length=0.5,
                             six_yard_width=18.32, six_yard_length=5.5, penalty_spot_distance=11.,
                             penalty_area_width=40.32, penalty_area_length=16.5,
                             circle_diameter=18.3, corner_diameter=2., goal_length=2.,
                             goal_width=7.32, arc=None, invert_y=True, origin_center=False)


def skillcorner_secondspectrum_dims(pitch_width, pitch_length):
    """ Create dimensions for 'skillcorner' and 'secondspectrum' pitches."""
    return VariableCenterDims(aspect=1., pitch_width=pitch_width, pitch_length=pitch_length,
                              goal_width=7.32, goal_length=2., goal_bottom=-3.66, goal_top=3.66,
                              six_yard_width=18.32, six_yard_length=5.5, six_yard_bottom=-9.16,
                              six_yard_top=9.16, penalty_spot_distance=11.,
                              penalty_area_width=40.32, penalty_area_length=16.5,
                              penalty_area_bottom=-20.16, penalty_area_top=20.16, center_width=0.,
                              center_length=0., circle_diameter=18.3, corner_diameter=2., arc=53.05,
                              invert_y=False, origin_center=True)


def tracab_dims(pitch_width, pitch_length):
    """ Create 'tracab' dimensions."""
    return VariableCenterDims(aspect=1., pitch_width=pitch_width, pitch_length=pitch_length,
                              goal_width=732., goal_length=200., goal_bottom=-366., goal_top=366.,
                              six_yard_width=1832., six_yard_length=550., six_yard_bottom=-916.,
                              six_yard_top=916., penalty_spot_distance=1100.,
                              penalty_area_width=4032., penalty_area_length=1650.,
                              penalty_area_bottom=-2016., penalty_area_top=2016.,
                              center_width=0., center_length=0., circle_diameter=1830.,
                              corner_diameter=200., arc=53.05, invert_y=False, origin_center=True)


def impect_dims():
    """ Create 'impect' dimensions."""
    return VariableCenterDims(aspect=1., pitch_width=68, pitch_length=105,
                              goal_width=7.32, goal_length=2., goal_bottom=-3.66, goal_top=3.66,
                              six_yard_width=18.32, six_yard_length=5.5, six_yard_bottom=-9.16,
                              six_yard_top=9.16, penalty_spot_distance=11.,
                              penalty_area_width=40.32, penalty_area_length=16.5,
                              penalty_area_bottom=-20.16, penalty_area_top=20.16, center_width=0.,
                              center_length=0., circle_diameter=18.3, corner_diameter=2., arc=53.05,
                              invert_y=False, origin_center=True)


def custom_dims(pitch_width, pitch_length):
    """ Create 'custom' dimensions."""
    return CustomDims(bottom=0., left=0., aspect=1., width=pitch_width, length=pitch_length,
                      pitch_length=pitch_length, pitch_width=pitch_width, six_yard_width=18.32,
                      six_yard_length=5.5, penalty_area_width=40.32, penalty_spot_distance=11.,
                      penalty_area_length=16.5, circle_diameter=18.3, corner_diameter=2.,
                      goal_length=2., goal_width=7.32, arc=53.05, invert_y=False,
                      origin_center=False)


def create_pitch_dims(pitch_type, pitch_width=None, pitch_length=None):
    """ Create pitch dimensions.

    Parameters
    ----------
    pitch_type : str
        The pitch type used in the plot.
        The supported pitch types are: 'opta', 'statsbomb', 'tracab', 'impect',
        'wyscout', 'uefa', 'metricasports', 'custom', 'skillcorner' and 'secondspectrum'.
    pitch_length : float, default None
        The pitch length in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type.
    pitch_width : float, default None
        The pitch width in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type

    Returns
    -------
    dataclass
        A dataclass holding the pitch dimensions.
    """
    if pitch_type == 'opta':
        return opta_dims()
    if pitch_type == 'wyscout':
        return wyscout_dims()
    if pitch_type == 'uefa':
        return uefa_dims()
    if pitch_type == 'statsbomb':
        return statsbomb_dims()
    if pitch_type == 'metricasports':
        return metricasports_dims(pitch_width, pitch_length)
    if pitch_type in ['skillcorner', 'secondspectrum']:
        return skillcorner_secondspectrum_dims(pitch_width, pitch_length)
    if pitch_type == 'tracab':
        pitch_width = pitch_width * 100.
        pitch_length = pitch_length * 100.
        return tracab_dims(pitch_width, pitch_length)
    if pitch_type == 'impect':
        return impect_dims()
    return custom_dims(pitch_width, pitch_length)
