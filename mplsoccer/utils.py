""" Python module containing helper functions for mplsoccer."""
# Authors: Anmol_Durgapal(@slothfulwave612), Andrew Rowlinson (@numberstorm)
# The FontManager is taken from the ridge_map package by Colin Carroll (@colindcarroll)
# ridge_map is available here: https://github.com/ColCarroll/ridge_map

from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import matplotlib.font_manager as fm
import numpy as np
from PIL import Image

from mplsoccer import dimensions

__all__ = ['add_image', 'validate_ax', 'set_visible', 'Standardizer', 'FontManager', 'set_labels']


def add_image(image, fig, left, bottom, width=None, height=None, **kwargs):
    """ Adds an image to a figure using fig.add_axes and ax.imshow

    If downsampling an image 'hamming' interpolation is recommended

    Parameters
    ----------
    image: array-like or PIL image
        The image data.
    fig: matplotlib.figure.Figure
        The figure on which to add the image.
    left, bottom: float
        The dimensions left, bottom of the new axes.
        All quantities are in fractions of figure width and height.
        This positions the image axis in the figure left% in from the figure side
        and bottom% in from the figure bottom.
    width, height: float, default None
        The width, height of the new axes.
        All quantities are in fractions of figure width and height.
        For best results use only one of these so the image is scaled appropriately.
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.

    Returns
    -------
    matplotlib.axes.Axes

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from PIL import Image
    >>> from mplsoccer import add_image
    >>> from urllib.request import urlopen
    >>> fig, ax = plt.subplots()
    >>> image_url = 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Messi_vs_Nigeria_2018.jpg'
    >>> image = urlopen(image_url)
    >>> image = Image.open(image)
    >>> ax_image = add_image(image, fig, left=0.1, bottom=0.2, width=0.4, height=0.4)
    """
    if isinstance(image, Image.Image):
        image_width, image_height = image.size
    else:
        image_height, image_width = image.shape[:2]

    image_aspect = image_width / image_height

    figsize = fig.get_size_inches()
    fig_aspect = figsize[0] / figsize[1]

    if height is None:
        height = width / image_aspect * fig_aspect

    if width is None:
        width = height * image_aspect / fig_aspect

    # add image
    ax_image = fig.add_axes((left, bottom, width, height))
    ax_image.axis('off')  # axis off so no labels/ ticks

    ax_image.imshow(image, **kwargs)

    return ax_image


def validate_ax(ax):
    """ Error message when ax is missing."""
    if ax is None:
        msg = "Missing 1 required argument: ax. A Matplotlib axis is required for plotting."
        raise TypeError(msg)


def set_visible(ax, spine_bottom=False, spine_top=False, spine_left=False, spine_right=False,
                grid=False, tick=False, label=False):
    """ Helper method to set the visibility of matplotlib spines, grid and ticks/ labels.
    By default, sets all to invisible.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to set visibility on.
    spine_bottom, spine_top, spine_left, spine_right : bool, default False
        Whether to show the spines.
    grid : bool, default False
        Whether to show the grid lines.
    tick : bool, deafult False
        Whether to draw the ticks.
    label : bool, default False
        Whether to draw the tick labels.
    """
    ax.spines['bottom'].set_visible(spine_bottom)
    ax.spines['top'].set_visible(spine_top)
    ax.spines['left'].set_visible(spine_left)
    ax.spines['right'].set_visible(spine_right)
    ax.grid(grid)
    ax.tick_params(bottom=tick, top=tick, left=tick, right=tick,
                   labelbottom=label, labeltop=label, labelleft=label, labelright=label)


def set_labels(ax, label_value, label_axis):
    """
    Function to set label for a given axis.

    Args:
        ax (axes.Axes): axis object.
        label_value (list): ticklabel values.
        label_axis (str): axis name, 'x' or 'y'

    Returns:
        list: label names
    """
    if label_axis == 'x':
        ax.set_xticks(np.arange(len(label_value)))
        axis = ax.get_xticklabels()
    else:
        ax.set_yticks(np.arange(len(label_value)) + 1)
        axis = ax.get_yticklabels()
    labels = [items.get_text() for items in axis]
    count = 0 if label_axis == 'x' else len(label_value) - 1
    for i in range(len(labels)):
        labels[i] = label_value[count]
        if label_axis == 'x':
            count += 1
        else:
            count -= 1
    return labels


