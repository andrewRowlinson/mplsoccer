""" Base class for drawing the soccer/ football pitch."""

import warnings
from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd
from matplotlib import rcParams

from .dimensions import create_pitch_dims, valid, size_varies
from .._pitch_base import BasePitch
from ..utils import validate_ax


class BasePitchBasketBall(BasePitch):
    """ A class for plotting soccer / football pitches in Matplotlib

    Parameters
    ----------
    pitch_type : str default 'nba'
        The pitch type used in the plot.
    half : bool, default False
        Whether to display half of the pitch.
    pitch_color : any Matplotlib color, default None
        The background color for each Matplotlib axis.
         If None, defaults to rcParams["axes.facecolor"].
        To remove the background set to "None" or 'None'.
    line_color : any Matplotlib color, default None
        The line color for the pitch markings. If None, defaults to rcParams["grid.color"].
    line_alpha : float, default 1
        The transparency of the pitch and the markings.
    linewidth : float, default 2
        The line width for the pitch markings.
    linestyle : str or typle
        Linestyle for the pitch lines:
        {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        see: https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    line_zorder : float, default 0.9
        Set the zorder for the pitch lines (a matplotlib artist).
        Artists with lower zorder values are drawn first.
    pad_left, pad_right : float, default None
        Adjusts the left xlim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_bottom, pad_top : float, default None
        Adjusts the bottom ylim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    shade_middle : bool, default False
         Whether to shade the middle third of the pitch.
    shade_color : any Matplotlib color, default '#f2f2f2'
        The fill color for the shading of the middle third of the pitch.
    shade_alpha : float, default 1
        The transparency of the shading of the middle third of the pitch.
    shade_zorder : float, default 0.7
        Set the zorder for the shading of the middle third of the pitch.
        Artists with lower zorder values are drawn first.
    pitch_length : float, default None
        The pitch length in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type.
    pitch_width : float, default None    
        The pitch width in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type
    axis : bool, default False
        Whether to set the axis spines to visible.
    label : bool, default False
        Whether to include the axis labels.
    tick : bool, default False
        Whether to include the axis ticks.
    """
    def __init__(self, pitch_type='nba', half=False,
                 pitch_color=None, line_color=None, line_alpha=1, linewidth=2,
                 linestyle=None, line_zorder=0.9,
                 pad_left=None, pad_right=None, pad_bottom=None, pad_top=None,
                 shade_middle=False, shade_color='#f2f2f2', shade_alpha=1, shade_zorder=0.7,
                 pitch_length=None, pitch_width=None,
                 axis=False, label=False, tick=False):

        # set pitch dimensions
        dim = create_pitch_dims(pitch_type)

        super().__init__(dim=dim,
                         pitch_type=pitch_type,
                         half=half,
                         pitch_color=pitch_color,
                         line_color=line_color, line_alpha=line_alpha, linewidth=linewidth, linestyle=linestyle, line_zorder=line_zorder,
                         pad_left=pad_left, pad_right=pad_right, pad_bottom=pad_bottom, pad_top=pad_top,
                         shade_middle=shade_middle, shade_color=shade_color, shade_alpha=shade_alpha, shade_zorder=shade_zorder,
                         pitch_length=pitch_length, pitch_width=pitch_width,
                         axis=axis, label=label, tick=tick)

        # data checks
        self._validation_checks()
        self.standardizer = None

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'pitch_type={self.pitch_type!r}, half={self.half!r}, '
                f'pitch_color={self.pitch_color!r}, line_color={self.line_color!r}, '
                f'linewidth={self.linewidth!r}, line_zorder={self.line_zorder!r}, '
                f'linestyle={self.linestyle!r}, '
                f'pad_left={self.pad_left!r}, pad_right={self.pad_right!r}, '
                f'pad_bottom={self.pad_bottom!r}, pad_top={self.pad_top!r}, '
                f'shade_middle={self.shade_middle!r}, '
                f'shade_color={self.shade_color!r}, shade_alpha={self.shade_alpha!r}, '
                f'shade_zorder={self.shade_zorder!r}, '
                f'pitch_length={self.pitch_length!r}, pitch_width={self.pitch_width!r}, '
                f'line_alpha={self.line_alpha!r}, label={self.label!r}, '
                f'tick={self.tick!r}, axis={self.axis!r})'
                )

    def _validation_checks(self):
        # pitch validation
        if self.pitch_type not in valid:
            raise TypeError(f'Invalid argument: pitch_type should be in {valid} '
                            'or a subclass of BaseSoccerDims.')
        if (self.pitch_length is None or self.pitch_width is None) \
                and self.pitch_type in size_varies:
            raise TypeError("Invalid argument: pitch_length and pitch_width must be specified.")
        if ((self.pitch_type not in size_varies) and
                ((self.pitch_length is not None) or (self.pitch_width is not None))):
            msg = f"Pitch length and widths are only used for {size_varies}" \
                  f" pitches and will be ignored"
            warnings.warn(msg)

        # type checks
        for attribute in ['axis', 'tick', 'label', 'shade_middle',
                          'half']:
            if not isinstance(getattr(self, attribute), bool):
                raise TypeError(f"Invalid argument: '{attribute}' should be bool.")
        # axis/ label warnings
        if (self.axis is False) and self.label:
            warnings.warn("Labels will not be shown unless axis=True")
        if (self.axis is False) and self.tick:
            warnings.warn("Ticks will not be shown unless axis=True")

    def _draw_ax(self, ax):
        self._set_axes(ax)
        self._set_background(ax)
        self._draw_pitch_markings(ax)

    def _set_background(self, ax):
        ax.set_facecolor(self.pitch_color)

    def _draw_pitch_markings(self, ax):
        # if we use rectangles here then the linestyle isn't consistent around the pitch
        # as sometimes the rectangles overlap with each other and the gaps between
        # lines can when they overlap can look like a solid line even with -. linestyles.
        line_prop = {'linewidth': self.linewidth, 'alpha': self.line_alpha,
                     'color': self.line_color, 'zorder': self.line_zorder,
                     'linestyle': self.linestyle,
                     }
        # main markings (outside of pitch and center line)
        xs_main = [self.dim.center_length, self.dim.center_length, self.dim.right,
                   self.dim.right, self.dim.left, self.dim.left, self.dim.center_length,
                   # key right
                   np.nan,
                   self.dim.right, self.dim.key_right,
                   self.dim.key_right, self.dim.right,
                   # key left
                   np.nan,
                   self.dim.left, self.dim.key_left,
                   self.dim.key_left, self.dim.left,
                   # three point lines left
                   np.nan,
                   self.dim.left, self.dim.three_point_left,
                   np.nan,
                   self.dim.left, self.dim.three_point_left,
                   # three point lines right
                   np.nan,
                   self.dim.right, self.dim.three_point_right,
                   np.nan,
                   self.dim.right, self.dim.three_point_right,
                   # hashes sideline left
                   np.nan,
                   self.dim.hash_sideline_left, self.dim.hash_sideline_left,
                   np.nan,
                   self.dim.hash_sideline_left, self.dim.hash_sideline_left,
                   # hashes sideline right
                   np.nan,
                   self.dim.hash_sideline_right, self.dim.hash_sideline_right,
                   np.nan,
                   self.dim.hash_sideline_right, self.dim.hash_sideline_right,
                   # substitution hashes
                   np.nan,
                   self.dim.hash_substitution_left, self.dim.hash_substitution_left,
                   np.nan,
                   self.dim.hash_substitution_right, self.dim.hash_substitution_right,
                   ]
        ys_main = [self.dim.bottom, self.dim.top, self.dim.top,
                   self.dim.bottom, self.dim.bottom, self.dim.top, self.dim.top,
                   # key right
                   np.nan,
                   self.dim.key_bottom, self.dim.key_bottom,
                   self.dim.key_top, self.dim.key_top,
                   # key left
                   np.nan,
                   self.dim.key_bottom, self.dim.key_bottom,
                   self.dim.key_top, self.dim.key_top,
                   # three point lines left
                   np.nan,
                   self.dim.three_point_bottom, self.dim.three_point_bottom,
                   np.nan,
                   self.dim.three_point_top, self.dim.three_point_top,
                   # three point lines right
                   np.nan,
                   self.dim.three_point_bottom, self.dim.three_point_bottom,
                   np.nan,
                   self.dim.three_point_top, self.dim.three_point_top,
                   # hashes sideline left
                   np.nan,
                   self.dim.bottom, self.dim.hash_sideline_bottom,
                   np.nan,
                   self.dim.top, self.dim.hash_sideline_top,
                   # hashes sideline right
                   np.nan,
                   self.dim.bottom, self.dim.hash_sideline_bottom,
                   np.nan,
                   self.dim.top, self.dim.hash_sideline_top,
                   # substitution hashes
                   np.nan,
                   self.dim.top, self.dim.hash_substitution_top,
                   np.nan,
                   self.dim.top, self.dim.hash_substitution_top,
                   ]
        self._draw_line(ax, xs_main, ys_main, **line_prop)


        circ_prop = {'fill': False, 'linewidth': self.linewidth, 'alpha': self.line_alpha,
                     'color': self.line_color, 'zorder': self.line_zorder,
                     'linestyle': self.linestyle,
                     }
        # center circle
        self._draw_ellipse(ax, self.dim.center_length, self.dim.center_width,
                           self.dim.center_circle_diameter_length,
                           self.dim.center_circle_diameter_width,
                           **circ_prop)
        # keys
        self._draw_arc(ax, self.dim.key_left, self.dim.center_width,
                       self.dim.center_circle_diameter_length,
                       self.dim.center_circle_diameter_width,
                       270, 90,
                       **circ_prop)
        self._draw_arc(ax, self.dim.key_right, self.dim.center_width,
                       self.dim.center_circle_diameter_length,
                       self.dim.center_circle_diameter_width,
                       90, 270,
                       **circ_prop)

        # theree point curved line
        self._draw_arc(ax, self.dim.hoop_left, self.dim.center_width,
                       self.dim.three_point_diameter_length,
                       self.dim.three_point_diameter_width,
                       self.dim.arc1_theta1, self.dim.arc1_theta2,
                       **circ_prop)
        self._draw_arc(ax, self.dim.hoop_right, self.dim.center_width,
                       self.dim.three_point_diameter_length,
                       self.dim.three_point_diameter_width,
                       self.dim.arc2_theta1, self.dim.arc2_theta2,
                       **circ_prop)

        # restricted area
        self._draw_arc(ax, self.dim.hoop_left, self.dim.center_width,
                       self.dim.restricted_area_diameter_length,
                       self.dim.restricted_area_diameter_width,
                       270, 90,
                       **circ_prop)
        self._draw_arc(ax, self.dim.hoop_right, self.dim.center_width,
                       self.dim.restricted_area_diameter_length,
                       self.dim.restricted_area_diameter_width,
                       90, 270,
                       **circ_prop)

        circ_prop2 = {'fill': False, 'linewidth': self.linewidth, 'alpha': self.line_alpha,
                     'color': self.line_color, 'zorder': self.line_zorder,
                     'linestyle': '--',
                     }
        self._draw_arc(ax, self.dim.key_left, self.dim.center_width,
                           self.dim.center_circle_diameter_length,
                           self.dim.center_circle_diameter_width,
                           90, 270,
                           **circ_prop2)
        self._draw_arc(ax, self.dim.key_right, self.dim.center_width,
                           self.dim.center_circle_diameter_length,
                           self.dim.center_circle_diameter_width,
                           270, 90,
                           **circ_prop2)

        # hoop
        hoop_prop = {'fill': False, 'linewidth': self.linewidth, 'alpha': self.line_alpha,
                     'color': self.line_color, 'zorder': self.line_zorder,
                     'linestyle': self.linestyle,
                     }
        self._draw_ellipse(ax, self.dim.hoop_left, self.dim.center_width,
                           self.dim.hoop_diameter_length,
                           self.dim.hoop_diameter_width,
                           **hoop_prop)
        self._draw_ellipse(ax, self.dim.hoop_right, self.dim.center_width,
                           self.dim.hoop_diameter_length,
                           self.dim.hoop_diameter_width,
                           **hoop_prop)

    # The methods below for drawing/ setting attributes for some pitch elements
    # are defined in pitch.py (Pitch/ VerticalPitch classes)
    # as they differ for horizontal/ vertical pitches
    @abstractmethod
    def _scale_pad(self):
        """ Implement a method to scale padding for equal aspect pitches."""

    @abstractmethod
    def _set_aspect(self):
        """ Implement a method to set the aspect attribute."""

    @abstractmethod
    def _set_extent(self):
        """ Implement a method to set the pitch extents, stripe locations,
         and attributes to help plot on different orientations."""

    @abstractmethod
    def _validate_pad(self):
        """ Implement a method to validate the pad values."""

    @abstractmethod
    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        """ Implement a method to draw rectangles on an axes."""

    @abstractmethod
    def _draw_centered_rectangle(self, ax, x, y, width, height, **kwargs):
        """ Implement a method to draw centered rectangles on an axes."""

    @abstractmethod
    def _draw_line(self, ax, x, y, **kwargs):
        """ Implement a method to draw lines on an axes."""

    @abstractmethod
    def _draw_ellipse(self, ax, x, y, width, height, **kwargs):
        """ Implement a method to draw ellipses (circles) on an axes."""

    @abstractmethod
    def _draw_arc(self, ax, x, y, width, height, theta1, theta2, **kwargs):
        """ Implement a method to draw arcs on an axes."""

    @staticmethod
    @abstractmethod
    def _reverse_if_vertical(x, y):
        """ Implement a method to reverse x and y coordinates if drawing on a vertical pitch."""

    @staticmethod
    @abstractmethod
    def _reverse_vertices_if_vertical(vert):
        """ Implement a method to reverse vertices if drawing on a vertical pitch."""

    @staticmethod
    @abstractmethod
    def _reverse_annotate_if_vertical(annotate):
        """ Implement a method to reverse annotations if drawing on a vertical pitch."""
