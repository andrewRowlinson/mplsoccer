''' `mplsoccer` is a python library for plotting soccer / football pitches in Matplotlib.
'''

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines
from matplotlib.colors import to_rgb
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap
import seaborn as sns
import numpy as np
import math
from utils import football_hexagon_marker, football_pentagon_marker

class Pitch(object):
    ''' A class for plotting soccer / football pitches in Matplotlib
    
    Parameters
    ----------
    
    self, figsize=None, layout=None, pitch_type='opta',orientation='horizontal',view='full',
                 pitch_color='#aabb97',line_color='white',linewidth=2,stripe=False,stripe_color='#c2d59d',
                 xpad=(3,3),ypad=(3,3),pitch_length=None,pitch_width=None,axis='off',*args, **kwargs):
    
    figsize : tuple of float, default Matplotlib figure size
        The figure size in inches by default.
    layout : tuple of int, default (1,1)
        Tuple of (rows, columns) for the layout of the plot.
    pitch_type : str, default 'opta'
        The pitch type used in the plot. The supported pitch types are: 'opta', 'statsbomb', 'tracab', 'stats', 'wyscout'. 
    orientation : str, default 'horizontal'
        The pitch orientation: 'horizontal' or 'vertical'.
    view : str, default 'full'
        The pitch view: 'full' or 'half'.
    pitch_color : any Matplotlib color, default '#aabb97'
        The background color for each Matplotlib axis.
    line_color : any Matplotlib color, default 'white'
        The line color for the pitch markings.
    linewidth : float, default 2
        The line width for the pitch markings.
    stripe : bool, default False
        Whether to show pitch stripes.    
    stripe_color : any Matplotlib color, default '#c2d59d'
        The color of the pitch stripes if stripe=True    
    xpad : tuple of float, default (3,3)
        Tuple of (pad_left, pad_right), which adjusts the xlim of the axis.
        Postive values increase the plot area, while negative values decrease the plot area.
    ypad : tuple of float, default (3,3)
        Tuple of (pad_bottom, pad_top), which adjusts the ylim of the axis.
        Postive values increase the plot area, while negative values decrease the plot area.
    pitch_length : float, default None
        The pitch length in meters. Only used for the 'tracab' pitch_type.
    pitch_width : float, default None
        The pitch width in meters. Only used for the 'tracab' pitch type. 
    goal_Type : str, default 'goal'
        Whether to display the goals as a 'line', a 'box' or to not display it at all (None)
    axis : str, default 'off'
        Whether to include the axis: 'on' or 'off'
    '''
    
    _pitch_dimensions = ['left','right','bottom','top','width','center_width','length','center_length',
                         'six_yard_from_side','six_yard_width','six_yard_length',
                         'penalty_area_from_side','penalty_area_width','penalty_area_length',
                         'left_penalty','right_penalty','circle_size',
                         'goal_width','goal_depth','goal_post',
                         'arc1_leftV','arc2_leftH']                         
    
    _opta_dimensions = {'left':100,'right':0,'bottom':0,'top':100,
                        'width':100,'center_width':50,'length':100,'center_length':50,
                        'six_yard_from_side':36.8,'six_yard_width':26.4,'six_yard_length':5.8,
                        'penalty_area_from_side':21.1,'penalty_area_width':57.8,'penalty_area_length':17.0,
                        'left_penalty':11.5,'right_penalty':88.5,'circle_size':9.15,
                        'goal_depth':1.9,'goal_width':10.76,'goal_post':44.62,
                        'arc1_leftV':None,'arc2_leftH':None}
    
    # wyscout dimensions are sourced from ggsoccer https://github.com/Torvaney/ggsoccer/blob/master/R/dimensions.R
    _wyscout_dimensions = {'left':100,'right':0,'bottom':0,'top':100,
                           'width':100,'center_width':50,'length':100,'center_length':50,
                           'six_yard_from_side':37,'six_yard_width':26,'six_yard_length':6,
                           'penalty_area_from_side':19,'penalty_area_width':62,'penalty_area_length':16,
                           'left_penalty':10,'right_penalty':90,'circle_size':9.15,
                           'goal_depth':1.9,'goal_width':12,'goal_post':44,
                           'arc1_leftV':None,'arc2_leftH':None}  
    
    _statsbomb_dimensions = {'left':0,'right':80,'bottom':0,'top':120,
                             'width':80,'center_width':40,'length':120,'center_length':60,
                             'six_yard_from_side':30,'six_yard_width':20,'six_yard_length':6,
                             'penalty_area_from_side':18,'penalty_area_width':44,'penalty_area_length':18,
                             'left_penalty':12,'right_penalty':108,'circle_size':10.46,
                             'goal_depth':2.4,'goal_width':8,'goal_post':36,
                             'arc1_leftV':35,'arc2_leftH':55}
    
    _tracab_dimensions = {'left':None,'right':None,'bottom':None,'top':None,
                          'width':None,'center_width':0,'length':None,'center_length':0,
                          'six_yard_from_side':-916,'six_yard_width':1832,'six_yard_length':550,
                          'penalty_area_from_side':-2016,'penalty_area_width':4032,'penalty_area_length':1650,
                          'left_penalty':None,'right_penalty':None,'circle_size':915,
                          'goal_depth':200,'goal_width':732,'goal_post':-366,
                          'arc1_leftV':36.95,'arc2_leftH':53.05}
    
    _stats_dimensions = {'left':0,'right':70,'bottom':0,'top':105,
                         'width':70,'center_width':35,'length':105,'center_length':52.5,
                         'six_yard_from_side':26,'six_yard_width':18,'six_yard_length':6,
                         'penalty_area_from_side':15,'penalty_area_width':40,'penalty_area_length':16.5,
                         'left_penalty':11,'right_penalty':94,'circle_size':9.15,
                         'goal_depth':2,'goal_width':7.32,'goal_post':31.34,
                         'arc1_leftV':36.95,'arc2_leftH':53.05}
     
    def __init__(self, figsize=None, layout=None, pitch_type='opta',orientation='horizontal',view='full',
                 pitch_color='#aabb97',line_color='white',linewidth=2,stripe=False,stripe_color='#c2d59d',
                 xpad=(4,4),ypad=(4,4),pitch_length=None,pitch_width=None,goal_type='goal',
                 label=False,tick=False,axis=False,tight_layout=True,*args, **kwargs):       
                
        # set figure and axes attributes
        self.axes = None
        self.fig = None
        self.figsize = figsize
        self.layout = layout
        self.axis = axis
        self.tick = tick
        self.label = label
        self.tight_layout = tight_layout

        # set attributes
        self.line_color = line_color
        self.pitch_color = pitch_color
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.linewidth = linewidth
        self.pitch_type = pitch_type      
        self.orientation = orientation
        self.view = view
        self.xpad_left, self.xpad_right = xpad
        self.ypad_left, self.ypad_right = ypad   
        self.stripe = stripe
        self.stripe_color = stripe_color
        self.goal_type = goal_type
        
        # set pitch dimensions
        if pitch_type=='opta':
            for attr in self._pitch_dimensions:
                setattr(self, attr, self._opta_dimensions.get(attr, None))
            self.pitch_length = 105
            self.pitch_width = 68
            self.aspect = 68/105
           
        elif pitch_type=='wyscout':
            for attr in self._pitch_dimensions:
                setattr(self, attr, self._wyscout_dimensions.get(attr, None))
            self.pitch_length = 105
            self.pitch_width = 68
            self.aspect = 68/105
            
        elif pitch_type == 'statsbomb':
            for attr in self._pitch_dimensions:
                setattr(self, attr, self._statsbomb_dimensions.get(attr, None))
            self.pitch_length = self.length
            self.pitch_width = self.width
            self.aspect = 1
            
        elif pitch_type == 'stats':
            for attr in self._pitch_dimensions:
                setattr(self, attr, self._stats_dimensions.get(attr, None))
            self.pitch_length = self.length
            self.pitch_width = self.width
            self.aspect = 1
            
        elif pitch_type == 'tracab':
            for attr in self._pitch_dimensions:
                setattr(self, attr, self._tracab_dimensions.get(attr, None))
            self.aspect = 1
            self.left = pitch_width/2 * 100
            self.right = -(pitch_width/2) * 100
            self.bottom = -(pitch_length/2) * 100
            self.top = (pitch_length/2)*100
            self.width = pitch_width*100
            self.length = pitch_length * 100
            self.left_penalty = self.bottom + 1100
            self.right_penalty = self.top - 1100
            self.xpad_left = self.xpad_left * 100
            self.ypad_left = self.ypad_left * 100
            self.xpad_right = self.xpad_right * 100
            self.ypad_right = self.ypad_right * 100    

        # scale the padding where the aspect is equal to one
        if pitch_type in ['opta','wyscout']:
            if self.orientation=='vertical':
                self.ypad_left = self.ypad_left * self.aspect
                self.ypad_right = self.ypad_right * self.aspect
            elif self.orientation=='horizontal':
                self.xpad_left = self.xpad_left * self.aspect
                self.xpad_right = self.xpad_right * self.aspect
            
    def _setup_subplots(self):
        
        if self.layout == None:
            nrows = 1
            ncols = 1            
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=self.figsize)
            axes = np.array([axes])
        
        else:
            nrows, ncols = self.layout
            if nrows>1 or ncols>1:
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=self.figsize)
                axes = axes.ravel()
            else:
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols,figsize=self.figsize)
                axes = np.array([axes])
                
        self.fig = fig
        self.axes = axes
                         
    def _set_axes(self,ax):
        if self.axis==True:
            axis_option='on'
        elif self.axis==False:
            axis_option='off'
            
        # set up vertical pitch
        if self.orientation=='vertical':
            if self.view=='full':
                ax.set_aspect(1/self.aspect)
                ax.axis(axis_option)
                ax.tick_params(top=self.tick,bottom=self.tick,left=self.tick,right=self.tick,
                               labelleft=self.label,labelbottom=self.label)
                if self.pitch_type in ['statsbomb','stats']:
                    ax.set_xlim(self.left-self.xpad_left,self.right+self.xpad_right)
                    ax.axvspan(self.left-self.xpad_left,self.right+self.xpad_right,0,1,facecolor=self.pitch_color)
                elif self.pitch_type in ['tracab','opta','wyscout']:
                    ax.set_xlim(self.left+self.xpad_left,self.right-self.xpad_right)
                    ax.axvspan(self.left+self.xpad_left,self.right-self.xpad_right,0,1,facecolor=self.pitch_color)
                ax.set_ylim(self.bottom-self.ypad_left,self.top+self.ypad_right)
                    
            elif self.view=='half':
                ax.set_aspect(1/self.aspect)
                ax.axis(axis_option)
                ax.tick_params(top=self.tick,bottom=self.tick,left=self.tick,right=self.tick,
                               labelleft=self.label,labelbottom=self.label)
                if self.pitch_type in ['statsbomb','stats']:
                    ax.set_xlim(self.left-self.xpad_left,self.right+self.xpad_right)
                    ax.axvspan(self.left-self.xpad_left,self.right+self.xpad_right,0,1,facecolor=self.pitch_color)
                elif self.pitch_type in ['tracab','opta','wyscout']:
                    ax.set_xlim(self.left+self.xpad_left,self.right-self.xpad_right)
                    ax.axvspan(self.left+self.xpad_left,self.right-self.xpad_right,0,1,facecolor=self.pitch_color)
                ax.set_ylim(self.center_length-self.ypad_left,self.top+self.ypad_right)
                        
        # set up horizontal pitch
        elif self.orientation=='horizontal':
            if self.view=='full':
                ax.set_aspect(self.aspect)
                ax.axis(axis_option)
                ax.tick_params(top=self.tick,bottom=self.tick,left=self.tick,right=self.tick,
                               labelleft=self.label,labelbottom=self.label)
                if self.pitch_type in ['statsbomb','stats']:
                    ax.set_ylim(self.right+self.ypad_left,self.left-self.ypad_right)
                    ax.axhspan(self.right+self.ypad_left,self.left-self.ypad_right,0,1,facecolor=self.pitch_color)
                elif self.pitch_type in ['tracab','opta','wyscout']:
                    ax.set_ylim(self.right-self.ypad_left,self.left+self.ypad_right)
                    ax.axhspan(self.right-self.ypad_left,self.left+self.ypad_right,0,1,facecolor=self.pitch_color) 
                ax.set_xlim(self.bottom-self.xpad_left,self.top+self.xpad_right)
                                          
            elif self.view=='half':
                ax.set_aspect(self.aspect)
                ax.axis(axis_option)
                ax.tick_params(top=self.tick,bottom=self.tick,left=self.tick,right=self.tick,
                               labelleft=self.label,labelbottom=self.label)
                if self.pitch_type in ['statsbomb','stats']:
                    ax.set_ylim(self.right+self.ypad_left,self.left-self.ypad_right)
                    ax.axhspan(self.right+self.ypad_left,self.left-self.ypad_right,0,1,facecolor=self.pitch_color)
                elif self.pitch_type in ['tracab','opta','wyscout']:
                    ax.set_ylim(self.right-self.ypad_left,self.left+self.ypad_right)
                    ax.axhspan(self.right-self.ypad_left,self.left+self.ypad_right,0,1,facecolor=self.pitch_color)
                ax.set_xlim(self.center_length-self.xpad_left,self.top+self.xpad_right)

 
    def _draw_stripes(self,ax):
        # calculate stripe length
        pitch_length = self.top - self.bottom
        stripe1_length = self.six_yard_length
        stripe2_length = (self.penalty_area_length - self.six_yard_length)/2
        stripe3_length = (pitch_length - (self.penalty_area_length - self.six_yard_length)*3 - self.six_yard_length*2)/10
                
        # calculate pitch width
        if self.pitch_type in ['statsbomb','stats']:
            pitch_width = self.right - self.left
        elif self.pitch_type in ['tracab','opta','wyscout']:
            pitch_width = self.left-self.right
        
        # calculate stripe start and end
        if self.orientation=='vertical':
            total_width = pitch_width + self.xpad_left + self.xpad_right
            stripe_start = max(self.xpad_left,0)/total_width
            stripe_end = min((self.xpad_left + pitch_width)/total_width,1)
        elif self.orientation=='horizontal':
            total_width = pitch_width + self.ypad_left + self.ypad_right
            stripe_start = max(self.ypad_left,0)/total_width
            stripe_end = min((self.ypad_left + pitch_width)/total_width,1)
        
        # draw stripes
        start = self.bottom
        for stripe in range(1,19):
            if stripe in [1,18]:
                end = round(start + stripe1_length,2)
            elif stripe in [2,3,4,15,16,17]:
                end = round(start + stripe2_length,2)
            else:
                end = round(start + stripe3_length,2)
            if (stripe % 2 == 1) & (self.orientation=='vertical'):
                ax.axhspan(start,end,stripe_start,stripe_end,facecolor=self.stripe_color)
            elif (stripe % 2 == 1) & (self.orientation=='horizontal'):
                ax.axvspan(start,end,stripe_start,stripe_end,facecolor=self.stripe_color)
            start = end

    def _draw_pitch_lines(self,ax):
        if self.orientation=='horizontal':
            if self.pitch_type in ['statsbomb','stats']:
                pitch_markings = patches.Rectangle((self.bottom,self.left),self.length,self.width,
                                                   fill=False,linewidth=self.linewidth,color=self.line_color)
            else:
                pitch_markings = patches.Rectangle((self.bottom,self.right),self.length,self.width,
                                                   fill=False,linewidth=self.linewidth,color=self.line_color)
            midline = lines.Line2D([self.center_length,self.center_length],[self.right,self.left],
                                   linewidth=self.linewidth,color=self.line_color,zorder=1)
        elif self.orientation=='vertical':
            if self.pitch_type in ['statsbomb','stats']:
                pitch_markings = patches.Rectangle((self.left,self.bottom),self.width,self.length,
                                                   fill=False,linewidth=self.linewidth,color=self.line_color)  
            else:
                pitch_markings = patches.Rectangle((self.right,self.bottom),self.width,self.length,
                                                   fill=False,linewidth=self.linewidth,color=self.line_color)
            midline = lines.Line2D([self.left,self.right],[self.center_length,self.center_length],
                                   linewidth=self.linewidth,color=self.line_color,zorder=1)
        ax.add_patch(pitch_markings)
        ax.add_artist(midline)
    
    def _draw_goals(self,ax):
        if self.goal_type=='box':
            if self.orientation=='horizontal':
                goal1 = patches.Rectangle((self.top,self.goal_post),self.goal_depth,self.goal_width,
                                          fill=False,linewidth=self.linewidth,color=self.line_color,alpha=0.7)
                goal2 = patches.Rectangle((self.bottom-self.goal_depth,self.goal_post),self.goal_depth,self.goal_width,
                                          fill=False,linewidth=self.linewidth,color=self.line_color,alpha=0.7)
            elif self.orientation=='vertical':
                goal1 = patches.Rectangle((self.goal_post,self.top),self.goal_width,self.goal_depth,
                                          fill=False,linewidth=self.linewidth,color=self.line_color,alpha=0.7)
                goal2 = patches.Rectangle((self.goal_post,self.bottom-self.goal_depth),self.goal_width,self.goal_depth,
                                          fill=False,linewidth=self.linewidth,color=self.line_color,alpha=0.7)
            ax.add_patch(goal1)
            ax.add_patch(goal2)
                    
        elif self.goal_type=='line':
            if self.orientation=='horizontal':
                goal1 = lines.Line2D([self.top,self.top],[self.goal_post+self.goal_width,self.goal_post],
                                     linewidth=self.linewidth*2,color=self.line_color)
                goal2 = lines.Line2D([self.bottom,self.bottom],[self.goal_post+self.goal_width,self.goal_post],
                                     linewidth=self.linewidth*2,color=self.line_color)
            elif self.orientation=='vertical':
                goal1 = lines.Line2D([self.goal_post+self.goal_width,self.goal_post],[self.top,self.top],
                                     linewidth=self.linewidth*2,color=self.line_color)
                goal2 = lines.Line2D([self.goal_post+self.goal_width,self.goal_post],[self.bottom,self.bottom],
                                     linewidth=self.linewidth*2,color=self.line_color)
            ax.add_artist(goal1)
            ax.add_artist(goal2)

    def _boxes(self,box_from_side,box_length,box_width,ax):
        if self.orientation=='horizontal':
            box1 = patches.Rectangle((self.bottom,box_from_side),box_length,box_width,
                                     fill=False,linewidth=self.linewidth,color=self.line_color)
            box2 = patches.Rectangle((self.top-box_length,box_from_side),box_length,box_width,
                                     fill=False,linewidth=self.linewidth,color=self.line_color)
        elif self.orientation=='vertical':
            box1 = patches.Rectangle((box_from_side,self.bottom),box_width,box_length,
                                     fill=False,linewidth=self.linewidth,color=self.line_color)
            box2 = patches.Rectangle((box_from_side,self.top-box_length),box_width,box_length,
                                     fill=False,linewidth=self.linewidth,color=self.line_color)
        ax.add_patch(box1)
        ax.add_patch(box2)
        
    def _draw_boxes(self,ax):
        self._boxes(self.six_yard_from_side,self.six_yard_length,self.six_yard_width,ax)
        self._boxes(self.penalty_area_from_side,self.penalty_area_length,self.penalty_area_width,ax)
            
    def _draw_circles_and_arcs(self,ax):
        size_spot = 0.005 * self.length
        if self.orientation=='vertical':
            xy = (self.center_width,self.center_length)
            center = (self.center_width,self.center_length)
            penalty1 = (self.center_width,self.left_penalty)
            penalty2 = (self.center_width,self.right_penalty)
            arc1_theta1 = self.arc1_leftV
            arc1_theta2 = 180 - self.arc1_leftV
            arc2_theta1 = 180 + self.arc1_leftV
            arc2_theta2 = 360 - self.arc1_leftV
            
        elif self.orientation=='horizontal':
            xy = (self.center_length,self.center_width)
            center = (self.center_length,self.center_width)
            penalty1 = (self.left_penalty,self.center_width)
            penalty2 = (self.right_penalty,self.center_width)
            arc1_theta2 = self.arc2_leftH
            arc1_theta1 = 360 - self.arc2_leftH
            arc2_theta1 = 180 - self.arc2_leftH
            arc2_theta2 = 180 + self.arc2_leftH                

        circle = patches.Circle(xy,self.circle_size,linewidth=self.linewidth,color=self.line_color, fill=False)
        center_spot = patches.Circle(center,size_spot,color=self.line_color)
        penalty1_spot = patches.Circle(penalty1,size_spot,color=self.line_color)
        penalty2_spot = patches.Circle(penalty2,size_spot,color=self.line_color)
        arc1_patch = patches.Arc(penalty1,self.circle_size*2,self.circle_size*2,
                                 theta1=arc1_theta1,theta2=arc1_theta2,
                                 linewidth=self.linewidth,color=self.line_color,fill=False)
        arc2_patch = patches.Arc(penalty2,self.circle_size*2,self.circle_size*2,
                                 theta1=arc2_theta1,theta2=arc2_theta2,
                                 linewidth=self.linewidth,color=self.line_color,fill=False)
        ax.add_patch(circle)
        ax.add_patch(center_spot)
        ax.add_patch(penalty1_spot)  
        ax.add_patch(penalty2_spot)  
        ax.add_patch(arc1_patch)
        ax.add_patch(arc2_patch)  
                
    def _draw_scaled_circles_and_arcs(self,ax):
        r1 = self.circle_size*self.width/self.pitch_width
        r2 = self.circle_size*self.length/self.pitch_length
        scaled_spot1 = self.length/(2*self.pitch_width)
        scaled_spot2 = self.length/(2*self.pitch_length)
        xy = (self.center_width,self.center_length)
        intersection = self.center_width-(r1*r2*(r2**2-(self.penalty_area_length - self.left_penalty)**2)**(0.5))/(r2**2)
            
        if self.orientation=='vertical':
            xy1 = (self.center_width+r1,self.center_length)
            xy2 = (self.center_width,self.center_length+r2)
            spot1 = (self.center_width,self.left_penalty)
            spot2 = (self.center_width,self.right_penalty)
            center_spot = (self.center_width,self.center_length)
            p1 = (self.center_width+scaled_spot1,self.left_penalty)
            p2 = (self.center_width,self.left_penalty+scaled_spot2)
            arc_pen_top1 = (intersection, self.penalty_area_length)
                
        elif self.orientation=='horizontal':
            xy1 = (self.center_width+r2,self.center_length)
            xy2 = (self.center_width,self.center_length+r1)
            spot1 = (self.left_penalty,self.center_width)
            spot2 = (self.right_penalty,self.center_width)
            center_spot = (self.center_length,self.center_width)
            p2 = (self.left_penalty,self.center_width+scaled_spot1)
            p1 = (self.left_penalty+scaled_spot2,self.center_width)
            arc_pen_top1 = (self.penalty_area_length,intersection)
        
        def to_ax_coord(ax,coord_system,point):
            return coord_system.inverted().transform(ax.transData.transform_point(point))
        
        ax_coordinate_system = ax.transAxes
        ax_xy = to_ax_coord(ax,ax_coordinate_system,xy)
        ax_spot1 = to_ax_coord(ax,ax_coordinate_system,spot1)
        ax_spot2 = to_ax_coord(ax,ax_coordinate_system,spot2)
        ax_center = to_ax_coord(ax,ax_coordinate_system,center_spot)
        ax_xy1 = to_ax_coord(ax,ax_coordinate_system,xy1)
        ax_xy2 = to_ax_coord(ax,ax_coordinate_system,xy2)
        ax_p1 = to_ax_coord(ax,ax_coordinate_system,p1)
        ax_p2 = to_ax_coord(ax,ax_coordinate_system,p2)
        ax_arc_pen_top1 = to_ax_coord(ax,ax_coordinate_system,arc_pen_top1) 
        diameter1 = (ax_xy1[0] - ax_xy[0])*2
        diameter2 = (ax_xy2[1] - ax_xy[1])*2
        diameter_spot1 = (ax_p1[0] - ax_spot1[0])*2
        diameter_spot2 = (ax_p2[1] - ax_spot1[1])*2
                
        if self.orientation=='vertical':
            a = ax_spot1[0] - ax_arc_pen_top1[0]
            o = ax_arc_pen_top1[1] - ax_spot1[1]
            arc1_left = np.degrees(np.arctan(o/a))
            arc1_right = 180 - arc1_left
            arc2_left = 180 + arc1_left
            arc2_right = 360 - arc1_left
                    
        elif self.orientation=='horizontal':
            a = ax_arc_pen_top1[0] - ax_spot1[0]
            o = ax_spot1[1] - ax_arc_pen_top1[1]  
            arc1_right = np.degrees(np.arctan(o/a))
            arc1_left = 360 - arc1_right
            arc2_left = 180 - arc1_right
            arc2_right = 180 + arc1_right
                
        circle = patches.Ellipse(ax_xy, diameter1, diameter2,transform=ax_coordinate_system,fill=False,
                                 linewidth=self.linewidth,color=self.line_color)
        penalty_spot1 = patches.Ellipse(ax_spot1, diameter_spot1, diameter_spot2,
                                        transform=ax_coordinate_system,
                                        linewidth=self.linewidth,color=self.line_color)
        penalty_spot2 = patches.Ellipse(ax_spot2, diameter_spot1, diameter_spot2,
                                        transform=ax_coordinate_system,
                                        linewidth=self.linewidth,color=self.line_color)
        kick_off_spot = patches.Ellipse(ax_center, diameter_spot1, diameter_spot2,
                                        transform=ax_coordinate_system,
                                        linewidth=self.linewidth,color=self.line_color)
        arc1_patch = patches.Arc(ax_spot1,diameter1, diameter2,transform=ax_coordinate_system,fill=False,
                                 theta1=arc1_left,theta2=arc1_right,
                                 linewidth=self.linewidth,color=self.line_color)
        arc2_patch = patches.Arc(ax_spot2,diameter1, diameter2,transform=ax_coordinate_system,fill=False,
                                 theta1=arc2_left,theta2=arc2_right,
                                 linewidth=self.linewidth,color=self.line_color)
                
        ax.add_patch(penalty_spot1)
        ax.add_patch(penalty_spot2)
        ax.add_patch(kick_off_spot)
        ax.add_patch(circle)
        ax.add_patch(arc1_patch)     
        ax.add_patch(arc2_patch)
            
    def _draw_ax(self,ax):
        self._set_axes(ax)
        if self.stripe == True:
            self._draw_stripes(ax)
        self._draw_pitch_lines(ax)
        if self.goal_type != None:
            self._draw_goals(ax)
        self._draw_boxes(ax)
        if self.aspect == 1:
            self._draw_circles_and_arcs(ax)
        else:
            self._draw_scaled_circles_and_arcs(ax)

    def draw(self,ax=None):
        ''' Returns a numpy array of Matplotlib axes with drawn soccer / football pitches.
        '''
        if ax==None:
            self._setup_subplots()
            self.fig.set_tight_layout(self.tight_layout)
            for ax in self.axes:
                self._draw_ax(ax)
            if self.axes.size == 1:
                self.axes = self.axes.item()
            return self.fig, self.axes
        else:
            self._draw_ax(ax)
    
    def plot(self,x,y,*args,ax=None, **kwargs):
        if ax==None:
            raise TypeError("plot() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
            
        # if using the football marker set the colors and lines, delete from kwargs so not used twice
        plot_football = False
        if 'marker' in kwargs.keys():
            if kwargs['marker']=='football':
                del kwargs['marker']
                plot_football = True               
                markeredgewidth = kwargs.pop('markeredgewidth', 0.25)
                markersize = kwargs.pop('markersize', 20)
                hexcolor = kwargs.pop('markerfacecolor', 'white')
                pentcolor = kwargs.pop('markeredgecolor', 'black')      

        # plot. Reverse coordinates if vertical plot            
        if self.orientation=='horizontal':
            if plot_football == True:
                ax.plot(x,y,
                        marker=football_pentagon_marker,
                        markerfacecolor=pentcolor,markeredgecolor=pentcolor,markersize=markersize,
                        markeredgewidth=markeredgewidth,*args, **kwargs)
                ax.plot(x,y,marker=football_hexagon_marker,
                        markerfacecolor=hexcolor,markeredgecolor=pentcolor,markersize=markersize,
                        markeredgewidth=markeredgewidth,linestyle='None',)
            else:
                ax.plot(x,y,*args, **kwargs)
                
        elif self.orientation=='vertical':
            if plot_football == True:
                ax.plot(y,x,
                        marker=football_pentagon_marker,
                        markerfacecolor=pentcolor,markeredgecolor=pentcolor,markersize=markersize,
                        markeredgewidth=markeredgewidth,*args, **kwargs)
                ax.plot(y,x,
                        marker=football_hexagon_marker,
                        markerfacecolor=hexcolor,markeredgecolor=pentcolor,markersize=markersize,
                        markeredgewidth=markeredgewidth,linestyle='None',)
            else:
                ax.plot(y,x,*args, **kwargs)
                        
    def kdeplot(self,x,y,*args,ax=None, **kwargs):
        if ax==None:
            raise TypeError("plot() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
        
        # rise kdeplot above background/ stripes (the axhspan/axvspan have the same zorder as the scatter)
        zorder = kwargs.pop('zorder', 2)
                
        # plot kde plot. reverse x and y if vertical
        if self.orientation=='horizontal':
            clip = kwargs.pop('clip',((self.bottom,self.top),(self.right,self.left)))
            sns.kdeplot(x,y,ax=ax,clip=clip,zorder=zorder,*args, **kwargs)
        elif self.orientation=='vertical':
            clip = kwargs.pop('clip',((self.left,self.right),(self.bottom,self.top)))
            sns.kdeplot(y,x,ax=ax,clip=clip,zorder=zorder,*args, **kwargs)
            
    def hexbin(self,x,y,*args,ax=None, **kwargs):
        if ax==None:
            raise TypeError("plot() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
        
        # rise hexbin above background/ stripes (the axhspan/axvspan have the same zorder as the scatter)
        zorder = kwargs.pop('zorder', 2)
        mincnt = kwargs.pop('mincnt', 1)
        cmap = kwargs.pop('cmap', 'rainbow')
        gridsize = kwargs.pop('gridsize', 20)
                
        # plot hexbin plot. reverse x and y if vertical
        if self.orientation=='horizontal':
            extent = kwargs.pop('extent', (self.bottom,self.top,self.right,self.left))
            ax.hexbin(x,y,zorder=zorder,mincnt=mincnt,gridsize=gridsize,extent=extent,cmap=cmap,*args, **kwargs)           
            
        elif self.orientation=='vertical':
            extent = kwargs.pop('extent', (self.left,self.right,self.bottom,self.top))
            ax.hexbin(y,x,zorder=zorder,mincnt=mincnt,gridsize=gridsize,extent=extent,cmap=cmap,*args, **kwargs)
                    
    def scatter(self,x,y,*args,ax=None, **kwargs):
        if ax==None:
            raise TypeError("scatter() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")
        
        # rise scatter above background/ stripes (the axhspan/axvspan have the same zorder as the scatter)
        zorder = kwargs.pop('zorder', 2)
   
        # if using the football marker set the colors and lines, delete from kwargs so not used twice
        plot_football = False
        if 'marker' in kwargs.keys():       
            if kwargs['marker']=='football':
                del kwargs['marker']
                plot_football = True
                
                linewidths = kwargs.pop('linewidths', 0.5)
                hexcolor = kwargs.pop('facecolor', 'white')
                pentcolor = kwargs.pop('edgecolor', 'black')
            
        # plot scatter. Reverse coordinates if vertical plot
        if self.orientation=='horizontal':
            if plot_football == True:
                ax.scatter(x,y,marker=football_pentagon_marker,
                           facecolor=pentcolor,edgecolor=pentcolor,
                           linewidths=linewidths,zorder=zorder,*args,**kwargs) 
                ax.scatter(x,y,marker=football_hexagon_marker,
                           facecolor=hexcolor,edgecolor=pentcolor,
                           linewidths=linewidths,zorder=zorder,*args, **kwargs)
             
            else:
                ax.scatter(x,y,zorder=zorder,*args, **kwargs)
                
        elif self.orientation=='vertical':
            if plot_football == True:
                ax.scatter(y,x,marker=football_pentagon_marker,
                           facecolor=pentcolor,edgecolor=pentcolor,
                           linewidths=linewidths,zorder=zorder,*args, **kwargs)
                ax.scatter(y,x,marker=football_hexagon_marker,
                           facecolor=hexcolor,edgecolor=pentcolor,
                           linewidths=linewidths,zorder=zorder,*args, **kwargs)     
            else:
                ax.scatter(y,x,zorder=zorder,*args, **kwargs)
              
            
    def _create_segments(self,xstart,xend,ystart,yend,n_segments):
        if self.orientation=='horizontal':
            x = np.linspace(xstart,xend,n_segments+1)
            y = np.linspace(ystart,yend,n_segments+1)
        elif self.orientation=='vertical':
            x = np.linspace(ystart,yend,n_segments+1)
            y = np.linspace(xstart,xend,n_segments+1)
        points = np.array([x, y]).T
        points = np.concatenate([points,np.expand_dims(points[:,-1,:],1)],axis=1)
        points = np.expand_dims(points,1)
        segments = np.concatenate([points[:,:,:-2,:],points[:,:,1:-1,:],points[:,:,2:,:]],axis=1)
        segments = np.transpose(segments,(0,2,1,3)).reshape(-1,3,2)
        return segments
    
    def _create_transparent_cmap(self,color,n_segments):
        if self.orientation=='horizontal':
            color = np.tile(np.array(color),(n_segments,1))
            color = np.append(color,np.linspace(0.1,0.5,n_segments).reshape(-1,1),axis=1)
            cmap = ListedColormap(color, name='line fade', N=n_segments)
        elif self.orientation=='vertical':
            color = np.tile(np.array(color),(n_segments,1))
            color = np.append(color,np.linspace(0.5,0.1,n_segments).reshape(-1,1),axis=1)
            cmap = ListedColormap(color, name='line fade', N=n_segments)                      
        return cmap   
                               
    def lines(self,xstart,xend,ystart,yend,n_segments=100, comet=False, transparent=False, ax=None,*args, **kwargs):
        if ax==None:
            raise TypeError("plot_line_fade() missing 1 required argument: ax. A Matplotlib axis is required for plotting.")

        lw = kwargs.pop('lw', 5)
        color = kwargs.pop('color','#34afed')
        color = to_rgb(color)
        
        # set pitch array for line segments
        if self.orientation=='horizontal':    
            if self.view=='full':
                pitch_array = np.linspace(self.bottom,self.top,n_segments) 
            elif self.view=='half':
                pitch_array = np.linspace(self.center_length,self.top,n_segments)  
        
        elif self.orientation=='vertical':
            pitch_array = np.linspace(self.left,self.right,n_segments)         
        
        # set color map, lw and segments
        if (transparent == True) and (comet == True):
            cmap = self._create_transparent_cmap(color,n_segments)
            lw = np.linspace(1,lw,n_segments)
            segments = self._create_segments(xstart,xend,ystart,yend,n_segments)
        
        elif (transparent == True) and (comet == False):
            cmap = self._create_transparent_cmap(color,n_segments)
            segments = self._create_segments(xstart,xend,ystart,yend,n_segments)
        
        elif (transparent == False) and (comet == True):
            lw = np.linspace(1,lw,n_segments)
            cmap = ListedColormap([color], name='single color', N=n_segments)
            segments = self._create_segments(xstart,xend,ystart,yend,n_segments)
        
        elif (transparent == False) and (comet == False):
            cmap = ListedColormap([color], name='single color', N=n_segments)
            if self.orientation == 'horizontal':
                segments = np.transpose(np.array([[xstart,ystart],[xend,yend]]),(2,0,1))
            elif self.orientation == 'vertical':
                segments = np.transpose(np.array([[ystart,xstart],[yend,xend]]),(2,0,1))
                
        # add line collection
        lc = LineCollection(segments, cmap=cmap, linewidth=lw,snap=False,*args, **kwargs)
        lc.set_array(pitch_array)
        ax.add_collection(lc)