class Standardizer:
    """ Convert from one set of coordinates to another.

    Parameters
    ----------
    pitch_from, pitch_to : str, default 'statsbomb'
        The pitch to convert the coordinates from (pitch_from) and to (pitch_to).
        The supported pitch types are: 'opta', 'statsbomb', 'tracab',
        'wyscout', 'uefa', 'metricasports', 'custom', 'skillcorner' and 'secondspectrum'.
    length_from, length_to : float, default None
        The pitch length in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type.
    width_from, width_to : float, default None
        The pitch width in meters. Only used for the 'tracab' and 'metricasports',
        'skillcorner', 'secondspectrum' and 'custom' pitch_type

    Examples
    --------
    >>> from mplsoccer import Standardizer
    >>> standard = Standardizer(pitch_from='statsbomb', pitch_to='custom', \
                                length_to=105, width_to=68)
    >>> x = [20, 30]
    >>> y = [50, 80]
    >>> x_std, y_std = standard.transform(x, y)

    """
    def __init__(self, pitch_from, pitch_to, length_from=None,
                 width_from=None, length_to=None, width_to=None):

        if pitch_from not in dimensions.valid:
            raise TypeError(f'Invalid argument: pitch_from should be in {dimensions.valid}')
        if (length_from is None or width_from is None) and pitch_from in dimensions.size_varies:
            raise TypeError("Invalid argument: width_from and length_from must be specified.")

        if pitch_to not in dimensions.valid:
            raise TypeError(f'Invalid argument: pitch_to should be in {dimensions.valid}')
        if (length_to is None or width_to is None) and pitch_to in dimensions.size_varies:
            raise TypeError("Invalid argument: width_to and length_to must be specified.")

        self.pitch_from = pitch_from
        self.pitch_to = pitch_to
        self.length_from = length_from
        self.width_from = width_from
        self.length_to = length_to
        self.width_to = width_to

        self.dim_from = dimensions.create_pitch_dims(pitch_type=pitch_from,
                                                     pitch_length=length_from,
                                                     pitch_width=width_from)
        self.dim_to = dimensions.create_pitch_dims(pitch_type=pitch_to,
                                                   pitch_length=length_to,
                                                   pitch_width=width_to)

    def transform(self, x, y, reverse=False):
        """ Transform the coordinates.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        reverse : bool, default False
            If reverse=True then reverse the transform. Therefore, the coordinates
            are converted from pitch_to to pitch_from.

        Returns
        ----------
        x_standardized, y_standardized : np.array 1d
            The coordinates standardized in pitch_to coordinates (or pitch_from if reverse=True).
        """
        # to numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)

        if reverse:
            dim_from, dim_to = self.dim_to, self.dim_from
        else:
            dim_from, dim_to = self.dim_from, self.dim_to

        # clip outside to pitch extents
        x = x.clip(min=dim_from.left, max=dim_from.right)
        y = y.clip(min=dim_from.pitch_extent[2], max=dim_from.pitch_extent[3])

        # for inverted axis flip the coordinates
        if dim_from.invert_y:
            y = dim_from.bottom - y

        x_standardized = self._standardize(dim_from.x_markings_sorted,
                                           dim_to.x_markings_sorted, x)
        y_standardized = self._standardize(dim_from.y_markings_sorted,
                                           dim_to.y_markings_sorted, y)

        # for inverted axis flip the coordinates
        if dim_to.invert_y:
            y_standardized = dim_to.bottom - y_standardized

        return x_standardized, y_standardized

    @staticmethod
    def _standardize(markings_from, markings_to, coordinate):
        """" Helper method to standardize the data"""
        # to deal with nans set nans to zero temporarily
        mask_nan = np.isnan(coordinate)
        coordinate[mask_nan] = 0
        pos = np.searchsorted(markings_from, coordinate)
        low_from = markings_from[pos - 1]
        high_from = markings_from[pos]
        proportion_of_way_between = (coordinate - low_from) / (high_from - low_from)
        low_to = markings_to[pos - 1]
        high_to = markings_to[pos]
        standardized_coordinate = low_to + ((high_to - low_to) * proportion_of_way_between)
        # then set nans back to nan
        standardized_coordinate[mask_nan] = np.nan
        return standardized_coordinate

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'pitch_from={self.pitch_from}, pitch_to={self.pitch_to}, '
                f'length_from={self.length_from}, width_from={self.width_from}, '
                f'length_to={self.length_to}, width_to={self.width_to})')


class FontManager:
    """Utility to load fun fonts from https://fonts.google.com/ for matplotlib.
    Find a nice font at https://fonts.google.com/, and then get its corresponding URL
    from https://github.com/google/fonts/.

    The FontManager is taken from the ridge_map package by Colin Carroll (@colindcarroll).

    Parameters
    ----------
    url : str, default is the url for Roboto-Regular.ttf
        Can really be any .ttf file, but probably looks like
        'https://github.com/google/fonts/blob/main/ofl/cinzel/static/Cinzel-Regular.ttf?raw=true'
        Note 1: make sure the ?raw=true is at the end.
        Note 2: urls like 'https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/static/Cinzel-Regular.ttf'
                allow Cross-Origin Resource Sharing, and work in browser environments
                based on PyOdide (e.g. JupyterLite). Those urls don't need the ?raw=true at the end

    Examples
    --------
    >>> from mplsoccer import FontManager
    >>> import matplotlib.pyplot as plt
    >>> font_url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/abel/Abel-Regular.ttf'
    >>> fm = FontManager(url=font_url)
    >>> fig, ax = plt.subplots()
    >>> ax.text(x=0.5, y=0.5, s="Good content.", fontproperties=fm.prop, size=30)
    """

    def __init__(self,
                 url=('https://raw.githubusercontent.com/google/fonts/main/'
                      'apache/roboto/Roboto%5Bwdth,wght%5D.ttf')):
        self.url = url
        with NamedTemporaryFile(delete=False, suffix=".ttf") as temp_file:
            temp_file.write(urlopen(self.url).read())
            self._prop = fm.FontProperties(fname=temp_file.name)

    @property
    def prop(self):
        """Get matplotlib.font_manager.FontProperties object that sets the custom font."""
        return self._prop

    def __repr__(self):
        return f'{self.__class__.__name__}(font_url={self.url})'
