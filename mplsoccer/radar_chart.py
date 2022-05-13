""" A Python module for plotting radar-chart.

Authors: Anmol_Durgapal(@slothfulwave612) and Andrew Rowlinson (@numberstorm)

The radar-chart theme is inspired by StatsBomb/Rami_Moghadam.
"""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Wedge

from mplsoccer.utils import set_visible

__all__ = ['Radar']


class Radar:
    """ A class for plotting radar charts in Matplotlib

    Parameters
    ----------
    params : sequence of str
        The name of parameters (e.g. 'Key Passes')
    min_range, max_range : sequence of floats
        Minimum and maximum range for each parameter (inner and outer edge of the Radar).
    round_int : sequence of bool, default None
        Whether to round the respective range values to integers (if True) or floats (if False).
        The default (None) sets all range values to floats.
    num_rings : int, default 4
        The number of concentric circles. This excludes the center circle so the
        total number is num_rings + 1.
    ring_width : float, default 1
        The width of the rings in data units.
    center_circle_radius : float, default 1
        The radius of the center circle in data units. The defaults mean that the ring_width is
        the same size as the center circle radius. If the center_circle_radius is increased to
        more than the ring_width then the center circle radius is wider than the rings.
    """
    def __init__(self, params, min_range, max_range, round_int=None,
                 num_rings=4, ring_width=1, center_circle_radius=1):
        self.params = np.asarray(params)
        self.min_range = np.asarray(min_range)
        self.max_range = np.asarray(max_range)
        if round_int is None:
            self.round_int = np.array([False] * self.params.size)
        else:
            self.round_int = np.asarray(round_int)
        self.ring_width = ring_width
        self.center_circle_radius = center_circle_radius
        self.num_rings = num_rings
        self.even_num_rings = self.num_rings % 2 == 0
        self.num_labels = len(self.params)

        # validation checks
        if self.params.size != self.min_range.size:
            msg = 'The size of params and min_range must match'
            raise ValueError(msg)
        if self.params.size != self.max_range.size:
            msg = 'The size of params and max_range must match'
            raise ValueError(msg)
        if self.params.size != self.round_int.size:
            msg = 'The size of params and round_int must match'
            raise ValueError(msg)
        if not isinstance(num_rings, int):
            msg = 'num_rings must be an integer'
            raise TypeError(msg)
        if self.params.size < 3:
            msg = "You are not making a pretty chart. Increase the number of params to 3 or more."
            raise ValueError(msg)

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
                f'ring_width={self.ring_width!r}, '
                f'center_circle_radius={self.center_circle_radius!r}, '
                f'num_rings={self.num_rings!r}, '
                f'params={self.params!r}, '
                f'min_range={self.min_range!r}, '
                f'max_range={self.max_range!r}, '
                f'round_int={self.round_int!r})')

    def _setup_axis(self, facecolor='#FFFFFF', ax=None):
        ax.set_facecolor(facecolor)
        ax.set_aspect('equal')
        lim = self.center_circle_radius + self.ring_width * (self.num_rings + 1.5)
        ax.set(xlim=(-lim, lim), ylim=(-lim, lim))
        set_visible(ax)

    def setup_axis(self, facecolor='#FFFFFF', figsize=(12, 12), ax=None, **kwargs):
        """ Setup an axis for plotting radar charts. If an ax is specified the settings are applied
         to an existing axis. This method equalises the aspect ratio,
         and sets the facecolor and limits.

        Parameters
        ----------
        facecolor : a Matplotlib color, default '#FFFFFF'
            The background color.
        figsize : tuple of floats, default (12, 12)
            The figure size in inches (width, height).
        ax : matplotlib axis, default None
            A matplotlib.axes.Axes to draw the pitch on.
            If None is specified the pitch is plotted on a new figure.
        **kwargs : All other keyword arguments are passed on to plt.subplots.

        Returns
        -------
        If ax=None returns a matplotlib Figure and Axes.
        Else the settings are applied on an existing axis and returns None.

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
max_range=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()

        >>> from mplsoccer import Radar
        >>> import matplotlib.pyplot as plt
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
max_range=[10, 10, 10])
        >>> fig, ax = plt.subplots(figsize=(12, 12))
        >>> radar.setup_axis(ax=ax)
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize, **kwargs)
            self._setup_axis(ax=ax, facecolor=facecolor)
            return fig, ax

        self._setup_axis(ax=ax, facecolor=facecolor)
        return None

    def draw_circles(self, ax=None, inner=True, **kwargs):
        """ Draw the radar chart's rings (concentric circles).

        Parameters
        ----------
        ax : matplotlib axis, default None
            The axis to plot on.
        inner : bool, default True
            Whether to plot the inner rings (True) or outer rings (False)
        **kwargs : All other keyword arguments are passed on to PatchCollection.

        Returns
        -------
        PatchCollection : matplotlib.collections.PatchCollection

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
max_range=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        """
        radius = np.tile(self.ring_width, self.num_rings + 1)
        radius = np.insert(radius, 0, self.center_circle_radius)
        radius = radius.cumsum()
        if (inner and self.even_num_rings) or (inner is False and self.even_num_rings is False):
            ax_circles = radius[::2]
            first_center = True
        else:
            ax_circles = radius[1::2]
            first_center = False
        rings = []
        for idx, radius in enumerate(ax_circles):
            if (idx == 0) and first_center:
                width = self.center_circle_radius
            else:
                width = self.ring_width
            ring = Wedge(center=(0, 0), r=radius, width=width, theta1=0, theta2=360)
            rings.append(ring)
        rings = PatchCollection(rings, **kwargs)
        rings = ax.add_collection(rings)
        return rings

    def _draw_radar(self, values, ax=None, **kwargs):
        # calculate vertices via the proportion of the way the value is between the low/high range
        label_range = np.abs(self.max_range - self.min_range)
        range_min = np.minimum(self.min_range, self.max_range)
        range_max = np.maximum(self.min_range, self.max_range)
        values_clipped = np.minimum(np.maximum(values, range_min), range_max)
        proportion = np.abs(values_clipped - self.min_range) / label_range
        vertices = (proportion * self.num_rings * self.ring_width) + self.center_circle_radius
        vertices = np.c_[self.rotation_sin * vertices, self.rotation_cos * vertices]
        # create radar patch from the vertices
        radar = Polygon(vertices, **kwargs)
        radar = ax.add_patch(radar)
        return radar, vertices

    def draw_radar(self, values, ax=None, kwargs_radar=None, kwargs_rings=None):
        """ Draw a single radar (polygon) and some outer rings clipped to the radar's shape.

        Parameters
        ----------
        values : sequence of floats
            A sequence of float values for each parameter.
        ax : matplotlib axis, default None
            The axis to plot on.
        **kwargs_radar : All keyword arguments are passed on to Polygon (radar).
        **kwargs_rings : All keyword arguments are passed on to PatchCollection (rings).

        Returns
        -------
        radar : Polygon : matplotlib.patches.Polygon
            The radar polygon.
        rings : PatchCollection : matplotlib.collections.PatchCollection
            The outer rings clipped to the radar polygon.
        vertices : a 2d numpy array (number of vertices, 2)
            The vertices of the radar polygon. Where the second dimension is the x, y coordinates.

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
max_range=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> radar_poly, rings, vertices = radar.draw_radar(values, ax=ax, \
kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6}, \
kwargs_rings={'facecolor': '#d80499', 'alpha': 0.6})
        """
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

    def draw_radar_compare(self, values, compare_values, ax=None,
                           kwargs_radar=None, kwargs_compare=None):
        """ Draw a radar comparison chart showing two radars.

        Parameters
        ----------
        values : sequence of floats
            A sequence of float values for each parameter for the first radar.
        compare_values : sequence of floats
            A sequence of float values for each parameter for the second radar.
        ax : matplotlib axis, default None
            The axis to plot on.
        **kwargs_radar : keyword arguments for the first radar are passed on to Polygon.
        **kwargs_compare : keyword arguments for the second radar are passed on to Polygon.

        Returns
        -------
        radar : Polygon : matplotlib.patches.Polygon
            The first radar polygon.
        radar2 : Polygon : matplotlib.patches.Polygon
            The second radar polygon.
        vertices : a 2d numpy array (number of vertices, 2)
            The vertices of the first radar. Where the second dimension is the x, y coordinates.
        vertices2 : a 2d numpy array (number of vertices, 2)
            The vertices of the second radar. Where the second dimension is the x, y coordinates.

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
max_range=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> compare_values = [10, 4, 3]
        >>> radar_output = radar.draw_radar_compare(values, compare_values, ax=ax, \
kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6}, \
kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
        """
        if kwargs_radar is None:
            kwargs_radar = {}
        if kwargs_compare is None:
            kwargs_compare = {}
        # to arrays
        values = np.asarray(values)
        compare_values = np.asarray(compare_values)
        # validate array size
        if values.size != self.params.size:
            msg = 'The size of params and values must match'
            raise ValueError(msg)
        if compare_values.size != self.params.size:
            msg = 'The size of params and compare_values must match'
            raise ValueError(msg)
        # plot radars
        radar, vertices = self._draw_radar(values, ax=ax, **kwargs_radar)
        radar2, vertices2 = self._draw_radar(compare_values, ax=ax, **kwargs_compare)
        return radar, radar2, vertices, vertices2

    def draw_range_labels(self, ax=None, offset=0, **kwargs):
        """ Draw the range labels.
        These labels are linearly interpolated between min_range and
        max_range on the ring edges.

        The range labels are formatted to 1 or 2, decimal places (dp),
        depending on whether the maximum of the range is less than or equal to one
        (1dp) or more than one (2dp). If round_int is True for the parameter, this is
        overriden so integers are shown instead.

        Parameters
        ----------
        ax : matplotlib axis, default None
            The axis to plot on.
        offset : float, default 0
            Offset the range labels from the center of the rings.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.text.

        Returns
        -------
        label_list : list of matplotlib.text.Text

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
                          max_range=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> radar_poly, rings, vertices = radar.draw_radar(values, ax=ax, \
                                                           kwargs_radar={'facecolor': '#00f2c1', \
                                                                         'alpha': 0.6}, \
                                                           kwargs_rings={'facecolor': '#d80499', \
                                                                         'alpha': 0.6})
        >>> range_labels = radar.draw_range_labels(ax=ax)
        """
        # create the label values - linearly interpolate between the low and high for each circle
        label_values = np.linspace(self.min_range.reshape(-1, 1), self.max_range.reshape(-1, 1),
                                   num=self.num_rings + 1, axis=1).ravel()
        # remove the first entry so we do not label the inner circle
        mask = np.ones_like(label_values, dtype=bool)
        mask[0::self.num_rings + 1] = 0
        label_values = label_values[mask]
        # if the range is under 1, round to 2 decimal places (2dp) else 1dp
        mask_round_to_2dp = np.repeat(np.maximum(self.min_range, self.max_range) <= 1,
                                      self.num_rings)
        round_format = np.where(mask_round_to_2dp, '%.2f', '%.1f')
        # if the round_int array is True format as an integer rather than a float
        mask_int = np.repeat(self.round_int, self.num_rings)
        round_format[mask_int] = '%.0f'
        # repeat the rotation degrees for each circle so it matches the length of the label_values
        label_rotations = np.repeat(self.rotation_degrees, self.num_rings)
        # calculate how far out from the center (radius) to place each label, convert to coordinates
        label_radius = np.linspace(self.ring_width,
                                   self.ring_width * self.num_rings,
                                   self.num_rings)
        label_radius = (self.center_circle_radius + offset + label_radius)
        label_xs = np.tile(label_radius, self.num_labels) * np.repeat(self.rotation_sin,
                                                                      label_radius.size)
        label_ys = np.tile(label_radius, self.num_labels) * np.repeat(self.rotation_cos,
                                                                      label_radius.size)
        # write the labels on the axis
        label_list = []
        for idx, label in enumerate(label_values):
            text = ax.text(label_xs[idx], label_ys[idx], round_format[idx] % label,
                           rotation=label_rotations[idx], ha='center', va='center', **kwargs)
            label_list.append(text)
        return label_list

    def draw_param_labels(self, ax=None, wrap=15, offset=1, **kwargs):
        """ Draw the parameter labels (e.g. 'Key Passes') on the edge of the chart.

        Parameters
        ----------
        ax : matplotlib axis, default None
            The axis to plot on.
        offset : float, default 1
            Offset the param labels from the last of the rings.
        wrap : int, default 15
            Wrap the labels so that every line is at most ``wrap`` characters long
            (long words are not broken).
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.text.

        Returns
        -------
        label_list : list of matplotlib.text.Text

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], min_range=[0, 0, 0], \
                          max_range=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> radar_poly, rings, vertices = radar.draw_radar(values, ax=ax, \
                                                           kwargs_radar={'facecolor': '#00f2c1', \
                                                                         'alpha': 0.6}, \
                                                           kwargs_rings={'facecolor': '#d80499', \
                                                                         'alpha': 0.6})
        >>> range_labels = radar.draw_range_labels(ax=ax)
        >>> param_labels = radar.draw_param_labels(ax=ax)
        """
        # calculate how far out from the center (radius) to place each label, convert to coordinates
        # default places one-and-a-half units (offset) away from the edge of the last circle
        outer_ring = self.center_circle_radius + (self.ring_width * self.num_rings)
        param_radius = outer_ring + offset
        param_xs = param_radius * self.rotation_sin
        param_ys = param_radius * self.rotation_cos
        label_list = []
        # write the labels on the axis
        for idx, label in enumerate(self.params):
            if wrap is not None:
                label = '\n'.join(textwrap.wrap(label, wrap, break_long_words=False))
            text = ax.text(param_xs[idx], param_ys[idx], label,
                           rotation=self.rotation_degrees[idx], ha='center', va='center', **kwargs)
            label_list.append(text)
        return label_list
