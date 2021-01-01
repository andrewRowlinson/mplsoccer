import numpy as np
from mplsoccer._pitch_base import BasePitch
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from mplsoccer.utils import validate_ax
from mplsoccer.quiver import arrows
from mplsoccer.linecollection import lines

__all__ = ['Pitch', 'VerticalPitch']


class Pitch(BasePitch):
        
    def _set_extent(self):
        extent = np.array([self.left, self.right, self.bottom, self.top], dtype=np.float32)
        pad = np.array([-self.pad_left, self.pad_right, -self.pad_bottom, self.pad_top], dtype=np.float32)
        visible_pad = np.clip(np.array([self.pad_left, self.pad_right,
                                        self.pad_bottom, self.pad_top], dtype=np.float32),
                              a_min=None, a_max=0.)
        visible_pad[[0, 2]] = - visible_pad[[0, 2]]
        if self.half:
            extent[0] = self.center_length  # pitch starts at center line
            visible_pad[0] = - self.pad_left  # do not want clipped values if half
        if self.invert_y:  # when inverted the padding is negative
            pad[2:] = -pad[2:]
            visible_pad[2:] = - visible_pad[2:]
        self.extent = extent + pad
        self.visible_pitch = extent + visible_pad
        if self.half:
            extent[0] = extent[0] - min(self.pad_left, self.pitch_length/2)
            
        # hexbin
        self.hexbin_gridsize = (17, 8)
        self.hex_extent = np.array([min(self.left, self.right), max(self.left, self.right),
                                    min(self.bottom, self.top), max(self.bottom, self.top)], dtype=np.float32)
        
        # kdeplot
        self.kde_clip = ((self.left, self.right), (self.bottom, self.top))
        
        # jointplot
        # self.jointplot_width = self.figsize[0]
        # self.jointplot_height = (self.jointplot_width / (abs(self.visible_pitch[1] - self.visible_pitch[0]) /
        #                                                abs(self.visible_pitch[3] - self.visible_pitch[2]))
        #                         * self.aspect)
        
        # lines
        self.reverse_cmap = self.invert_y
        
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
        return rectangle
        
    def _draw_line(self, ax, x, y, **kwargs):
        line = Line2D(x, y, **kwargs)
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
                if ((self.extent[0] <= self.stripe_locations[i] <= self.extent[1]) or
                        (self.extent[0] <= self.stripe_locations[i + 1] <= self.extent[1])):
                    start = int((max(self.stripe_locations[i], self.extent[0]) - self.extent[0]) / total_width * 1000)
                    end = int((min(self.stripe_locations[i+1], self.extent[1]) - self.extent[0]) / total_width * 1000)    
                    pitch_color[self.grass_stripe_start: self.grass_stripe_end, start: end] = \
                        pitch_color[self.grass_stripe_start: self.grass_stripe_end, start: end] + 2
        return pitch_color

    @staticmethod
    def _reverse_if_vertical(x, y):
        return x, y

    @staticmethod
    def _reverse_vertices_if_vertical(vert):
        return vert

    @staticmethod
    def _rotate_if_horizontal(rotation_degrees):
        return rotation_degrees - 90       
    
    def annotate(self, text, xy, xytext=None, ax=None, **kwargs):
        validate_ax(ax)        
        return ax.annotate(text, xy, xytext, **kwargs)
    
    def heatmap(self, bin_statistic, ax=None, **kwargs):
        validate_ax(ax)
        mesh = ax.pcolormesh(bin_statistic['x_grid'], bin_statistic['y_grid'],
                             bin_statistic['statistic'], **kwargs)
        return mesh
    
    @staticmethod
    def arrows(xstart, ystart, xend, yend, *args, ax=None, **kwargs):
        q = arrows(xstart, ystart, xend, yend, *args, ax=ax, vertical=False, **kwargs)
        return q

    def lines(self, xstart, ystart, xend, yend, color=None, n_segments=100,
              comet=False, transparent=False, alpha_start=0.01,
              alpha_end=1, cmap=None, ax=None, **kwargs):
        lc = lines(xstart, ystart, xend, yend, color=color, n_segments=n_segments, comet=comet, transparent=transparent,
                   alpha_start=alpha_start, alpha_end=alpha_end, cmap=cmap, ax=ax, vertical=False,
                   reverse_cmap=self.reverse_cmap, **kwargs)
        return lc


