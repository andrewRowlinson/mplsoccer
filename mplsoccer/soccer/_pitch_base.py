""" Base class for drawing the soccer/ football pitch."""

import warnings
from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd

from mplsoccer.soccer.heatmap import bin_statistic_positional, heatmap_positional
from mplsoccer.soccer import dimensions
from mplsoccer.utils import validate_ax, copy_doc, Standardizer
from mplsoccer.cm import grass_cmap
from mplsoccer._pitch_base import BasePitch


class BasePitchSoccer(BasePitch):
    """ A class for plotting soccer / football pitches in Matplotlib

    Parameters
    ----------
    pitch_type : str or subclass of dimensions.BaseDims, default 'statsbomb'
        The pitch type used in the plot.
        The supported pitch types are: 'opta', 'statsbomb', 'tracab',
        'wyscout', 'uefa', 'metricasports', 'custom', 'skillcorner', 'secondspectrum'
        and 'impect'. Alternatively, you can pass a custom dimensions
        object by creating a subclass of dimensions.BaseDims.
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
    spot_scale : float, default 0.002
        The size of the penalty and center spots relative to the pitch length.
    spot_type : str, default 'circle'
        Whether to display the spots as a 'circle' or 'square'.
    stripe : bool, default False
        Whether to show pitch stripes.
    stripe_color : any Matplotlib color, default '#c2d59d'
        The color of the pitch stripes if stripe=True
    stripe_zorder : float, default 0.6
        Set the zorder for the stripes (a matplotlib artist).
         Artists with lower zorder values are drawn first.
    pad_left, pad_right : float, default None
        Adjusts the left xlim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_bottom, pad_top : float, default None
        Adjusts the bottom ylim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    positional : bool, default False
        Whether to draw Juego de Posición lines.
    positional_zorder : float, default 0.8
        Set the zorder for the Juego de Posición lines.
         Artists with lower zorder values are drawn first.
    positional_linewidth : float, default None
        Linewidth for the Juego de Posición lines.
        If None then this defaults to the same linewidth as the pitch lines (linewidth).
    positional_linestyle : str or tuple
        Linestyle for the Juego de Posición lines:
         {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        see: https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    positional_color : any Matplotlib color, default '#eadddd'
        The line color for the Juego de Posición lines.
    shade_middle : bool, default False
         Whether to shade the middle third of the pitch.
    shade_color : any Matplotlib color, default '#f2f2f2'
        The fill color for the shading of the middle third of the pitch.
    shade_zorder : float, default 0.7
        Set the zorder for the shading of the middle third of the pitch.
        Artists with lower zorder values are drawn first.
    pitch_length : float, default None
        The pitch length in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type.
    pitch_width : float, default None    
        The pitch width in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type
    goal_type : str, default 'line'
        Whether to display the goals as a 'line', 'box', 'circle' or to not display it at all (None)
    goal_alpha : float, default 1
        The transparency of the goal.
    goal_linestyle : str or typle
        Linestyle for the pitch lines:
        {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        see: https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    axis : bool, default False
        Whether to set the axis spines to visible.
    label : bool, default False
        Whether to include the axis labels.
    tick : bool, default False
        Whether to include the axis ticks.
    corner_arcs : bool, default False
        Whether to include corner arcs.
    """
    def __init__(self, pitch_type='statsbomb', half=False,
                 pitch_color=None, line_color=None, line_alpha=1, linewidth=2,
                 linestyle=None, line_zorder=0.9, spot_scale=0.002, spot_type='circle',
                 stripe=False, stripe_color='#c2d59d', stripe_zorder=0.6,
                 pad_left=None, pad_right=None, pad_bottom=None, pad_top=None,
                 positional=False, positional_zorder=0.8, positional_linewidth=None,
                 positional_linestyle=None, positional_color='#eadddd', positional_alpha=1,
                 shade_middle=False, shade_color='#f2f2f2', shade_alpha=1, shade_zorder=0.7,
                 pitch_length=None, pitch_width=None,
                 goal_type='line', goal_alpha=1, goal_linestyle=None,
                 axis=False, label=False, tick=False, corner_arcs=False):
        super().__init__(pitch_type=pitch_type,
                 half=half,
                 pitch_color=pitch_color,
                 line_color=line_color, line_alpha=line_alpha, linewidth=linewidth, linestyle=linestyle, line_zorder=line_zorder,
                 pad_left=pad_left, pad_right=pad_right, pad_bottom=pad_bottom, pad_top=pad_top,
                 shade_middle=shade_middle, shade_color=shade_color, shade_alpha=shade_alpha, shade_zorder=shade_zorder,
                 pitch_length=pitch_length, pitch_width=pitch_width,
                 axis=axis, label=label, tick=tick,
                 )
        self.spot_scale = spot_scale
        self.spot_type = spot_type
        self.stripe = stripe
        self.stripe_color = stripe_color
        self.stripe_zorder = stripe_zorder
        self.positional = positional
        self.positional_zorder = positional_zorder
        self.positional_linewidth = positional_linewidth
        if self.positional_linewidth is None:
            self.positional_linewidth = linewidth
        self.positional_linestyle = positional_linestyle
        self.positional_color = positional_color
        self.positional_alpha = positional_alpha
        self.goal_type = goal_type
        self.goal_alpha = goal_alpha
        self.goal_linestyle = goal_linestyle
        self.line_alpha = line_alpha
        self.corner_arcs = corner_arcs

        # other attributes for plotting circles - completed by
        # _init_circles_and_arcs / _init_circles_and_arcs_equal_aspect
        self.diameter1 = None
        self.diameter2 = None
        self.diameter_spot1 = None
        self.diameter_spot2 = None
        self.diameter_corner1 = None
        self.diameter_corner2 = None
        self.arc1_theta1 = None
        self.arc1_theta2 = None
        self.arc2_theta1 = None
        self.arc2_theta2 = None

        # data checks
        self._validation_checks()

        self.standardizer = Standardizer(pitch_from=pitch_type,
                                         width_from=pitch_width,
                                         length_from=pitch_length,
                                         pitch_to='custom',
                                         width_to=68 if pitch_width is None else pitch_width,
                                         length_to=105 if pitch_length is None else pitch_length)
        # set pitch dimensions
        if issubclass(type(pitch_type), dimensions.BaseDims):
            self.dim = pitch_type
        else:
            self.dim = dimensions.create_pitch_dims(pitch_type, pitch_width, pitch_length)

        # if the padding is None set it to 4 on all sides, or 0.04 in the case of metricasports
        # for tracab multiply the padding by 100
        for pad in ['pad_left', 'pad_right', 'pad_bottom', 'pad_top']:
            if getattr(self, pad) is None:
                setattr(self, pad, self.dim.pad_default)
            if self.dim.pad_multiplier != 1:
                setattr(self, pad, getattr(self, pad) * self.dim.pad_multiplier)
        self._set_aspect()

        # scale the padding where the aspect is not equal to one
        # this means that you can easily set the padding the same
        # all around the pitch (e.g. when using an Opta pitch)
        if not self.dim.aspect_equal:
            self._scale_pad()

        # set the extent (takes into account padding)
        # [xleft, xright, ybottom, ytop] and the aspect ratio of the axis
        # also sets some attributes used for plotting hexbin/ arrows/ lines/ kdeplot/ stripes
        self._set_extent()

        # validate the padding
        self._validate_pad()

        # calculate locations of arcs and circles.
        # Where the pitch has an unequal aspect ratio we need to calculate them separately
        if self.dim.aspect_equal:
            self._init_circles_and_arcs()

        # set the positions of the goal posts
        self.goal_left = np.array([[self.dim.left, self.dim.goal_bottom],
                                   [self.dim.left, self.dim.goal_top]])
        self.goal_right = np.array([[self.dim.right, self.dim.goal_bottom],
                                    [self.dim.right, self.dim.goal_top]])

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'pitch_type={self.pitch_type!r}, half={self.half!r}, '
                f'pitch_color={self.pitch_color!r}, line_color={self.line_color!r}, '
                f'linewidth={self.linewidth!r}, line_zorder={self.line_zorder!r}, '
                f'linestyle={self.linestyle!r}, '
                f'stripe={self.stripe!r}, stripe_color={self.stripe_color!r}, '
                f'stripe_zorder={self.stripe_zorder!r}, '
                f'pad_left={self.pad_left!r}, pad_right={self.pad_right!r}, '
                f'pad_bottom={self.pad_bottom!r}, pad_top={self.pad_top!r}, '
                f'positional={self.positional!r}, positional_zorder={self.positional_zorder!r}, '
                f'positional_linewidth={self.positional_linewidth!r}, '
                f'positional_linestyle={self.positional_linestyle!r}, '
                f'positional_color={self.positional_color!r}, '
                f'positional_alpha={self.positional_alpha!r}, '
                f'shade_middle={self.shade_middle!r}, '
                f'shade_color={self.shade_color!r}, shade_alpha={self.shade_alpha!r}, '
                f'shade_zorder={self.shade_zorder!r}, '
                f'pitch_length={self.pitch_length!r}, pitch_width={self.pitch_width!r}, '
                f'goal_type={self.goal_type!r}, goal_alpha={self.goal_alpha!r}, '
                f'line_alpha={self.line_alpha!r}, label={self.label!r}, '
                f'tick={self.tick!r}, axis={self.axis!r}, spot_scale={self.spot_scale!r}, '
                f'spot_type={self.spot_type!r}), '
                f'corner_arcs={self.corner_arcs!r})'
                )

    def _validation_checks(self):
        # pitch validation
        if (self.pitch_type not in dimensions.valid and
            not issubclass(type(self.pitch_type), dimensions.BaseDims)
           ):
            raise TypeError(f'Invalid argument: pitch_type should be in {dimensions.valid} '
                            'or a subclass of dimensions.BaseDims.')
        if (self.pitch_length is None or self.pitch_width is None) \
                and self.pitch_type in dimensions.size_varies:
            raise TypeError("Invalid argument: pitch_length and pitch_width must be specified.")
        if ((self.pitch_type not in dimensions.size_varies) and
                ((self.pitch_length is not None) or (self.pitch_width is not None))):
            msg = f"Pitch length and widths are only used for {dimensions.size_varies}" \
                  f" pitches and will be ignored"
            warnings.warn(msg)

        # type checks
        for attribute in ['axis', 'stripe', 'tick', 'label', 'shade_middle',
                          'half', 'positional']:
            if not isinstance(getattr(self, attribute), bool):
                raise TypeError(f"Invalid argument: '{attribute}' should be bool.")
        valid_goal_type = ['line', 'box', 'circle']
        if self.goal_type not in valid_goal_type:
            raise TypeError(f'Invalid argument: goal_type should be in {valid_goal_type}')

        valid_spot_type = ['circle', 'square']
        if self.spot_type not in valid_spot_type:
            raise TypeError(f'Invalid argument: spot_type should be in {valid_spot_type}')

        # axis/ label warnings
        if (self.axis is False) and self.label:
            warnings.warn("Labels will not be shown unless axis=True")
        if (self.axis is False) and self.tick:
            warnings.warn("Ticks will not be shown unless axis=True")

    def _init_circles_and_arcs(self):
        self.diameter1 = self.dim.circle_diameter
        self.diameter2 = self.dim.circle_diameter
        self.diameter_spot1 = self.spot_scale * self.dim.length * 2
        self.diameter_spot2 = self.spot_scale * self.dim.length * 2
        self.diameter_corner1 = self.dim.corner_diameter
        self.diameter_corner2 = self.dim.corner_diameter
        self.arc1_theta1 = -self.dim.arc
        self.arc1_theta2 = self.dim.arc
        self.arc2_theta1 = 180 - self.dim.arc
        self.arc2_theta2 = 180 + self.dim.arc

    def _diameter_circle_equal_aspect(self, x, y, ax, radius):
        # coordinates of center/ perimeter
        center = (x, y)
        circle_perimeter_length = (x + radius * self.dim.length / self.dim.pitch_length, y)
        circle_perimeter_width = (x, y + radius * self.dim.width / self.dim.pitch_width)
        # to ax coordinates
        center = self._to_ax_coord(ax, ax.transAxes, center)
        circle_perimeter_length = self._to_ax_coord(ax, ax.transAxes, circle_perimeter_length)
        circle_perimeter_width = self._to_ax_coord(ax, ax.transAxes, circle_perimeter_width)
        # calculate diameter
        diameter1 = (circle_perimeter_length[0] - center[0]) * 2
        diameter2 = (circle_perimeter_width[1] - center[1]) * 2
        return diameter1, diameter2

    def _arc_angles_equal_aspect(self, ax, radius):
        # calculate the point that the arc intersects the penalty area
        radius_length = radius * self.dim.length / self.dim.pitch_length
        radius_width = radius * self.dim.width / self.dim.pitch_width
        intersection = self.dim.center_width - ((radius_width * radius_length *
                                                 (radius_length ** 2 -
                                                  (self.dim.penalty_area_length -
                                                   self.dim.penalty_spot_distance) ** 2) ** 0.5) /
                                                radius_length ** 2)
        arc_pen_top1 = (self.dim.penalty_area_left, intersection)
        spot_xy = (self.dim.penalty_left, self.dim.center_width)
        # to ax coordinates
        arc_pen_top1 = self._to_ax_coord(ax, ax.transAxes, arc_pen_top1)
        spot_xy = self._to_ax_coord(ax, ax.transAxes, spot_xy)
        # work out the arc angles
        adjacent = arc_pen_top1[0] - spot_xy[0]
        opposite = spot_xy[1] - arc_pen_top1[1]
        self.arc1_theta2 = np.degrees(np.arctan(opposite / adjacent))
        self.arc1_theta1 = 360 - self.arc1_theta2
        self.arc2_theta1 = 180 - self.arc1_theta2
        self.arc2_theta2 = 180 + self.arc1_theta2

    def _init_circles_and_arcs_equal_aspect(self, ax):
        radius_center = self.dim.circle_diameter / 2
        radius_corner = self.dim.corner_diameter / 2
        radius_spot = self.spot_scale * self.dim.pitch_length

        (self.diameter1,
         self.diameter2) = self._diameter_circle_equal_aspect(self.dim.center_length,
                                                              self.dim.center_width,
                                                              ax, radius_center)
        (self.diameter_spot1,
         self.diameter_spot2) = self._diameter_circle_equal_aspect(self.dim.penalty_left,
                                                                   self.dim.center_width,
                                                                   ax, radius_spot)

        (self.diameter_corner1,
         self.diameter_corner2) = self._diameter_circle_equal_aspect(self.dim.left,
                                                                     self.dim.bottom,
                                                                     ax, radius_corner)

        self._arc_angles_equal_aspect(ax, radius_center)

    def _draw_ax(self, ax):
        if self.arc1_theta1 is None:
            self._init_circles_and_arcs_equal_aspect(ax)
        self._set_axes(ax)
        self._set_background(ax)
        self._draw_pitch_markings(ax)
        self._draw_goals(ax)
        if self.positional:
            self._draw_juego_de_posicion(ax)
        if self.shade_middle:
            self._draw_shade_middle(ax)

    def _set_background(self, ax):
        if self.pitch_color != 'grass':
            ax.set_facecolor(self.pitch_color)
            if self.stripe:
                self._plain_stripes(ax)
        else:
            pitch_color = np.random.normal(size=(1000, 1000))
            if self.stripe:
                pitch_color = self._draw_stripe_grass(pitch_color)
            ax.imshow(pitch_color, cmap=grass_cmap(), extent=self.extent, aspect=self.aspect)

    def _plain_stripes(self, ax):
        for i in range(len(self.dim.stripe_locations) - 1):
            if i % 2 == 0:
                self._draw_stripe(ax, i)

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
                   ]
        ys_main = [self.dim.bottom, self.dim.top, self.dim.top,
                   self.dim.bottom, self.dim.bottom, self.dim.top, self.dim.top,
                   ]
        self._draw_line(ax, xs_main, ys_main, **line_prop)
        # penalty boxs
        xs_pbox_right = [self.dim.right, self.dim.penalty_area_right,
                         self.dim.penalty_area_right, self.dim.right,
                         ]
        xs_pbox_left = [self.dim.left, self.dim.penalty_area_left,
                        self.dim.penalty_area_left, self.dim.left,
                        ]
        ys_pbox = [self.dim.penalty_area_bottom, self.dim.penalty_area_bottom,
                   self.dim.penalty_area_top, self.dim.penalty_area_top,
                   ]
        self._draw_line(ax, xs_pbox_right, ys_pbox, **line_prop)
        self._draw_line(ax, xs_pbox_left, ys_pbox, **line_prop)
        # six-yard box
        xs_sixbox_right = [self.dim.right, self.dim.six_yard_right,
                           self.dim.six_yard_right, self.dim.right,
                           ]
        xs_sixbox_left = [self.dim.left, self.dim.six_yard_left,
                          self.dim.six_yard_left, self.dim.left,
                          ]
        ys_sixbox = [self.dim.six_yard_bottom, self.dim.six_yard_bottom,
                     self.dim.six_yard_top, self.dim.six_yard_top,
                     ]
        self._draw_line(ax, xs_sixbox_right, ys_sixbox, **line_prop)
        self._draw_line(ax, xs_sixbox_left, ys_sixbox, **line_prop)
        self._draw_circles_and_arcs(ax)

    def _draw_circles_and_arcs(self, ax):
        circ_prop = {'fill': False, 'linewidth': self.linewidth, 'alpha': self.line_alpha,
                     'color': self.line_color, 'zorder': self.line_zorder,
                     'linestyle': self.linestyle,
                     }

        # draw center circle and penalty area arcs
        self._draw_ellipse(ax, self.dim.center_length, self.dim.center_width,
                           self.diameter1, self.diameter2, **circ_prop)
        self._draw_arc(ax, self.dim.penalty_left, self.dim.center_width,
                       self.diameter1, self.diameter2,
                       theta1=self.arc1_theta1, theta2=self.arc1_theta2, **circ_prop)
        self._draw_arc(ax, self.dim.penalty_right, self.dim.center_width,
                       self.diameter1, self.diameter2,
                       theta1=self.arc2_theta1, theta2=self.arc2_theta2, **circ_prop)

        if self.corner_arcs:
            if self.dim.invert_y:
                thetas = [(0, 90), (90, 180), (180, 270), (270, 360)]
            else:
                thetas = [(270, 360), (180, 270), (90, 180), (0, 90)]
            if self.vertical:
                thetas = np.flip(thetas, axis=0)
            corner_points = [(self.dim.left, self.dim.top),
                             (self.dim.right, self.dim.top),
                             (self.dim.right, self.dim.bottom),
                             (self.dim.left, self.dim.bottom)]
            for i, (x, y) in enumerate(corner_points):
                t1, t2 = thetas[i]
                self._draw_arc(ax, x, y, self.diameter_corner1, self.diameter_corner2,
                               theta1=t1, theta2=t2, **circ_prop)

        # draw center and penalty spots
        if self.spot_scale > 0:
            if self.spot_type == 'circle':
                spot_func = self._draw_ellipse
            else:
                spot_func = self._draw_centered_rectangle
            spot_func(ax, self.dim.center_length, self.dim.center_width,
                      self.diameter_spot1, self.diameter_spot2,
                      alpha=self.line_alpha, color=self.line_color,
                      zorder=self.line_zorder)
            spot_func(ax, self.dim.penalty_left, self.dim.center_width,
                      self.diameter_spot1, self.diameter_spot2,
                      alpha=self.line_alpha, color=self.line_color,
                      zorder=self.line_zorder)
            spot_func(ax, self.dim.penalty_right, self.dim.center_width,
                      self.diameter_spot1, self.diameter_spot2,
                      alpha=self.line_alpha, color=self.line_color,
                      zorder=self.line_zorder)

    def _draw_goals(self, ax):
        if self.goal_type == 'box':
            line_prop = {'linewidth': self.linewidth, 'color': self.line_color,
                         'alpha': self.goal_alpha, 'zorder': self.line_zorder,
                         'linestyle': self.goal_linestyle,
                         }
            # left goal
            xs_left = [self.dim.left, self.dim.left - self.dim.goal_length,
                       self.dim.left - self.dim.goal_length, self.dim.left,
                       ]
            ys_left = [self.dim.goal_bottom, self.dim.goal_bottom,
                       self.dim.goal_top, self.dim.goal_top,
                       ]

            self._draw_line(ax, xs_left, ys_left, **line_prop)
            # right goal
            xs_right = [self.dim.right, self.dim.right + self.dim.goal_length,
                        self.dim.right + self.dim.goal_length, self.dim.right,
                        ]
            ys_right = [self.dim.goal_bottom, self.dim.goal_bottom,
                        self.dim.goal_top, self.dim.goal_top,
                        ]
            self._draw_line(ax, xs_right, ys_right, **line_prop)

        elif self.goal_type == 'line':
            line_prop = {'linewidth': self.linewidth * 2, 'color': self.line_color,
                         'alpha': self.goal_alpha, 'zorder': self.line_zorder,
                         'linestyle': self.goal_linestyle,
                         }
            self._draw_line(ax, [self.dim.right, self.dim.right],
                            [self.dim.goal_top, self.dim.goal_bottom], **line_prop)
            self._draw_line(ax, [self.dim.left, self.dim.left],
                            [self.dim.goal_top, self.dim.goal_bottom], **line_prop)

        elif self.goal_type == 'circle':
            posts = [[self.dim.right, self.dim.goal_bottom], [self.dim.right, self.dim.goal_top],
                     [self.dim.left, self.dim.goal_bottom], [self.dim.left, self.dim.goal_top]]
            for post in posts:
                self._draw_ellipse(ax, post[0], post[1], self.diameter_spot1, self.diameter_spot2,
                                   alpha=self.goal_alpha, color=self.line_color,
                                   zorder=self.line_zorder)

    def _draw_juego_de_posicion(self, ax):
        line_prop = {'linewidth': self.positional_linewidth, 'color': self.positional_color,
                     'alpha': self.positional_alpha, 'linestyle': self.positional_linestyle,
                     'zorder': self.positional_zorder}
        # x lines for Juego de Posición
        # through lines
        self._draw_line(ax, [self.dim.positional_x[1], self.dim.positional_x[1]],
                        [self.dim.bottom, self.dim.top], **line_prop)
        self._draw_line(ax, [self.dim.positional_x[5], self.dim.positional_x[5]],
                        [self.dim.bottom, self.dim.top], **line_prop)
        # short lines
        for coord in self.dim.positional_x[2:5]:
            self._draw_line(ax, [coord, coord], [self.dim.bottom, self.dim.penalty_area_bottom],
                            **line_prop)
            self._draw_line(ax, [coord, coord], [self.dim.top, self.dim.penalty_area_top],
                            **line_prop)
        # y lines for Juego de Posición
        self._draw_line(ax, [self.dim.left, self.dim.right],
                        [self.dim.positional_y[1], self.dim.positional_y[1]], **line_prop)
        self._draw_line(ax, [self.dim.penalty_area_left, self.dim.penalty_area_right],
                        [self.dim.positional_y[2], self.dim.positional_y[2]], **line_prop)
        self._draw_line(ax, [self.dim.penalty_area_left, self.dim.penalty_area_right],
                        [self.dim.positional_y[3], self.dim.positional_y[3]], **line_prop)
        self._draw_line(ax, [self.dim.left, self.dim.right],
                        [self.dim.positional_y[4], self.dim.positional_y[4]], **line_prop)

    def _draw_shade_middle(self, ax):
        shade_prop = {'fill': True, 'facecolor': self.shade_color,
                      'alpha': self.shade_alpha,
                      'zorder': self.shade_zorder}
        self._draw_rectangle(ax, self.dim.positional_x[2], self.dim.bottom,
                             self.dim.positional_x[4] - self.dim.positional_x[2], self.dim.width,
                             **shade_prop)

    @property
    def formations(self) -> List[str]:
        """ Return a list of valid mplsoccer formations."""
        return list(self.dim.formations.keys())

    @property
    def formations_dataframe(self) -> pd.DataFrame:
        """ Return a dataframe of mplsoccer formations, positions and coordinates."""
        return pd.concat(
            [pd.DataFrame([formation.__dict__ for formation in self.dim.formations[key]])
                 .assign(formation=key)
                 .drop('location', axis='columns')
             for key in self.dim.formations])

    def get_positions(self, line=5, second_striker=True) -> pd.DataFrame:
        """ Get the player positions.

           Parameters
           ----------
           line : int, default 5
               Whether to have either five or four positions per line
           second_striker : bool, default True
               Whether to have a separate line for the second striker.
               If False, the attacking players are more evenly spaced.

           Returns
           -------
           positions : pd.DataFrame
           """

        if line not in (4, 5):
            raise ValueError('line must be either 4 or 5')
        if not isinstance(second_striker, bool):
            raise TypeError('second_striker must be boolean')
        if line == 5 and second_striker:
            return pd.DataFrame({key: value.__dict__ for key, value in
                                 self.dim.position_line5_with_ss.__dict__.items()}).T
        if line == 4 and second_striker:
            return pd.DataFrame({key: value.__dict__ for key, value in
                                 self.dim.position_line4_with_ss.__dict__.items()}).T
        if line == 5:
            return pd.DataFrame(
                {key: value.__dict__ for key, value in self.dim.position_line5.__dict__.items()}).T
        return pd.DataFrame(
            {key: value.__dict__ for key, value in self.dim.position_line4.__dict__.items()}).T

    def get_formation(self, formation):
        """ Get a formation.

           Parameters
           ----------
           formation : str
               The formation. For valid formations see the attribute formations
               For example, pitch = Pitch()
               print(pitch.formations)

           Returns
           -------
           formation : list[mplsoccer.formations.Position]
               A list of the mplsoccer dataclass for holding the positions and coordinates

           Examples
           --------
           >>> from mplsoccer import Pitch
           >>> pitch = Pitch()
           >>> formation = pitch.get_formation('442')
           """
        formation = formation.replace('-', '').replace('0', '')
        if formation not in self.formations:
            raise ValueError(
                f'Formation {formation} not supported.'
                f' Currently supported formations are: {self.formations}')
        return self.dim.formations[formation]

    def formation(self,
                  formation,
                  positions=None,
                  kind='scatter',
                  text=None,
                  image=None,
                  flip=False,
                  half=False,
                  height=None,
                  width=None,
                  aspect=None,
                  polar=False,
                  xoffset=None,
                  yoffset=None,
                  ax=None,
                  **kwargs):

        """ A method to plot formations

        Parameters
        ----------
        formation : str
            The formation to plot. For valid formations see the attribute formations
            For example, pitch = Pitch(); print(pitch.formations)
        positions : Collection
            A collection of position identifiers to map the xoffset, yoffset, image and text
            arguments to mplsoccer positions. Only necessary for pitch_type='statsbomb',
            kind='image', kind='text' or where one of the xoffset/yoffset is not None
            
            For StatsBomb pitches, the position identifiers are between 1 and 25.
            For Opta pitches, the position identifiers are between 1 and 11.
            For Wyscout pitches, the position identifiers are:
            'gk', 'rwb', 'rb5', 'rb', 'rcb3', 'rcb', 'cb', 'lcb', 'lcb3', 'lb', 'lb5',
            'lwb', 'rdmf', 'dmf', 'ldmf', 'rcmf3', 'rcmf', 'lcmf', 'lcmf3', 'rw',
            'ramf', 'amf', 'lamf', 'lw', 'ss', 'cf'.
            For other pitches, the position identifiers are: 
            'GK', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'RWB', 'LWB', 'RDM', 'CDM', 'LDM',
            'RM', 'RCM', 'CM', 'LCM', 'LM', 'RW', 'RAM', 'CAM', 'LAM', 'LW', 'RCF',
            'ST', 'LCF', 'SS'.
        kind : string, default 'scatter'
            The kind of plot to produce: 'scatter', 'text', 'image', 'pitch', or 'axes'.
        text : Collection[string], default None
            The text data to plot if kind = 'text'.
        image : Collection[array-like or PIL image], default None
            The image data to plot if kind = 'image'.
        flip : bool, default False
            Whether to flip the positions horizontally so the direction of attack is right to left.
        half : bool, default False
            Whether to fit the positions in one half of the pitch rather than the full pitch.
        height, width : float, default None
            The height/width of the inset axes, inset pitch, or inset image in
            the x/y data coordinates.
        aspect : float, default None
            The aspect ratio of the inset axes or inset image. You can specify a combination of
            height and aspect or width and aspect. This will make the axes visually have the
            given aspect ratio (length/width). For example, if you want an inset axes to appear
            square set aspect = 1. For polar plots, this is defaulted to 1.
        polar : bool, default False
            Whether the inset axes if a polar projection for kind='axes'.
        xoffset, yoffset : Collection[float] or float, default None
            Offsets for the positions for plotting the positions off-center.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to:

            - Axes.scatter for kind='scatter'
            - Axes.text for kind='text'
            - Axes.imshow for kind='image'
            - Temporarily amends the pitch attributes (e.g. line_color) for kind='pitch'
            - Axes.inset_axes for kind='axes'


        Returns
        -------
        positions : dict[str, axes], matplotlib.PathCollection or list[matplotlib.Text]

            - A dictionary of player positions (e.g. GK) and matplotlib axes
              for kind='image', kind='pitch' or kind='axes'.
              If the formation is a valid formation used by the data provider (pitch_type),
            the dictionary keys will be the data provider's position identifiers.
            - matplotlib.PathCollection for kind='scatter'.
            - A list of matplotlib.Text for kind='text'.


        Examples
        --------
        >>> from mplsoccer import VerticalPitch
        >>> pitch = VerticalPitch()
        >>> fig, ax = pitch.draw(figsize=(6.875, 10))
        >>> position_text = pitch.formation('442',
        ...                                 positions=[1, 2, 3, 5, 6, 9, 11, 12, 16, 22, 24],
        ...                                 text=['GK', 'RB', 'RCB', 'LCB', 'LB', 'RDM', 'LDM',
        ...                                 'RM', 'LM', 'RCF', 'LCF'],
        ...                                 ax=ax,
        ...                                 kind='text')

        >>> from mplsoccer import VerticalPitch
        >>> pitch = VerticalPitch()
        >>> fig, ax = pitch.draw(figsize=(6.875, 10))
        >>> position_scatter = pitch.formation('442',
        ...                                    positions=[1, 2, 3, 5, 6, 9, 11, 12, 16, 22, 24],
        ...                                    ax=ax,
        ...                                    kind='scatter')

        >>> from mplsoccer import VerticalPitch
        >>> from urllib.request import urlopen
        >>> from PIL import Image
        >>> image = Image.open(urlopen('https://upload.wikimedia.org/wikipedia/commons/b/b8/Messi_vs_Nigeria_2018.jpg'))
        >>> pitch = VerticalPitch()
        >>> fig, ax = pitch.draw(figsize=(6.875, 10))
        >>> position_image = pitch.formation('442',
        ...                                  positions=[1, 2, 3, 5, 6, 9, 11, 12, 16, 22, 24],
        ...                                  image=[image] * 11,
        ...                                  height=15,
        ...                                  ax=ax,
        ...                                  kind='image')

        >>> from mplsoccer import VerticalPitch
        >>> pitch = VerticalPitch()
        >>> fig, ax = pitch.draw(figsize=(6.875, 10))
        >>> position_image = pitch.formation('442',
        ...                                  positions=[1, 2, 3, 5, 6, 9, 11, 12, 16, 22, 24],
        ...                                  height=15,
        ...                                  ax=ax,
        ...                                  linewidth=1,
        ...                                  kind='pitch')

        >>> from mplsoccer import VerticalPitch
        >>> pitch = VerticalPitch()
        >>> fig, ax = pitch.draw(figsize=(6.875, 10))
        >>> position_image = pitch.formation('442',
        ...                                  positions=[1, 2, 3, 5, 6, 9, 11, 12, 16, 22, 24],
        ...                                  height=15,
        ...                                  aspect=1,
        ...                                  ax=ax,
        ...                                  kind='axes')
        """
        # get all the player coordinates and position names for a formation
        formation_positions = self.get_formation(formation)
        possible_position_list = [
            getattr(pos, self.pitch_type) if hasattr(pos, self.pitch_type) and
                                             getattr(pos, self.pitch_type) is not None
            else pos.name
            for pos in formation_positions]

        requires_positions = (
                xoffset is not None or
                yoffset is not None or
                self.pitch_type == 'statsbomb' or
                kind in ('text', 'image')
        )

        if xoffset is None:
            xoffset = 0
        if yoffset is None:
            yoffset = 0
        xoffset = np.ravel(xoffset)
        yoffset = np.ravel(yoffset)

        # validtions
        validate_ax(ax)
        if positions is None and requires_positions:
            raise TypeError("Missing 1 required argument: 'positions'. "
                            "Provide a collection of positions. For example, try a list of "
                            f"positions from {possible_position_list} for formation='{formation}' "
                            f"and pitch_type='{self.pitch_type}'."
                            )
        if positions is not None and len(positions) != len(formation_positions):
            raise ValueError(
                f'There are {len(formation_positions)} players in the formation, but you have '
                f'provided {len(positions)} positions. You need as many positions as players.'
            )
        if text is None and kind == 'text':
            raise TypeError("Missing 1 required argument: 'text'. "
                            "Text (kind='text') requires a collection of strings ('text') to plot."
                            )
        if text is not None and len(text) != len(formation_positions):
            raise ValueError(
                f'There are {len(formation_positions)} players in the formation, but you have '
                f'provided {len(text)} text strings for argument s. '
                f'You need as many text strings as players.'
            )
        if image is not None and len(image) != len(formation_positions):
            raise ValueError(
                f'There are {len(formation_positions)} players in the formation, but you have '
                f'provided {len(image)} images for argument image. '
                f'You need as many images as players.'
            )
        if image is None and kind == 'image':
            raise TypeError("Missing 1 required argument: 'image'. "
                            "Images (kind='image') require a collection of 'image' to plot."
                            )
        if not isinstance(half, bool):
            raise TypeError(f"Invalid 'half' argument: '{half}' should be bool.")
        if not isinstance(flip, bool):
            raise TypeError(f"Invalid 'flip' argument: '{flip}' should be bool.")

        # validate the offsets are the same length as the number of players
        if (((len(formation_positions) != xoffset.size) and xoffset.size > 1) or
                ((len(formation_positions) != yoffset.size) and yoffset.size > 1)):
            raise ValueError(
                f'There are {len(formation_positions)} players in the formation, but you have '
                f'provided {xoffset.size} xoffset and {yoffset.size} yoffset. '
                f'You need to supply either a single offset '
                f'for all players (e.g. xoffset=1) or as many offsets as players.'
            )

        # tile a single offset to all the players when a single number provided
        if xoffset.size == 1:
            xoffset = np.tile(xoffset, len(formation_positions))
        if yoffset.size == 1:
            yoffset = np.tile(yoffset, len(formation_positions))

        x = []
        y = []
        position_names = []
        sorted_image = []
        sorted_text = []
        sorted_xoffset = []
        sorted_yoffset = []

        for position in formation_positions:
            if half and flip:
                x.append(position.x_half_flip)
                y.append(position.y_half_flip)
            elif half:
                x.append(position.x_half)
                y.append(position.y_half)
            elif flip:
                x.append(position.x_flip)
                y.append(position.y_flip)
            else:
                x.append(position.x)
                y.append(position.y)

            if self.pitch_type == 'statsbomb':
                possible_positions = set(position.statsbomb).intersection(set(positions))
                if len(possible_positions) == 1:
                    pos = possible_positions.pop()
                else:
                    raise ValueError(
                        f'Cannot standardize to the {formation} formation. '
                        f'The following possible identifiers are returned by'
                        f' mplsoccer for the {position.name} position: {position.statsbomb}. '
                        f'These are either contained multiple times or no times in the list '
                        f'supplied to the positions keyword argument: {positions}.'
                    )
            elif self.pitch_type in ('wyscout', 'opta') and getattr(position,
                                                                    self.pitch_type) is not None:
                pos = getattr(position, self.pitch_type)
            else:
                pos = position.name
            position_names.append(pos)
            # find the index of the position in the original list supplied to the positions argument
            if requires_positions:
                if (np.array(positions) == pos).sum() == 0:
                    raise ValueError(
                        f"The position identifier {pos} returned by mplsoccer is not contained in "
                        f"the positions argument: {positions}. "
                        f"For example try a list of positions from:'{possible_position_list}'"
                    )
                position_idx = np.arange(len(positions))[np.array(positions) == pos].item()
                if text is not None:
                    sorted_text.append(text[position_idx])
                if image is not None:
                    sorted_image.append(image[position_idx])
                sorted_xoffset.append(xoffset[position_idx])
                sorted_yoffset.append(yoffset[position_idx])

        if requires_positions:
            x = np.asarray(x) + sorted_xoffset
            y = np.asarray(y) + sorted_yoffset

        if requires_positions and set(position_names) != set(positions):
            raise ValueError(
                f'The positions argument: {positions} does'
                f' not match the positions returned by mplsoccer: {position_names}.'
                f' You need to change the positions argument so it is consistent.'
            )

        if kind == 'scatter':
            return self.scatter(x, y, ax=ax, **kwargs)
        if kind == 'image':
            axes = {}
            for i in range(len(formation_positions)):
                axes[position_names[i]] = self.inset_image(x[i], y[i], sorted_image[i], width=width,
                                                           height=height, ax=ax, **kwargs)
            return axes
        if kind == 'pitch':
            axes = {}
            old_attr = {key: getattr(self, key) for key, value in kwargs.items() if
                        hasattr(self, key)}
            self._set_multiple_attributes(kwargs)
            for i in range(len(formation_positions)):
                axes[position_names[i]] = self.inset_axes(x=x[i], y=y[i], height=height,
                                                          width=width,
                                                          aspect=1 / self.ax_aspect, polar=False,
                                                          ax=ax)
                self.draw(axes[position_names[i]])
            self._set_multiple_attributes(old_attr)
            return axes
        if kind == 'axes':
            axes = {}
            for i in range(len(formation_positions)):
                axes[position_names[i]] = self.inset_axes(x=x[i], y=y[i], height=height,
                                                          width=width,
                                                          aspect=aspect, polar=polar, ax=ax,
                                                          **kwargs)
            return axes
        if kind == 'text':
            text = []
            for i in range(len(formation_positions)):
                text.append(self.text(x[i], y[i], sorted_text[i], ax=ax, **kwargs))
            return text
        raise NotImplementedError(f"kind = '{kind}' is not implemented. "
                                  "Valid arguments are 'scatter', 'image', 'axes', "
                                  "'pitch', or 'text'."
                                  )

    @copy_doc(bin_statistic_positional)
    def bin_statistic_positional(self, x, y, values=None, positional='full',
                                 statistic='count', normalize=False):
        return bin_statistic_positional(x, y, values=values,
                                        dim=self.dim, positional=positional,
                                        statistic=statistic, normalize=normalize)

    @copy_doc(heatmap_positional)
    def heatmap_positional(self, stats, ax=None, **kwargs):
        return heatmap_positional(stats, ax=ax, vertical=self.vertical, **kwargs)

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

    @abstractmethod
    def _draw_stripe(self, ax, i):
        """ Implement a method to draw stripes on a pitch (axvspan/axhspan)."""

    @abstractmethod
    def _draw_stripe_grass(self, pitch_color):
        """ Implement a method to draw stripes on a pitch.
        Increase the array values at stripe locations."""

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
