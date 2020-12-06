import numpy as np
from mplsoccer._pitch_base import BasePitch
import matplotlib.patches as patches
import matplotlib.lines as lines


class Pitch(BasePitch):
        
    def _set_extent(self):
        extent = np.array([self.left, self.right, self.bottom, self.top])
        pad = np.array([-self.pad_left, self.pad_right, -self.pad_bottom, self.pad_top])
        if self.half:
            extent[0] = self.center_length  # pitch starts at center line
        if self.invert_y:
            pad[2:] = -pad[2:]  # when inverted the padding is negative
        self.extent = extent + pad
        
        # stripe
        total_height = abs(self.extent[3] - self.extent[2])
        pad_top, pad_bottom = -min(self.pad_top, 0), min(self.pad_bottom, 0)
        if self.invert_y:
            pad_top, pad_bottom = -pad_top, -pad_bottom
        top_side = abs(self.extent[2] - self.top + pad_top)
        bottom_side = abs(self.extent[2] - self.bottom + pad_bottom)
        self.stripe_end = top_side / total_height
        self.stripe_start = bottom_side / total_height
        self.grass_stripe_end = int((1 - self.stripe_start) * 1000)
        self.grass_stripe_start = int((1 - self.stripe_end) * 1000)

    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        rectangle = patches.Rectangle((x, y), width, height, **kwargs)
        ax.add_patch(rectangle)
        
    def _draw_line(self, ax, x, y, **kwargs):
        line = lines.Line2D(x, y, **kwargs)
        ax.add_artist(line)
        
    def _draw_ellipse(self, ax, x, y, width, height, **kwargs):
        ellipse = patches.Ellipse((x, y), width, height, **kwargs)
        ax.add_patch(ellipse)
               
    def _draw_arc(self, ax, x, y, width, height, theta1, theta2, **kwargs):
        arc = patches.Arc((x, y), width, height, theta1=theta1, theta2=theta2, **kwargs)
        ax.add_patch(arc)
                
    def _draw_stripe(self, ax, i):
        ax.axvspan(self.stripe_locations[i], self.stripe_locations[i + 1],  # note axvspan
                   self.stripe_start, self.stripe_end,
                   facecolor=self.stripe_color, zorder=self.stripe_zorder)
        
    def _draw_stripe_grass(self, pitch_color):
        total_width = self.extent[1] - self.extent[0]
        for i in range(len(self.stripe_locations) - 1):
            if i % 2 == 0:
                if ((self.extent[0] <= self.stripe_locations[i] <=  self.extent[1]) or
                    (self.extent[0] <= self.stripe_locations[i + 1] <=  self.extent[1])):
                    start = int((max(self.stripe_locations[i], self.extent[0]) - self.extent[0]) / total_width * 1000)
                    end = int((min(self.stripe_locations[i+1], self.extent[1]) - self.extent[0]) / total_width * 1000)    
                    pitch_color[self.grass_stripe_start: self.grass_stripe_end, start: end] = \
                    pitch_color[self.grass_stripe_start: self.grass_stripe_end, start: end] + 2
        return pitch_color
    

class VerticalPitch(BasePitch):
    
    def _set_extent(self):
        extent = np.array([self.top, self.bottom, self.left, self.right])
        pad = np.array([self.pad_left, -self.pad_right, -self.pad_bottom, self.pad_top])
        if self.half:
            extent[2] = self.center_length  # pitch starts at center line
        if self.invert_y:
            pad[0:2] = -pad[0:2]  # when inverted the padding is negative
        self.extent = extent + pad
        self.aspect = 1 / self.aspect
        # stripe
        total_height = abs(self.extent[1] - self.extent[0])
        pad_top, pad_bottom = -min(self.pad_left, 0), min(self.pad_right, 0)
        if self.invert_y:
            pad_top, pad_bottom = -pad_top, -pad_bottom
        top_side = abs(self.extent[0] - self.top + pad_top)
        bottom_side = abs(self.extent[0] - self.bottom + pad_bottom)
        self.stripe_start = top_side / total_height
        self.stripe_end = bottom_side / total_height
        self.grass_stripe_end = int(self.stripe_end * 1000)
        self.grass_stripe_start = int(self.stripe_start * 1000)
       
    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        rectangle = patches.Rectangle((y, x), height, width, **kwargs)
        ax.add_patch(rectangle)
        
    def _draw_line(self, ax, x, y, **kwargs):
        line = lines.Line2D(y, x, **kwargs)
        ax.add_artist(line)
        
    def _draw_ellipse(self, ax, x, y, width, height, **kwargs):
        ellipse = patches.Ellipse((y, x), height, width, **kwargs)
        ax.add_patch(ellipse)
               
    def _draw_arc(self, ax, x, y, width, height, theta1, theta2, **kwargs):
        arc = patches.Arc((y, x), height, width, theta1=theta1 + 90, theta2=theta2 + 90, **kwargs)
        ax.add_patch(arc)
        
    def _draw_stripe(self, ax, i):
        ax.axhspan(self.stripe_locations[i], self.stripe_locations[i + 1],  # note axhspan
                   self.stripe_start, self.stripe_end,
                   facecolor=self.stripe_color, zorder=self.stripe_zorder)
        
    def _draw_stripe_grass(self, pitch_color):
        return pitch_color
        
    def _draw_stripe_grass(self, pitch_color):
        total_width = self.extent[3] - self.extent[2] 
        for i in range(len(self.stripe_locations) - 1):
            if i % 2 == 0:
                if ((self.extent[2] <= self.stripe_locations[i] <=  self.extent[3]) or
                    (self.extent[2] <= self.stripe_locations[i + 1] <=  self.extent[3])):
                    start = 1000 -int((min(self.stripe_locations[i+1], self.extent[3]) - self.extent[2]) / total_width * 1000) 
                    end = 1000 - int((max(self.stripe_locations[i], self.extent[2]) - self.extent[2]) / total_width * 1000)
                    pitch_color[start: end, self.grass_stripe_start: self.grass_stripe_end] = \
                    pitch_color[start: end, self.grass_stripe_start: self.grass_stripe_end] + 2                    
        return pitch_color
