""" Module containing: Pitch and VerticalPitch, which are used to plot pitches in mplsoccer"""

import numpy as np
from matplotlib import patches
from matplotlib.lines import Line2D

from ._pitch_base import BasePitchBasketBall

__all__ = ['BasketBallCourt', 'VerticalBasketBallCourt']


class BasketBallCourt(BasePitchBasketBall):

    def _set_aspect(self):
        self.aspect = self.dim.aspect

    def _scale_pad(self):
        self.pad_left = self.pad_left * self.aspect
        self.pad_right = self.pad_right * self.aspect

    def _validate_pad(self):
        # make sure padding not too large for the pitch
        if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.dim.length:
            raise ValueError("pad_left/pad_right too negative for pitch length")
        if abs(min(self.pad_top, 0) + min(self.pad_bottom, 0)) >= self.dim.width:
            raise ValueError("pad_top/pad_bottom too negative for pitch width")
        if self.half:
            if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.dim.length / 2:
                raise ValueError("pad_left/pad_right too negative for pitch length")

    def _set_extent(self):
        extent = np.array([self.dim.left, self.dim.right,
                           self.dim.bottom, self.dim.top], dtype=np.float32)
        pad = np.array([-self.pad_left, self.pad_right,
                        -self.pad_bottom, self.pad_top], dtype=np.float32)
        visible_pad = np.clip(np.array([self.pad_left, self.pad_right,
                                        self.pad_bottom, self.pad_top],
                                       dtype=np.float32), a_min=None, a_max=0.)
        visible_pad[[0, 2]] = - visible_pad[[0, 2]]
        if self.half:
            extent[0] = self.dim.center_length  # pitch starts at center line
            visible_pad[0] = - self.pad_left  # do not want clipped values if half
        if self.dim.invert_y:  # when inverted the padding is negative
            pad[2:] = -pad[2:]
            visible_pad[2:] = - visible_pad[2:]
        self.extent = extent + pad
        self.ax_aspect = (abs(self.extent[1] - self.extent[0]) /
                          (abs(self.extent[3] - self.extent[2]) * self.aspect))
        self.visible_pitch = extent + visible_pad
        if self.half:
            extent[0] = extent[0] - min(self.pad_left, self.dim.pitch_length/2)

        # hexbin
        self.hexbin_gridsize = (17, 8)
        self.hex_extent = np.array([self.dim.left, self.dim.right,
                                    min(self.dim.bottom, self.dim.top),
                                    max(self.dim.bottom, self.dim.top)], dtype=np.float32)

        # kdeplot
        self.kde_clip = ((self.dim.left, self.dim.right), (self.dim.bottom, self.dim.top))

        # lines
        self.reverse_cmap = self.dim.invert_y

        # vertical for lines/ arrows
        self.vertical = False

    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        if self.dim.invert_y:
            height = - height
        rectangle = patches.Rectangle((x, y), width, height, **kwargs)
        ax.add_patch(rectangle)
        return rectangle

    def _draw_centered_rectangle(self, ax, x, y, width, height, **kwargs):
        if self.dim.invert_y:
            height = - height
        x = x - width / 2
        y = y - height / 2
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

    @staticmethod
    def _reverse_if_vertical(x, y):
        return x, y

    @staticmethod
    def _reverse_vertices_if_vertical(vert):
        return vert

    @staticmethod
    def _reverse_annotate_if_vertical(annotate):
        return annotate


class VerticalBasketBallCourt(BasePitchBasketBall):

    def _set_aspect(self):
        self.aspect = 1 / self.dim.aspect

    def _scale_pad(self):
        self.pad_bottom = self.pad_bottom / self.aspect
        self.pad_top = self.pad_top / self.aspect

    def _validate_pad(self):
        # make sure padding not too large for the pitch
        if abs(min(self.pad_bottom, 0) + min(self.pad_top, 0)) >= self.dim.length:
            raise ValueError("pad_bottom/pad_top too negative for pitch length")
        if abs(min(self.pad_left, 0) + min(self.pad_right, 0)) >= self.dim.width:
            raise ValueError("pad_left/pad_right too negative for pitch width")
        if self.half:
            if abs(min(self.pad_bottom, 0) + min(self.pad_top, 0)) >= self.dim.length / 2:
                raise ValueError("pad_bottom/pad_top too negative for pitch length")

    def _set_extent(self):
        extent = np.array([self.dim.top, self.dim.bottom,
                           self.dim.left, self.dim.right], dtype=np.float32)
        pad = np.array([self.pad_left, -self.pad_right, -self.pad_bottom,
                        self.pad_top], dtype=np.float32)
        visible_pad = np.clip(np.array([self.pad_left, self.pad_right,
                                        self.pad_bottom, self.pad_top], dtype=np.float32),
                              a_min=None, a_max=0.)
        visible_pad[[1, 2]] = - visible_pad[[1, 2]]
        if self.half:
            extent[2] = self.dim.center_length  # pitch starts at center line
            visible_pad[2] = - self.pad_bottom  # do not want clipped values if half
        if self.dim.invert_y:  # when inverted the padding is negative
            pad[0:2] = -pad[0:2]
            visible_pad[0:2] = - visible_pad[0:2]
        self.extent = extent + pad
        self.ax_aspect = (abs(self.extent[1] - self.extent[0]) /
                          (abs(self.extent[3] - self.extent[2]) * self.aspect))
        self.visible_pitch = extent + visible_pad
        if self.half:
            extent[2] = extent[2] - min(self.pad_bottom, self.dim.pitch_length/2)

        # hexbin
        self.hexbin_gridsize = (17, 17)
        self.hex_extent = np.array([min(self.dim.bottom, self.dim.top),
                                    max(self.dim.bottom, self.dim.top),
                                    self.dim.left, self.dim.right], dtype=np.float32)

        # kdeplot
        self.kde_clip = ((self.dim.top, self.dim.bottom), (self.dim.left, self.dim.right))

        # lines
        self.reverse_cmap = False

        # vertical for lines/ arrows
        self.vertical = True

    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        if self.dim.invert_y:
            height = - height
        rectangle = patches.Rectangle((y, x), height, width, **kwargs)
        ax.add_patch(rectangle)
        return rectangle

    def _draw_centered_rectangle(self, ax, x, y, width, height, **kwargs):
        if self.dim.invert_y:
            height = - height
        x = x - width / 2
        y = y - height / 2
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

    @staticmethod
    def _reverse_if_vertical(x, y):
        return y, x

    @staticmethod
    def _reverse_vertices_if_vertical(vert):
        return vert[:, [1, 0]].copy()

    @staticmethod
    def _reverse_annotate_if_vertical(annotate):
        return annotate[::-1]
