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

__all__ = ['add_image', 'validate_ax', 'get_indices_between',
           'get_coordinates', 'Standardizer', 'FontManager']


def get_coordinates(n):
    """
    Function for getting coordinates and rotation values for the labels.

    Args:
        n (int): number of labels.

    Returns:
        list: coordinate and rotation values.
    """

    # calculate alpha
    alpha = 2 * np.pi / n

    # rotation values
    alphas = alpha * np.arange(n)

    # x-coordinate value
    coord_x = np.cos(alphas)

    # y-coordinate value
    coord_y = np.sin(alphas)

    return np.c_[coord_x, coord_y, alphas]


def get_vertex_coord(old_value, old_min, old_max, new_min, new_max):
    """
    Function for getting coordinate for each vertex of the polygon.

    Args:
        old_value, old_min, old_max, new_min, new_max -- float values.

    Returns:
        float: the coordinate value either x or y.
    """

    # calculate the value
    new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

    return new_value


def get_indices_between(range_list, coord_list, value, reverse):
    """
    Function to get the x-coordinate and y-coordinate for the polygon vertex.

    Args:
        range_list (list): range value for a particular parameter.
        coord_list (list): coordinate values where the numerical labels are placed.
        value (float): the value of the parameter.
        reverse (bool): to tell whether the range values are in reversed order or not.

    Returns:
        tuple: x-coordinate and y-coordinate value.
    """

    # getting index value
    idx_1, idx_2 = get_index(array=range_list, value=value, reverse=reverse)

    # get x coordinate
    x_coord = get_vertex_coord(
        old_value=value,
        old_min=range_list[idx_1],
        old_max=range_list[idx_2],
        new_min=coord_list[idx_1][0],
        new_max=coord_list[idx_2][0]
    )

    # get y coordinate
    y_coord = get_vertex_coord(
        old_value=value,
        old_min=range_list[idx_1],
        old_max=range_list[idx_2],
        new_min=coord_list[idx_1][1],
        new_max=coord_list[idx_2][1]
    )

    return x_coord, y_coord


def get_index(array, value, reverse):
    """
    Function to get the indices of two list items between which the value lies.

    Args:
        array (list): containing numerical values.
        value (float/int): value to be searched.
        reverse (bool): whether or not the range values are in reverse order.

    Returns:
        int: the two indices between which value lies.
    """

    if reverse:
        # loop over the array/list
        for i in range(0, len(array) - 1):
            if array[i] >= value >= array[i + 1]:
                return i, i + 1

    # loop over the array/list
    for i in range(0, len(array) - 1):
        if array[i] <= value <= array[i + 1]:
            return i, i + 1


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

    # fetch labels
    labels = [items.get_text() for items in axis]

    # init a count variable
    if label_axis == 'x':
        count = 0
    else:
        count = len(label_value) - 1

    # iterate through all the labels and change the label name
    for i in range(len(labels)):
        labels[i] = label_value[count]

        if label_axis == 'x':
            count += 1
        else:
            count -= 1

    return labels


def add_image(image, fig, left, bottom, width=None, height=None, **kwargs):
    """ Adds an image to a figure using fig.add_axes and ax.imshow

    If downsampling an image 'hamming' interpolation is recommended

    Parameters
    ----------
    image: str
        The path to the image.
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
    matplotlib.figure.Figure

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from mplsoccer import add_image
    >>> from urllib.request import urlopen
    >>> fig, ax = plt.subplots()
    >>> image_url = 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Messi_vs_Nigeria_2018.jpg'
    >>> image = urlopen(image_url)
    >>> fig = add_image(image, fig, left=0.1, bottom=0.2, width=0.4, height=0.4)
    """
    # open image
    image = Image.open(image)

    # height, width, channel of shape
    image_width, image_height = image.size
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

    return fig


def set_size(w, h, ax=None):
    """
    Function to set size of an axes in a subplot.

    Args:
        w (float): width of the axes.
        h (float): height of the axes.
        ax (axes.Axes): axes object
    """
    # compute width and height
    left = ax.figure.subplotpars.left
    right = ax.figure.subplotpars.right
    top = ax.figure.subplotpars.top
    bottom = ax.figure.subplotpars.bottom
    figw = float(w) / (right - left)
    figh = float(h) / (top - bottom)

    # set size
    ax.figure.set_size_inches(figw, figh)


def validate_ax(ax):
    """ Error message when ax is missing."""
    if ax is None:
        msg = "Missing 1 required argument: ax. A Matplotlib axis is required for plotting."
        raise TypeError(msg)


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
            If reverse=True then reverse the transform. Therefore the coordinates
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
        'https://github.com/google/fonts/blob/master/ofl/cinzel/static/Cinzel-Regular.ttf?raw=true'
        Note make sure the ?raw=true is at the end.

    Examples
    --------
    >>> from mplsoccer import FontManager
    >>> import matplotlib.pyplot as plt
    >>> font_url = 'https://github.com/google/fonts/blob/master/ofl/abel/Abel-Regular.ttf?raw=true'
    >>> fm = FontManager(url=font_url)
    >>> fig, ax = plt.subplots()
    >>> ax.text("Good content.", fontproperties=fm.prop, size=60)
    """

    def __init__(self,
                 url=('https://github.com/google/fonts/blob/master/'
                      'apache/roboto/static/Roboto-Regular.ttf?raw=true')):
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
