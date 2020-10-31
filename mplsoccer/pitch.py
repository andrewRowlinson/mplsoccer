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
        
class VerticalPitch(BasePitch):
    
    def _set_extent(self):
        extent = np.array([self.top, self.bottom, self.left, self.right])
        pad = np.array([self.pad_left, -self.pad_right, -self.pad_bottom, self.pad_top])
        if self.half:
            extent[2] = self.center_length  # pitch starts at center line
        if self.invert_y:
            pad[0:2] = -pad[0:2]  # when inverted the padding is negative
            
        self.extent = extent + pad
        self._flip_aspect()

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