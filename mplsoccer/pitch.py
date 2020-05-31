""" `mplsoccer.pitch` is a python module for plotting soccer / football pitches in Matplotlib. """

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import matplotlib.lines as lines
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.markers as mmarkers
import numpy as np
import seaborn as sns
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.legend_handler import HandlerLineCollection, HandlerPathCollection, HandlerLine2D
from matplotlib.cm import get_cmap
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgb, to_rgba_array
from matplotlib import rcParams
from matplotlib.legend import Legend
from scipy.stats import binned_statistic_2d
from scipy.spatial import Voronoi
from .scatterutils import football_hexagon_marker, football_pentagon_marker, _mscatter
from collections import Sequence, namedtuple
import warnings

_BinnedStatisticResult = namedtuple('BinnedStatisticResult',
                                    ('statistic', 'x_grid', 'y_grid', 'cx', 'cy'))


class Pitch(object):
    """ A class for plotting soccer / football pitches in Matplotlib
    
    Parameters
    ----------
    figsize : tuple of float, default Matplotlib figure size
        The figure size in inches by default.
    layout : tuple of int, default (1,1)
        Tuple of (columns, rows) for the layout of the plot.
    pitch_type : str, default 'statsbomb'
        The pitch type used in the plot.
        The supported pitch types are: 'opta', 'statsbomb', 'tracab', 'stats',
        'wyscout', 'statsperform', 'metricasports'.
    orientation : str, default 'horizontal'
        The pitch orientation: 'horizontal' or 'vertical'.
    view : str, default 'full'
        The pitch view: 'full' or 'half'.
    pitch_color : any Matplotlib color, default None
        The background color for each Matplotlib axis. If None, defaults to rcParams["axes.facecolor"].
        To remove the background set to "None" or 'None'.
    line_color : any Matplotlib color, default None
        The line color for the pitch markings. If None, defaults to rcParams["grid.color"].       
    line_zorder : float, default 0.9
        Set the zorder for the pitch lines (a matplotlib artist). Artists with lower zorder values are drawn first.
    background_zorder : float, default 0.8
        Set the zorder for the pitch background (a matplotlib artist). Artists with lower zorder values are drawn first.
    linewidth : float, default 2
        The line width for the pitch markings.
    spot_scale : float, default 0.002
        The size of the penalty and center spots relative to the pitch length.
    stripe : bool, default False
        Whether to show pitch stripes.    
    stripe_color : any Matplotlib color, default '#c2d59d'
        The color of the pitch stripes if stripe=True    
    pad_left : float, default None
        Adjusts the left xlim of the axis. Postive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_right : float, default None
        Adjusts the right xlim of the axis. Postive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_bottom : float, default None
        Adjusts the bottom ylim of the axis. Postive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pad_top : float, default None
        Adjusts the top ylim of the axis. Postive values increase the plot area,
        while negative values decrease the plot area.
        If None set to 0.04 for 'metricasports' pitch and 4 otherwise.
    pitch_length : float, default None
        The pitch length in meters. Only used for the 'tracab' and 'metricasports' pitch_type.
    pitch_width : float, default None
        The pitch width in meters. Only used for the 'tracab' and 'metricasports' pitch type. 
    goal_type : str, default 'line'
        Whether to display the goals as a 'line', a 'box' or to not display it at all (None)
    axis : bool, default False
        Whether to include the axis: True means the axis is 'on' and False means the axis is'off'.
    label : bool, default False
        Whether to include the axis labels.
    tick : bool, default False
        Whether to include the axis ticks.
    tight_layout : bool, default True
        Whether to use Matplotlib's tight layout.
    constrained_layout : bool, default False
        Whether to use Matplotlib's constrained layout.
    """

    # the stripe_scale has been manually selected so that all stripe widths
    # are integers when multiplied by the stripe_scale
    _opta_dimensions = {'top': 100, 'bottom': 0, 'left': 0, 'right': 100,
                        'width': 100, 'center_width': 50, 'length': 100, 'center_length': 50,
                        'six_yard_from_side': 36.8, 'six_yard_width': 26.4, 'six_yard_length': 5.8,
                        'penalty_area_from_side': 21.1, 'penalty_area_width': 57.8, 'penalty_area_length': 17.0,
                        'left_penalty': 11.5, 'right_penalty': 88.5, 'circle_size': 9.15,
                        'goal_depth': 1.9, 'goal_width': 10.76, 'goal_post': 44.62,
                        'arc1_leftV': None, 'arc2_leftH': None, 'invert_y': False, 'stripe_scale': 25}

    # wyscout dimensions are sourced from ggsoccer https://github.com/Torvaney/ggsoccer/blob/master/R/dimensions.R
    _wyscout_dimensions = {'top': 0, 'bottom': 100, 'left': 0, 'right': 100,
                           'width': 100, 'center_width': 50, 'length': 100, 'center_length': 50,
                           'six_yard_from_side': 37, 'six_yard_width': 26, 'six_yard_length': 6,
                           'penalty_area_from_side': 19, 'penalty_area_width': 62, 'penalty_area_length': 16,
                           'left_penalty': 10, 'right_penalty': 90, 'circle_size': 9.15,
                           'goal_depth': 1.9, 'goal_width': 12, 'goal_post': 44,
                           'arc1_leftV': None, 'arc2_leftH': None, 'invert_y': True, 'stripe_scale': 5}

    _statsbomb_dimensions = {'top': 0, 'bottom': 80, 'left': 0, 'right': 120,
                             'width': 80, 'center_width': 40, 'length': 120, 'center_length': 60,
                             'six_yard_from_side': 30, 'six_yard_width': 20, 'six_yard_length': 6,
                             'penalty_area_from_side': 18, 'penalty_area_width': 44, 'penalty_area_length': 18,
                             'left_penalty': 12, 'right_penalty': 108, 'circle_size': 10.46,
                             'goal_depth': 2.4, 'goal_width': 8, 'goal_post': 36,
                             'arc1_leftV': 35, 'arc2_leftH': 55, 'invert_y': True, 'stripe_scale': 5}
    
    # real-life pitches are in yards and the meter conversions are slightly different
    # but with this size of visualisation the differences will be minimal
    _tracab_dimensions = {'top': None, 'bottom': None, 'left': None, 'right': None,
                          'width': None, 'center_width': 0, 'length': None, 'center_length': 0,
                          'six_yard_from_side': -916, 'six_yard_width': 1832, 'six_yard_length': 550,
                          'penalty_area_from_side': -2016, 'penalty_area_width': 4032, 'penalty_area_length': 1650,
                          'left_penalty': None, 'right_penalty': None, 'circle_size': 915,
                          'goal_depth': 200, 'goal_width': 732, 'goal_post': -366,
                          'arc1_leftV': 36.95, 'arc2_leftH': 53.05, 'invert_y': False, 'stripe_scale': 0.1}

    # real-life pitches are in yards and the meter conversions are slightly different
    # but with this size of visualisation the differences will be minimal
    _metricasports_dimensions = {'top': 0., 'bottom': 1., 'left': 0., 'right': 1.,
                                 'width': 1, 'center_width': 0.5, 'length': 1, 'center_length': 0.5,
                                 'six_yard_from_side': None, 'six_yard_width': 18.32, 'six_yard_length': 5.5,
                                 'penalty_area_from_side': None, 'penalty_area_width': 40.32,
                                 'penalty_area_length': 16.5,
                                 'left_penalty': 11., 'right_penalty': 11., 'circle_size': 9.15,
                                 'goal_depth': 2., 'goal_width': 7.32, 'goal_post': 3.6,
                                 'arc1_leftV': None, 'arc2_leftH': None, 'invert_y': True, 'stripe_scale': 1000}

    _stats_dimensions = {'top': 0, 'bottom': 70, 'left': 0, 'right': 105,
                         'width': 70, 'center_width': 35, 'length': 105, 'center_length': 52.5,
                         'six_yard_from_side': 26, 'six_yard_width': 18, 'six_yard_length': 6,
                         'penalty_area_from_side': 15, 'penalty_area_width': 40, 'penalty_area_length': 16.5,
                         'left_penalty': 11, 'right_penalty': 94, 'circle_size': 9.15,
                         'goal_depth': 2, 'goal_width': 7.32, 'goal_post': 31.34,
                         'arc1_leftV': 36.95, 'arc2_leftH': 53.05, 'invert_y': True, 'stripe_scale': 20}
    
    _statsperform_dimensions = {'top': 68, 'bottom': 0, 'left': 0, 'right': 105,
                                'width': 68, 'center_width': 34, 'length': 105, 'center_length': 52.5,
                                'six_yard_from_side': 24.84, 'six_yard_width': 18.32, 'six_yard_length': 5.5,
                                'penalty_area_from_side': 13.84, 'penalty_area_width': 40.32,
                                'penalty_area_length': 16.5, 'left_penalty': 11, 'right_penalty': 94,
                                'circle_size': 9.15, 'goal_depth': 2, 'goal_width': 7.32, 'goal_post': 30.34,
                                'arc1_leftV': 36.95, 'arc2_leftH': 53.05, 'invert_y': False, 'stripe_scale': 10}
      
    def __init__(self, figsize=None, layout=None, pitch_type='statsbomb', orientation='horizontal', view='full',
                 pitch_color=None, line_color=None, linewidth=2, line_zorder=0.9, background_zorder=0.8, stripe=False,
                 stripe_color='#c2d59d', pad_left=None, pad_right=None, pad_bottom=None, pad_top=None,
                 pitch_length=None, pitch_width=None, goal_type='line', label=False, tick=False, axis=False,
                 tight_layout=True, constrained_layout=False, spot_scale=0.002):

        # set figure and axes attributes
        self.axes = None
        self.fig = None
        self.figsize = figsize
        self.layout = layout
        self.axis = axis
        self.tick = tick
        self.label = label
        self.tight_layout = tight_layout
        self.constrained_layout = constrained_layout

        # set attributes
        self.line_color = line_color
        if self.line_color is None:
            self.line_color = rcParams["grid.color"]
        self.line_zorder = line_zorder
        self.background_zorder = background_zorder
        self.pitch_color = pitch_color
        if self.pitch_color is None:
            self.pitch_color = rcParams['axes.facecolor']
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.linewidth = linewidth
        self.pitch_type = pitch_type
        self.orientation = orientation
        self.view = view
        self.pad_left = pad_left
        self.pad_right = pad_right
        self.pad_bottom = pad_bottom
        self.pad_top = pad_top
        self.stripe = stripe
        self.stripe_color = stripe_color
        self.goal_type = goal_type
        self.spot_scale = spot_scale
        
        valid_pitch = ['statsbomb', 'stats', 'tracab', 'opta', 'wyscout', 'statsperform', 'metricasports']
        if self.pitch_type not in valid_pitch:
            raise TypeError(f'Invalid argument: pitch_type should be in {valid_pitch}')
        
        # set padding  
        if self.pad_left is None:
            if pitch_type != 'metricasports':
                self.pad_left = 4
            else:
                self.pad_left = 0.04
        if self.pad_right is None:
            if pitch_type != 'metricasports':
                self.pad_right = 4
            else:
                self.pad_right = 0.04
        if self.pad_bottom is None:
            if pitch_type != 'metricasports':
                self.pad_bottom = 4
            else:
                self.pad_bottom = 0.04
        if self.pad_top is None:
            if pitch_type != 'metricasports':
                self.pad_top = 4
            else:
                self.pad_top = 0.04

        # set pitch dimensions
        if pitch_type == 'opta':
            for k, v in self._opta_dimensions.items():
                setattr(self, k, v)
            self.pitch_length = 105
            self.pitch_width = 68
            self.aspect = 68 / 105

        elif pitch_type == 'wyscout':
            for k, v in self._wyscout_dimensions.items():
                setattr(self, k, v)
            self.pitch_length = 105
            self.pitch_width = 68
            self.aspect = 68 / 105

        elif pitch_type == 'statsbomb':
            for k, v in self._statsbomb_dimensions.items():
                setattr(self, k, v)
            self.pitch_length = self.length
            self.pitch_width = self.width
            self.aspect = 1

        elif pitch_type == 'stats':
            for k, v in self._stats_dimensions.items():
                setattr(self, k, v)
            self.pitch_length = self.length
            self.pitch_width = self.width
            self.aspect = 1
        
        elif pitch_type == 'statsperform':
            for k, v in self._statsperform_dimensions.items():
                setattr(self, k, v)
            self.pitch_length = self.length
            self.pitch_width = self.width
            self.aspect = 1

        elif pitch_type == 'tracab':
            for k, v in self._tracab_dimensions.items():
                setattr(self, k, v)
            if (pitch_length is None) or (pitch_width is None):
                raise TypeError("Invalid argument: pitch_length and pitch_width must be specified for a tracab pitch.")
            self.aspect = 1
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
            for k, v in self._metricasports_dimensions.items():
                setattr(self, k, v)
            if (pitch_length is None) or (pitch_width is None):
                raise TypeError("Invalid argument: pitch_length and pitch_width "
                                "must be specified for a metricasports pitch.")
            self.aspect = self.pitch_width/self.pitch_length
            self.six_yard_width = round(self.six_yard_width/self.pitch_width, 4)
            self.six_yard_length = round(self.six_yard_length/self.pitch_length, 4)
            self.six_yard_from_side = (self.width - self.six_yard_width)/2
            self.penalty_area_width = round(self.penalty_area_width/self.pitch_width, 4)
            self.penalty_area_length = round(self.penalty_area_length/self.pitch_length, 4)
            self.penalty_area_from_side = (self.width - self.penalty_area_width)/2
            self.left_penalty = round(self.left_penalty/self.pitch_length, 4)
            self.right_penalty = self.right - self.left_penalty
            self.goal_depth = round(self.goal_depth/self.pitch_length, 4)
            self.goal_width = round(self.goal_width/self.pitch_width, 4)
            self.goal_post = self.center_width - round(self.goal_post/self.pitch_width, 4)
                          
        # scale the padding where the aspect is not equal to one, reverse aspect if vertical
        if self.aspect != 1:
            if self.orientation == 'vertical':
                self.pad_bottom = self.pad_bottom * self.aspect
                self.pad_top = self.pad_top * self.aspect
                self.aspect = 1 / self.aspect
            elif self.orientation == 'horizontal':
                self.pad_left = self.pad_left * self.aspect
                self.pad_right = self.pad_right * self.aspect
       
        if pitch_color == 'grass':
            cm = LinearSegmentedColormap.from_list('grass', [(0.25, 0.44, 0.12, 1), (0.48, 1, 0.55, 1)], N=50)
            grass = cm(np.linspace(0, 1, 50))
            grass = np.concatenate((grass[::-1], grass))
            grass = grass[40:-20]
            self.grass_cmap = ListedColormap(grass)
            
        # pitch extent
        self.pitch_extent = [min(self.left, self.right), max(self.left, self.right),
                             min(self.bottom, self.top), max(self.bottom, self.top)]
        
        # set ax extents: [xmin, xmax, ymin, ymax]
        if self.invert_y:
            
            if self.orientation == 'horizontal':
                if self.view == 'full':
                    self.extent = [self.left - self.pad_left, self.right + self.pad_right,
                                   self.bottom + self.pad_bottom, self.top - self.pad_top]
                elif self.view == 'half':
                    self.extent = [self.center_length - self.pad_left, self.right + self.pad_right,
                                   self.bottom + self.pad_bottom, self.top - self.pad_top]
                    
            elif self.orientation == 'vertical':               
                if self.view == 'full':
                    self.extent = [self.top - self.pad_left, self.bottom + self.pad_right,
                                   self.left - self.pad_bottom, self.right + self.pad_top] 
                elif self.view == 'half':
                    self.extent = [self.top - self.pad_left, self.bottom + self.pad_right,
                                   self.center_length - self.pad_bottom, self.right + self.pad_top]              
                    
        else:
            
            if self.orientation == 'horizontal':                     
                if self.view == 'full':
                    self.extent = [self.left - self.pad_left, self.right + self.pad_right,
                                   self.bottom - self.pad_bottom, self.top + self.pad_top]
                elif self.view == 'half':
                    self.extent = [self.center_length - self.pad_left, self.right + self.pad_right,
                                   self.bottom - self.pad_bottom, self.top + self.pad_top]                 
                        
            elif self.orientation == 'vertical':
                if self.view == 'full':
                    self.extent = [self.top + self.pad_left, self.bottom - self.pad_right,
                                   self.left - self.pad_bottom, self.right + self.pad_top]
                elif self.view == 'half':
                    self.extent = [self.top + self.pad_left, self.bottom - self.pad_right,
                                   self.center_length - self.pad_bottom, self.right + self.pad_top]
                                    
        # data checks
        if not isinstance(self.axis, bool):
            raise TypeError("Invalid argument: axis should be bool (True or False).")                

        if not isinstance(self.stripe, bool):
            raise TypeError("Invalid argument: stripe should be bool (True or False).")

        if not isinstance(self.tick, bool):
            raise TypeError("Invalid argument: tick should be bool (True or False).")

        if not isinstance(self.label, bool):
            raise TypeError("Invalid argument: label should be bool (True or False).")

        if not isinstance(self.tight_layout, bool):
            raise TypeError("Invalid argument: tight_layout should be bool (True or False).")

        if (self.axis is False) and self.label:
            warnings.warn("Labels will not be shown unless axis=True")

        if (self.axis is False) and self.tick:
            warnings.warn("Ticks will not be shown unless axis=True")

        if ((self.pitch_type not in ['tracab', 'metricasports'])
                and ((pitch_length is not None) or (pitch_width is not None))):
            warnings.warn("Pitch length and widths are only used for tracab pitches and will be ignored")

        valid_orientation = ['horizontal', 'vertical']
        if self.orientation not in valid_orientation:
            raise TypeError(f'Invalid argument: orientation should be in {valid_orientation}')

        valid_goal_type = ['line', 'box']
        if self.goal_type not in valid_goal_type:
            raise TypeError(f'Invalid argument: goal_type should be in {valid_goal_type}')

        valid_view = ['full', 'half']
        if self.view not in valid_view:
            raise TypeError(f'Invalid argument: view should be in {valid_view}')
        
        # make sure padding not too large for the pitch
        if self.orientation == 'horizontal':                 
            if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.length:
                raise ValueError("pad_left/pad_right too negative for pitch length")
            if abs(min(self.pad_top, 0) + min(self.pad_bottom, 0)) >= self.width:
                raise ValueError("pad_top/pad_bottom too negative for pitch width")
            if self.view == 'half':
                if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.length/2:
                    raise ValueError("pad_left/pad_right too negative for pitch length")

        if self.orientation == 'vertical':
            if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.width:
                raise ValueError("pad_left/pad_right too negative for pitch width")
            if abs(min(self.pad_top, 0) + min(self.pad_bottom, 0)) >= self.length:
                raise ValueError("pad_top/pad_bottom too negative for pitch length")
            if self.view == 'half':
                if abs(min(self.pad_top, 0) + min(self.pad_bottom, 0)) >= self.length/2:
                    raise ValueError("pad_top/pad_bottom too negative for pitch length")
                    
        self.goal_right = np.array([[self.right, self.center_width - self.goal_width/2],
                                    [self.right, self.center_width + self.goal_width/2]])
        
        self.goal_left = np.array([[self.left, self.center_width - self.goal_width/2],
                                   [self.left, self.center_width + self.goal_width/2]])
        
        self.ax_aspect = abs(self.extent[0] - self.extent[1])/abs(self.extent[2]-self.extent[3])*self.aspect

    def _setup_subplots(self):

        if self.layout is None:
            nrows = 1
            ncols = 1
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=self.figsize,
                                     constrained_layout=self.constrained_layout)
            axes = np.array([axes])

        else:
            nrows, ncols = self.layout
            if nrows > 1 or ncols > 1:
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=self.figsize,
                                         constrained_layout=self.constrained_layout)
                axes = axes.ravel()
            else:
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=self.figsize,
                                         constrained_layout=self.constrained_layout)
                axes = np.array([axes])

        self.fig = fig
        self.axes = axes

    def _set_axes(self, ax):   
        # set axis on/off, and labels and ticks
        if self.axis:
            axis_option = 'on'
        elif not self.axis:
            axis_option = 'off'       
        ax.axis(axis_option) 
        ax.grid(False)
        ax.tick_params(top=self.tick, bottom=self.tick, left=self.tick, right=self.tick,
                       labelleft=self.label, labelbottom=self.label)
        # set limits and aspect
        ax.set_xlim(self.extent[0], self.extent[1])
        ax.set_ylim(self.extent[2], self.extent[3])
        ax.set_aspect(self.aspect)
             
    def _set_background(self, ax):
        if self.pitch_color != 'grass':
            ax.axhspan(self.extent[2], self.extent[3], 0, 1, facecolor=self.pitch_color, zorder=self.background_zorder)
            
        if (self.stripe is False) & (self.pitch_color == 'grass'):
            pitch_color = np.random.normal(size=(1000, 1000))
            ax.imshow(pitch_color, cmap=self.grass_cmap, extent=self.extent, aspect=self.aspect)
            
        if self.stripe:
            # calculate stripe length
            pitch_length = self.right - self.left
            stripe1_length = self.six_yard_length
            stripe2_length = (self.penalty_area_length - self.six_yard_length) / 2
            stripe3_length = (pitch_length - (
                self.penalty_area_length - self.six_yard_length) * 3 - self.six_yard_length * 2) / 10
            
            if self.pitch_color == 'grass':                   
                stripe1_length = int(self.stripe_scale*stripe1_length)
                stripe2_length = int(self.stripe_scale*stripe2_length)
                stripe3_length = int(self.stripe_scale*stripe3_length)
                s = int(self.stripe_scale*pitch_length)        
                
                if self.orientation == 'horizontal':
                    s = s + int((max(self.pad_left, 0) + max(self.pad_right, 0))*self.stripe_scale)
                    start = int(max(self.pad_left, 0) * self.stripe_scale)
                    if self.pad_left < 0:
                        slice1 = int(-self.pad_left * self.stripe_scale)
                    else:
                        slice1 = None
                    if self.pad_right < 0:
                        slice2 = int(self.pad_right * self.stripe_scale)
                    else:
                        slice2 = None
                    if self.pad_bottom < 0:
                        pitch_start = None
                    else:
                        pitch_start = int(s * self.pad_bottom/(self.pad_bottom+self.pad_top+self.width))
                    if self.pad_top < 0:
                        pitch_end = None
                    else:
                        pitch_end = s - int(s * self.pad_top/(self.pad_bottom+self.pad_top+self.width))
                                
                elif self.orientation == 'vertical':
                    s = s + int((max(self.pad_bottom, 0) + max(self.pad_top, 0))*self.stripe_scale)
                    start = int(max(self.pad_bottom, 0) * self.stripe_scale)
                    if self.pad_bottom < 0:
                        slice1 = int(-self.pad_bottom * self.stripe_scale)
                    else:
                        slice1 = None
                    if self.pad_top < 0:
                        slice2 = int(self.pad_top * self.stripe_scale)
                    else:
                        slice2 = None
                    if self.pad_left < 0:
                        pitch_start = None
                    else:
                        pitch_start = int(s * self.pad_left/(self.pad_left+self.pad_right+self.width))
                    if self.pad_right < 0:
                        pitch_end = None
                    else:
                        pitch_end = s - int(s * self.pad_right/(self.pad_left+self.pad_right+self.width))
                        
                # if half a pitch slice off half of the grass background
                if self.view == 'half':
                    if slice1 is not None:
                        slice1 = slice1 + int((self.length/2)*self.stripe_scale)
                    else:
                        slice1 = int((self.length/2)*self.stripe_scale)
                
                pitch_color = np.random.normal(size=(s, s))
            
            # calculate pitch width
            if self.invert_y:
                pitch_width = self.bottom - self.top
            else:
                pitch_width = self.top - self.bottom
                
            # calculate stripe start and end
            if self.orientation == 'vertical':
                total_width = pitch_width + self.pad_left + self.pad_right
                stripe_start = max(self.pad_left, 0) / total_width
                stripe_end = min((self.pad_left + pitch_width) / total_width, 1)
                
            elif self.orientation == 'horizontal':
                total_width = pitch_width + self.pad_bottom + self.pad_top
                stripe_start = max(self.pad_bottom, 0) / total_width
                stripe_end = min((self.pad_bottom + pitch_width) / total_width, 1)

            # draw stripes
            if self.pitch_color != 'grass':
                start = int(self.left)

            for stripe in range(1, 19):
                if stripe in [1, 18]:
                    end = round(start + stripe1_length, 4)
                elif stripe in [2, 3, 4, 15, 16, 17]:
                    end = round(start + stripe2_length, 4)
                else:
                    end = round(start + stripe3_length, 4)
                if (stripe % 2 == 1) & (self.orientation == 'vertical'):
                    if self.pitch_color != 'grass':
                        ax.axhspan(start, end, stripe_start, stripe_end, facecolor=self.stripe_color,
                                   zorder=self.background_zorder)
                    else:
                        pitch_color[start:end, pitch_start:pitch_end] = \
                            pitch_color[start:end, pitch_start:pitch_end] + 2
                        
                elif (stripe % 2 == 1) & (self.orientation == 'horizontal'):
                    if self.pitch_color != 'grass':
                        ax.axvspan(start, end, stripe_start, stripe_end, facecolor=self.stripe_color,
                                   zorder=self.background_zorder)
                    else:
                        pitch_color[pitch_start:pitch_end, start:end] = \
                            pitch_color[pitch_start:pitch_end:, start:end] + 2
                start = end
                
        # draw grass background
        if self.stripe & (self.pitch_color == 'grass'):
            if self.orientation == 'horizontal':
                pitch_color = pitch_color[:, slice1:slice2]
            elif self.orientation == 'vertical':
                pitch_color = pitch_color[slice1:slice2, :]
            ax.imshow(pitch_color, cmap=self.grass_cmap, extent=self.extent, aspect=self.aspect, origin='lower')
                
    def _draw_pitch_lines(self, ax):
        if self.orientation == 'horizontal':
            if self.invert_y:
                pitch_markings = patches.Rectangle((self.left, self.top), self.length, self.width,
                                                   fill=False, linewidth=self.linewidth, color=self.line_color,
                                                   zorder=self.line_zorder)
            else:
                pitch_markings = patches.Rectangle((self.left, self.bottom), self.length, self.width,
                                                   fill=False, linewidth=self.linewidth, color=self.line_color,
                                                   zorder=self.line_zorder)
            midline = lines.Line2D([self.center_length, self.center_length], [self.bottom, self.top],
                                   linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        elif self.orientation == 'vertical':
            if self.invert_y:
                pitch_markings = patches.Rectangle((self.top, self.left), self.width, self.length,
                                                   fill=False, linewidth=self.linewidth, color=self.line_color,
                                                   zorder=self.line_zorder)
            else:
                pitch_markings = patches.Rectangle((self.bottom, self.left), self.width, self.length,
                                                   fill=False, linewidth=self.linewidth, color=self.line_color,
                                                   zorder=self.line_zorder)
            midline = lines.Line2D([self.top, self.bottom], [self.center_length, self.center_length],
                                   linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        ax.add_patch(pitch_markings)
        ax.add_artist(midline)

    def _draw_goals(self, ax):
        if self.goal_type == 'box':
            if self.orientation == 'horizontal':
                goal1 = patches.Rectangle((self.right, self.goal_post), self.goal_depth, self.goal_width,
                                          fill=False, linewidth=self.linewidth, color=self.line_color, alpha=0.7,
                                          zorder=self.line_zorder)
                goal2 = patches.Rectangle((self.left - self.goal_depth, self.goal_post), self.goal_depth,
                                          self.goal_width,
                                          fill=False, linewidth=self.linewidth, color=self.line_color, alpha=0.7,
                                          zorder=self.line_zorder)
            elif self.orientation == 'vertical':
                goal1 = patches.Rectangle((self.goal_post, self.right), self.goal_width, self.goal_depth,
                                          fill=False, linewidth=self.linewidth, color=self.line_color, alpha=0.7,
                                          zorder=self.line_zorder)
                goal2 = patches.Rectangle((self.goal_post, self.left - self.goal_depth), self.goal_width,
                                          self.goal_depth,
                                          fill=False, linewidth=self.linewidth, color=self.line_color, alpha=0.7,
                                          zorder=self.line_zorder)
            ax.add_patch(goal1)
            ax.add_patch(goal2)

        elif self.goal_type == 'line':
            if self.orientation == 'horizontal':
                goal1 = lines.Line2D([self.right, self.right], [self.goal_post + self.goal_width, self.goal_post],
                                     linewidth=self.linewidth * 2, color=self.line_color, zorder=self.line_zorder)
                goal2 = lines.Line2D([self.left, self.left], [self.goal_post + self.goal_width, self.goal_post],
                                     linewidth=self.linewidth * 2, color=self.line_color, zorder=self.line_zorder)
            elif self.orientation == 'vertical':
                goal1 = lines.Line2D([self.goal_post + self.goal_width, self.goal_post], [self.right, self.right],
                                     linewidth=self.linewidth * 2, color=self.line_color, zorder=self.line_zorder)
                goal2 = lines.Line2D([self.goal_post + self.goal_width, self.goal_post], [self.left, self.left],
                                     linewidth=self.linewidth * 2, color=self.line_color, zorder=self.line_zorder)
            ax.add_artist(goal1)
            ax.add_artist(goal2)

    def _boxes(self, box_from_side, box_length, box_width, ax):
        if self.orientation == 'horizontal':
            box1 = patches.Rectangle((self.left, box_from_side), box_length, box_width, fill=False,
                                     linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
            box2 = patches.Rectangle((self.right - box_length, box_from_side), box_length, box_width,
                                     fill=False, linewidth=self.linewidth, color=self.line_color,
                                     zorder=self.line_zorder)
        elif self.orientation == 'vertical':
            box1 = patches.Rectangle((box_from_side, self.left), box_width, box_length, fill=False,
                                     linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
            box2 = patches.Rectangle((box_from_side, self.right - box_length), box_width, box_length, fill=False,
                                     linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        ax.add_patch(box1)
        ax.add_patch(box2)

    def _draw_boxes(self, ax):
        self._boxes(self.six_yard_from_side, self.six_yard_length, self.six_yard_width, ax)
        self._boxes(self.penalty_area_from_side, self.penalty_area_length, self.penalty_area_width, ax)

    def _draw_circles_and_arcs(self, ax):
        size_spot = self.spot_scale * self.length
        if self.orientation == 'vertical':
            xy = (self.center_width, self.center_length)
            center = (self.center_width, self.center_length)
            penalty1 = (self.center_width, self.left_penalty)
            penalty2 = (self.center_width, self.right_penalty)
            arc1_theta1 = self.arc1_leftV
            arc1_theta2 = 180 - self.arc1_leftV
            arc2_theta1 = 180 + self.arc1_leftV
            arc2_theta2 = 360 - self.arc1_leftV

        elif self.orientation == 'horizontal':
            xy = (self.center_length, self.center_width)
            center = (self.center_length, self.center_width)
            penalty1 = (self.left_penalty, self.center_width)
            penalty2 = (self.right_penalty, self.center_width)
            arc1_theta2 = self.arc2_leftH
            arc1_theta1 = 360 - self.arc2_leftH
            arc2_theta1 = 180 - self.arc2_leftH
            arc2_theta2 = 180 + self.arc2_leftH

        circle = patches.Circle(xy, self.circle_size, linewidth=self.linewidth, color=self.line_color, fill=False,
                                zorder=self.line_zorder)
        center_spot = patches.Circle(center, size_spot, color=self.line_color, zorder=self.line_zorder)
        penalty1_spot = patches.Circle(penalty1, size_spot, color=self.line_color, zorder=self.line_zorder)
        penalty2_spot = patches.Circle(penalty2, size_spot, color=self.line_color, zorder=self.line_zorder)
        arc1_patch = patches.Arc(penalty1, self.circle_size * 2, self.circle_size * 2,
                                 theta1=arc1_theta1, theta2=arc1_theta2,
                                 linewidth=self.linewidth, color=self.line_color, fill=False, zorder=self.line_zorder)
        arc2_patch = patches.Arc(penalty2, self.circle_size * 2, self.circle_size * 2,
                                 theta1=arc2_theta1, theta2=arc2_theta2,
                                 linewidth=self.linewidth, color=self.line_color, fill=False, zorder=self.line_zorder)
        ax.add_patch(circle)
        if self.spot_scale > 0:
            ax.add_patch(center_spot)
            ax.add_patch(penalty1_spot)
            ax.add_patch(penalty2_spot)
        ax.add_patch(arc1_patch)
        ax.add_patch(arc2_patch)

    def _draw_scaled_circles_and_arcs(self, ax):
        r1 = self.circle_size * self.width / self.pitch_width
        r2 = self.circle_size * self.length / self.pitch_length
        size_spot = self.spot_scale * self.pitch_length
        scaled_spot1 = size_spot * self.width / self.pitch_width
        scaled_spot2 = size_spot * self.length / self.pitch_length
        xy = (self.center_width, self.center_length)
        intersection = self.center_width - (
                    r1 * r2 * (r2 ** 2 - (self.penalty_area_length - self.left_penalty) ** 2) ** 0.5) / (r2 ** 2)

        if self.orientation == 'vertical':
            xy1 = (self.center_width + r1, self.center_length)
            xy2 = (self.center_width, self.center_length + r2)
            spot1 = (self.center_width, self.left_penalty)
            spot2 = (self.center_width, self.right_penalty)
            center_spot = (self.center_width, self.center_length)
            p1 = (self.center_width + scaled_spot1, self.left_penalty)
            p2 = (self.center_width, self.left_penalty + scaled_spot2)
            arc_pen_top1 = (intersection, self.penalty_area_length)

        elif self.orientation == 'horizontal':
            xy1 = (self.center_width + r2, self.center_length)
            xy2 = (self.center_width, self.center_length + r1)
            spot1 = (self.left_penalty, self.center_width)
            spot2 = (self.right_penalty, self.center_width)
            center_spot = (self.center_length, self.center_width)
            p2 = (self.left_penalty, self.center_width + scaled_spot1)
            p1 = (self.left_penalty + scaled_spot2, self.center_width)
            arc_pen_top1 = (self.penalty_area_length, intersection)

        def to_ax_coord(axes, coord_system, point):
            return coord_system.inverted().transform(axes.transData.transform_point(point))

        ax_coordinate_system = ax.transAxes
        ax_xy = to_ax_coord(ax, ax_coordinate_system, xy)
        ax_spot1 = to_ax_coord(ax, ax_coordinate_system, spot1)
        ax_spot2 = to_ax_coord(ax, ax_coordinate_system, spot2)
        ax_center = to_ax_coord(ax, ax_coordinate_system, center_spot)
        ax_xy1 = to_ax_coord(ax, ax_coordinate_system, xy1)
        ax_xy2 = to_ax_coord(ax, ax_coordinate_system, xy2)
        ax_p1 = to_ax_coord(ax, ax_coordinate_system, p1)
        ax_p2 = to_ax_coord(ax, ax_coordinate_system, p2)
        ax_arc_pen_top1 = to_ax_coord(ax, ax_coordinate_system, arc_pen_top1)
        diameter1 = (ax_xy1[0] - ax_xy[0]) * 2
        diameter2 = (ax_xy2[1] - ax_xy[1]) * 2
        diameter_spot1 = (ax_p1[0] - ax_spot1[0]) * 2
        diameter_spot2 = (ax_p2[1] - ax_spot1[1]) * 2

        if self.orientation == 'vertical':
            a = ax_spot1[0] - ax_arc_pen_top1[0]
            o = ax_arc_pen_top1[1] - ax_spot1[1]
            arc1_left = np.degrees(np.arctan(o / a))
            arc1_right = 180 - arc1_left
            arc2_left = 180 + arc1_left
            arc2_right = 360 - arc1_left

        elif self.orientation == 'horizontal':
            a = ax_arc_pen_top1[0] - ax_spot1[0]
            o = ax_spot1[1] - ax_arc_pen_top1[1]
            arc1_right = np.degrees(np.arctan(o / a))
            arc1_left = 360 - arc1_right
            arc2_left = 180 - arc1_right
            arc2_right = 180 + arc1_right

        circle = patches.Ellipse(ax_xy, diameter1, diameter2, transform=ax_coordinate_system, fill=False,
                                 linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        penalty_spot1 = patches.Ellipse(ax_spot1, diameter_spot1, diameter_spot2,
                                        transform=ax_coordinate_system,
                                        linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        penalty_spot2 = patches.Ellipse(ax_spot2, diameter_spot1, diameter_spot2,
                                        transform=ax_coordinate_system,
                                        linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        kick_off_spot = patches.Ellipse(ax_center, diameter_spot1, diameter_spot2,
                                        transform=ax_coordinate_system,
                                        linewidth=self.linewidth, color=self.line_color)
        arc1_patch = patches.Arc(ax_spot1, diameter1, diameter2, transform=ax_coordinate_system, fill=False,
                                 theta1=arc1_left, theta2=arc1_right,
                                 linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        arc2_patch = patches.Arc(ax_spot2, diameter1, diameter2, transform=ax_coordinate_system, fill=False,
                                 theta1=arc2_left, theta2=arc2_right,
                                 linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)

        if self.spot_scale > 0:
            ax.add_patch(penalty_spot1)
            ax.add_patch(penalty_spot2)
            ax.add_patch(kick_off_spot)
        ax.add_patch(circle)
        ax.add_patch(arc1_patch)
        ax.add_patch(arc2_patch)

    def _draw_ax(self, ax):
        self._set_axes(ax)
        self._set_background(ax)
        self._draw_pitch_lines(ax)
        if self.goal_type is not None:
            self._draw_goals(ax)
        self._draw_boxes(ax)
        if self.aspect == 1:
            self._draw_circles_and_arcs(ax)
        else:
            self._draw_scaled_circles_and_arcs(ax)

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
        Else plotted on existing axis and returns None.

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
            for ax in self.axes:
                self._draw_ax(ax)
            if self.axes.size == 1:
                self.axes = self.axes.item()
            return self.fig, self.axes
        else:
            self._draw_ax(ax)

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
        if ax is None:
            raise TypeError("plot() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")

        # plot. Reverse coordinates if vertical plot            
        if self.orientation == 'horizontal':
            plot = ax.plot(x, y, **kwargs)

        elif self.orientation == 'vertical':
            plot = ax.plot(y, x, **kwargs)
            
        return plot

    def kdeplot(self, x, y, ax=None, **kwargs):
        """ Utility wrapper around seaborn.kdeplot,
        which automatically flips the x and y coordinates if the pitch is vertical and clips to the pitch boundaries.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.

        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
            
        **kwargs : All other keyword arguments are passed on to seaborn.kdeplot.
            
        Returns
        -------            
        ax : matplotlib.axes
        """
        if ax is None:
            raise TypeError("kdeplot() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        # plot kde plot. reverse x and y if vertical
        if self.orientation == 'horizontal':
            clip = kwargs.pop('clip', ((self.left, self.right), (self.bottom, self.top)))
            kde = sns.kdeplot(x, y, ax=ax, clip=clip, **kwargs)
        elif self.orientation == 'vertical':
            clip = kwargs.pop('clip', ((self.top, self.bottom), (self.left, self.right)))
            kde = sns.kdeplot(y, x, ax=ax, clip=clip, **kwargs)
            
        return kde

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

        gridsize : int or (int, int), default: 20
            If a single int, the number of hexagons in the x-direction. The number of hexagons in the y-direction
            is chosen such that the hexagons are approximately regular.
            Alternatively, if a tuple (nx, ny), the number of hexagons in the x-direction and the y-direction.
            
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.hexbin.
            
        Returns
        -------
        polycollection : `~matplotlib.collections.PolyCollection`
            A `.PolyCollection` defining the hexagonal bins.

            - `.PolyCollection.get_offset` contains a Mx2 array containing
              the x, y positions of the M hexagon centers.
            - `.PolyCollection.get_array` contains the values of the M
              hexagons.

            If *marginals* is *True*, horizontal
            bar and vertical bar (both PolyCollections) will be attached
            to the return collection as attributes *hbar* and *vbar*.

        """
        if ax is None:
            raise TypeError("hexbin() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        mincnt = kwargs.pop('mincnt', 1)
        gridsize = kwargs.pop('gridsize', 20)

        # plot hexbin plot. reverse x and y if vertical
        if self.orientation == 'horizontal':
            extent = kwargs.pop('extent', (self.left, self.right, self.bottom, self.top))
            hexb = ax.hexbin(x, y, mincnt=mincnt, gridsize=gridsize, extent=extent, **kwargs)

        elif self.orientation == 'vertical':
            extent = kwargs.pop('extent', (self.top, self.bottom, self.left, self.right))
            hexb = ax.hexbin(y, x, mincnt=mincnt, gridsize=gridsize, extent=extent, **kwargs)
            
        return hexb
        
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
            and hexagons the color of the 'c' argument.

        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
            
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.
            
        Returns
        -------
        paths : matplotlib.collections.PathCollection or a tuple of (paths, paths) if marker='football'
        
        """
        if ax is None:
            raise TypeError("scatter() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
                   
        if marker is None:
            marker = rcParams['scatter.marker']
            
        # if using the football marker set the colors and lines, delete from kwargs so not used twice
        plot_football = False
        if marker == 'football':
            if rotation_degrees is not None:
                raise NotImplementedError("rotated football markers are not implemented.")
            plot_football = True
            linewidths = kwargs.pop('linewidths', 0.5)
            hexcolor = kwargs.pop('c', 'white')
            pentcolor = kwargs.pop('edgecolors', 'black')
            x = np.ma.ravel(x)
            y = np.ma.ravel(y)
            s = kwargs.pop('s', 500)

        if rotation_degrees is not None:
            x = np.ma.ravel(x)
            y = np.ma.ravel(y)
            rotation_degrees = np.ma.ravel(rotation_degrees)
            if x.size != y.size:
                raise ValueError("x and y must be the same size")
            if x.size != rotation_degrees.size:
                raise ValueError("x and rotation_degrees must be the same size")
                
            if not isinstance(rotation_degrees, (Sequence, np.ndarray)):
                # rotated counter clockwise - this makes it clockwise
                rotation_degrees = np.array(-rotation_degrees)
                if self.orientation == 'horizontal':
                    rotation_degrees = rotation_degrees - 90                    
                t = mmarkers.MarkerStyle(marker=marker)
                t._transform = t.get_transform().rotate_deg(rotation_degrees)
                markers = [t] 
            else:
                # rotated counter clockwise - this makes it clockwise with zero facing the direction of play
                rotation_degrees = -rotation_degrees
                if self.orientation == 'horizontal':
                    rotation_degrees = rotation_degrees - 90  
                markers = []
                for i in range(len(rotation_degrees)):
                    t = mmarkers.MarkerStyle(marker=marker)
                    t._transform = t.get_transform().rotate_deg(rotation_degrees[i])
                    markers.append(t)
                    
        # plot scatter. Reverse coordinates if vertical plot
        if self.orientation == 'horizontal':
            if plot_football:
                sc_hex = ax.scatter(x, y, edgecolors=pentcolor, c=hexcolor, linewidths=linewidths,
                                    marker=football_hexagon_marker, s=s, **kwargs)
                if 'label' in kwargs.keys():
                    Legend.update_default_handler_map({sc_hex: HandlerFootball()})
                    del kwargs['label']
                sc_pent = ax.scatter(x, y, edgecolors=pentcolor, c=pentcolor, linewidths=linewidths,
                                     marker=football_pentagon_marker, s=s, **kwargs)
                       
                sc = (sc_hex, sc_pent)
            elif rotation_degrees is not None:
                sc = _mscatter(x, y, markers=markers, ax=ax, **kwargs)
            else:
                sc = ax.scatter(x, y, marker=marker, **kwargs)

        elif self.orientation == 'vertical':
            if plot_football:
                sc_hex = ax.scatter(y, x, edgecolors=pentcolor, c=hexcolor, linewidths=linewidths,
                                    marker=football_hexagon_marker, s=s, **kwargs)
                if 'label' in kwargs.keys():
                    Legend.update_default_handler_map({sc_hex: HandlerFootball()})
                    del kwargs['label']
                sc_pent = ax.scatter(y, x, edgecolors=pentcolor, c=pentcolor, linewidths=linewidths,
                                     marker=football_pentagon_marker, s=s, **kwargs)
                sc = (sc_hex, sc_pent)
            elif rotation_degrees is not None:
                sc = _mscatter(y, x, markers=markers, ax=ax, **kwargs)
            else:
                sc = ax.scatter(y, x, marker=marker, **kwargs)

        return sc

    def _create_segments(self, xstart, ystart, xend, yend, n_segments):
        if self.orientation == 'horizontal':
            x = np.linspace(xstart, xend, n_segments + 1)
            y = np.linspace(ystart, yend, n_segments + 1)
        elif self.orientation == 'vertical':
            x = np.linspace(ystart, yend, n_segments + 1)
            y = np.linspace(xstart, xend, n_segments + 1)
        points = np.array([x, y]).T
        points = np.concatenate([points, np.expand_dims(points[:, -1, :], 1)], axis=1)
        points = np.expand_dims(points, 1)
        segments = np.concatenate([points[:, :, :-2, :], points[:, :, 1:-1, :], points[:, :, 2:, :]], axis=1)
        segments = np.transpose(segments, (0, 2, 1, 3)).reshape(-1, 3, 2)
        return segments

    def _create_transparent_cmap(self, color, n_segments, alpha_start, alpha_end):
        if self.orientation == 'horizontal':
            color = np.tile(np.array(color), (n_segments, 1))
            color = np.append(color, np.linspace(alpha_start, alpha_end, n_segments).reshape(-1, 1), axis=1)
            if self.invert_y:
                color = color[::-1]
            cmap = ListedColormap(color, name='line fade', N=n_segments)
        elif self.orientation == 'vertical':
            color = np.tile(np.array(color), (n_segments, 1))
            color = np.append(color, np.linspace(alpha_end, alpha_start, n_segments).reshape(-1, 1), axis=1)
            color = color[::-1]
            cmap = ListedColormap(color, name='line fade', N=n_segments)
        return cmap

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

        if ax is None:
            raise TypeError(
                "lines() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        if not isinstance(comet, bool):
            raise TypeError("Invalid argument: comet should be bool (True or False).")
            
        if not isinstance(transparent, bool):
            raise TypeError("Invalid argument: transparent should be bool (True or False).")
            
        if alpha_start < 0 or alpha_start > 1:
            raise TypeError("alpha_start values should be within 0-1 range")
            
        if alpha_end < 0 or alpha_end > 1:
            raise TypeError("alpha_end values should be within 0-1 range")  
            
        if 'colors' in kwargs.keys():
            warnings.warn("lines method takes 'color' as an argument, 'colors' in ignored")
            
        if alpha_start > alpha_end:
            warnings.warn("Alpha start > alpha end. The line will increase in transparency nearer to the end")
            
        if color is not None and cmap is not None:
            raise ValueError("Only use one of color or cmap arguments not both.")
            
        if 'lw' in kwargs.keys() and 'linewidth' in kwargs.keys():
            raise TypeError("lines got multiple values for 'linewidth' argument (linewidth and lw).")
            
        # set linewidth
        if 'lw' in kwargs.keys():
            lw = kwargs.pop('lw', 5)
        elif 'linewidth' in kwargs.keys():
            lw = kwargs.pop('linewidth', 5)
        else:
            lw = 5
        
        # to arrays
        xstart = np.ravel(xstart)
        ystart = np.ravel(ystart)
        xend = np.ravel(xend)
        yend = np.ravel(yend)
        lw = np.ravel(lw)
        
        if (comet or transparent) and (lw.size > 1):
            raise NotImplementedError("Multiple linewidths with a comet or transparent line is not implemented.")
            
        # set color
        if color is None:
            color = rcParams['lines.color']
            
        if (comet or transparent) and (cmap is None) and (to_rgba_array(color).shape[0] > 1):
            raise NotImplementedError("Multiple colors with a comet or transparent line is not implemented.")          
            
        if lw.size == 1:
            lw = lw[0]
            
        if xstart.size != ystart.size:
            raise ValueError("xstart and ystart must be the same size")
            
        if xstart.size != xend.size:
            raise ValueError("xstart and xend must be the same size")
            
        if ystart.size != yend.size:
            raise ValueError("ystart and yend must be the same size")     
            
        if (lw.size > 1) and (lw.size != xstart.size):
            raise ValueError("lw and xstart must be the same size")

        # set pitch array for line segments
        pitch_array = np.linspace(self.extent[2], self.extent[3], n_segments)
        
        # create segments
        if (transparent is False) and (comet is False) and (cmap is None):
            if self.orientation == 'horizontal':
                segments = np.transpose(np.array([[xstart, ystart], [xend, yend]]), (2, 0, 1))
            elif self.orientation == 'vertical':
                segments = np.transpose(np.array([[ystart, xstart], [yend, xend]]), (2, 0, 1))
        else:
            segments = self._create_segments(xstart, ystart, xend, yend, n_segments)
            
        # create linewidth
        if comet:
            lw = np.linspace(1, lw, n_segments)
        
        # set color map or color for transparent lines
        if transparent:
            handler_cmap = True
            if cmap is None:
                color = to_rgb(color)
                cmap = self._create_transparent_cmap(color, n_segments, alpha_start, alpha_end)
            else:
                if isinstance(cmap, str):
                    cmap = get_cmap(cmap)
                elif not isinstance(cmap, (ListedColormap, LinearSegmentedColormap)):
                    raise ValueError("cmap: not a recognised cmap type.")  
                
                cmap = cmap(np.linspace(0, 1, n_segments))
                
                # invert colour scheme if needed and add alpha channel
                if self.invert_y and self.orientation == 'horizontal':
                    cmap = cmap[::-1]
                    alpha_channel = np.linspace(alpha_end, alpha_start, n_segments)
                else:
                    alpha_channel = np.linspace(alpha_start, alpha_end, n_segments)  
                cmap[:, 3] = alpha_channel
                
                cmap = ListedColormap(cmap)
        
        # set color map or color for solid lines
        else:
            if cmap is not None:
                handler_cmap = True
                if isinstance(cmap, str):
                    cmap = get_cmap(cmap).reversed()
                if ((self.invert_y & (self.orientation == 'vertical')) |
                        (self.invert_y is False & (self.orientation == 'horizontal'))):
                    cmap = cmap.reversed()
            else:
                color = to_rgba_array(color)
                handler_cmap = False
                if (color.shape[0] > 1) and (color.shape[0] != xstart.size):
                    raise ValueError("xstart and color must be the same size")
                              
        # add line collection using cmap
        if cmap is not None:
            lc = LineCollection(segments, cmap=cmap, linewidth=lw, snap=False, **kwargs)
            lc.set_array(pitch_array)
        # add line collection using color (the set_array is not needed for colors)
        else:
            lc = LineCollection(segments, color=color, linewidth=lw, snap=False, **kwargs)
            
        lc = ax.add_collection(lc)
        
        # setup legend handler
        if self.orientation == 'horizontal' and self.invert_y:
            handler_invert_y = True
        else:
            handler_invert_y = False
        if comet:
            handler_first_lw = False
        else:
            handler_first_lw = True
        lc_handler = HandlerLines(numpoints=n_segments, invert_y=handler_invert_y, first_lw=handler_first_lw,
                                  use_cmap=handler_cmap)           
        Legend.update_default_handler_map({lc: lc_handler})
        
        return lc

    def polygon(self, verts, ax=None, **kwargs):
        """ Plot polygons using a PathCollection.
        See: https://matplotlib.org/3.1.1/api/collections_api.html
        
        Valid Collection keyword arguments:
            edgecolors: None
            facecolors: None
            linewidths: None
            antialiaseds: None
            offsets: None
            transOffset: transforms.IdentityTransform()
            norm: None (optional for matplotlib.cm.ScalarMappable)
            cmap: None (optional for matplotlib.cm.ScalarMappable)
            
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
        if ax is None:
            raise TypeError("polygon() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        verts = np.asarray(verts)
        patch_list = []
                
        for vert in verts:
            if self.orientation == 'vertical':
                vert = vert[:, [1, 0]].copy()
            polygon = patches.Polygon(vert, closed=True)
            patch_list.append(polygon)
        p = PatchCollection(patch_list, **kwargs)
        p = ax.add_collection(p)
        
        return p

    def goal_angle(self, x, y, ax=None, goal='right', **kwargs):
        """ Plot a polygon with the angle to the goal using PathCollection.
        See: https://matplotlib.org/3.1.1/api/collections_api.html
        
        Valid Collection keyword arguments:
            edgecolors: None
            facecolors: None
            linewidths: None
            antialiaseds: None
            offsets: None
            transOffset: transforms.IdentityTransform()
            norm: None (optional for matplotlib.cm.ScalarMappable)
            cmap: None (optional for matplotlib.cm.ScalarMappable)
            
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
        if ax is None:
            raise TypeError("goal_angle() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
        
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

    def voronoi(self, x, y, teams):
        """ Get Voronoi vertices for a set of coordinates.
        Uses a trick by Dan Nichol (@D4N__ on Twitter) where points are reflected in the pitch lines
        before calculating the Voronoi. This means that the Vornoi extends to the edges of the pitch
        see: https://github.com/ProformAnalytics/tutorial_nbs/blob/master/notebooks/Voronoi%20Reflection%20Trick.ipynb
        
        Players outside of the pitch dimensions are assumed to be standing on the pitch edge.
        This means that their coordinates are clipped to the pitch edges before calculating the Voronoi.        
            
        Parameters
        ----------
        x, y: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the coordinates on the pitch.
        
        team: array-like or scalar.
            This splits the results into the Voronoi vertices for each team.
            This can either have integer (1/0) values or boolean (True/False) values.
            team1 is where team==1 or team==True
            team2 is where team==0 or team==False
            
        Returns
        -------
        team1 : a 1d numpy array (length number of players in team 1) of 2d arrays
            Where the individual 2d arrays are coodinates of the Voronoi vertices.
            
        team2 : a 1d numpy array (length number of players in team 2) of 2d arrays
            Where the individual 2d arrays are coodinates of the Voronoi vertices.
        """
        x = np.ravel(x)
        y = np.ravel(y)
        teams = np.ravel(teams)
        
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
            
        if teams.size != x.size:
            raise ValueError("x and team must be the same size")
        
        # clip outside to pitch extents
        x = x.clip(min=self.pitch_extent[0], max=self.pitch_extent[1]).reshape(-1, 1)
        y = y.clip(min=self.pitch_extent[2], max=self.pitch_extent[3]).reshape(-1, 1)
        
        # reflect in pitch lines
        left = x.copy()
        right = x.copy()
        bottom = y.copy()
        top = y.copy()
        
        left = self.left - abs(left - self.left)
        right = self.right + abs(right - self.right)
        
        if self.invert_y:
            top = self.top - abs(top - self.top)
            bottom = self.bottom + abs(bottom - self.bottom)
        else:
            top = self.top + abs(top - self.top)
            bottom = self.bottom - abs(bottom - self.bottom)
        
        reflect = np.concatenate([np.concatenate([x, y], axis=1),
                                  np.concatenate([x, bottom], axis=1),
                                  np.concatenate([x, top], axis=1),
                                  np.concatenate([left, y], axis=1),
                                  np.concatenate([right, y], axis=1)])
        
        # create Voronoi
        vor = Voronoi(reflect)
        
        # get region vertices
        regions = vor.point_region[:x.size]
        regions = np.array(vor.regions)[regions]
        region_vertices = []
        for region in regions:
            verts = vor.vertices[region]
            verts[:, 0] = np.clip(verts[:, 0], a_min=self.pitch_extent[0], a_max=self.pitch_extent[1])
            verts[:, 1] = np.clip(verts[:, 1], a_min=self.pitch_extent[2], a_max=self.pitch_extent[3])
            region_vertices.append(verts)
        region_vertices = np.array(region_vertices)
        
        # seperate team1/ team2 vertices
        team1 = region_vertices[teams==1]
        team2 = region_vertices[teams==0]
        
        return team1, team2
        
    def arrows(self, xstart, ystart, xend, yend, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.quiver,
        Quiver uses locations and direction vectors usually. Here these are instead calculated automatically
        from the start and end points of the arrow.
        The function also automatically flips the x and y coordinates if the pitch is vertical.
        
        Plot a 2D field of arrows.
        See: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.quiver.html

        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the start and end coordinates of the lines.

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
        if ax is None:
            raise TypeError("quiver() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")

        # set so plots in data units
        units = kwargs.pop('units', 'dots')
        scale_units = kwargs.pop('scale_units', 'xy')
        angles = kwargs.pop('angles', 'xy')
        scale = kwargs.pop('scale', 1)
        width = kwargs.pop('width', 4)
        
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

        # vectors for direction
        u = xend - xstart
        v = yend - ystart

        # plot. Reverse coordinates if vertical plot            
        if self.orientation == 'horizontal':
            q = ax.quiver(xstart, ystart, u, v,
                          units=units, scale_units=scale_units, angles=angles, scale=scale,
                          width=width, **kwargs)

        elif self.orientation == 'vertical':
            q = ax.quiver(ystart, xstart, v, u,
                          units=units, scale_units=scale_units, angles=angles, scale=scale,
                          width=width, **kwargs)
            
        quiver_handler = HandlerQuiver()
        Legend.update_default_handler_map({q: quiver_handler})

        return q

    def jointplot(self, x, y, **kwargs):
        """ Utility wrapper around seaborn.jointplot
        which automatically flips the x and y coordinates if the pitch is vertical, sets the height from the figsize,
        and clips kernel density plots (kind = 'kde') to the pitch boundaries.
        
        Draw a plot of two variables with bivariate and univariate graphs.
        See: https://seaborn.pydata.org/generated/seaborn.jointplot.html
        
        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        
        **kwargs : All other keyword arguments are passed on to seaborn.jointplot.
            
        Returns
        -------
        grid : seaborn.axisgrid.JointGrid         
        """
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        if ('kind' in kwargs) and (kwargs['kind'] == 'kde'):
            if self.orientation == 'horizontal':
                clip = kwargs.pop('clip', ((self.left, self.right), (self.bottom, self.top)))
            elif self.orientation == 'vertical':
                clip = kwargs.pop('clip', ((self.top, self.bottom), (self.left, self.right)))
            
        # plot. Reverse coordinates if vertical plot 
        if self.orientation == 'horizontal':
            if ('kind' in kwargs) and (kwargs['kind'] == 'kde'):
                clip = kwargs.pop('clip', ((self.left, self.right), (self.bottom, self.top)))
                joint_plot = sns.jointplot(x, y, clip=clip, **kwargs)
            else:
                joint_plot = sns.jointplot(x, y, **kwargs)
            
        elif self.orientation == 'vertical':
            if ('kind' in kwargs) and (kwargs['kind'] == 'kde'):
                clip = kwargs.pop('clip', ((self.top, self.bottom), (self.left, self.right)))
                joint_plot = sns.jointplot(y, x, clip=clip, **kwargs)
            else:
                joint_plot = sns.jointplot(y, x, **kwargs)
                
        joint_plot_ax = joint_plot.ax_joint
        self.draw(ax=joint_plot_ax)

        return joint_plot
    
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
        if ax is None:
            raise TypeError("annotate() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
               
        if self.orientation == 'vertical':
            xy = xy[::-1]
            if xytext is not None:
                xytext = xytext[::-1]
                
        annotation = ax.annotate(text, xy, xytext, **kwargs)
        
        return annotation
    
    def bin_statistic(self, x, y, values=None, statistic='count', bins=(5, 4)):
        """ Calculates binned statistics using scipy.stats.binned_statistic_2d.
        
        This method automatically sets the range, changes some of the scipy defaults,
        and outputs the grids and centers for plotting.
        
        The default statistic has been changed to count instead of mean.
        The default bins has been set to (5,4).
        
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
                      
        if self.invert_y:
            pitch_range = [[self.left, self.right], [self.top, self.bottom]]
        else:
            pitch_range = [[self.left, self.right], [self.bottom, self.top]]
            
        result = binned_statistic_2d(x, y, values, statistic=statistic, bins=bins, range=pitch_range)
        
        x_grid, y_grid = np.meshgrid(result.x_edge, result.y_edge)
        cx, cy = np.meshgrid(result.x_edge[:-1] + 0.5 * np.diff(result.x_edge),
                             result.y_edge[:-1] + 0.5 * np.diff(result.y_edge))

        bin_statistic = _BinnedStatisticResult(result.statistic, x_grid, y_grid, cx, cy)._asdict()
        
        return bin_statistic
              
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
        if ax is None:
            raise TypeError("heatmap() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
               
        if self.orientation == 'horizontal':
            mesh = ax.pcolormesh(bin_statistic['x_grid'].T, bin_statistic['y_grid'].T,
                                 bin_statistic['statistic'], **kwargs)
            
        elif self.orientation == 'vertical':
            mesh = ax.pcolormesh(bin_statistic['y_grid'].T, bin_statistic['x_grid'].T, 
                                 bin_statistic['statistic'], **kwargs)
            
        return mesh
            
    def bin_statistic_positional(self, x, y, values=None, positional='full', statistic='count'):
        """ Calculates binned statistics for the Juegos de posición (position game) concept.
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
        # x positions
        x1 = min(self.left, self.right)
        x4 = self.center_length
        x7 = max(self.left, self.right)
        x2 = x1 + self.penalty_area_length
        x6 = x7 - self.penalty_area_length
        x3 = x2 + (x4 - x2)/2
        x5 = x4 + (x6 - x4)/2
        
        # y positions
        y1 = min(self.bottom, self.top)
        y6 = max(self.bottom, self.top)
        if self.pitch_type == 'tracab':
            y2 = self.penalty_area_from_side
            y3 = self.six_yard_from_side
            y4 = -self.six_yard_from_side
            y5 = -self.penalty_area_from_side
        else:    
            y3 = y1 + self.six_yard_from_side
            y2 = y1 + self.penalty_area_from_side
            y4 = y6 - self.six_yard_from_side
            y5 = y6 - self.penalty_area_from_side
            y4 = y6 - self.six_yard_from_side
        
        # I tried several ways of creating positional bins. It's hard to do this because
        # of points on the edges of bins. You have to be sure they are only counted once consistently
        # I tried doing this by adding or subtracting a small value near the edges, but it didn't work for all cases
        # I settled on this idea, which is to create binned statistics with an additional row, column either
        # side (unless the side of the pitch) so that the scipy binned_statistic_2d functions handles the edges
        if positional == 'full':
            # top and bottom of pitch - we create a grid with three rows and then ignore the middle row when slicing
            xedge = np.array([x1, x2, x3, x4, x5, x6, x7])
            yedge = np.array([y1, y2, y5, y6])
            bin_statistic1 = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            stat1 = bin_statistic1['statistic']
            x_grid1 = bin_statistic1['x_grid']
            y_grid1 = bin_statistic1['y_grid']
            cx1 = bin_statistic1['cx']
            cy1 = bin_statistic1['cy']

            # slicing second row            
            stat2 = stat1[:, 2].reshape(-1, 1).copy()
            x_grid2 = x_grid1[2:, :].copy()
            y_grid2 = y_grid1[2:, :].copy()
            cx2 = cx1[2, :].copy()
            cy2 = cy1[2, :].copy()
            # slice first row
            stat1 = stat1[:, 0].reshape(-1, 1).copy()
            x_grid1 = x_grid1[:2, :].copy()
            y_grid1 = y_grid1[:2, :].copy()
            cx1 = cx1[0, :].copy()
            cy1 = cy1[0, :].copy()

            # middle of pitch
            xedge = np.array([x1, x2, x4, x6, x7])
            yedge = np.array([y1, y2, y3, y4, y5, y6])
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
            
            # penalty area 1
            xedge = np.array([x1, x2, x3]).astype(np.float64)
            yedge = np.array([y2, y5, y6]).astype(np.float64)
            bin_statistic4 = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            stat4 = bin_statistic4['statistic']
            x_grid4 = bin_statistic4['x_grid']
            y_grid4 = bin_statistic4['y_grid']
            cx4 = bin_statistic4['cx']
            cy4 = bin_statistic4['cy']
            stat4 = stat4[:-1, :-1]
            x_grid4 = x_grid4[:-1, :-1].copy()
            y_grid4 = y_grid4[:-1, :-1].copy()
            cx4 = cx4[:1, :1].copy()
            cy4 = cy4[:1, :1].copy()
            
            # penalty area 2
            xedge = np.array([x6, x7]).astype(np.float64)
            yedge = np.array([y2, y5, y6]).astype(np.float64)
            bin_statistic5 = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            stat5 = bin_statistic5['statistic']
            x_grid5 = bin_statistic5['x_grid']
            y_grid5 = bin_statistic5['y_grid']
            cx5 = bin_statistic5['cx']
            cy5 = bin_statistic5['cy']
            stat5 = stat5[:, :-1]
            x_grid5 = x_grid5[:-1, :].copy()
            y_grid5 = y_grid5[:-1, :].copy()
            cy5 = cy5[0].copy()
            cx5 = cx5[0].copy()
                        
            # collect stats
            result1 = _BinnedStatisticResult(stat1, x_grid1, y_grid1, cx1, cy1)._asdict()
            result2 = _BinnedStatisticResult(stat2, x_grid2, y_grid2, cx2, cy2)._asdict()
            result3 = _BinnedStatisticResult(stat3, x_grid3, y_grid3, cx3, cy3)._asdict()
            result4 = _BinnedStatisticResult(stat4, x_grid4, y_grid4, cx4, cy4)._asdict()
            result5 = _BinnedStatisticResult(stat5, x_grid5, y_grid5, cx5, cy5)._asdict()
            
            bin_statistic = [result1, result2, result3, result4, result5]    
            
        elif positional == 'horizontal':
            xedge = np.array([x1, x7])
            yedge = np.array([y1, y2, y3, y4, y5, y6])
            bin_horizontal = self.bin_statistic(x, y, values, statistic=statistic, bins=(xedge, yedge))
            bin_statistic = [bin_horizontal]
            
        elif positional == 'vertical':
            xedge = np.array([x1, x2, x3, x4, x5, x6, x7])
            yedge = np.array([y1, y6])
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
        if ax is None:
            raise TypeError("label_heatmap() missing 1 required argument:"
                            " ax. A Matplotlib axis is required for plotting.")
        vmax = kwargs.pop('vmax', np.array([stat['statistic'].max() for stat in bin_statistic]).max())
        vmin = kwargs.pop('vmin', np.array([stat['statistic'].min() for stat in bin_statistic]).min())
        
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
        
        if ax is None:
            raise TypeError("label_heatmap() missing 1 required argument: "
                            "ax. A Matplotlib axis is required for plotting.")
            
        if not isinstance(bin_statistic, list):
            bin_statistic = [bin_statistic]
    
        annotation_list = []
        for bs in bin_statistic:
            # remove labels outside the plot extents
            if self.orientation == 'horizontal':
                mask_x_outside = (bs['cx'] < min(self.extent[0], self.extent[1])) |\
                                 (bs['cx'] > max(self.extent[0], self.extent[1]))
                mask_y_outside = (bs['cy'] < min(self.extent[2], self.extent[3])) |\
                                 (bs['cy'] > max(self.extent[2], self.extent[3]))
            else:
                mask_x_outside = (bs['cx'] < min(self.extent[2], self.extent[3])) |\
                                 (bs['cx'] > max(self.extent[2], self.extent[3]))
                mask_y_outside = (bs['cy'] < min(self.extent[0], self.extent[1])) |\
                                 (bs['cy'] > max(self.extent[0], self.extent[1]))
            mask_clip = mask_x_outside | mask_y_outside
            mask_clip = np.ravel(mask_clip)
            
            text = np.ravel(bs['statistic'].T)[~mask_clip]
            cx = np.ravel(bs['cx'])[~mask_clip]
            cy = np.ravel(bs['cy'])[~mask_clip]
            for i in range(len(text)):
                annotation = self.annotate(text[i], (cx[i], cy[i]), ax=ax, **kwargs)
                annotation_list.append(annotation)
            
        return annotation_list


# Amended from
# https://stackoverflow.com/questions/49223702/adding-a-legend-to-a-matplotlib-plot-with-a-multicolored-line?rq=1
class HandlerLines(HandlerLineCollection):
    """Automatically generated by Pitch.lines() to allow use of linecollection in legend."""
    
    def __init__(self, invert_y=False, first_lw=False, use_cmap=False, marker_pad=0.3, numpoints=None, **kw):
        HandlerLineCollection.__init__(self, marker_pad=marker_pad, numpoints=numpoints, **kw)
        self.invert_y = invert_y
        self.first_lw = first_lw
        self.use_cmap = use_cmap
    
    def create_artists(self, legend, artist, xdescent, ydescent,
                       width, height, fontsize, trans):
        x = np.linspace(0, width, self.get_numpoints(legend)+1)
        y = np.zeros(self.get_numpoints(legend) + 1)+height/2.-ydescent
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lw = artist.get_linewidth()
        if self.first_lw:
            lw = lw[0]
        if self.use_cmap:
            cmap = artist.cmap
            if self.invert_y:
                cmap = cmap.reversed()
            lc = LineCollection(segments, lw=lw, cmap=cmap, snap=False, transform=trans)
            lc.set_array(x)
        else:
            lc = LineCollection(segments, lw=lw, colors=artist.get_colors()[0], snap=False, transform=trans)
        return [lc]
    
    
class HandlerFootball(HandlerPathCollection):   
    """Automatically generated by Pitch.scatter() to allow use of football marker in legend."""
    def create_collection(self, orig_handle, sizes, offsets, transOffset):
        edgecolor = orig_handle.get_edgecolor()[0]
        facecolor = orig_handle.get_facecolor()[0]
        sizes = [size*0.249 for size in sizes]
        p = type(orig_handle)([football_hexagon_marker, football_pentagon_marker],
                              sizes=sizes,
                              offsets=offsets,
                              transOffset=transOffset,
                              facecolors=[facecolor, edgecolor],
                              edgecolors=edgecolor)
        return p
    
    def _default_update_prop(self, legend_handle, orig_handle):
        facecolor = legend_handle.get_facecolor()
        edgecolor = legend_handle.get_edgecolor()
        legend_handle.update_from(orig_handle)
        legend_handle.set_facecolor(facecolor)
        legend_handle.set_edgecolor(edgecolor)

        
class HandlerQuiver(HandlerLine2D):
    """Automatically generated by Pitch.quiver() to allow use of arrows in legend."""
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent, width, height, fontsize)
        ydata = ((height - ydescent) / 2.) * np.ones(xdata.shape, float)
        head_width = orig_handle.width * orig_handle.headwidth
        head_length = orig_handle.width * orig_handle.headlength
        overhang = (orig_handle.headlength - orig_handle.headaxislength)/orig_handle.headlength
        edgecolor = orig_handle.get_edgecolor()
        facecolor = orig_handle.get_facecolor()
        if len(edgecolor) == 0:
            edgecolor = None
        else:
            edgecolor = edgecolor[0]
        if len(facecolor) == 0:
            facecolor = None
        else:
            facecolor = facecolor[0]
        legline = patches.FancyArrow(x=xdata[0],
                                     y=ydata[0],
                                     dx=xdata[-1]-xdata[0],
                                     dy=ydata[-1]-ydata[0],
                                     head_width=head_width,
                                     head_length=head_length,
                                     overhang=overhang,
                                     length_includes_head=True,
                                     width=orig_handle.width,
                                     lw=orig_handle.get_linewidths()[0],
                                     edgecolor=edgecolor,
                                     facecolor=facecolor)
        legline.set_transform(trans)
        return [legline]

    
def add_image(image, fig, left, bottom, width=None, height=None, **kwargs):
    """ Adds an image to a figure using fig.add_axes and ax.imshow
    
    Recommended additional keyword arguments for imshow
        interpolation str, optional
            'hamming' is recommended for images that are reduced in size
                    
        alpha scalar or array-like, optional
            The alpha blending value, between 0 (transparent) and 1 (opaque).
            
    Parameters
    ----------
    image: array-like or PIL image
        The image data.
        
    fig: matplotlib.
        A matplotlib.figure.Figure
        
    left, bottom: float
        The dimensions left, bottom of the new axes. All quantities are in fractions of figure width and height.
        This positions the image axis in the figure left% in from the figure side 
        and bottom% in from the figure bottom.
        
    width, height: float
        The width, height of the new axes. All quantities are in fractions of figure width and height.
        For best results use only one of these so the image is scaled appropriately.
        
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.
    
    Returns
    -------            
    ax : matplotlib.axes        
    """
    image_height, image_width, _ = np.array(image).shape       
    image_aspect = image_width / image_height
    
    figsize = fig.get_size_inches()
    fig_aspect = figsize[0] / figsize[1]
    
    if height is None:
        height = width / image_aspect * fig_aspect
    
    if width is None:
        width = height*image_aspect/fig_aspect
        
    ax_image = fig.add_axes((left, bottom, width, height))
    ax_image.axis('off')  # axis off so no labels/ ticks
    
    img = ax_image.imshow(image, **kwargs)
    
    return ax_image
