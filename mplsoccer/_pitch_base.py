""" Base class for drawing the soccer/ football pitch."""

import warnings
from abc import ABC, abstractmethod
from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

from mplsoccer import dimensions
from mplsoccer.cm import grass_cmap
from mplsoccer.utils import Standardizer

_BinnedStatisticResult = namedtuple('BinnedStatisticResult',
                                    ('statistic', 'x_grid', 'y_grid', 'cx', 'cy'))


class BasePitch(ABC):
    """ A class for plotting soccer / football pitches in Matplotlib

    Parameters
    ----------
    figsize : tuple of float, default Matplotlib figure size
        The figure size in inches by default uses rcParams["figure.figsize"].
    nrows, ncols : int, default 1
        Number of rows/columns of the subplot grid.
    pitch_type : str, default 'statsbomb'
        The pitch type used in the plot.
        The supported pitch types are: 'opta', 'statsbomb', 'tracab',
        'wyscout', 'uefa', 'metricasports', 'custom', 'skillcorner' and 'secondspectrum'.
    half : bool, default False
        Whether to display half of the pitch.
    pitch_color : any Matplotlib color, default None
        The background color for each Matplotlib axis.
         If None, defaults to rcParams["axes.facecolor"].
        To remove the background set to "None" or 'None'.
    line_color : any Matplotlib color, default None
        The line color for the pitch markings. If None, defaults to rcParams["grid.color"].
    line_zorder : float, default 0.9
        Set the zorder for the pitch lines (a matplotlib artist).
         Artists with lower zorder values are drawn first.
    linewidth : float, default 2
        The line width for the pitch markings.
    spot_scale : float, default 0.002
        The size of the penalty and center spots relative to the pitch length.
    stripe : bool, default False
        Whether to show pitch stripes.
    stripe_color : any Matplotlib color, default '#c2d59d'
        The color of the pitch stripes if stripe=True
    stripe_zorder : float, default 0.6
        Set the zorder for the stripes (a matplotlib artist).
         Artists with lower zorder values are drawn first.
    pad_left : float, default None
        Adjusts the left xlim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_right : float, default None
        Adjusts the right xlim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_bottom : float, default None
        Adjusts the bottom ylim of the axis. Positive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_top : float, default None
        Adjusts the top ylim of the axis. Positive values increase the plot area,
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
        see: https://matplotlib.org/3.2.1/gallery/lines_bars_and_markers/linestyles.html
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
    goal_alpha : float, default 0.7
        The transparency of the goal. This is used when the goal_type='box'
    axis : bool, default False
        Whether to include the axis: True means the axis is 'on' and False means the axis is 'off'.
    label : bool, default False
        Whether to include the axis labels.
    tick : bool, default False
        Whether to include the axis ticks.
    tight_layout : bool, default True
        Whether to use Matplotlib's tight layout.
    constrained_layout : bool, default False
        Whether to use Matplotlib's constrained layout.
    layout : deprecated, default None
        Layout is deprecated. Please use nrows and ncols arguments instead.
    view : deprecated, default None
        View is deprecated. Please use half=True or half=False arguements instead.
    orientation : deprecated, default None
        Orientation is deprecated. Please use the VerticalPitch class instead:
        from mplsoccer import VerticalPitch.
    """

    def __init__(self, figsize=None, nrows=1, ncols=1, pitch_type='statsbomb', half=False,
                 pitch_color=None, line_color=None, linewidth=2, line_zorder=0.9,
                 stripe=False, stripe_color='#c2d59d', stripe_zorder=0.6,
                 pad_left=None, pad_right=None, pad_bottom=None, pad_top=None,
                 positional=False, positional_zorder=0.8, positional_linewidth=None,
                 positional_linestyle=None, positional_color='#eadddd',
                 shade_middle=False, shade_color='#f2f2f2', shade_zorder=0.7,
                 pitch_length=None, pitch_width=None, goal_type='line', goal_alpha=0.7,
                 label=False, tick=False, axis=False,
                 tight_layout=True, constrained_layout=False, spot_scale=0.002,
                 layout=None, view=None, orientation=None):

        # initialize attributes
        self.figsize = figsize
        if self.figsize is None:
            self.figsize = rcParams['figure.figsize']
        self.nrows = nrows
        self.ncols = ncols
        self.pitch_type = pitch_type
        self.half = half
        self.pitch_color = pitch_color
        if self.pitch_color is None:
            self.pitch_color = rcParams['axes.facecolor']
        self.line_color = line_color
        if self.line_color is None:
            self.line_color = rcParams["grid.color"]
        self.linewidth = linewidth
        self.line_zorder = line_zorder
        self.stripe = stripe
        self.stripe_color = stripe_color
        self.stripe_zorder = stripe_zorder
        self.pad_left = pad_left
        self.pad_right = pad_right
        self.pad_bottom = pad_bottom
        self.pad_top = pad_top
        self.positional = positional
        self.positional_zorder = positional_zorder
        self.positional_linewidth = positional_linewidth
        if self.positional_linewidth is None:
            self.positional_linewidth = linewidth
        self.positional_linestyle = positional_linestyle
        self.positional_color = positional_color
        self.shade_middle = shade_middle
        self.shade_color = shade_color
        self.shade_zorder = shade_zorder
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.goal_type = goal_type
        self.goal_alpha = goal_alpha
        self.label = label
        self.tick = tick
        self.axis = axis
        self.tight_layout = tight_layout
        self.constrained_layout = constrained_layout
        self.spot_scale = spot_scale

        # other attributes for plotting circles - completed by
        # _init_circles_and_arcs / _init_circles_and_arcs_equal_aspect
        self.diameter1 = None
        self.diameter2 = None
        self.diameter_spot1 = None
        self.diameter_spot2 = None
        self.arc1_theta1 = None
        self.arc1_theta2 = None
        self.arc2_theta1 = None
        self.arc2_theta2 = None

        # the other attributes - completed by
        # set_extent in Pitch and VerticalPitch (inherit from BasePitch)
        self.extent = None
        self.visible_pitch = None
        self.ax_aspect = None
        self.kde_clip = None
        self.hexbin_gridsize = None
        self.hex_extent = None
        self.vertical = None
        self.reverse_cmap = None
        self.standardizer = Standardizer(pitch_from=pitch_type, width_from=pitch_width,
                                         length_from=pitch_length, pitch_to='uefa')

        # deprecation warnings
        if layout is not None:
            msg = "layout is deprecated. Please use nrows and ncols arguments instead."
            warnings.warn(msg)
        if view is not None:
            msg = "view is deprecated. Please use half=True or half=False arguements instead."
            warnings.warn(msg)
        if orientation is not None:
            msg = ("orientation is deprecated. Please use the VerticalPitch class instead: "
                   "from mplsoccer import VerticalPitch.")
            warnings.warn(msg)

        # data checks
        self._validation_checks()

        # set pitch dimensions
        self.dim = dimensions.create_pitch_dims(pitch_type, pitch_width, pitch_length)

        # if the padding is None set it to 4 on all sides, or 0.04 in the case of metricasports
        # for tracab multiply the padding by 100
        for pad in ['pad_left', 'pad_right', 'pad_bottom', 'pad_top']:
            if getattr(self, pad) is None:
                if pitch_type != 'metricasports':
                    setattr(self, pad, 4)
                else:
                    setattr(self, pad, 0.04)
            if pitch_type == 'tracab':
                setattr(self, pad, getattr(self, pad) * 100)

        # scale the padding where the aspect is not equal to one
        # this means that you can easily set the padding the same
        # all around the pitch (e.g. when using an Opta pitch)
        if self.dim.aspect != 1:
            self._scale_pad()

        # set the extent (takes into account padding)
        # [xleft, xright, ybottom, ytop] and the aspect ratio of the axis
        # also sets some attributes used for plotting hexbin/ arrows/ lines/ kdeplot/ stripes
        self._set_extent()

        # validate the padding
        self._validate_pad()

        # calculate locations of arcs and circles.
        # Where the pitch has an unequal aspect ratio we need to do this seperately
        if (self.dim.aspect == 1) and (self.pitch_type != 'metricasports'):
            self._init_circles_and_arcs()

        # set the positions of the goal posts
        self.goal_left = np.array([[self.dim.left, self.dim.goal_bottom],
                                   [self.dim.left, self.dim.goal_top]])
        self.goal_right = np.array([[self.dim.right, self.dim.goal_bottom],
                                    [self.dim.right, self.dim.goal_top]])

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'figsize={self.figsize!r}, nrows={self.nrows!r}, ncols={self.ncols!r}, '
                f'pitch_type={self.pitch_type!r}, half={self.half!r}, '
                f'pitch_color={self.pitch_color!r}, line_color={self.line_color!r}, '
                f'linewidth={self.linewidth!r}, line_zorder={self.line_zorder!r}, '
                f'stripe={self.stripe!r}, stripe_color={self.stripe_color!r}, '
                f'stripe_zorder={self.stripe_zorder!r}, '
                f'pad_left={self.pad_left!r}, pad_right={self.pad_right!r}, '
                f'pad_bottom={self.pad_bottom!r}, pad_top={self.pad_top!r}, '
                f'positional={self.positional!r}, positional_zorder={self.positional_zorder!r}, '
                f'positional_linewidth={self.positional_linewidth!r}, '
                f'positional_linestyle={self.positional_linestyle!r}, '
                f'positional_color={self.positional_color!r}, shade_middle={self.shade_middle!r}, '
                f'shade_color={self.shade_color!r}, shade_zorder={self.shade_zorder!r}, '
                f'pitch_length={self.pitch_length!r}, pitch_width={self.pitch_width!r}, '
                f'goal_type={self.goal_type!r}, goal_alpha={self.goal_alpha!r}, '
                f'label={self.label!r}, tick={self.tick!r}, axis={self.axis!r}, '
                f'tight_layout={self.tight_layout!r}, '
                f'constrained_layout={self.constrained_layout!r}, '
                f'spot_scale={self.spot_scale!r})')

    def _validation_checks(self):
        # pitch validation
        if self.pitch_type not in dimensions.valid:
            raise TypeError(f'Invalid argument: pitch_type should be in {dimensions.valid}')
        if (self.pitch_length is None or self.pitch_width is None) \
                and self.pitch_type in dimensions.size_varies:
            raise TypeError("Invalid argument: pitch_length and pitch_width must be specified.")
        if ((self.pitch_type not in dimensions.size_varies) and
                ((self.pitch_length is not None) or (self.pitch_width is not None))):
            msg = f"Pitch length and widths are only used for {dimensions.size_varies}" \
                  f" pitches and will be ignored"
            warnings.warn(msg)

        # type checks
        for attribute in ['axis', 'stripe', 'tick', 'label', 'shade_middle', 'tight_layout',
                          'half', 'positional', 'constrained_layout']:
            if not isinstance(getattr(self, attribute), bool):
                raise TypeError(f"Invalid argument: '{attribute}' should be bool.")
        valid_goal_type = ['line', 'box', 'circle']
        if self.goal_type not in valid_goal_type:
            raise TypeError(f'Invalid argument: goal_type should be in {valid_goal_type}')

        # axis/ label warnings
        if (self.axis is False) and self.label:
            warnings.warn("Labels will not be shown unless axis=True")
        if (self.axis is False) and self.tick:
            warnings.warn("Ticks will not be shown unless axis=True")

    def _validate_pad(self):
        # make sure padding not too large for the pitch
        if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.dim.length:
            raise ValueError("pad_left/pad_right too negative for pitch length")
        if abs(min(self.pad_top, 0) + min(self.pad_bottom, 0)) >= self.dim.width:
            raise ValueError("pad_top/pad_bottom too negative for pitch width")
        if self.half:
            if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.dim.length / 2:
                raise ValueError("pad_left/pad_right too negative for pitch length")

    def _init_circles_and_arcs(self):
        self.diameter1 = self.dim.circle_diameter
        self.diameter2 = self.dim.circle_diameter
        self.diameter_spot1 = self.spot_scale * self.dim.length * 2
        self.diameter_spot2 = self.spot_scale * self.dim.length * 2
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
                                                  self.dim.penalty_left) ** 2) ** 0.5) /
                                                radius_length ** 2)
        arc_pen_top1 = (self.dim.penalty_area_length, intersection)
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
        radius_spot = self.spot_scale * self.dim.pitch_length

        (self.diameter1,
         self.diameter2) = self._diameter_circle_equal_aspect(self.dim.center_length,
                                                              self.dim.center_width,
                                                              ax, radius_center)
        (self.diameter_spot1,
         self.diameter_spot2) = self._diameter_circle_equal_aspect(self.dim.penalty_left,
                                                                   self.dim.center_width,
                                                                   ax, radius_spot)
        self._arc_angles_equal_aspect(ax, radius_center)

    @staticmethod
    def _to_ax_coord(ax, coord_system, point):
        return coord_system.inverted().transform(ax.transData.transform_point(point))

    def draw(self, ax=None):
        """ Draws the specified soccer/ football pitch(es).
        If an ax is specified the pitch is drawn on an existing axis.

        Parameters
        ----------
        ax : matplotlib axis, default None
            A matplotlib.axes.Axes to draw the pitch on.
            If None is specified the pitch is plotted on a new figure.

        Returns
        -------
        If ax=None returns a matplotlib Figure and Axes.
        Else plotted on an existing axis and returns None.

        Examples
        --------
        # plot on new figure
        pitch = Pitch()
        fig, ax = pitch.draw()

        # plot on an existing figure
        fig, ax = plt.subplots()
        pitch = Pitch()
        pitch.draw(ax=ax)
        """
        if ax is None:
            fig, axs = self._setup_subplots()
            fig.set_tight_layout(self.tight_layout)
            for axis in axs.flat:
                self._draw_ax(axis)
            if axs.size == 1:
                axs = axs.item()
            return fig, axs

        self._draw_ax(ax)
        return None

    def _setup_subplots(self):
        fig, axs = plt.subplots(nrows=self.nrows, ncols=self.ncols, figsize=self.figsize,
                                constrained_layout=self.constrained_layout)
        if (self.nrows == 1) and (self.ncols == 1):
            axs = np.array([axs])
        return fig, axs

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

    def _set_axes(self, ax):
        # set axis on/off, and labels and ticks
        if self.axis is False:
            ax.spines['bottom'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
        ax.grid(False)
        ax.tick_params(top=self.tick, bottom=self.tick, left=self.tick, right=self.tick,
                       labelleft=self.label, labelbottom=self.label)
        # set limits and aspect
        ax.set_xlim(self.extent[0], self.extent[1])
        ax.set_ylim(self.extent[2], self.extent[3])
        ax.set_aspect(self.dim.aspect)

    def _set_background(self, ax):
        if self.pitch_color != 'grass':
            ax.set_facecolor(self.pitch_color)
            if self.stripe:
                self._plain_stripes(ax)
        else:
            pitch_color = np.random.normal(size=(1000, 1000))
            if self.stripe:
                pitch_color = self._draw_stripe_grass(pitch_color)
            ax.imshow(pitch_color, cmap=grass_cmap(), extent=self.extent, aspect=self.dim.aspect)

    def _plain_stripes(self, ax):
        for i in range(len(self.dim.stripe_locations) - 1):
            if i % 2 == 0:
                self._draw_stripe(ax, i)

    def _draw_pitch_markings(self, ax):
        rect_prop = {'fill': False, 'linewidth': self.linewidth,
                     'color': self.line_color, 'zorder': self.line_zorder}
        line_prop = {'linewidth': self.linewidth,
                     'color': self.line_color, 'zorder': self.line_zorder}
        self._draw_rectangle(ax, self.dim.left, self.dim.six_yard_bottom,
                             self.dim.six_yard_length, self.dim.six_yard_width, **rect_prop)
        self._draw_rectangle(ax, self.dim.six_yard_right, self.dim.six_yard_bottom,
                             self.dim.six_yard_length, self.dim.six_yard_width, **rect_prop)
        self._draw_rectangle(ax, self.dim.left, self.dim.penalty_area_bottom,
                             self.dim.penalty_area_length, self.dim.penalty_area_width, **rect_prop)
        self._draw_rectangle(ax, self.dim.penalty_area_right, self.dim.penalty_area_bottom,
                             self.dim.penalty_area_length, self.dim.penalty_area_width, **rect_prop)

        # pitch
        self._draw_rectangle(ax, self.dim.left, self.dim.bottom,
                             self.dim.length, self.dim.width, **rect_prop)
        # mid-line
        self._draw_line(ax, [self.dim.center_length, self.dim.center_length],
                        [self.dim.bottom, self.dim.top], **line_prop)
        # circles and arcs
        self._draw_circles_and_arcs(ax)

    def _draw_circles_and_arcs(self, ax):
        circ_prop = {'fill': False, 'linewidth': self.linewidth,
                     'color': self.line_color, 'zorder': self.line_zorder}

        # draw center cicrle and penalty area arcs
        self._draw_ellipse(ax, self.dim.center_length, self.dim.center_width,
                           self.diameter1, self.diameter2, **circ_prop)
        self._draw_arc(ax, self.dim.penalty_left, self.dim.center_width,
                       self.diameter1, self.diameter2,
                       theta1=self.arc1_theta1, theta2=self.arc1_theta2, **circ_prop)
        self._draw_arc(ax, self.dim.penalty_right, self.dim.center_width,
                       self.diameter1, self.diameter2,
                       theta1=self.arc2_theta1, theta2=self.arc2_theta2, **circ_prop)

        # draw center and penalty spots
        if self.spot_scale > 0:
            self._draw_ellipse(ax, self.dim.center_length, self.dim.center_width,
                               self.diameter_spot1, self.diameter_spot2,
                               color=self.line_color, zorder=self.line_zorder)
            self._draw_ellipse(ax, self.dim.penalty_left, self.dim.center_width,
                               self.diameter_spot1, self.diameter_spot2,
                               color=self.line_color, zorder=self.line_zorder)
            self._draw_ellipse(ax, self.dim.penalty_right, self.dim.center_width,
                               self.diameter_spot1, self.diameter_spot2,
                               color=self.line_color, zorder=self.line_zorder)

    def _draw_goals(self, ax):
        if self.goal_type == 'box':
            rect_prop = {'fill': False, 'linewidth': self.linewidth, 'color': self.line_color,
                         'alpha': self.goal_alpha, 'zorder': self.line_zorder}
            self._draw_rectangle(ax, self.dim.right, self.dim.goal_bottom,
                                 self.dim.goal_length, self.dim.goal_width, **rect_prop)
            self._draw_rectangle(ax, self.dim.left - self.dim.goal_length,
                                 self.dim.goal_bottom, self.dim.goal_length,
                                 self.dim.goal_width, **rect_prop)

        elif self.goal_type == 'line':
            goal_linewidth = self.linewidth * 2
            line_prop = {'linewidth': goal_linewidth, 'color': self.line_color,
                         'zorder': self.line_zorder}
            self._draw_line(ax, [self.dim.right, self.dim.right],
                            [self.dim.goal_top, self.dim.goal_bottom], **line_prop)
            self._draw_line(ax, [self.dim.left, self.dim.left],
                            [self.dim.goal_top, self.dim.goal_bottom], **line_prop)

        elif self.goal_type == 'circle':
            posts = [[self.dim.right, self.dim.goal_bottom], [self.dim.right, self.dim.goal_top],
                     [self.dim.left, self.dim.goal_bottom], [self.dim.left, self.dim.goal_top]]
            for post in posts:
                self._draw_ellipse(ax, post[0], post[1], self.diameter_spot1, self.diameter_spot2,
                                   color=self.line_color, zorder=self.line_zorder)

    def _draw_juego_de_posicion(self, ax):
        line_prop = {'linewidth': self.positional_linewidth, 'color': self.positional_color,
                     'linestyle': self.positional_linestyle, 'zorder': self.positional_zorder}
        # x lines for Juego de Posición
        for coord in self.dim.positional_x[1:-1]:
            self._draw_line(ax, [coord, coord], [self.dim.bottom, self.dim.top], **line_prop)
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
        shade_prop = {'fill': True, 'facecolor': self.shade_color, 'zorder': self.shade_zorder}
        self._draw_rectangle(ax, self.dim.positional_x[2], self.dim.bottom,
                             self.dim.positional_x[4] - self.dim.positional_x[2], self.dim.width,
                             **shade_prop)

    def grid(self, grid_height=0.7, space=0.05, bottom=0.1, left=None,
             figsize=None, nrows=None, ncols=None):
        """ A helper to create a grid of pitches in a specified location

        Parameters
        ----------
        grid_height : float, default 0.7
            The height of the grid area in fractions of the figure height.
            The default is the grid height is 70% of the figure height.
        space : float, default 0.05
            The total amount of the grid height reserved for spacing between axes.
            Expressed as a fraction of the grid height. The default is 5% of the grid height.
            The spacing across the grid width is automatically calculated to maintain even spacing.
        bottom : float, default 0.1
            The location of the bottom side of the grid in fractions of the figure height.
            The default means that the grid is located 10% in from the bottom of the figure.
        left : float, default None
            The location of the left hand side of the grid in fractions of the figure width.
            The default of None places the grid in the middle of the figure.
        figsize : tuple of float, default None
            The figure size in inches. The defalt of None uses the Pitch figsize.
        nrows, ncols : int, default None
            Number of rows/columns of the subplot grid.
            The default of None uses the Pitch ncols/ nrows.

        Returns
        -------
        fig : matplotlib.figure.Figure
        ax : a numpy array of matplotlib.axes.Axes
        """

        if figsize is None:
            figsize = self.figsize
        if ncols is None:
            ncols = self.ncols
        if nrows is None:
            nrows = self.nrows

        fig_aspect = figsize[0] / figsize[1]
        total_space_height = grid_height * space
        total_space_width = total_space_height * self.ax_aspect / fig_aspect

        if grid_height + bottom > 1:
            error_msg = ('The grid axes extends past the figure height. '
                         'Reduce one of the grid_height or space so the total is ≤ 1.')
            raise ValueError(error_msg)

        if nrows > 1:
            individual_space_height = total_space_height / (nrows - 1)
        else:
            total_space_height = 0
            individual_space_height = 0

        if ncols > 1:
            individual_space_width = total_space_width / (ncols - 1)
        else:
            individual_space_width = 0

        individual_pitch_height = (grid_height - total_space_height) / nrows
        individual_pitch_width = individual_pitch_height * self.ax_aspect / fig_aspect
        grid_width = (individual_pitch_width * ncols) + total_space_width

        if grid_width > 1:
            error_msg = ('The grid axes extends past the figure width. '
                         'Reduce one of the grid_height/ space, or '
                         'increase the figure width (the first number of the figsize).')
            raise ValueError(error_msg)

        if left is None:
            left = (1 - grid_width) / 2

        if grid_width + left > 1:
            error_msg = ('The grid axes extends past the figure width. '
                         'Reduce one of the grid_height/ space, or '
                         'increase the figure width (the first number of the figsize).')
            raise ValueError(error_msg)

        bottom_coordinates = np.tile(individual_space_height + individual_pitch_height,
                                     reps=nrows - 1).cumsum()
        bottom_coordinates = np.insert(bottom_coordinates, 0, 0.)
        bottom_coordinates = np.repeat(bottom_coordinates, ncols)
        bottom_coordinates = bottom_coordinates + bottom
        bottom_coordinates = bottom_coordinates[::-1]

        left_coordinates = np.tile(individual_space_width + individual_pitch_width,
                                   reps=ncols - 1).cumsum()
        left_coordinates = np.insert(left_coordinates, 0, 0.)
        left_coordinates = np.tile(left_coordinates, nrows)
        left_coordinates = left_coordinates + left

        fig = plt.figure(figsize=figsize)
        axs = []
        for idx, bottom_coord in enumerate(bottom_coordinates):
            axs.append(fig.add_axes((left_coordinates[idx], bottom_coord,
                                     individual_pitch_width, individual_pitch_height)))
            self.draw(ax=axs[idx])
        axs = np.squeeze(np.array(axs).reshape((nrows, ncols)))
        if axs.size == 1:
            axs = axs.item()

        return fig, axs

    def jointgrid(self, pitch_height=0.5, marginal_height=0.1, space_height=0,
                  left=0.1, bottom=0.1, ax_left=True, ax_top=True, ax_right=True, ax_bottom=False):
        """ Create a grid with a pitch at the center and axes on the
         top and right handside of the pitch.

        Parameters
        ----------
        pitch_height : float, default 0.5
            The height of the pitch in fractions of the figure height.
            The default is 50% of the figure.
        marginal_height : float, default 0.1
            The height of the marginal axes (either side of the pitch) in fractions
             of the figure height.
            The default is 10% of the figure.
        space_height : float, default 0
            The space between the pitch and the other axes in fractions of the figure height.
            The default is no space (note it will still look like there is space
            if the pitch has padding).
        left : float, default 0.1
            The location of the left hand side of the pitch in fractions of the figure width.
            The default means that the pitch is located 10% in from the left of the figure.
        bottom : float, default 0.1
            The location of the bottom side of the pitch in fractions of the figure height.
            The default means that the pitch is located 10% in from the bottom of the figure.
        ax_left, ax_top, ax_right : bool, default True
            Whether to include a Matplotlib Axes on the left/top/right side of the pitch.
        ax_bottom : bool, default False
            Whether to include a Matplotlib Axes on the bottom side of the pitch.
        Returns
        -------
        fig : matplotlib.figure.Figure
        ax : a 1d numpy array (length 5) of matplotlib.axes.Axes
            format = array([pitch, marginal axes in order left, top, right, bottom])
            if marginal axes is not present then axes replaced by None
        """
        if bottom + pitch_height + ((space_height + marginal_height) * ax_top) > 1.:
            error_msg = ('The jointplot axes extends past the figure height. '
                         'Reduce one of the pitch_height, space_height, marginal_height, '
                         'or bottom so the total is ≤ 1')
            raise ValueError(error_msg)

        if bottom - ((space_height + marginal_height) * ax_bottom) < 0.:
            error_msg = ('The jointplot axes extends past the figure bottom border. '
                         'Increase the bottom argument so it is more than the space_height '
                         '+ marginal_height.')
            raise ValueError(error_msg)

        fig_aspect = self.figsize[0] / self.figsize[1]
        pitch_width = pitch_height * self.ax_aspect / fig_aspect
        marginal_width = marginal_height / fig_aspect
        space_width = space_height / fig_aspect
        if left + pitch_width + ((space_width + marginal_width) * ax_right) > 1.:
            error_msg = ('The jointplot axes extends past the figure width. '
                         'Reduce one of the pitch_height, space_height, marginal_height, '
                         'or left.')
            raise ValueError(error_msg)

        if left - ((space_width + marginal_width) * ax_left) < 0.:
            error_msg = ('The jointplot axes extends past the figure left border. '
                         'Increase the left argument so there is space for the left marginal axis.')
            raise ValueError(error_msg)

        left_pad = (np.abs(self.visible_pitch - self.extent)[0] /
                    np.abs(self.extent[1] - self.extent[0]))
        right_pad = (np.abs(self.visible_pitch - self.extent)[1] /
                     np.abs(self.extent[1] - self.extent[0]))
        bottom_pad = (np.abs(self.visible_pitch - self.extent)[2] /
                      np.abs(self.extent[3] - self.extent[2]))
        top_pad = (np.abs(self.visible_pitch - self.extent)[3] /
                   np.abs(self.extent[3] - self.extent[2]))

        # add axes and draw pitch
        fig = plt.figure(figsize=self.figsize)

        # set axes limits
        x0, x1, y0, y1 = self.visible_pitch

        axs = []

        if ax_left:
            ax_0 = fig.add_axes((left - space_width - marginal_width,
                                 bottom + (bottom_pad * pitch_height),
                                 marginal_width,
                                 pitch_height - (bottom_pad + top_pad) * pitch_height))
            ax_0.set_ylim(y0, y1)
            ax_0.invert_xaxis()
            for spine in ['left', 'bottom', 'top']:
                ax_0.spines[spine].set_visible(False)
            axs.append(ax_0)
        else:
            axs.append(None)

        if ax_top:
            ax_1 = fig.add_axes((left + (left_pad * pitch_width),
                                 bottom + pitch_height + space_height,
                                 pitch_width - (left_pad + right_pad) * pitch_width,
                                 marginal_height))
            for spine in ['left', 'right', 'top']:
                ax_1.spines[spine].set_visible(False)
            ax_1.set_xlim(x0, x1)
            axs.append(ax_1)
        else:
            axs.append(None)

        if ax_right:
            ax_2 = fig.add_axes((left + pitch_width + space_width,
                                 bottom + (bottom_pad * pitch_height),
                                 marginal_width,
                                 pitch_height - (bottom_pad + top_pad) * pitch_height))
            ax_2.set_ylim(y0, y1)
            for spine in ['right', 'bottom', 'top']:
                ax_2.spines[spine].set_visible(False)
            axs.append(ax_2)
        else:
            axs.append(None)

        if ax_bottom:
            ax_3 = fig.add_axes((left + (left_pad * pitch_width),
                                 bottom - space_height - marginal_height,
                                 pitch_width - (left_pad + right_pad) * pitch_width,
                                 marginal_height))
            for spine in ['left', 'right', 'bottom']:
                ax_3.spines[spine].set_visible(False)
            ax_3.set_xlim(x0, x1)
            ax_3.invert_yaxis()
            axs.append(ax_3)
        else:
            axs.append(None)

        ax_pitch = fig.add_axes((left, bottom, pitch_width, pitch_height))
        self.draw(ax=ax_pitch)
        axs.insert(0, ax_pitch)

        for ax in axs[1:]:
            if ax is not None:
                plt.setp(ax.get_xticklabels(), visible=False)
                plt.setp(ax.get_yticklabels(), visible=False)
                ax.set_xticks([])
                ax.set_yticks([])

        axs = np.array(axs)

        return fig, axs

    # The methods below for drawing/ setting attributes for some of the pitch elements
    # are defined in pitch.py (Pitch/ VerticalPitch classes)
    # as they differ for horizontal/ vertical pitches
    @abstractmethod
    def _scale_pad(self):
        """ Implement a method to scale padding for equal aspect pitches."""

    @abstractmethod
    def _set_extent(self):
        """ Implement a method to set the pitch extents, stripe locations,
         and attributes to help plotting on differnt orientations."""

    @abstractmethod
    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        """ Implement a method to draw rectangles on a axes."""

    @abstractmethod
    def _draw_line(self, ax, x, y, **kwargs):
        """ Implement a method to draw lines on a axes."""

    @abstractmethod
    def _draw_ellipse(self, ax, x, y, width, height, **kwargs):
        """ Implement a method to draw ellipses (circles) on a axes."""

    @abstractmethod
    def _draw_arc(self, ax, x, y, width, height, theta1, theta2, **kwargs):
        """ Implement a method to draw arcs on a axes."""

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

    # The plotting methods below are defined in _pitch_plot.py (BasePlotPitch)
    # This module contains all the plotting methods
    @abstractmethod
    def plot(self, x, y, ax=None, **kwargs):
        """ Implement a wrapper for matplotlib.axes.Axes.plot."""

    @abstractmethod
    def scatter(self, x, y, rotation_degrees=None, marker=None, ax=None, **kwargs):
        """ Implement a wrapper for matplotlib.axes.Axes.scatter, while adding additional
        features for rotating markers and plotting footballs."""

    @abstractmethod
    def _reflect_2d(self, x, y, standardized=False):
        """ Implement a method to reflect points in the pitch sides."""

    @abstractmethod
    def kdeplot(self, x, y, ax=None, reflect=True, **kwargs):
        """ Implement a wrapper for seaborn.kdeplot."""

    @abstractmethod
    def hexbin(self, x, y, ax=None, **kwargs):
        """ Implement a wrapper for matplotlib.axes.Axes.hexbin."""

    @abstractmethod
    def polygon(self, verts, ax=None, **kwargs):
        """ Implement a method to add polygons to the pitch."""

    @abstractmethod
    def goal_angle(self, x, y, ax=None, goal='right', **kwargs):
        """ Implement a method to plot a triangle between a point and goal posts."""

    @abstractmethod
    def annotate(self, text, xy, xytext=None, ax=None, **kwargs):
        """ Implement a wrapper for matplotlib.axes.Axes.annotate."""

    @abstractmethod
    def bin_statistic(self, x, y, values=None, statistic='count', bins=(5, 4), standardized=False):
        """ Calculate 2d binned statistics for arbritary shaped bins."""

    @abstractmethod
    def heatmap(self, stats, ax=None, **kwargs):
        """ Implement drawing heatmaps for arbritary shaped bins."""

    @abstractmethod
    def bin_statistic_positional(self, x, y, values=None, positional='full', statistic='count'):
        """ Calculate the binned statistics for Juegos de posición zones."""

    @abstractmethod
    def heatmap_positional(self, stats, ax=None, **kwargs):
        """ Implement a heatmap for the Juegos de posición zones."""

    @abstractmethod
    def label_heatmap(self, stats, ax=None, **kwargs):
        """ Implement a heatmap labeller."""

    @abstractmethod
    def arrows(self, xstart, ystart, xend, yend, *args, ax=None, **kwargs):
        """ Implement a method to plot arrows."""

    @abstractmethod
    def lines(self, xstart, ystart, xend, yend, color=None, n_segments=100,
              comet=False, transparent=False, alpha_start=0.01,
              alpha_end=1, cmap=None, ax=None, **kwargs):
        """ Implement a method to plot lines."""

    @abstractmethod
    def voronoi(self, x, y, teams):
        """ Calculate the Voronoi polygons for each team."""

    @abstractmethod
    def calculate_angle_and_distance(self, xstart, ystart, xend, yend,
                                     standardized=False, degrees=False):
        """ Calculate the angle and distance from a start and end location."""

    @abstractmethod
    def flow(self, xstart, ystart, xend, yend, bins=(5, 4), arrow_type='same', arrow_length=5,
             color=None, ax=None, **kwargs):
        """ Implement a flow diagram with arrows showing the average direction and
        a heatmap showing the counts in each bin."""