class VerticalPitch(BasePitch):
    
    def _set_extent(self):
        extent = np.array([self.top, self.bottom, self.left, self.right], dtype=np.float32)
        pad = np.array([self.pad_left, -self.pad_right, -self.pad_bottom, self.pad_top], dtype=np.float32)
        visible_pad = np.clip(np.array([self.pad_left, self.pad_right,
                                        self.pad_bottom, self.pad_top], dtype=np.float32),
                              a_min=None, a_max=0.)
        visible_pad[[1, 2]] = - visible_pad[[1, 2]]
        if self.half:
            extent[2] = self.center_length  # pitch starts at center line
            visible_pad[2] = - self.pad_bottom  # do not want clipped values if half
        if self.invert_y:  # when inverted the padding is negative
            pad[0:2] = -pad[0:2]
            visible_pad[0:2] = - visible_pad[0:2]
        self.extent = extent + pad
        self.visible_pitch = extent + visible_pad
        if self.half:
            extent[2] = extent[2] - min(self.pad_bottom, self.pitch_length/2)
        self.aspect = 1 / self.aspect
        
        # hexbin
        self.hexbin_gridsize = (17, 17)
        self.hex_extent = np.array([min(self.bottom, self.top), max(self.bottom, self.top),
                                    min(self.left, self.right), max(self.left, self.right)], dtype=np.float32)
        
        # kdeplot
        self.kde_clip = ((self.top, self.bottom), (self.left, self.right))
        
        # jointplot
        # self.jointplot_width = self.figsize[0]
        # self.jointplot_height = self.jointplot_width * (abs(self.visible_pitch[3] - self.visible_pitch[2]) /
        #                                                abs(self.visible_pitch[3] - self.visible_pitch[2]))
        
        # lines
        self.reverse_cmap = False
        
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
        return rectangle
        
    def _draw_line(self, ax, x, y, **kwargs):
        line = Line2D(y, x, **kwargs)
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
        total_width = self.extent[3] - self.extent[2] 
        for i in range(len(self.stripe_locations) - 1):
            if i % 2 == 0:
                if ((self.extent[2] <= self.stripe_locations[i] <= self.extent[3]) or
                        (self.extent[2] <= self.stripe_locations[i + 1] <= self.extent[3])):
                    start = (1000 - int((min(self.stripe_locations[i+1], self.extent[3]) - self.extent[2])
                                        / total_width * 1000))
                    end = (1000 - int((max(self.stripe_locations[i], self.extent[2]) - self.extent[2])
                                      / total_width * 1000))
                    pitch_color[start: end, self.grass_stripe_start: self.grass_stripe_end] = \
                        pitch_color[start: end, self.grass_stripe_start: self.grass_stripe_end] + 2
        return pitch_color

    @staticmethod
    def _reverse_if_vertical(x, y):
        return y, x

    @staticmethod
    def _reverse_vertices_if_vertical(vert):
        return vert[:, [1, 0]].copy()

    @staticmethod
    def _rotate_if_horizontal(rotation_degrees):
        return rotation_degrees    
    
    def annotate(self, text, xy, xytext=None, ax=None, **kwargs):
        validate_ax(ax)        
        xy = xy[::-1]
        if xytext is not None:
            xytext = xytext[::-1]
        return ax.annotate(text, xy, xytext, **kwargs)
    
    def heatmap(self, bin_statistic, ax=None, **kwargs):
        validate_ax(ax)
        mesh = ax.pcolormesh(bin_statistic['y_grid'], bin_statistic['x_grid'], 
                             bin_statistic['statistic'], **kwargs)
        return mesh
    
    @staticmethod
    def arrows(xstart, ystart, xend, yend, *args, ax=None, **kwargs):
        q = arrows(xstart, ystart, xend, yend, *args, ax=ax, vertical=True, **kwargs)
        return q

    def lines(self, xstart, ystart, xend, yend, color=None, n_segments=100,
              comet=False, transparent=False, alpha_start=0.01,
              alpha_end=1, cmap=None, ax=None, **kwargs):
        lc = lines(xstart, ystart, xend, yend, color=color, n_segments=n_segments, comet=comet, transparent=transparent,
                   alpha_start=alpha_start, alpha_end=alpha_end, cmap=cmap, ax=ax, vertical=True,
                   reverse_cmap=self.reverse_cmap, **kwargs)
        return lc
