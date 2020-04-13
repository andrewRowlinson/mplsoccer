""" `mplsoccer.pitch` is a python module for plotting soccer / football pitches in Matplotlib. """

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import matplotlib.lines as lines
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.markers as mmarkers
import numpy as np
import seaborn as sns
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import to_rgb
from matplotlib import rcParams
from scipy.stats import binned_statistic_2d
from .utils import football_hexagon_marker, football_pentagon_marker, _mscatter
from collections import Sequence, namedtuple
import warnings

BinnedStatisticResult = namedtuple('BinnedStatisticResult',
                                   ('statistic', 'x_grid', 'y_grid', 'cx', 'cy'))

class Pitch(object):
    """ A class for plotting soccer / football pitches in Matplotlib
    
    Parameters
    ----------
    figsize : tuple of float, default Matplotlib figure size
        The figure size in inches by default.
    layout : tuple of int, default (1,1)
        Tuple of (rows, columns) for the layout of the plot.
    pitch_type : str, default 'statsbomb'
        The pitch type used in the plot.
        The supported pitch types are: 'opta', 'statsbomb', 'tracab', 'stats', 'wyscout', 'statsperform', 'metricasports'.
    orientation : str, default 'horizontal'
        The pitch orientation: 'horizontal' or 'vertical'.
    view : str, default 'full'
        The pitch view: 'full' or 'half'.
    pitch_color : any Matplotlib color, default '#aabb97'
        The background color for each Matplotlib axis.
    line_color : any Matplotlib color, default 'white'
        The line color for the pitch markings.
    line_zorder : float, default 1
        Set the zorder for the pitch lines (a matplotlib artist). Artists with lower zorder values are drawn first.
    linewidth : float, default 2
        The line width for the pitch markings.
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
    tight_layout : bool, default False
        Whether to use Matplotlib's tight layout.
    constrained_layout : bool, default True
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
                                 'penalty_area_from_side': None, 'penalty_area_width': 40.32, 'penalty_area_length': 16.5,
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
                 pitch_color='#aabb97', line_color='white', line_zorder=1, linewidth=2, stripe=False, stripe_color='#c2d59d',
                 pad_left=None, pad_right=None, pad_bottom=None, pad_top=None, pitch_length=None, pitch_width=None,
                 goal_type='line', label=False, tick=False, axis=False, tight_layout=False, constrained_layout=True):

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
        self.line_zorder = line_zorder
        self.pitch_color = pitch_color
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
                raise TypeError("Invalid argument: pitch_length and pitch_width must be specified for a metricasports pitch.")
            self.aspect = self.pitch_width/self.pitch_length
            self.six_yard_width = round(self.six_yard_width/self.pitch_width,4)
            self.six_yard_length = round(self.six_yard_length/self.pitch_length,4)
            self.six_yard_from_side = (self.width - self.six_yard_width)/2
            self.penalty_area_width = round(self.penalty_area_width/self.pitch_width,4)
            self.penalty_area_length = round(self.penalty_area_length/self.pitch_length,4)
            self.penalty_area_from_side = (self.width - self.penalty_area_width)/2
            self.left_penalty = round(self.left_penalty/self.pitch_length,4)
            self.right_penalty = self.right - self.left_penalty
            self.goal_depth = round(self.goal_depth/self.pitch_length,4)
            self.goal_width = round(self.goal_width/self.pitch_width,4)
            self.goal_post = self.center_width - round(self.goal_post/self.pitch_width,4)
                          
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
        
        # set pitch extents: [xmin, xmax, ymin, ymax]
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

        valid_pitch = ['statsbomb', 'stats', 'tracab', 'opta', 'wyscout', 'statsperform', 'metricasports']
        if self.pitch_type not in valid_pitch:
            raise TypeError(f'Invalid argument: pitch_type should be in {valid_pitch}')

        if (self.axis is False) and self.label:
            warnings.warn("Labels will not be shown unless axis=True")

        if (self.axis is False) and self.tick:
            warnings.warn("Ticks will not be shown unless axis=True")

        if (self.pitch_type not in ['tracab','metricasports']) and ((pitch_length is not None) or (pitch_width is not None)):
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
        ax.tick_params(top=self.tick, bottom=self.tick, left=self.tick, right=self.tick,
                       labelleft=self.label, labelbottom=self.label)
        # set limits and aspect
        ax.set_xlim(self.extent[0], self.extent[1])
        ax.set_ylim(self.extent[2], self.extent[3])
        ax.set_aspect(self.aspect)
             
    def _set_background(self, ax):
        if self.pitch_color != 'grass':
            ax.axhspan(self.extent[2], self.extent[3], 0, 1, facecolor=self.pitch_color)
            
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
                        ax.axhspan(start, end, stripe_start, stripe_end, facecolor=self.stripe_color)
                    else:
                        pitch_color[start:end, pitch_start:pitch_end] = \
                            pitch_color[start:end, pitch_start:pitch_end] + 2
                        
                elif (stripe % 2 == 1) & (self.orientation == 'horizontal'):
                    if self.pitch_color != 'grass':
                        ax.axvspan(start, end, stripe_start, stripe_end, facecolor=self.stripe_color)
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
            box1 = patches.Rectangle((self.left, box_from_side), box_length, box_width,
                                     fill=False, linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
            box2 = patches.Rectangle((self.right - box_length, box_from_side), box_length, box_width,
                                     fill=False, linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        elif self.orientation == 'vertical':
            box1 = patches.Rectangle((box_from_side, self.left), box_width, box_length,
                                     fill=False, linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
            box2 = patches.Rectangle((box_from_side, self.right - box_length), box_width, box_length,
                                     fill=False, linewidth=self.linewidth, color=self.line_color, zorder=self.line_zorder)
        ax.add_patch(box1)
        ax.add_patch(box2)

    def _draw_boxes(self, ax):
        self._boxes(self.six_yard_from_side, self.six_yard_length, self.six_yard_width, ax)
        self._boxes(self.penalty_area_from_side, self.penalty_area_length, self.penalty_area_width, ax)

    def _draw_circles_and_arcs(self, ax):
        size_spot = 0.005 * self.length
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
        ax.add_patch(center_spot)
        ax.add_patch(penalty1_spot)
        ax.add_patch(penalty2_spot)
        ax.add_patch(arc1_patch)
        ax.add_patch(arc2_patch)

    def _draw_scaled_circles_and_arcs(self, ax):
        r1 = self.circle_size * self.width / self.pitch_width
        r2 = self.circle_size * self.length / self.pitch_length
        scaled_spot1 = self.length / (2 * self.pitch_width)
        scaled_spot2 = self.length / (2 * self.pitch_length)
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
            lines = ax.plot(x, y, **kwargs)

        elif self.orientation == 'vertical':
            lines = ax.plot(y, x, **kwargs)
            
        return lines

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

        # rise kdeplot above background/ stripes (the axhspan/axvspan have the same zorder as the kdeplot)
        zorder = kwargs.pop('zorder', 2)

        # plot kde plot. reverse x and y if vertical
        if self.orientation == 'horizontal':
            clip = kwargs.pop('clip', ((self.left, self.right), (self.bottom, self.top)))
            kde = sns.kdeplot(x, y, ax=ax, clip=clip, zorder=zorder, **kwargs)
        elif self.orientation == 'vertical':
            clip = kwargs.pop('clip', ((self.top, self.bottom), (self.left, self.right)))
            kde = sns.kdeplot(y, x, ax=ax, clip=clip, zorder=zorder, **kwargs)
            
        return kde

    def hexbin(self, x, y, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.hexbin,
        which automatically flips the x and y coordinates if the pitch is vertical.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.

        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
            
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

        # rise hexbin above background/ stripes (the axhspan/axvspan have the same zorder as the hexbin)
        zorder = kwargs.pop('zorder', 2)
        mincnt = kwargs.pop('mincnt', 1)
        cmap = kwargs.pop('cmap', 'rainbow')
        gridsize = kwargs.pop('gridsize', 20)

        # plot hexbin plot. reverse x and y if vertical
        if self.orientation == 'horizontal':
            extent = kwargs.pop('extent', (self.left, self.right, self.bottom, self.top))
            hexb = ax.hexbin(x, y, zorder=zorder, mincnt=mincnt, gridsize=gridsize, extent=extent, cmap=cmap, **kwargs)

        elif self.orientation == 'vertical':
            extent = kwargs.pop('extent', (self.top, self.bottom, self.left, self.right))
            hexb = ax.hexbin(y, x, zorder=zorder, mincnt=mincnt, gridsize=gridsize, extent=extent, cmap=cmap, **kwargs)
            
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

        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
            
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.
            
        Returns
        -------
        paths : matplotlib.collections.PathCollection
        
        """
        if ax is None:
            raise TypeError("scatter() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
        
        if marker is None:
            marker = rcParams['scatter.marker']

        # rise scatter above background/ stripes (the axhspan/axvspan have the same zorder as the scatter)
        zorder = kwargs.pop('zorder', 2)

        # if using the football marker set the colors and lines, delete from kwargs so not used twice
        plot_football = False
        if marker == 'football':
            if rotation_degrees is not None:
                raise NotImplementedError("rotated football markers are not implemented.")
            plot_football = True
            linewidths = kwargs.pop('linewidths', 0.5)
            hexcolor = kwargs.pop('c', 'white')
            pentcolor = kwargs.pop('edgecolors', 'black')
            n = len(x)
            x = np.repeat(x, 2).copy()
            y = np.repeat(y, 2).copy()
            paths = np.tile([football_hexagon_marker, football_pentagon_marker], n)
            c = np.tile([hexcolor, pentcolor], n)
            # to make the football the same size as the circle marker we need to expand it
            # the markers are a different shape and this is the easiest way to make them similar
            expansion_factor = 0.249
            s = kwargs.pop('s', 400)
            s = s * expansion_factor
        
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
                sc = ax.scatter(x, y, c=c, edgecolors=pentcolor, s=s,
                                linewidths=linewidths, zorder=zorder, **kwargs)
                sc.set_paths(paths)
            elif rotation_degrees is not None:
                sc = _mscatter(x, y, zorder=zorder, markers=markers, ax=ax, **kwargs)
            else:
                sc = ax.scatter(x, y, zorder=zorder, **kwargs)

        elif self.orientation == 'vertical':
            if plot_football:
                sc = ax.scatter(y, x, c=c, edgecolors=pentcolor, s=s,
                                linewidths=linewidths, zorder=zorder, **kwargs)
                sc.set_paths(paths)
            elif rotation_degrees is not None:
                sc = _mscatter(y, x, zorder=zorder, markers=markers, ax=ax, **kwargs)
            else:
                sc = ax.scatter(y, x, zorder=zorder, **kwargs)

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

    def _create_transparent_cmap(self, color, n_segments):
        if self.orientation == 'horizontal':
            color = np.tile(np.array(color), (n_segments, 1))
            color = np.append(color, np.linspace(0.1, 0.5, n_segments).reshape(-1, 1), axis=1)
            if self.invert_y:
                color = color[::-1]
            cmap = ListedColormap(color, name='line fade', N=n_segments)
        elif self.orientation == 'vertical':
            color = np.tile(np.array(color), (n_segments, 1))
            color = np.append(color, np.linspace(0.5, 0.1, n_segments).reshape(-1, 1), axis=1)
            color = color[::-1]
            cmap = ListedColormap(color, name='line fade', N=n_segments)
        return cmap

    def lines(self, xstart, ystart, xend, yend, n_segments=100, comet=False, transparent=False, ax=None, **kwargs):
        """ Plots lines using matplotlib.collections.LineCollection.
        This is a fast way to plot multiple lines without loops.

        Also enables lines that increase in width or opacity by splitting the line into n_segments of increasing
        width or opacity as the line progresses.

        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the start and end coordinates of the lines.

        n_segments : int, default 100
            If comet=True or transparent=True this is used to split the line
            into n_segments of increasing width/opacity.

        comet : bool default False
            Whether to plot the lines increasing in width.

        transparent : bool, default False
            Whether to plot the lines increasing in opacity.
            
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
            
        lw = kwargs.pop('lw', 5)
        color = kwargs.pop('color', '#34afed')
        color = to_rgb(color)

        # set pitch array for line segments
        pitch_array = np.linspace(self.extent[2], self.extent[3], n_segments)

        # set color map, lw and segments
        if transparent and comet:
            cmap = self._create_transparent_cmap(color, n_segments)
            lw = np.linspace(1, lw, n_segments)
            segments = self._create_segments(xstart, ystart, xend, yend, n_segments)

        elif transparent and (comet is False):
            cmap = self._create_transparent_cmap(color, n_segments)
            segments = self._create_segments(xstart, ystart, xend, yend, n_segments)

        elif (transparent is False) and comet:
            lw = np.linspace(1, lw, n_segments)
            cmap = ListedColormap([color], name='single color', N=n_segments)
            segments = self._create_segments(xstart, ystart, xend, yend, n_segments)

        elif (transparent is False) and (comet is False):
            cmap = ListedColormap([color], name='single color', N=n_segments)
            if self.orientation == 'horizontal':
                segments = np.transpose(np.array([[xstart, ystart], [xend, yend]]), (2, 0, 1))
            elif self.orientation == 'vertical':
                segments = np.transpose(np.array([[ystart, xstart], [yend, xend]]), (2, 0, 1))

        # add line collection
        lc = LineCollection(segments, cmap=cmap, linewidth=lw, snap=False, **kwargs)
        lc.set_array(pitch_array)
        lc = ax.add_collection(lc)
        
        return lc

    def quiver(self, xstart, ystart, xend, yend, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.quiver,
        Quiver uses locations and directions usually. Here these are instead calculated automatically
        from the start and end points of the arrow.
        The function also automatically flips the x and y coordinates if the pitch is vertical.
        
        Plot a 2D field of arrows.
        see: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.quiver.html

        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the start and end coordinates of the lines.

        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
            
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.quiver.
            
        Returns
        -------
        PolyCollection : matplotlib.quiver.Quiver   
        """
        if ax is None:
            raise TypeError("quiver() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")

        # rise quiver above background/ stripes (the axhspan/axvspan have the same zorder as the quiver)
        zorder = kwargs.pop('zorder', 2)

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
                          zorder=zorder, width=width, **kwargs)

        elif self.orientation == 'vertical':
            q = ax.quiver(ystart, xstart, v, u,
                          units=units, scale_units=scale_units, angles=angles, scale=scale,
                          zorder=zorder, width=width, **kwargs)
            
        return q

    def jointplot(self, x, y, **kwargs):
        """ Utility wrapper around seaborn.jointplot
        which automatically flips the x and y coordinates if the pitch is vertical, sets the height from the figsize,
        and clips kernel density plots (kind = 'kde') to the pitch boundaries.
        
        Draw a plot of two variables with bivariate and univariate graphs.
        see: https://seaborn.pydata.org/generated/seaborn.jointplot.html
        
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
        zorder = kwargs.pop('zorder', 2)
        if ('kind' in kwargs) and (kwargs['kind'] == 'kde'):
            if self.orientation == 'horizontal':
                clip = kwargs.pop('clip', ((self.left, self.right), (self.bottom, self.top)))
            elif self.orientation == 'vertical':
                clip = kwargs.pop('clip', ((self.top, self.bottom), (self.left, self.right)))
            
        # plot. Reverse coordinates if vertical plot 
        if self.orientation == 'horizontal':
            if ('kind' in kwargs) and (kwargs['kind'] == 'kde'):
                clip = kwargs.pop('clip', ((self.left, self.right), (self.bottom, self.top)))
                joint_plot = sns.jointplot(x, y, zorder = zorder, clip = clip, **kwargs)
            else:
                joint_plot = sns.jointplot(x, y, zorder = zorder, **kwargs)
            
        elif self.orientation == 'vertical':
            if ('kind' in kwargs) and (kwargs['kind'] == 'kde'):
                clip = kwargs.pop('clip', ((self.top, self.bottom), (self.left, self.right)))
                joint_plot = sns.jointplot(y, x, zorder = zorder, clip = clip, **kwargs)
            else:
                joint_plot = sns.jointplot(y, x, zorder = zorder, **kwargs)
                
        joint_plot_ax = joint_plot.ax_joint
        self.draw(ax=joint_plot_ax)

        return joint_plot
    
    def annotate(self, text, xy, xytext=None, ax=None, **kwargs):
        """ Utility wrapper around ax.annotate
        which automatically flips the xy and xytext coordinates if the pitch is vertical.
        
        Annotate the point xy with text.
        see: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html
        
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
            The following statistics are available:
              * 'count' : compute the count of points within each bin.  This is
                 identical to an unweighted histogram.  `values` array is not
                 referenced.
              * 'mean' : compute the mean of values for points within each bin.
                 Empty bins will be represented by NaN.
              * 'std' : compute the standard deviation within each bin. This
                 is implicitly calculated with ddof=0.
              * 'median' : compute the median of values for points within each
                 bin. Empty bins will be represented by NaN.
              * 'sum' : compute the sum of values for points within each bin.
                 This is identical to a weighted histogram.
              * 'min' : compute the minimum of values for points within each bin.
                 Empty bins will be represented by NaN.
              * 'max' : compute the maximum of values for point within each bin.
                 Empty bins will be represented by NaN.
              * function : a user-defined function which takes a 1D array of
                 values, and outputs a single numerical statistic. This function
                 will be called on the values in each bin.  Empty bins will be
                 represented by function([]), or NaN if this returns an error.
        
        bins : int or [int, int] or array_like or [array, array], optional
            The bin specification:
              * the number of bins for the two dimensions (nx = ny = bins),
              * the number of bins in each dimension (nx, ny = bins),
              * the bin edges for the two dimensions (x_edge = y_edge = bins),
              * the bin edges in each dimension (x_edge, y_edge = bins).
            If the bin edges are specified, the number of bins will be,
            (nx = len(x_edge)-1, ny = len(y_edge)-1).
            
        Returns
        ----------
        namedtuple : BinnedStatisticResult. Containing:
            * statistic : (nx, ny) ndarray
                The values of the selected statistic in each two-dimensional bin.
            * x_grid : (ny + 1, nx + 1) ndarray
                The grid edges along the first dimension.
            * y_grid : (ny + 1, nx + 1) ndarray
                The grid edges along the second dimension.
            * cx : (ny, nx) array
                This contains the bin centers along the first dimension.
            * cy : (ny, nx) array
                This contains the bin centers along the second dimension.
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
            
        result = binned_statistic_2d(x, y, values, statistic='count', bins=bins, range=pitch_range)
        
        x_grid, y_grid = np.meshgrid(result.x_edge, result.y_edge)
        cx, cy = np.meshgrid(result.x_edge[:-1] + 0.5 * np.diff(result.x_edge),
                             result.y_edge[:-1] + 0.5 * np.diff(result.y_edge))

        bin_statistic = BinnedStatisticResult(result.statistic, x_grid, y_grid, cx, cy)
        
        return bin_statistic
              
    def heatmap(self, bin_statistic, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.pcolormesh
        which automatically flips the x_grid and y_grid coordinates if the pitch is vertical.
        
        see: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html
       
        Parameters
        ----------
        bin_statistic : BinnedStatisticResult. This should be calculated via Pitch.bin_statistic().
            It contains:
              * statistic : (nx, ny) ndarray
                    The values of the selected statistic in each two-dimensional bin.
              * x_grid : (ny + 1, nx + 1) ndarray
                    The grid edges along the first dimension.
              * y_grid : (ny + 1, nx + 1) ndarray
                    The grid edges along the second dimension.
              * cx : (ny, nx) array
                    his contains the bin centers along the first dimension.
              * cy : (ny, nx) array
                    This contains the bin centers along the second dimension.
        
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.pcolormesh.

        Returns
        ----------
        mesh : matplotlib.collections.QuadMesh
        """
        if ax is None:
            raise TypeError("heatmap() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        zorder = kwargs.pop('zorder', 2)
               
        if self.orientation == 'horizontal':
            mesh = ax.pcolormesh(bin_statistic.x_grid.T, bin_statistic.y_grid.T,
                                 bin_statistic.statistic, zorder=zorder, **kwargs)
            
        elif self.orientation == 'vertical':
            mesh = ax.pcolormesh(bin_statistic.y_grid.T, bin_statistic.x_grid.T, 
                                 bin_statistic.statistic, zorder=zorder, **kwargs)
            
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
            The following statistics are available:
              * 'count' : compute the count of points within each bin.  This is
                 identical to an unweighted histogram.  `values` array is not
                 referenced.
              * 'mean' : compute the mean of values for points within each bin.
                 Empty bins will be represented by NaN.
              * 'std' : compute the standard deviation within each bin. This
                 is implicitly calculated with ddof=0.
              * 'median' : compute the median of values for points within each
                 bin. Empty bins will be represented by NaN.
              * 'sum' : compute the sum of values for points within each bin.
                 This is identical to a weighted histogram.
              * 'min' : compute the minimum of values for points within each bin.
                 Empty bins will be represented by NaN.
              * 'max' : compute the maximum of values for point within each bin.
                 Empty bins will be represented by NaN.
              * function : a user-defined function which takes a 1D array of
                 values, and outputs a single numerical statistic. This function
                 will be called on the values in each bin.  Empty bins will be
                 represented by function([]), or NaN if this returns an error.
            
        Returns
        ----------
        list of BinnedStatisticResult : A list of namedtuple. The namedtuples contain:
            statistic : (nx, ny) ndarray
                The values of the selected statistic in each two-dimensional bin.
            x_grid : (ny + 1, nx + 1) ndarray
                The grid edges along the first dimension.
            y_grid : (ny + 1, nx + 1) ndarray
                The grid edges along the second dimension.
            cx : (ny, nx) array
                This contains the bin centers along the first dimension.
            cy : (ny, nx) array
                This contains the bin centers along the second dimension.
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
            xedge = np.array([x1,x2,x3,x4,x5,x6,x7])
            yedge = np.array([y1,y2,y5,y6])
            stat1, x_grid1, y_grid1, cx1, cy1 = self.bin_statistic(x, y, values, statistic = statistic,
                                                                   bins = (xedge, yedge))

            # slicing second row
            stat2 = stat1[:,2].reshape(-1,1).copy()
            x_grid2 = x_grid1[2:,:].copy()
            y_grid2 = y_grid1[2:,:].copy()
            cx2 = cx1[2,:].copy()
            cy2 = cy1[2,:].copy()
            # slice first row
            stat1 = stat1[:,0].reshape(-1,1).copy()
            x_grid1 = x_grid1[:2,:].copy()
            y_grid1 = y_grid1[:2,:].copy()
            cx1 = cx1[0,:].copy()
            cy1 = cy1[0,:].copy()

            # middle of pitch
            xedge = np.array([x1,x2,x4,x6,x7])
            yedge = np.array([y1,y2,y3,y4,y5,y6])
            stat3, x_grid3, y_grid3, cx3, cy3 = self.bin_statistic(x, y, values, statistic = statistic, 
                                                                   bins = (xedge, yedge))
            stat3 = stat3[1:-1,1:-1]
            x_grid3 = x_grid3[1:-1:,1:-1].copy()
            y_grid3 = y_grid3[1:-1,1:-1].copy()
            cx3 = cx3[1:-1,1:-1].copy()
            cy3 = cy3[1:-1,1:-1].copy()
            
            #penalty area 1
            xedge = np.array([x1,x2,x3]).astype(np.float64)
            yedge = np.array([y2,y5,y6]).astype(np.float64)
            stat4, x_grid4, y_grid4, cx4, cy4 = self.bin_statistic(x, y, values, statistic = statistic, 
                                                                   bins = (xedge, yedge))
            stat4 = stat4[:-1,:-1]
            x_grid4 = x_grid4[:-1,:-1].copy()
            y_grid4 = y_grid4[:-1,:-1].copy()
            cx4 = cx4[:1,:1].copy()
            cy4 = cy4[:1,:1].copy()
            
            #penalty area 2
            xedge = np.array([x6,x7]).astype(np.float64)
            yedge = np.array([y2,y5,y6]).astype(np.float64)
            stat5, x_grid5, y_grid5, cx5, cy5 = self.bin_statistic(x, y, values, statistic = statistic, 
                                                                   bins = (xedge, yedge))
            stat5 = stat5[:,:-1]
            x_grid5 = x_grid5[:-1,:].copy()
            y_grid5 = y_grid5[:-1,:].copy()
            cy5 = cy5[0].copy()
            cx5 = cx5[0].copy()
                        
            # collect stats
            result1 = BinnedStatisticResult(stat1, x_grid1, y_grid1, cx1, cy1)
            result2 = BinnedStatisticResult(stat2, x_grid2, y_grid2, cx2, cy2)
            result3 = BinnedStatisticResult(stat3, x_grid3, y_grid3, cx3, cy3)
            result4 = BinnedStatisticResult(stat4, x_grid4, y_grid4, cx4, cy4)
            result5 = BinnedStatisticResult(stat5, x_grid5, y_grid5, cx5, cy5)
            
            bin_statistic = [result1, result2, result3, result4, result5]    
            
        elif positional == 'horizontal':
            xedge = np.array([x1, x7])
            yedge = np.array([y1, y2, y3, y4, y5, y6])
            statistic, x_grid, y_grid, cx, cy = self.bin_statistic(x, y, values, statistic = statistic, 
                                                                   bins = (xedge, yedge))      
            bin_statistic = [BinnedStatisticResult(statistic, x_grid, y_grid, cx, cy)]
            
        elif positional == 'vertical':
            xedge = np.array([x1, x2, x3, x4, x5, x6, x7])
            yedge = np.array([y1, y6])
            statistic, x_grid, y_grid, cx, cy = self.bin_statistic(x, y, values, statistic = statistic, 
                                                                   bins = (xedge, yedge))
            bin_statistic = [BinnedStatisticResult(statistic, x_grid, y_grid, cx, cy)]
        else:
            raise ValueError("positional must be one of 'full', 'vertical' or 'horizontal'")
                  
        return bin_statistic  

    def heatmap_positional(self, bin_statistic, ax=None, **kwargs):
        """ Plots several heatmaps for the different Juegos de posición areas.
       
        Parameters
        ----------
        bin_statistic : A list of BinnedStatisticResult. This should be calculated via Pitch.bin_statistic_positional().
            It contains:
              * statistic : (nx, ny) ndarray
                    The values of the selected statistic in each two-dimensional bin.
              * x_grid : (ny + 1, nx + 1) ndarray
                    The grid edges along the first dimension.
              * y_grid : (ny + 1, nx + 1) ndarray
                    The grid edges along the second dimension.
              * cx : (ny, nx) array
                    his contains the bin centers along the first dimension.
              * cy : (ny, nx) array
                    This contains the bin centers along the second dimension.
        
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.pcolormesh.
        
        Returns
        ----------
        mesh : matplotlib.collections.QuadMesh
        """
        if ax is None:
            raise TypeError("label_heatmap() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
        vmax = kwargs.pop('vmax',np.array([stat.statistic.max() for stat in bin_statistic]).max())
        vmin = kwargs.pop('vmin',np.array([stat.statistic.min() for stat in bin_statistic]).min())
        
        mesh_list = []
        for bin_stat in bin_statistic:
            mesh = self.heatmap(bin_stat, vmin=vmin, vmax=vmax, ax=ax, **kwargs)
            mesh_list.append(mesh)
            
        return mesh_list
            
    def label_heatmap(self, bin_statistic, ax=None, **kwargs):
        """ Labels the heatmaps and automatically flips the coordinates if the pitch is vertical.
              
        Parameters
        ----------
        bin_statistic : A list of BinnedStatisticResult. This should be calculated via Pitch.bin_statistic_positional().
            It contains:
              * statistic : (nx, ny) ndarray
                    The values of the selected statistic in each two-dimensional bin.
              * x_grid : (ny + 1, nx + 1) ndarray
                    The grid edges along the first dimension.
              * y_grid : (ny + 1, nx + 1) ndarray
                    The grid edges along the second dimension.
              * cx : (ny, nx) array
                    his contains the bin centers along the first dimension.
              * cy : (ny, nx) array
                    This contains the bin centers along the second dimension.
        
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.annotate.
            
        Returns
        ----------
        annotations : A list of matplotlib.text.Annotation.
        """
        
        if ax is None:
            raise TypeError("label_heatmap() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        if not isinstance(bin_statistic, list):
            bin_statistic = [bin_statistic]
    
        annotation_list = []
        for stat in bin_statistic:
            text = stat.statistic.T.ravel()
            cx = np.ravel(stat.cx)
            cy = np.ravel(stat.cy)
            for i in range(len(text)):
                annotation = self.annotate(text[i], (cx[i], cy[i]), ax=ax, **kwargs)
                annotation_list.append(annotation)
            
        return annotation_list
            