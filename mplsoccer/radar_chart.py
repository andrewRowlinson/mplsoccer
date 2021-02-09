""" A Python module for plotting radar-chart.

Authors: Anmol_Durgapal(@slothfulwave612) and Andrew Rowlinson (@numberstorm)

The radar-chart theme is inspired by @Statsbomb/Rami_Moghadam.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Wedge


class Radar:
    """ A class for plotting radar charts in Matplotlib

    Parameters
    ----------
    params : sequence of str
        The name of parameters (e.g. 'Key Passes')
    range_min, range_max : sequence of floats
         min and max values for each parameter.
    num_rings : int, default 5
        The number of concentric circles. This excludes the center circle so the
        total number is num_rings + 1.
    ring_width : float, default 1
        The width of the rings in data units.
    center_circle_radius : float, default 1
        The radius of the center circle in data units. The defaults mean that the ring_width is
        the same size as the center circle radius. If the center_circle_radius is increased to
        more than the ring_width then the center circle radius is wider than the rings.
    """
    def __init__(self, params, range_min, range_max,
                 num_rings=5, ring_width=1, center_circle_radius=1):
        self.params = np.asarray(params)
        self.range_min = np.asarray(range_min)
        self.range_max = np.asarray(range_max)
        self.ring_width = ring_width
        self.center_circle_radius = center_circle_radius
        self.num_rings = num_rings
        self.even_num_rings = self.num_rings % 2 == 0
        self.num_labels = len(self.params)

        # validation checks
        if self.params.size != self.range_min.size:
            msg = 'The size of params and range_min must match'
            raise ValueError(msg)
        if self.params.size != self.range_max.size:
            msg = 'The size of params and range_max must match'
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
                f'ring_width={self.ring_width!r}, num_rings={self.num_rings!r}, '
                f'params={self.params!r}, range_min={self.range_min!r}, '
                f'range_max={self.range_max!r})')

    def _setup_axis(self, facecolor='#FFFFFF', ax=None):
        ax.set_facecolor(facecolor)
        ax.set_aspect('equal')
        lim = self.ring_width * (self.num_rings + 4)
        ax.set(xlim=(-lim, lim), ylim=(-lim, lim))
        ax.axis('off')

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
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0], \
range_max=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()

        >>> from mplsoccer import Radar
        >>> import matplotlib.pyplot as plt
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0], \
range_max=[10, 10, 10])
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
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0], \
range_max=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        """
        radius = np.tile(self.ring_width, self.num_rings)
        radius = np.insert(radius, 0, self.center_circle_radius)
        radius = radius.cumsum()
        if (inner and self.even_num_rings) or (inner is False and self.even_num_rings is False):
            ax_circles = radius[0::2]
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
        values_min_max = np.minimum(np.maximum(values, self.range_min), self.range_max)
        proportion = (values_min_max - self.range_min) / (self.range_max - self.range_min)
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
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0],
range_max=[10, 10, 10])
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

    def draw_radar_compare(self, values, values_compare, ax=None,
                           kwargs_radar=None, kwargs_compare=None):
        """ Draw a radar comparison chart showing two radars.

        Parameters
        ----------
        values : sequence of floats
            A sequence of float values for each parameter for the first radar.
        values_compare : sequence of floats
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
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0],
range_max=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> values_compare = [10, 4, 3]
        >>> radar_output = radar.draw_radar_compare(values, values_compare, ax=ax, \
kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6}, \
kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
        """
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
        """ Draw the range labels.
        These are linearly interpolated labels between range_min and range_max on the ring edges.

        Parameters
        ----------
        ax : matplotlib axis, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.text.

        Returns
        -------
        label_list : list of matplotlib.text.Text

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0],
range_max=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> radar_poly, rings, vertices = radar.draw_radar(values, ax=ax, \
kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6}, \
kwargs_rings={'facecolor': '#d80499', 'alpha': 0.6})
        >>> range_labels = radar.draw_range_labels(ax=ax)
        """
        # create the label values - linearly interpolate between the low and high for each circle
        label_values = np.linspace(self.range_min.reshape(-1, 1), self.range_max.reshape(-1, 1),
                                   num=self.num_rings, axis=1).ravel()
        # if the range is under 1, round to 2 decimal places (2dp) else 1dp
        mask_round_to_2dp = np.repeat(self.range_max < 1, self.num_rings)
        rounding = ['%.2f' if mask else '%.1f' for mask in mask_round_to_2dp]
        # repeat the rotation degrees for each circle so it matches the length of the label_values
        label_rotations = np.repeat(self.rotation_degrees, self.num_rings)
        # calculate how far out from the center (radius) to place each label, convert to coordinates
        label_radius = (self.center_circle_radius + np.linspace(self.ring_width,
                                                                self.ring_width * self.num_rings,
                                                                self.num_rings))
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
        """ Draw the parameter labels (e.g. 'Key Passes') on the edge of the chart.

        Parameters
        ----------
        ax : matplotlib axis, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.text.

        Returns
        -------
        label_list : list of matplotlib.text.Text

        Examples
        --------
        >>> from mplsoccer import Radar
        >>> radar = Radar(params=['Agility', 'Speed', 'Strength'], range_min=[0, 0, 0],
range_max=[10, 10, 10])
        >>> fig, ax = radar.setup_axis()
        >>> rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')
        >>> values = [5, 3, 10]
        >>> radar_poly, rings, vertices = radar.draw_radar(values, ax=ax, \
kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6}, \
kwargs_rings={'facecolor': '#d80499', 'alpha': 0.6})
        >>> range_labels = radar.draw_range_labels(ax=ax)
        >>> param_labels = radar.draw_param_labels(ax=ax)
        """
        # calculate how far out from the center (radius) to place each label, convert to coordinates
        # place one-and-a-half ring widths away from the edge of the last circle
        param_radius = self.center_circle_radius + (self.ring_width * (self.num_rings + 1.5))
        param_xs = param_radius * self.rotation_sin
        param_ys = param_radius * self.rotation_cos
        label_list = []
        # write the labels on the axis
        for idx, label in enumerate(self.params):
            text = ax.text(param_xs[idx], param_ys[idx], label,
                           rotation=self.rotation_degrees[idx], ha='center', va='center', **kwargs)
            label_list.append(text)
        return label_list
