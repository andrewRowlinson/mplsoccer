""" A Python module for plotting radar-chart.

Author: Anmol_Durgapal(@slothfulwave612)

The radar-chart theme is inspired by @Statsbomb/Rami_Moghadam.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Wedge


class Radar:
    def __init__(self, params, range_low, range_high, figsize=(12, 12), facecolor='#FFFFFF',
                 width=1, num_circles=5):
        self.params = np.asarray(params)
        self.range_low = np.asarray(range_low)
        self.range_high = np.asarray(range_high)
        self.figsize = figsize
        self.facecolor = facecolor
        self.width = width
        self.num_circles = num_circles
        self.even_num_circles = self.num_circles % 2 == 0
        self.num_labels = len(self.params)

        # validation checks
        if self.params.size != self.range_low.size:
            msg = 'The size of params and range_low must match'
            raise ValueError(msg)
        if self.params.size != self.range_high.size:
            msg = 'The size of params and range_high must match'
            raise ValueError(msg)
        if not isinstance(num_circles, int):
            msg = 'num_circles must be an integer'
            raise TypeError(msg)

        # get the rotation angles
        self.rotation = (2 * np.pi / self.num_labels) * np.arange(self.num_labels)
        self.rotation_sin = np.sin(self.rotation)
        self.rotation_cos = np.cos(self.rotation)

        # flip the rotation if the label is in lower half
        mask_flip_label = (self.rotation > np.pi / 2) & (self.rotation < np.pi / 2 * 3)
        self.rotation[mask_flip_label] = self.rotation[mask_flip_label] + np.pi
        self.rotation_degrees = -np.rad2deg(self.rotation)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'figsize={self.figsize!r}, facecolor={self.facecolor!r}, '
                f'width={self.width!r}, num_circles={self.num_circles!r}, '
                f'params={self.params!r}, range_low={self.range_low!r}, '
                f'range_high={self.range_high!r})')

    def _setup_axis(self, ax=None):
        ax.set_facecolor(self.facecolor)
        ax.set_aspect('equal')
        lim = self.width * (self.num_circles + 4)
        ax.set(xlim=(-lim, lim), ylim=(-lim, lim))
        ax.axis('off')

    def setup_axis(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
            self._setup_axis(ax)
            return fig, ax

        self._setup_axis(ax)
        return None

    def draw_circles(self, ax=None, inner=True, **kwargs):
        radius = np.tile(np.array([self.width]), self.num_circles + 1).cumsum()
        if (inner and self.even_num_circles) or (inner is False and self.even_num_circles is False):
            ax_circles = radius[0::2]
        else:
            ax_circles = radius[1::2]
        rings = [Wedge(center=(0, 0), r=radius, width=self.width, theta1=0, theta2=360) for radius
                 in ax_circles]
        rings = PatchCollection(rings, **kwargs)
        rings = ax.add_collection(rings)
        return rings

    def _draw_radar(self, values, ax=None, **kwargs):
        # calculate vertices via the proportion of the way the value is between the low/high range
        values_min_max = np.minimum(np.maximum(values, self.range_low), self.range_high)
        proportion = (values_min_max - self.range_low) / (self.range_high - self.range_low)
        vertices = (proportion * self.num_circles * self.width) + self.width
        vertices = np.c_[self.rotation_sin * vertices, self.rotation_cos * vertices]
        # create radar patch from the vertices
        radar = Polygon(vertices, **kwargs)
        radar = ax.add_patch(radar)
        return radar, vertices

    def draw_radar(self, values, ax=None, kwargs_radar=None, kwargs_rings=None):
        if kwargs_radar is None:
            kwargs_radar = {}
        if kwargs_rings is None:
            kwargs_rings = {}
        # to arrays
        values = np.asarray(values)
        # validate array size
        if values.size != self.params.size:
            msg = 'The size of params and values must match'
            raise ValueError(msg)
        # plot radar and outer rings, clip the outer rings to the radar
        radar, vertices = self._draw_radar(values, ax=ax, zorder=1, **kwargs_radar)
        rings = self.draw_circles(ax=ax, inner=False, zorder=2, **kwargs_rings)
        rings.set_clip_path(radar)
        return radar, rings, vertices

    def draw_radar_compare(self, values, values_compare, ax=None,
                           kwargs_radar=None, kwargs_compare=None):
        if kwargs_radar is None:
            kwargs_radar = {}
        if kwargs_compare is None:
            kwargs_compare = {}
        # to arrays
        values = np.asarray(values)
        values_compare = np.asarray(values_compare)
        # validate array size
        if values.size != self.params.size:
            msg = 'The size of params and values must match'
            raise ValueError(msg)
        if values_compare.size != self.params.size:
            msg = 'The size of params and values_compare must match'
            raise ValueError(msg)
        # plot radars
        radar, vertices = self._draw_radar(values, ax=ax, **kwargs_radar)
        radar2, vertices2 = self._draw_radar(values_compare, ax=ax, **kwargs_compare)
        return radar, radar2, vertices, vertices2

    def draw_range_labels(self, ax=None, **kwargs):
        # create the label values - linearly interpolate between the low and high for each circle
        label_values = np.linspace(self.range_low.reshape(-1, 1), self.range_high.reshape(-1, 1),
                                   num=self.num_circles, axis=1).ravel()
        # if the range is under 1, round to 2 decimal places (2dp) else 1dp
        mask_round_to_2dp = np.repeat(self.range_high < 1, self.num_circles)
        rounding = ['%.2f' if mask else '%.1f' for mask in mask_round_to_2dp]
        # repeat the rotation degrees for each circle so it matches the length of the label_values
        label_rotations = np.repeat(self.rotation_degrees, self.num_circles)
        # calculate how far out from the center (radius) to place each label, convert to coordinates
        label_radius = self.width + np.linspace(self.width, self.width * self.num_circles,
                                                self.num_circles)
        label_xs = np.tile(label_radius, self.num_labels) * np.repeat(self.rotation_sin,
                                                                      label_radius.size)
        label_ys = np.tile(label_radius, self.num_labels) * np.repeat(self.rotation_cos,
                                                                      label_radius.size)
        # write the labels on the axis
        label_list = []
        for idx, label in enumerate(label_values):
            text = ax.text(label_xs[idx], label_ys[idx], rounding[idx] % float(label),
                           rotation=label_rotations[idx], ha='center', va='center', **kwargs)
            label_list.append(text)
        return label_list

    def draw_param_labels(self, ax=None, **kwargs):
        # calculate how far out from the center (radius) to place each label, convert to coordinates
        param_xs = self.width * (self.num_circles + 2.5) * self.rotation_sin
        param_ys = self.width * (self.num_circles + 2.5) * self.rotation_cos
        label_list = []
        # write the labels on the axis
        for idx, label in enumerate(self.params):
            text = ax.text(param_xs[idx], param_ys[idx], label,
                           rotation=self.rotation_degrees[idx], ha='center', va='center', **kwargs)
            label_list.append(text)
        return label_list
