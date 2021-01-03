import warnings
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.markers as mmarkers
import numpy as np
import seaborn as sns
from scipy.stats import binned_statistic_2d, circmean
from scipy.spatial import Voronoi
from collections import namedtuple

from mplsoccer import dimensions
from mplsoccer.utils import validate_ax
from mplsoccer.cm import grass_cmap
from mplsoccer.scatterutils import _mscatter, scatter_football

_BinnedStatisticResult = namedtuple('BinnedStatisticResult',
                                    ('statistic', 'x_grid', 'y_grid', 'cx', 'cy'))


class BasePitch(ABC):
    """ A class for plotting soccer / football pitches in Matplotlib

    Parameters
    ----------
    figsize : tuple of float, default Matplotlib figure size
        The figure size in inches by default.
    nrows, ncols : int, default 1
        Number of rows/columns of the subplot grid.
    pitch_type : str, default 'statsbomb'
        The pitch type used in the plot.
        The supported pitch types are: 'opta', 'statsbomb', 'tracab',
        'wyscout', 'uefa', 'metricasports', 'custom'.
    half : bool, default False
        Whether to display half of the pitch.
    pitch_color : any Matplotlib color, default None
        The background color for each Matplotlib axis. If None, defaults to rcParams["axes.facecolor"].
        To remove the background set to "None" or 'None'.
    line_color : any Matplotlib color, default None
        The line color for the pitch markings. If None, defaults to rcParams["grid.color"].
    line_zorder : float, default 0.9
        Set the zorder for the pitch lines (a matplotlib artist). Artists with lower zorder values are drawn first.
    linewidth : float, default 2
        The line width for the pitch markings.
    spot_scale : float, default 0.002
        The size of the penalty and center spots relative to the pitch length.
    stripe : bool, default False
        Whether to show pitch stripes.
    stripe_color : any Matplotlib color, default '#c2d59d'
        The color of the pitch stripes if stripe=True
    stripe_zorder : float, default 0.6
        Set the zorder for the stripes (a matplotlib artist). Artists with lower zorder values are drawn first.
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
        Set the zorder for the Juego de Posición lines. Artists with lower zorder values are drawn first.
    positional_linewidth : float, default None
        Linewidth for the Juego de Posición lines.
        If None then this defaults to the same linewidth as the pitch lines (linewidth).
    positional_linestyle : str or tuple
        Linestyle for the Juego de Posición lines: {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
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
        The pitch length in meters. Only used for the 'tracab' and 'metricasports' pitch_type.
    pitch_width : float, default None
        The pitch width in meters. Only used for the 'tracab' and 'metricasports' pitch type.
    goal_type : str, default 'line'
        Whether to display the goals as a 'line', a 'box' or to not display it at all (None)
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
    """

    def __init__(self, figsize=None, nrows=1, ncols=1, pitch_type='statsbomb', half=False,
                 pitch_color=None, line_color=None, linewidth=2, line_zorder=0.9, stripe=False,
                 stripe_color='#c2d59d', stripe_zorder=0.6, pad_left=None, pad_right=None, pad_bottom=None,
                 pad_top=None,
                 positional=False, positional_zorder=0.8, positional_linewidth=None,
                 positional_linestyle=None, positional_color='#eadddd',
                 shade_middle=False, shade_color='#f2f2f2', shade_zorder=0.7,
                 pitch_length=None, pitch_width=None, goal_type='line', label=False, tick=False, axis=False,
                 tight_layout=True, constrained_layout=False, spot_scale=0.002):

        # validate the pitch_type and for pitches where the size varies check they have a pitch_length/width
        if pitch_type not in dimensions.valid:
            raise TypeError(f'Invalid argument: pitch_type should be in {dimensions.valid}')
        if (pitch_length is None or pitch_width is None) and pitch_type in dimensions.size_varies:
            raise TypeError("Invalid argument: pitch_length and pitch_width must be specified.")
        if ((pitch_type not in dimensions.size_varies) and
                ((pitch_length is not None) or (pitch_width is not None))):
            warnings.warn(
                f"Pitch length and widths are only used for {dimensions.size_varies} pitches and will be ignored")

        self.axes = None
        self.fig = None
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
        self.label = label
        self.tick = tick
        self.axis = axis
        self.tight_layout = tight_layout
        self.constrained_layout = constrained_layout
        self.spot_scale = spot_scale

        # if the padding is None set it to 4 on all sides, or 0.04 in the case of metricasports
        for pad in ['pad_left', 'pad_right', 'pad_bottom', 'pad_top']:
            if getattr(self, pad) is None:
                if pitch_type != 'metricasports':
                    setattr(self, pad, 4)
                else:
                    setattr(self, pad, 0.04)

        # set the dimensions for individual pitch_type(s)
        if pitch_type == 'opta':
            self._set_dimensions(dimensions.opta)
            self.pitch_length = 105
            self.pitch_width = 68

        elif pitch_type == 'wyscout':
            self._set_dimensions(dimensions.wyscout)
            self.pitch_length = 105
            self.pitch_width = 68

        elif pitch_type == 'statsbomb':
            self._set_dimensions(dimensions.statsbomb)
            self.pitch_length = self.length
            self.pitch_width = self.width

        elif pitch_type == 'uefa':
            self._set_dimensions(dimensions.uefa)
            self.pitch_length = self.length
            self.pitch_width = self.width

        elif pitch_type == 'tracab':
            self._set_dimensions(dimensions.tracab)
            self.top = pitch_width / 2 * 100
            self.bottom = -(pitch_width / 2) * 100
            self.left = -(pitch_length / 2) * 100
            self.right = (pitch_length / 2) * 100
            self.width = pitch_width * 100
            self.length = pitch_length * 100
            self.left_penalty = self.left + 1100
            self.right_penalty = self.right - 1100
            self.pad_left = self.pad_left * 100
            self.pad_bottom = self.pad_bottom * 100
            self.pad_right = self.pad_right * 100
            self.pad_top = self.pad_top * 100

        elif pitch_type == 'metricasports':
            # note do not scale the circle_size as scaled seperately for the width/ length when drawing circle/arcs
            self._set_dimensions(dimensions.metricasports)
            self.aspect = self.pitch_width / self.pitch_length
            self.six_yard_width = round(self.six_yard_width / self.pitch_width, 4)
            self.six_yard_length = round(self.six_yard_length / self.pitch_length, 4)
            self.six_yard_from_side = (self.width - self.six_yard_width) / 2
            self.penalty_area_width = round(self.penalty_area_width / self.pitch_width, 4)
            self.penalty_area_length = round(self.penalty_area_length / self.pitch_length, 4)
            self.penalty_area_from_side = (self.width - self.penalty_area_width) / 2
            self.left_penalty = round(self.left_penalty / self.pitch_length, 4)
            self.right_penalty = self.right - self.left_penalty
            self.goal_depth = round(self.goal_depth / self.pitch_length, 4)
            self.goal_width = round(self.goal_width / self.pitch_width, 4)
            self.goal_post = self.center_width - round(self.goal_post / self.pitch_width, 4)

        elif pitch_type == 'custom':
            self._set_dimensions(dimensions.custom)
            self.right = self.pitch_length
            self.top = self.pitch_width
            self.length = self.pitch_length
            self.width = self.pitch_width
            self.center_length = self.pitch_length / 2
            self.center_width = self.pitch_width / 2
            self.six_yard_from_side = self.center_width - self.six_yard_width / 2
            self.penalty_area_from_side = self.center_width - self.penalty_area_width / 2
            self.right_penalty = self.right - self.left_penalty
            self.goal_post = self.center_width - self.goal_width / 2

        elif pitch_type in ['skillcorner', 'secondspectrum']:
            self._set_dimensions(dimensions.skillcorner_secondspectrum)
            self.top = pitch_width / 2
            self.bottom = -(pitch_width / 2)
            self.left = -(pitch_length / 2)
            self.right = (pitch_length / 2)
            self.width = pitch_width
            self.length = pitch_length
            self.left_penalty = self.left + 11
            self.right_penalty = self.right - 11
        
        # scale the padding where the aspect is not equal to one
        # this means that you can easily set the padding the same all around the pitch (e.g. when using an Opta pitch)
        if self.aspect != 1:
            self._scale_pad()

        # set the pitch_extent: [xmin, xmax, ymin, ymax]
        self.pitch_extent = np.array([min(self.left, self.right), max(self.left, self.right),
                                      min(self.bottom, self.top), max(self.bottom, self.top)])
        
        # set the extent (takes into account padding) [xleft, xright, ybottom, ytop] and the aspect ratio of the axis
        self._set_extent()
        self.ax_aspect = abs(self.extent[0] - self.extent[1]) / abs(self.extent[2] - self.extent[3]) * self.aspect
        
        # data checks
        self._validation_checks()
        self._validate_pad()

        # positions of the Juego de Posición lines and stripe locations
        self._juego_de_posicion()
        self._stripe_locations()

        # calculate locations of arcs and circles.
        # Where the pitch has an unequal aspect ratio we need to do this seperately
        if (self.aspect == 1) and (self.pitch_type != 'metricasports'):
            self._init_circles_and_arcs()

        # set the positions of the goal posts
        self.goal_right = np.array([[self.right, self.center_width - self.goal_width / 2],
                                    [self.right, self.center_width + self.goal_width / 2]])
        self.goal_left = np.array([[self.left, self.center_width - self.goal_width / 2],
                                   [self.left, self.center_width + self.goal_width / 2]])
        
        # set the positions of the pitch markings - used to standardize to common coordinates
        self._pitch_markings()

    def _set_dimensions(self, pitch_dimensions):
        for key, value in pitch_dimensions.items():
            setattr(self, key, value)

    def _scale_pad(self):
        self.pad_left = self.pad_left * self.aspect
        self.pad_right = self.pad_right * self.aspect

    def _validation_checks(self):
        for attribute in ['axis', 'stripe', 'tick', 'label', 'shade_middle', 'tight_layout',
                          'half', 'positional', 'constrained_layout']:
            if not isinstance(getattr(self, attribute), bool):
                raise TypeError(f"Invalid argument: '{attribute}' should be bool.")
        if (self.axis is False) and self.label:
            warnings.warn("Labels will not be shown unless axis=True")
        if (self.axis is False) and self.tick:
            warnings.warn("Ticks will not be shown unless axis=True")
        valid_goal_type = ['line', 'box']
        if self.goal_type not in valid_goal_type:
            raise TypeError(f'Invalid argument: goal_type should be in {valid_goal_type}')

    def _validate_pad(self):
        # make sure padding not too large for the pitch
        if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.length:
            raise ValueError("pad_left/pad_right too negative for pitch length")
        if abs(min(self.pad_top, 0) + min(self.pad_bottom, 0)) >= self.width:
            raise ValueError("pad_top/pad_bottom too negative for pitch width")
        if self.half:
            if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.length / 2:
                raise ValueError("pad_left/pad_right too negative for pitch length")

    def _juego_de_posicion(self):
        # x positions for Juego de Posición
        self.x1 = self.left
        self.x4 = self.center_length
        self.x7 = self.right
        self.x2 = self.x1 + self.penalty_area_length
        self.x6 = self.x7 - self.penalty_area_length
        self.x3 = self.x2 + (self.x4 - self.x2) / 2
        self.x5 = self.x4 + (self.x6 - self.x4) / 2

        # y positions for Juego de Posición
        self.y1 = min(self.bottom, self.top)
        self.y6 = max(self.bottom, self.top)
        if self.origin_center:
            self.y2 = self.penalty_area_from_side
            self.y3 = self.six_yard_from_side
            self.y4 = -self.six_yard_from_side
            self.y5 = -self.penalty_area_from_side
        else:
            self.y3 = self.y1 + self.six_yard_from_side
            self.y2 = self.y1 + self.penalty_area_from_side
            self.y4 = self.y6 - self.six_yard_from_side
            self.y5 = self.y6 - self.penalty_area_from_side
            self.y4 = self.y6 - self.six_yard_from_side
            
    def _pitch_markings(self):
        # the pitch markings are sorted from minimum to maximum so that np.search sorted works
        # x = [left, six-yard, penalty spot, penalty area, center, penalty area, penalty spot, six-yard, right]
        self.x_markings = np.array([self.x1, self.left + self.six_yard_length, 
                                    self.left_penalty, self.x2, self.x4, 
                                    self.x6, self.right_penalty, self.right - self.six_yard_length, self.x7])
        # y = [min(top, bottom), penalty area, six-yard, goal-post left, goal_post right,
        # six-yard, penalty area, max(bottom, top)]
        self.y_markings = np.array([self.y1, self.y2, self.y3, 
                                    self.goal_left[:, 1].min(initial=None),                                     
                                    self.goal_left[:, 1].max(initial=None),
                                    self.y4, self.y5, self.y6])
        # x_markings_uefa = [0., dimensions.uefa['six_yard_length'], dimensions.uefa['left_penalty'],
        # dimensions.uefa['penalty_area_length'], 105/2,
        # 105 - dimensions.uefa['penalty_area_length'],
        # 105 - dimensions.uefa['left_penalty'],
        # 105 - dimensions.uefa['six_yard_length'], 105]
        self.x_markings_uefa = np.array([0., 5.5, 11., 16.5, 52.5, 88.5, 94., 99.5, 105.])
        # y_markings_uefa = [0, 68/2 - dimensions.uefa['penalty_area_width'] / 2,
        # 68/2 - dimensions.uefa['six_yard_width'] / 2,
        # 68/2 - dimensions.uefa['goal_width'] / 2,
        # 68/2 + dimensions.uefa['goal_width'] / 2,
        # 682 + dimensions.uefa['six_yard_width'] / 2,                
        # 68/2 + dimensions.uefa['penalty_area_width'] / 2, 68]
        self.y_markings_uefa = np.array([0., 13.84, 24.84, 30.34, 37.66, 43.16, 54.16, 68.])
        
    def _stripe_locations(self):
        stripe_six_yard = self.six_yard_length
        stripe_pen_area = (self.penalty_area_length - self.six_yard_length) / 2
        stripe_other = (self.right - self.left -
                        (self.penalty_area_length - self.six_yard_length) * 3 - self.six_yard_length * 2) / 10
        stripe_locations = ([self.left] + [stripe_six_yard] + [stripe_pen_area] * 3 +
                            [stripe_other] * 10 + [stripe_pen_area] * 3 + [stripe_six_yard])
        self.stripe_locations = np.array(stripe_locations).cumsum()

    def _init_circles_and_arcs(self):
        self.diameter1 = self.circle_diameter
        self.diameter2 = self.circle_diameter
        self.size_spot1 = self.spot_scale * self.length * 2  # *2 as elipse uses diameter rather than radius
        self.size_spot2 = self.spot_scale * self.length * 2  # *2 as elipse uses diameter rather than radius
        self.arc1_theta1 = -self.arc
        self.arc1_theta2 = self.arc
        self.arc2_theta1 = 180 - self.arc
        self.arc2_theta2 = 180 + self.arc

    def _init_circles_and_arcs_equal_aspect(self, ax):
        r1 = self.circle_diameter / 2 * self.width / self.pitch_width
        r2 = self.circle_diameter / 2 * self.length / self.pitch_length
        size_spot = self.spot_scale * self.pitch_length
        scaled_spot1 = size_spot * self.width / self.pitch_width
        scaled_spot2 = size_spot * self.length / self.pitch_length
        xy = (self.center_width, self.center_length)
        intersection = self.center_width - (
                r1 * r2 * (r2 ** 2 - (self.penalty_area_length - self.left_penalty) ** 2) ** 0.5) / (r2 ** 2)

        xy1 = (self.center_width + r2, self.center_length)
        xy2 = (self.center_width, self.center_length + r1)
        spot1 = (self.left_penalty, self.center_width)
        spot2 = (self.right_penalty, self.center_width)
        center_spot = (self.center_length, self.center_width)
        p2 = (self.left_penalty, self.center_width + scaled_spot1)
        p1 = (self.left_penalty + scaled_spot2, self.center_width)
        arc_pen_top1 = (self.penalty_area_length, intersection)

        ax_coordinate_system = ax.transAxes
        coord_name = ['xy', 'spot1', 'spot2', 'center', 'xy1', 'xy2', 'p1', 'p2', 'arc_pen_top1']
        coord_dict = {}
        for i, coord in enumerate([xy, spot1, spot2, center_spot, xy1, xy2, p1, p2, arc_pen_top1]):
            coord_dict[coord_name[i]] = self._to_ax_coord(ax, ax_coordinate_system, coord)

        self.center = coord_dict['center']
        self.penalty1 = coord_dict['spot1']
        self.penalty2 = coord_dict['spot2']
        self.diameter1 = (coord_dict['xy1'][0] - coord_dict['xy'][0]) * 2
        self.diameter2 = (coord_dict['xy2'][1] - coord_dict['xy'][1]) * 2
        self.size_spot1 = (coord_dict['p1'][0] - coord_dict['spot1'][0]) * 2
        self.size_spot2 = (coord_dict['p2'][1] - coord_dict['spot1'][1]) * 2

        a = coord_dict['arc_pen_top1'][0] - coord_dict['spot1'][0]
        o = coord_dict['spot1'][1] - coord_dict['arc_pen_top1'][1]

        self.arc1_theta2 = np.degrees(np.arctan(o / a))
        self.arc1_theta1 = 360 - self.arc1_theta2
        self.arc2_theta1 = 180 - self.arc1_theta2
        self.arc2_theta2 = 180 + self.arc1_theta2

    @staticmethod
    def _to_ax_coord(ax, coord_system, point):
        return coord_system.inverted().transform(ax.transData.transform_point(point))

    def draw(self, ax=None):
        """ Draws the specified soccer/ football pitch(es).
        If an ax is specified the pitch is drawn on an existing axis.

        Parameters
        ----------
        ax : matplotlib axis, default None
            A matplotlib.axes.Axes to draw the pitch on. If None is specified the pitch is plotted on a new figure.

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
            self._setup_subplots()
            self.fig.set_tight_layout(self.tight_layout)
            if hasattr(self, 'arc1_theta1') is False:
                self._init_circles_and_arcs_equal_aspect(self.axes.flat[0])
            for ax in self.axes.flat:
                self._draw_ax(ax)
            if self.axes.size == 1:
                self.axes = self.axes.item()
            return self.fig, self.axes

        else:
            if hasattr(self, 'arc1_theta1') is False:
                self._init_circles_and_arcs_equal_aspect(ax)
            self._draw_ax(ax)

    def _setup_subplots(self):
        fig, axes = plt.subplots(nrows=self.nrows, ncols=self.ncols, figsize=self.figsize,
                                 constrained_layout=self.constrained_layout)
        if (self.nrows == 1) and (self.ncols == 1):
            axes = np.array([axes])
        self.fig = fig
        self.axes = axes

    def _draw_ax(self, ax):
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
        ax.set_aspect(self.aspect)

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
        for i in range(len(self.stripe_locations) - 1):
            if i % 2 == 0:
                self._draw_stripe(ax, i)

    def _draw_pitch_markings(self, ax):
        rect_prop = {'fill': False, 'linewidth': self.linewidth, 'color': self.line_color, 'zorder': self.line_zorder}
        line_prop = {'linewidth': self.linewidth, 'color': self.line_color, 'zorder': self.line_zorder}
        # penalty boxes and six-yard boxes
        self._draw_rectangle(ax, self.left, self.six_yard_from_side,
                             self.six_yard_length, self.six_yard_width, **rect_prop)
        self._draw_rectangle(ax, self.right - self.six_yard_length, self.six_yard_from_side,
                             self.six_yard_length, self.six_yard_width, **rect_prop)
        self._draw_rectangle(ax, self.left, self.penalty_area_from_side,
                             self.penalty_area_length, self.penalty_area_width, **rect_prop)
        self._draw_rectangle(ax, self.right - self.penalty_area_length, self.penalty_area_from_side,
                             self.penalty_area_length, self.penalty_area_width, **rect_prop)
        # pitch
        self._draw_rectangle(ax, self.left, self.pitch_extent[2], self.length, self.width, **rect_prop)
        # mid-line
        self._draw_line(ax, [self.center_length, self.center_length], [self.bottom, self.top], **line_prop)
        # circles and arcs
        self._draw_circles_and_arcs(ax)

    def _draw_circles_and_arcs(self, ax):
        circ_prop = {'fill': False, 'linewidth': self.linewidth, 'color': self.line_color, 'zorder': self.line_zorder}

        # draw center cicrle and penalty area arcs
        self._draw_ellipse(ax, self.center_length, self.center_width, self.diameter1, self.diameter2, **circ_prop)
        self._draw_arc(ax, self.left_penalty, self.center_width, self.diameter1, self.diameter2,
                       theta1=self.arc1_theta1, theta2=self.arc1_theta2, **circ_prop)
        self._draw_arc(ax, self.right_penalty, self.center_width, self.diameter1, self.diameter2,
                       theta1=self.arc2_theta1, theta2=self.arc2_theta2, **circ_prop)

        # draw center and penalty spots
        if self.spot_scale > 0:
            self._draw_ellipse(ax, self.center_length, self.center_width,
                               self.size_spot1, self.size_spot2, color=self.line_color, zorder=self.line_zorder)
            self._draw_ellipse(ax, self.left_penalty, self.center_width,
                               self.size_spot1, self.size_spot2, color=self.line_color, zorder=self.line_zorder)
            self._draw_ellipse(ax, self.right_penalty, self.center_width,
                               self.size_spot1, self.size_spot2, color=self.line_color, zorder=self.line_zorder)

    def _draw_goals(self, ax):
        rect_prop = {'fill': False, 'linewidth': self.linewidth, 'color': self.line_color, 'alpha': 0.7,
                     'zorder': self.line_zorder}
        line_prop = {'linewidth': self.linewidth * 2, 'color': self.line_color, 'zorder': self.line_zorder}
        if self.goal_type == 'box':
            self._draw_rectangle(ax, self.right, self.goal_post, self.goal_depth, self.goal_width, **rect_prop)
            self._draw_rectangle(ax, self.left - self.goal_depth,
                                 self.goal_post, self.goal_depth, self.goal_width, **rect_prop)

        elif self.goal_type == 'line':
            self._draw_line(ax, [self.right, self.right], [self.goal_post + self.goal_width, self.goal_post],
                            **line_prop)
            self._draw_line(ax, [self.left, self.left], [self.goal_post + self.goal_width, self.goal_post], **line_prop)

    def _draw_juego_de_posicion(self, ax):
        line_prop = {'linewidth': self.positional_linewidth, 'color': self.positional_color,
                     'linestyle': self.positional_linestyle, 'zorder': self.positional_zorder}
        # x lines for Juego de Posición
        for coord in [self.x2, self.x3, self.x4, self.x5, self.x6]:
            self._draw_line(ax, [coord, coord], [self.bottom, self.top], **line_prop)
        # y lines for Juego de Posición
        self._draw_line(ax, [self.left, self.right], [self.y2, self.y2], **line_prop)
        self._draw_line(ax, [self.left, self.right], [self.y5, self.y5], **line_prop)
        self._draw_line(ax, [self.left + self.penalty_area_length, self.right - self.penalty_area_length],
                        [self.y3, self.y3], **line_prop)
        self._draw_line(ax, [self.left + self.penalty_area_length, self.right - self.penalty_area_length],
                        [self.y4, self.y4], **line_prop)

    def _draw_shade_middle(self, ax):
        shade_prop = {'fill': True, 'facecolor': self.shade_color, 'zorder': self.shade_zorder}
        self._draw_rectangle(ax, self.x3, self.pitch_extent[2], self.x5 - self.x3, self.width, **shade_prop)

    @abstractmethod
    def _set_extent(self):
        pass

    @abstractmethod
    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        pass

    @abstractmethod
    def _draw_line(self, ax, x, y, **kwargs):
        pass

    @abstractmethod
    def _draw_ellipse(self, ax, x, y, width, height, **kwargs):
        pass

    @abstractmethod
    def _draw_arc(self, ax, x, y, width, height, theta1, theta2, **kwargs):
        pass
    
    @abstractmethod
    def _draw_stripe(self, ax, i):
        pass

    @abstractmethod
    def _draw_stripe_grass(self, pitch_color):
        pass

    @staticmethod
    @abstractmethod
    def _reverse_if_vertical(x, y):
        pass

    @staticmethod
    @abstractmethod
    def _reverse_vertices_if_vertical(vert):
        pass

    def plot(self, x, y, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.plot,
        which automatically flips the x and y coordinates if the pitch is vertical.
        
        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.plot.
            
        Returns
        -------              
        lines : A list of Line2D objects representing the plotted data.
        """
        validate_ax(ax)
        x, y = self._reverse_if_vertical(x, y)
        return ax.plot(x, y, **kwargs)
    
    def _scatter_rotation(self, x, y, rotation_degrees, marker=None, ax=None, **kwargs):
        rotation_degrees = np.ma.ravel(rotation_degrees)
        if x.size != rotation_degrees.size:
            raise ValueError("x and rotation_degrees must be the same size")
        # rotated counter clockwise - this makes it clockwise with zero facing the direction of play
        rotation_degrees = -rotation_degrees
        rotation_degrees = self._rotate_if_horizontal(rotation_degrees)              
        markers = []
        for i in range(len(rotation_degrees)):
            t = mmarkers.MarkerStyle(marker=marker)
            t._transform = t.get_transform().rotate_deg(rotation_degrees[i])
            markers.append(t)
                
        sc = _mscatter(x, y, markers=markers, ax=ax, **kwargs)
        return sc

    @staticmethod
    @abstractmethod
    def _rotate_if_horizontal(rotation_degrees):
        pass
        
    def scatter(self, x, y, rotation_degrees=None, marker=None, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.scatter,
        which automatically flips the x and y coordinates if the pitch is vertical.
        Can optionally use a football marker with marker='football'.
        
        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        rotation_degrees: array-like or scalar, default None.
            Rotates the marker in degrees, clockwise. 0 degrees is facing the direction of play.
            In a horizontal pitch, 0 degrees is this way →, in a vertical pitch, 0 degrees is this way ↑
        marker: MarkerStyle, optional
            The marker style. marker can be either an instance of the class or the text shorthand for a
            particular marker. Defaults to None, in which case it takes the value of rcParams["scatter.marker"]
            (default: 'o') = 'o'.
            If marker='football' plots a football shape with the pentagons the color of the edgecolors
            and hexagons the color of the 'c' argument; 'linewidths' also sets the 
            linewidth of the football marker.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.
            
        Returns
        -------
        paths : matplotlib.collections.PathCollection or a tuple of (paths, paths) if marker='football'
        
        """
        validate_ax(ax)
        
        x = np.ma.ravel(x)
        y = np.ma.ravel(y)
        
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
            
        x, y = self._reverse_if_vertical(x, y)
        
        if marker is None:
            marker = rcParams['scatter.marker']
        
        if marker == 'football' and rotation_degrees is not None:
            raise NotImplementedError("rotated football markers are not implemented.")
        
        if marker == 'football':
            sc = scatter_football(x, y, ax=ax, **kwargs)
        elif rotation_degrees is not None:
            sc = self._scatter_rotation(x, y, rotation_degrees, marker=marker, ax=ax, **kwargs)
        else:
            sc = ax.scatter(x, y, marker=marker, **kwargs)
        return sc   

    def _reflect_x(self, x, standardized=False):
        x = np.ravel(x)
        if standardized:
            limits = [0, 105]
        else:
            limits = [self.left, self.right]
        return np.r_[x,  2 * limits[0] - x, 2 * limits[1] - x]
    
    def _reflect_y(self, y, standardized=False):
        y = np.ravel(y)
        if standardized:
            limits = [0, 68]
        else:
            limits = [self.bottom, self.top]
        return np.r_[y, 2 * limits[0] - y, 2 * limits[1] - y]
    
    def _reflect_2d(self, x, y, standardized=False):
        x = np.ravel(x)
        y = np.ravel(y)
        if standardized:
            x_limits, y_limits = [0, 105], [0, 68]
        else:
            x_limits, y_limits = [self.left, self.right], [self.bottom, self.top]
        reflected_data_x = np.r_[x,  2 * x_limits[0] - x, 2 * x_limits[1] - x, x, x]
        reflected_data_y = np.r_[y, y, y, 2 * y_limits[0] - y, 2 * y_limits[1] - y]      
        return reflected_data_x, reflected_data_y    
    
    def kdeplot(self, x, y, ax=None, reflect=True, **kwargs):
        """ Routine to perform kernel density estimation using seaborn kdeplot and plot the result on the given ax.
        The method used here includes a simple reflection method for boundary correction, so that probability
        mass is not assigned to areas outside the pitch.
        Automatically flips the x and y coordinates if the pitch is vertical.
        
        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        reflect : bool, default True
            Whether to reflect the coordinates for boundary correction
        **kwargs : All other keyword arguments are passed on to seaborn.kdeplot.
            
        Returns
        -------            
        contour : matplotlib.contour.ContourSet
        """
        validate_ax(ax)
        
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
            
        if reflect:
            x, y = self._reflect_2d(x, y)
        x, y = self._reverse_if_vertical(x, y)

        contour_plot = sns.kdeplot(x=x, y=y, ax=ax, clip=self.kde_clip, **kwargs)
        return contour_plot
    
    def hexbin(self, x, y, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.hexbin,
        which automatically flips the x and y coordinates if the pitch is vertical and clips to the pitch boundaries.
        
        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        mincnt : int > 0, default: 1
            If not None, only display cells with more than mincnt number of points in the cell.
        gridsize : int or (int, int), default: (17, 8) for Pitch/ (17, 17) for VerticalPitch
            If a single int, the number of hexagons in the x-direction. The number of hexagons in the y-direction
            is chosen such that the hexagons are approximately regular.
            Alternatively, if a tuple (nx, ny), the number of hexagons in the x-direction and the y-direction.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.hexbin.
            
        Returns
        -------
        polycollection : `~matplotlib.collections.PolyCollection`
            A `PolyCollection` defining the hexagonal bins.
            - `PolyCollection.get_offset` contains a Mx2 array containing
              the x, y positions of the M hexagon centers.
            - `PolyCollection.get_array` contains the values of the M
              hexagons.
            If *marginals* is *True*, horizontal
            bar and vertical bar (both PolyCollections) will be attached
            to the return collection as attributes *hbar* and *vbar*.
        """
        validate_ax(ax)
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        x, y = self._reverse_if_vertical(x, y)
        mincnt = kwargs.pop('mincnt', 1)
        gridsize = kwargs.pop('gridsize', self.hexbin_gridsize)
        extent = kwargs.pop('extent', self.hex_extent)
        hexbin = ax.hexbin(x, y, mincnt=mincnt, gridsize=gridsize, extent=extent, **kwargs)
        rect = patches.Rectangle((self.visible_pitch[0], self.visible_pitch[2]),
                                 self.visible_pitch[1] - self.visible_pitch[0],
                                 self.visible_pitch[3] - self.visible_pitch[2], 
                                 fill=False)
        ax.add_patch(rect)
        hexbin.set_clip_path(rect)
        return hexbin
    
    def polygon(self, verts, ax=None, **kwargs):
        """ Plot polygons using a PathCollection.
        See: https://matplotlib.org/3.1.1/api/collections_api.html.
        Valid Collection keyword arguments: edgecolors, facecolors, linewidths, antialiaseds,
        transOffset, norm, cmap
        Automatically flips the x and y vertices if the pitch is vertical.
            
        Parameters
        ----------
        verts: verts is a sequence of (verts0, verts1, ...) 
            where verts_i is a numpy array of shape (number of vertices, 2).
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.    
        **kwargs : All other keyword arguments are passed on to matplotlib.collections.PatchCollection.
            
        Returns
        -------
        PathCollection : matplotlib.collections.PatchCollection
        """
        validate_ax(ax)
        verts = np.asarray(verts)
        patch_list = []
        for vert in verts:
            vert = self._reverse_vertices_if_vertical(vert)
            polygon = patches.Polygon(vert, closed=True)
            patch_list.append(polygon)
        p = PatchCollection(patch_list, **kwargs)
        p = ax.add_collection(p)
        return p

    def goal_angle(self, x, y, ax=None, goal='right', **kwargs):
        """ Plot a polygon with the angle to the goal using PathCollection.
        See: https://matplotlib.org/3.1.1/api/collections_api.html.
        Valid Collection keyword arguments: edgecolors, facecolors, linewidths, antialiaseds,
        transOffset, norm, cmap
        
        Parameters
        ----------
        x, y: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the coordinates on the pitch.
        goal: str default 'right'.
            The goal to plot, either 'left' or 'right'.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.         
        **kwargs : All other keyword arguments are passed on to matplotlib.collections.PathCollection.
            
        Returns
        -------
        PathCollection : matplotlib.collections.PathCollection  
        """
        validate_ax(ax)
        valid_goal = ['left', 'right']
        if goal not in valid_goal:
            raise TypeError(f'Invalid argument: goal should be in {valid_goal}')
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        if goal == 'right':
            goal_coordinates = self.goal_right
        else:
            goal_coordinates = self.goal_left
        verts = np.zeros((x.size, 3, 2))
        verts[:, 0, 0] = x
        verts[:, 0, 1] = y
        verts[:, 1:, :] = np.expand_dims(goal_coordinates, 0)
        p = self.polygon(verts, ax=ax, **kwargs)
        return p
    
    @abstractmethod
    def annotate(self, text, xy, xytext=None, ax=None, **kwargs):
        """ Utility wrapper around ax.annotate
        which automatically flips the xy and xytext coordinates if the pitch is vertical.
        
        Annotate the point xy with text.
        See: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html
        
        Parameters
        ----------
        text : str
            The text of the annotation.
        xy : (float, float)
            The point (x, y) to annotate.
        xytext : (float, float), optional
            The position (x, y) to place the text at. If None, defaults to xy.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.annotate.
        
        Returns
        -------
        annotation : matplotlib.text.Annotation
        """
        pass
    
    def bin_statistic(self, x, y, values=None, statistic='count', bins=(5, 4), standardized=False):
        """ Calculates binned statistics using scipy.stats.binned_statistic_2d.
        
        This method automatically sets the range, changes some of the scipy defaults,
        and outputs the grids and centers for plotting.
        
        The default statistic has been changed to count instead of mean.
        The default bins have been set to (5,4).
        
        Parameters
        ----------
        x, y, values : array-like or scalar.
            Commonly, these parameters are 1D arrays.
            If the statistic is 'count' then values are ignored.       
        statistic : string or callable, optional
            The statistic to compute (default is 'count').
            The following statistics are available: 'count' (default),
            'mean', 'std', 'median', 'sum', 'min', 'max', or a user-defined function.
            See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html
        bins : int or [int, int] or array_like or [array, array], optional
            The bin specification.
              * the number of bins for the two dimensions (nx = ny = bins),
              * the number of bins in each dimension (nx, ny = bins),
              * the bin edges for the two dimensions (x_edge = y_edge = bins),
              * the bin edges in each dimension (x_edge, y_edge = bins).
                If the bin edges are specified, the number of bins will be,
                (nx = len(x_edge)-1, ny = len(y_edge)-1).
        standardized : bool, default False
            Whether the x, y values have been standardized to the 'uefa' pitch coordinates (105m x 68m)
            
        Returns
        ----------
        bin_statistic : dict.
            The keys are 'statistic' (the calculated statistic),
            'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).
        """
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
   
        if values is not None:
            values = np.ravel(values)
        if (values is None) & (statistic == 'count'):
            values = x
        if (values is None) & (statistic != 'count'):
            raise ValueError("values on which to calculate the statistic are missing")
        if values.size != x.size:
            raise ValueError("x and values must be the same size")
        
        if standardized:
            pitch_range = [[0, 105], [0, 68]]
        else:
            if self.invert_y:
                pitch_range = [[self.left, self.right], [self.top, self.bottom]]
                y = self.bottom - y  # for inverted axis flip the coordinates
            else:
                pitch_range = [[self.left, self.right], [self.bottom, self.top]]
        
        result = binned_statistic_2d(x, y, values, statistic=statistic, bins=bins, range=pitch_range)
        
        statistic = result.statistic.T
        # this ensures that all the heatmaps are created consistently at the heatmap edges
        # i.e. grid cells are created from the bottom to the top of the pitch. where the top edge
        # always belongs to the cell above. First the raw coordinates have been flipped above
        # then the statistic is flipped back here
        if self.invert_y and standardized is False:
            statistic = np.flip(statistic, axis=0)
                           
        x_grid, y_grid = np.meshgrid(result.x_edge, result.y_edge)
           
        cx, cy = np.meshgrid(result.x_edge[:-1] + 0.5 * np.diff(result.x_edge),
                             result.y_edge[:-1] + 0.5 * np.diff(result.y_edge))
        
        bin_statistic = _BinnedStatisticResult(statistic, x_grid, y_grid, cx, cy)._asdict()

        return bin_statistic
    
    @abstractmethod
    def heatmap(self, bin_statistic, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.pcolormesh
        which automatically flips the x_grid and y_grid coordinates if the pitch is vertical.
        
        See: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html
       
        Parameters
        ----------
        bin_statistic : dict.
            This should be calculated via Pitch.bin_statistic().
            The keys are 'statistic' (the calculated statistic),
            'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.pcolormesh.
        
        Returns
        ----------
        mesh : matplotlib.collections.QuadMesh
        """
        pass

    def bin_statistic_positional(self, x, y, values=None, positional='full', statistic='count'):
        """ Calculates binned statistics for the Juego de posición (position game) concept.
        It uses scipy.stats.binned_statistic_2d.
        Parameters
        ----------
        x, y, values : array-like or scalar.
            Commonly, these parameters are 1D arrays.
            If the statistic is 'count' then values are ignored.
        
        positional : str
            One of 'full', 'horizontal' or 'vertical' for the respective heatmaps.        
        
        statistic : string or callable, optional
            The statistic to compute (default is 'count').
            The following statistics are available: 'count' (default),
            'mean', 'std', 'median', 'sum', 'min', 'max', or a user-defined function.
            See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html.
            
        Returns
        ----------
        bin_statistic : A list of dictionaries.
            The dictionary keys are 'statistic' (the calculated statistic),
            'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).
        """
        
        # I tried several ways of creating positional bins. It's hard to do this because
        # of points on the edges of bins. You have to be sure they are only counted once consistently
        # I tried doing this by adding or subtracting a small value near the edges, but it didn't work for all cases
        # I settled on this idea, which is to create binned statistics with an additional row, column either
        # side (unless the side of the pitch) so that the scipy binned_statistic_2d functions handles the edges
        if positional == 'full':
            # top and bottom row - we create a grid with three rows and then ignore the middle row when slicing
            xedge = np.array([self.x1, self.x2, self.x3, self.x4, self.x5, self.x6, self.x7])
            yedge = np.array([self.y1, self.y2, self.y5, self.y6])
            bin_statistic1 = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            stat1 = bin_statistic1['statistic']
            x_grid1 = bin_statistic1['x_grid']
            y_grid1 = bin_statistic1['y_grid']
            cx1 = bin_statistic1['cx']
            cy1 = bin_statistic1['cy']
            # slicing second row
            stat2 = stat1[2, :].reshape(1, -1).copy()
            x_grid2 = x_grid1[2:, :].copy()
            y_grid2 = y_grid1[2:, :].copy()
            cx2 = cx1[2, :].copy()
            cy2 = cy1[2, :].copy()
            # slice first row
            stat1 = stat1[0, :].reshape(1, -1).copy()
            x_grid1 = x_grid1[:2, :].copy()
            y_grid1 = y_grid1[:2, :].copy()
            cx1 = cx1[0, :].copy()
            cy1 = cy1[0, :].copy()

            # middle of pitch
            xedge = np.array([self.x1, self.x2, self.x4, self.x6, self.x7])
            yedge = np.array([self.y1, self.y2, self.y3, self.y4, self.y5, self.y6])
            bin_statistic3 = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            stat3 = bin_statistic3['statistic']
            x_grid3 = bin_statistic3['x_grid']
            y_grid3 = bin_statistic3['y_grid']
            cx3 = bin_statistic3['cx']
            cy3 = bin_statistic3['cy']
            stat3 = stat3[1:-1, 1:-1]
            x_grid3 = x_grid3[1:-1:, 1:-1].copy()
            y_grid3 = y_grid3[1:-1, 1:-1].copy()
            cx3 = cx3[1:-1, 1:-1].copy()
            cy3 = cy3[1:-1, 1:-1].copy()
            
            # penalty areas
            xedge = np.array([self.x1, self.x2, self.x3, self.x6, self.x7]).astype(np.float64)
            yedge = np.array([self.y1, self.y2, self.y5, self.y6]).astype(np.float64)
            bin_statistic4 = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            stat4 = bin_statistic4['statistic']
            x_grid4 = bin_statistic4['x_grid']
            y_grid4 = bin_statistic4['y_grid']
            cx4 = bin_statistic4['cx']
            cy4 = bin_statistic4['cy']
            # slicing each penalty box
            stat5 = stat4[1:-1, -1:]
            stat4 = stat4[1:-1, :1]
            y_grid5 = y_grid4[1:-1, -2:]
            y_grid4 = y_grid4[1:-1, 0:2]
            x_grid5 = x_grid4[1:-1, -2:]
            x_grid4 = x_grid4[1:-1, 0:2]
            cx5 = cx4[1:-1, -1:]
            cx4 = cx4[1:-1, :1]
            cy5 = cy4[1:-1, -1:]
            cy4 = cy4[1:-1, :1]

            result1 = _BinnedStatisticResult(stat1, x_grid1, y_grid1, cx1, cy1)._asdict()
            result2 = _BinnedStatisticResult(stat2, x_grid2, y_grid2, cx2, cy2)._asdict()
            result3 = _BinnedStatisticResult(stat3, x_grid3, y_grid3, cx3, cy3)._asdict()
            result4 = _BinnedStatisticResult(stat4, x_grid4, y_grid4, cx4, cy4)._asdict()
            result5 = _BinnedStatisticResult(stat5, x_grid5, y_grid5, cx5, cy5)._asdict()
            
            bin_statistic = [result1, result2, result3, result4, result5]    
            
        elif positional == 'horizontal':
            xedge = np.array([self.x1, self.x7])
            yedge = np.array([self.y1, self.y2, self.y3, self.y4, self.y5, self.y6])
            bin_horizontal = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            bin_statistic = [bin_horizontal]
            
        elif positional == 'vertical':
            xedge = np.array([self.x1, self.x2, self.x3, self.x4, self.x5, self.x6, self.x7])
            yedge = np.array([self.y1, self.y6])
            bin_vertical = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            bin_statistic = [bin_vertical]
        else:
            raise ValueError("positional must be one of 'full', 'vertical' or 'horizontal'")
                  
        return bin_statistic 
    
    def heatmap_positional(self, bin_statistic, ax=None, **kwargs):
        """ Plots several heatmaps for the different Juegos de posición areas.
       
        Parameters
        ----------
        bin_statistic : A list of dictionaries.
            This should be calculated via Pitch.bin_statistic_positional().
            The dictionary keys are 'statistic' (the calculated statistic),
            'x_grid' and 'y_grid (the bin's edges), and cx and cy (the bin centers).
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.pcolormesh.
        
        Returns
        ----------
        mesh : matplotlib.collections.QuadMesh
        """
        validate_ax(ax)
        vmax = kwargs.pop('vmax', np.array([stat['statistic'].max() for stat in bin_statistic]).max(initial=None))
        vmin = kwargs.pop('vmin', np.array([stat['statistic'].min() for stat in bin_statistic]).min(initial=None))
        
        mesh_list = []
        for bin_stat in bin_statistic:
            mesh = self.heatmap(bin_stat, vmin=vmin, vmax=vmax, ax=ax, **kwargs)
            mesh_list.append(mesh)
            
        return mesh_list
    
    def label_heatmap(self, bin_statistic, ax=None, **kwargs):
        """ Labels the heatmaps and automatically flips the coordinates if the pitch is vertical.
              
        Parameters
        ----------
        bin_statistic : A dictionary or list of dictionaries.
            This should be calculated via Pitch.bin_statistic_positional() or Pitch.bin_statistic().
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.annotate.
            
        Returns
        ----------
        annotations : A list of matplotlib.text.Annotation.
        """
        validate_ax(ax)

        if not isinstance(bin_statistic, list):
            bin_statistic = [bin_statistic]
    
        annotation_list = []
        for bs in bin_statistic:
            # remove labels outside the plot extents
            mask_x_outside1 = bs['cx'] < self.pitch_extent[0]
            mask_x_outside2 = bs['cx'] > self.pitch_extent[1]
            mask_y_outside1 = bs['cy'] < self.pitch_extent[2]
            mask_y_outside2 = bs['cy'] > self.pitch_extent[3]
            mask_clip = mask_x_outside1 | mask_x_outside2 | mask_y_outside1 | mask_y_outside2
            mask_clip = np.ravel(mask_clip)
            
            text = np.ravel(bs['statistic'])[~mask_clip]
            cx = np.ravel(bs['cx'])[~mask_clip]
            cy = np.ravel(bs['cy'])[~mask_clip]
            for i in range(len(text)):
                annotation = self.annotate(text[i], (cx[i], cy[i]), ax=ax, **kwargs)
                annotation_list.append(annotation)
            
        return annotation_list
    
    @abstractmethod
    def arrows(self, xstart, ystart, xend, yend, *args, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.quiver.
        Quiver uses locations and direction vectors usually. Here these are instead calculated automatically
        from the start and endpoints of the arrow.
        The function also automatically flips the x and y coordinates if the pitch is vertical.
        
        Plot a 2D field of arrows.
        See: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.quiver.html
        
        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the start and end coordinates of the lines.
        C: 1D or 2D array-like, optional
            Numeric data that defines the arrow colors by colormapping via norm and cmap.
            This does not support explicit colors. If you want to set colors directly, use color instead.
            The size of C must match the number of arrow locations.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.          
        width : float, default 4
            Arrow shaft width in points.     
        headwidth : float, default 3
            Head width as a multiple of the arrow shaft width.
        headlength : float, default 5
            Head length as a multiple of the arrow shaft width.
        headaxislength : float, default: 4.5
            Head length at the shaft intersection.
            If this is equal to the headlength then the arrow will be a triangular shape.
            If greater than the headlength then the arrow will be wedge shaped.
            If less than the headlength the arrow will be swept back.
        color : color or color sequence, optional
            Explicit color(s) for the arrows. If C has been set, color has no effect.    
        linewidth or linewidths or lw : float or sequence of floats
            Edgewidth of arrow.
        edgecolor or ec or edgecolors : color or sequence of colors or 'face'
        alpha : float or None
            Transparency of arrows.                
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.quiver.
            
        Returns
        -------
        PolyCollection : matplotlib.quiver.Quiver   
        """
        pass

    @abstractmethod
    def lines(self, xstart, ystart, xend, yend, color=None, n_segments=100,
              comet=False, transparent=False, alpha_start=0.01,
              alpha_end=1, cmap=None, ax=None, **kwargs):
        """ Plots lines using matplotlib.collections.LineCollection.
        This is a fast way to plot multiple lines without loops.
        Also enables lines that increase in width or opacity by splitting the line into n_segments of increasing
        width or opacity as the line progresses.
        
        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the start and end coordinates of the lines.
        color : A matplotlib color or sequence of colors, defaults to None.
            Defaults to None. In that case the marker color is determined 
            by the value rcParams['lines.color']
        n_segments : int, default 100
            If comet=True or transparent=True this is used to split the line
            into n_segments of increasing width/opacity.
        comet : bool default False
            Whether to plot the lines increasing in width.
        transparent : bool, default False
            Whether to plot the lines increasing in opacity.
        linewidth or lw : array-like or scalar, default 5.
            Multiple linewidths not supported for the comet or transparent lines.
        alpha_start: float, default 0.01
            The starting alpha value for transparent lines, between 0 (transparent) and 1 (opaque).
            If transparent = True the line will be drawn to
            linearly increase in opacity between alpha_start and alpha_end.
        alpha_end : float, default 1
            The ending alpha value for transparent lines, between 0 (transparent) and 1 (opaque).
            If transparent = True the line will be drawn to
            linearly increase in opacity between alpha_start and alpha_end.
        cmap : str, default None
            A matplotlib cmap (colormap) name
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.collections.LineCollection.
            
        Returns
        -------
        LineCollection : matplotlib.collections.LineCollection
        """
        pass
    
    def to_uefa_coordinates(self, x, y):
        """ Converts from the pitch's coordinates to a standard uefa pitch's coordinates (105m x 68m).
        Values outside the pitch extents are clipped to the pitch lines.
        The coordinates are converted using the ggsoccer (https://github.com/Torvaney/ggsoccer)
        method. Any x or y coordinate is rescaled linearly between the nearest two pitch markings.
        For example, the edge of the penalty box and the half way-line.
        
        Parameters
        ----------
        x, y: array-like or scalar.
            The x/y coordinates that you want to convert to uefa coordinates.
            
        Returns
        -------
        tuple (x_standardized, y_standardized) : A tuple of numpy.arrays in uefa coordinates.    
        """
        # to numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)
        
        # clip outside to pitch extents        
        x = x.clip(min=self.pitch_extent[0], max=self.pitch_extent[1])
        y = y.clip(min=self.pitch_extent[2], max=self.pitch_extent[3])
    
        # for inverted axis flip the coordinates
        if self.invert_y:
            y = self.bottom - y
        
        x_standardized = self._standardize(self.x_markings, self.x_markings_uefa, x)
        y_standardized = self._standardize(self.y_markings, self.y_markings_uefa, y)
        return x_standardized, y_standardized
    
    def from_uefa_coordinates(self, x, y):
        """ Converts from the standard uefa pitch's coordinates (105m x 68m) to the pitch's coordinates.
        Values outside the pitch extents are clipped to the pitch lines.
        The coordinates are converted using the ggsoccer (https://github.com/Torvaney/ggsoccer)
        method. Any x or y coordinate is rescaled linearly between the nearest two pitch markings.
        For example, the edge of the penalty box and the half way-line.
        
        Parameters
        ----------
        x, y: array-like or scalar.
            The x/y coordinates that you want to convert from uefa coordinates.
            
        Returns
        -------
        tuple (x_standardized, y_standardized) : A tuple of numpy.arrays in the pitch's coordinates.        
        """
        # to numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)
        
        # clip outside to pitch extents        
        x = x.clip(min=0, max=105)
        y = y.clip(min=0, max=68)
                
        x_standardized = self._standardize(self.x_markings_uefa, self.x_markings, x)
        y_standardized = self._standardize(self.y_markings_uefa, self.y_markings, y)
        
        # for inverted axis flip the coordinates
        if self.invert_y:
            y_standardized = self.bottom - y_standardized
        
        return x_standardized, y_standardized
    
    @staticmethod
    def _standardize(markings_from, markings_to, coordinate):
        pos = np.searchsorted(markings_from, coordinate)
        low_from = markings_from[pos - 1]
        high_from = markings_from[pos]
        proportion_of_way_between = (coordinate - low_from) / (high_from - low_from)
        low_to = markings_to[pos - 1]
        high_to = markings_to[pos]
        return low_to + ((high_to - low_to) * proportion_of_way_between)
              
    def voronoi(self, x, y, teams):
        """ Get Voronoi vertices for a set of coordinates.
        Uses a trick by Dan Nichol (@D4N__ on Twitter) where points are reflected in the pitch lines
        before calculating the Voronoi. This means that the Voronoi extends to the edges of the pitch
        see: https://github.com/ProformAnalytics/tutorial_nbs/blob/master/notebooks/Voronoi%20Reflection%20Trick.ipynb
        
        Players outside of the pitch dimensions are assumed to be standing on the pitch edge.
        This means that their coordinates are clipped to the pitch edges before calculating the Voronoi.        
            
        Parameters
        ----------
        x, y: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the coordinates on the pitch.
        
        teams: array-like or scalar.
            This splits the results into the Voronoi vertices for each team.
            This can either have integer (1/0) values or boolean (True/False) values.
            team1 is where team==1 or team==True
            team2 is where team==0 or team==False
            
        Returns
        -------
        team1 : a 1d numpy array (length number of players in team 1) of 2d arrays
            Where the individual 2d arrays are coordinates of the Voronoi vertices.
            
        team2 : a 1d numpy array (length number of players in team 2) of 2d arrays
            Where the individual 2d arrays are coordinates of the Voronoi vertices.
        """
        x = np.ravel(x)
        y = np.ravel(y)
        teams = np.ravel(teams)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        if teams.size != x.size:
            raise ValueError("x and team must be the same size")
            
        if self.aspect != 1:
            standardized = True
            x, y = self.to_uefa_coordinates(x, y)
            extent = np.array([0, 105, 0, 68])
        else:
            standardized = False
            extent = self.pitch_extent
        
        # clip outside to pitch extents
        x = x.clip(min=extent[0], max=extent[1])
        y = y.clip(min=extent[2], max=extent[3])

        # reflect in pitch lines
        reflect_x, reflect_y = self._reflect_2d(x, y, standardized=standardized)
        reflect = np.vstack([reflect_x, reflect_y]).T
        
        # create Voronoi
        vor = Voronoi(reflect)
        
        # get region vertices
        regions = vor.point_region[:x.size]
        regions = np.array(vor.regions, dtype='object')[regions]
        region_vertices = []
        for region in regions:
            verts = vor.vertices[region]
            verts[:, 0] = np.clip(verts[:, 0], a_min=extent[0], a_max=extent[1])
            verts[:, 1] = np.clip(verts[:, 1], a_min=extent[2], a_max=extent[3])
            # convert back to coordinates if previously standardized
            if standardized:
                x_std, y_std = self.from_uefa_coordinates(verts[:, 0], verts[:, 1])
                verts[:, 0] = x_std
                verts[:, 1] = y_std     
            region_vertices.append(verts)
        region_vertices = np.array(region_vertices, dtype='object')
        
        # seperate team1/ team2 vertices
        team1 = region_vertices[teams == 1]
        team2 = region_vertices[teams == 0]
        
        return team1, team2
    
    def calculate_angle_and_distance(self, xstart, ystart, xend, yend, standardized=False):
        """ Calculates the angle in radians counter-clockwise between a start and end location and the distance.
        Where the angle 0 is this way → (the straight line from left to right) in a horizontally orientated pitch
        and this way ↑ in a vertically orientated pitch.
        The angle goes from 0 to 2pi. To convert the angle to degrees use np.degrees(angle).
        
        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. 
            These should be the start and end coordinates to calculate the angle between.
        standardized : bool, default False
            Whether the x, y values have been standardized to the 'uefa' pitch coordinates (105m x 68m)
            
        Returns
        -------
        angle: ndarray
            Array of angles in radians counter-clockwise in the range [0, 2pi].
            Where 0 is the straight line left to right in a horizontally orientated pitch
            and the straight line bottom to top in a vertically orientated pitch.
        distance: ndarray
            Array of distances.
        """
        xstart = np.ravel(xstart)
        ystart = np.ravel(ystart)
        xend = np.ravel(xend)
        yend = np.ravel(yend)
        
        if xstart.size != ystart.size:
            raise ValueError("xstart and ystart must be the same size")
        if xstart.size != xend.size:
            raise ValueError("xstart and xend must be the same size")
        if ystart.size != yend.size:
            raise ValueError("ystart and yend must be the same size")  
        
        x_dist = xend - xstart
        if self.invert_y and standardized is False:
            y_dist = ystart - yend
        else:
            y_dist = yend - ystart
                   
        angle = np.arctan2(y_dist, x_dist)
        # if negative angle make positive angle, so goes from 0 to 2 * pi
        angle[angle < 0] = 2 * np.pi + angle[angle < 0]
        
        distance = (x_dist ** 2 + y_dist ** 2) ** 0.5
        
        return angle, distance
    
    def flow(self, xstart, ystart, xend, yend, bins=(5, 4), arrow_type='same', arrow_length=5,
             color=None, ax=None, **kwargs):
        """ Create a flow map by binning  the data into cells and calculating the average
        angles and distances. The colors of each arrow are        
        
        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. 
            These should be the start and end coordinates to calculate the angle between.
        bins : int or [int, int] or array_like or [array, array], optional
            The bin specification for binning the data to calculate the angles/ distances.
              * the number of bins for the two dimensions (nx = ny = bins),
              * the number of bins in each dimension (nx, ny = bins),
              * the bin edges for the two dimensions (x_edge = y_edge = bins),
              * the bin edges in each dimension (x_edge, y_edge = bins).
                If the bin edges are specified, the number of bins will be,
                (nx = len(x_edge)-1, ny = len(y_edge)-1).
        arrow_type : str, default 'same'
            The supported arrow types are: 'same', 'scale', and 'average'.
            'same' makes the arrows the same size (arrow_length).
            'scale' scales the arrow length by the average distance in the cell (up to a max of arrow_length).
            'average' makes the arrow size the average distance in the cell.
        arrow_length : float, default 5
            The arrow_length for the flow map. If the arrow_type='same',
            all the arrows will be arrow_length. If the arrow_type='scale',
            the arrows will be scaled by the average distance.
            If the arrow_type='average', the arrows_length is ignored
            This is automatically multipled by 100 if using a Tracab pitch (i.e. the default is 500).
        color : A matplotlib color, defaults to None.
            Defaults to None. In that case the marker color is determined by the cmap (default 'viridis').
            and the counts of the starting positions in each bin.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.quiver.
        
        Returns
        -------
        PolyCollection : matplotlib.quiver.Quiver                
        """
        validate_ax(ax)
        if self.aspect != 1:
            standardized = True
            xstart, ystart = self.to_uefa_coordinates(xstart, ystart)
            xend, yend = self.to_uefa_coordinates(xend, yend)
        else:
            standardized = False

        # calculate  the binned statistics
        angle, distance = self.calculate_angle_and_distance(xstart, ystart, xend, yend, standardized=standardized)
        bs_distance = self.bin_statistic(xstart, ystart, values=distance,
                                         statistic='mean', bins=bins, standardized=standardized)
        bs_angle = self.bin_statistic(xstart, ystart, values=angle,
                                      statistic=circmean, bins=bins, standardized=standardized)

        # calculate the arrow length
        if self.pitch_type == 'tracab':
            arrow_length = arrow_length * 100
        if arrow_type == 'scale':
            new_d = (bs_distance['statistic'] / np.nan_to_num(bs_distance['statistic']).max(initial=None)) \
                    * arrow_length
        elif arrow_type == 'same':
            new_d = arrow_length
        elif arrow_type == 'average':
            new_d = bs_distance['statistic']
        else:
            valid_arrows = ['scale', 'same', 'average']
            raise TypeError(f'Invalid argument: arrow_type should be in {valid_arrows}')

        # calculate the end positions of the arrows
        endx = bs_angle['cx'] + (np.cos(bs_angle['statistic']) * new_d)
        if self.invert_y and standardized is False:
            endy = bs_angle['cy'] - (np.sin(bs_angle['statistic']) * new_d)  # invert_y
        else:
            endy = bs_angle['cy'] + (np.sin(bs_angle['statistic']) * new_d)
                    
        # get coordinates and convert back to the pitch coordinates if necessary
        cx, cy = bs_angle['cx'], bs_angle['cy']
        if standardized:
            cx, cy = self.from_uefa_coordinates(cx, cy)
            endx, endy = self.from_uefa_coordinates(endx, endy)
        
        # plot arrows
        if color is None:
            bs_count = self.bin_statistic(xstart, ystart, statistic='count', bins=bins, standardized=standardized)
            flow = self.arrows(cx, cy, endx, endy, bs_count['statistic'], ax=ax, **kwargs)
        else:
            flow = self.arrows(cx, cy, endx, endy, color=color, ax=ax, **kwargs)            
        
        return flow
    

#    def jointplot(self, x, y, **kwargs):
#        """ Utility wrapper around seaborn.jointplot
#        which automatically flips the x and y coordinates if the pitch is vertical, sets the height from the figsize,
#        and clips kernel density plots (kind = 'kde') to the pitch boundaries.
#
#        Draw a plot of two variables with bivariate and univariate graphs.
#        See: https://seaborn.pydata.org/generated/seaborn.jointplot.html
#
#        Parameters
#        ----------
#        x, y : array-like or scalar.
#            Commonly, these parameters are 1D arrays.
#
#        kind : str default 'kde'
#            Kind of plot to draw. One of 'scatter', 'kde', 'hist', 'hex', 'reg', or resid'
#
#        **kwargs : All other keyword arguments are passed on to seaborn.jointplot.
#
#        Returns
#        -------
#        grid : seaborn.axisgrid.JointGrid
#        """
#        x = np.ravel(x)
#        y = np.ravel(y)
#        if x.size != y.size:
#            raise ValueError("x and y must be the same size")
#        x, y = self._reverse_if_vertical(x, y)  
#        clip = kwargs.pop('clip', self.kde_clip)
#        kind = kwargs.pop('kind', 'kde')
#        extent = kwargs.pop('extent', self.hex_extent)
    
#        if kind == 'kde':
#            joint_plot = sns.jointplot(x=x, y=y, kind=kind, clip=clip,
#                                       xlim=self.visible_pitch[:2],
#                                       ylim=self.visible_pitch[2:],
#                                       **kwargs)
#        elif kind == 'hex':
#            dropna = kwargs.pop('dropna', True)
#            gridsize = kwargs.pop('gridsize', self.hexbin_gridsize)
#            joint_plot = sns.jointplot(x=x, y=y,
#                                       kind=kind, 
#                                       extent=extent,
#                                       gridsize=gridsize,
#                                       dropna=True, 
#                                       xlim=self.visible_pitch[:2],
#                                       ylim=self.visible_pitch[2:],
#                                       **kwargs)
#        else:
#            joint_plot = sns.jointplot(x=x, y=y, kind=kind, **kwargs)
        
#        joint_plot_ax = joint_plot.ax_joint
#        self.draw(ax=joint_plot_ax)
#        joint_plot.fig.set_figwidth(self.jointplot_width)
#        joint_plot.fig.set_figheight(self.jointplot_height)
                
#        if kind == 'hex':
#            hexbin = joint_plot_ax.__dict__['collections'][0]
#            rect = patches.Rectangle((self.visible_pitch[0], self.visible_pitch[2]),
#                                     self.visible_pitch[1] - self.visible_pitch[0],
#                                     self.visible_pitch[3] - self.visible_pitch[2], 
#                                     fill=False)
#            joint_plot_ax.add_patch(rect)
#            hexbin.set_clip_path(rect)
#        return joint_plot

# TO DO
# jointplot
# peter mckeever arrow lines?
