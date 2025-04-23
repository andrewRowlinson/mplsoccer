""" Python module containing helper functions for mplsoccer."""
# Authors: Anmol_Durgapal(@slothfulwave612), Andrew Rowlinson (@numberstorm)
# The FontManager is taken from the ridge_map package by Colin Carroll (@colindcarroll)
# ridge_map is available here: https://github.com/ColCarroll/ridge_map

import warnings
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import matplotlib.font_manager as fm
import numpy as np
from PIL import Image


__all__ = ['add_image', 'validate_ax', 'inset_axes',
           'set_visible', 'FontManager', 'set_labels', 'get_aspect',
           'copy_doc', 'inset_image']


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


def inset_image(x, y, image, width=None, height=None, vertical=False, ax=None, **kwargs):
    """ Adds an image as an inset_axes.

    Parameters
    ----------
    x, y: float
    image: array-like or PIL image
        The image data.
    width, height: float, default None
        The width, height of the inset_axes for plotting the image.
        By default, in the data coordinates.
    vertical : bool, default False
        If the orientation is vertical (True), then the code switches the x and y coordinates.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.

    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.

    Returns
    -------
    matplotlib.axes.Axes

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from PIL import Image
    >>> from urllib.request import urlopen
    >>> from mplsoccer import inset_image
    >>> fig, ax = plt.subplots()
    >>> image_url = 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Messi_vs_Nigeria_2018.jpg'
    >>> image = urlopen(image_url)
    >>> image = Image.open(image)
    >>> ax_image = inset_image(0.5, 0.5, image, width=0.2, ax=ax)
    """
    validate_ax(ax)

    if isinstance(image, Image.Image):
        image_width, image_height = image.size
    else:
        image_height, image_width = image.shape[:2]
    image_aspect = image_height / image_width

    ax_aspect = ax.get_aspect()
    if ax_aspect == 'auto':
        ax_aspect = get_aspect(ax)

    if vertical:
        x, y = y, x

    if height is not None and width is not None:
        raise TypeError('Invalid argument: you must only give one of height or width not both')
    if height is None and width is None:
        raise TypeError('Invalid argument: you must supply one of height or width')

    if width is None:
        width = height / image_aspect * ax_aspect
    elif height is None:
        height = width * image_aspect / ax_aspect

    bbox = (x - width / 2, y - height / 2, width, height)
    ax_inset = ax.inset_axes(bbox, transform=ax.transData, xlim=(0, image_width),
                             ylim=(image_height, 0), **kwargs)
    ax_inset.imshow(image, **kwargs)
    ax_inset.axis('off')
    return ax_inset


def validate_ax(ax):
    """ Error message when ax is missing."""
    if ax is None:
        msg = "Missing 1 required argument: ax. A Matplotlib axis is required for plotting."
        raise TypeError(msg)


def get_aspect(ax):
    """ Get the aspect ratio of an axes.
    From Stackoverflow post by askewchan:
    https://stackoverflow.com/questions/41597177/get-aspect-ratio-of-axes

    Parameters
    ----------
    ax : matplotlib.axes.Axes, default None
    Returns
    -------
    float
    """
    left_bottom, right_top = ax.get_position() * ax.figure.get_size_inches()
    width, height = right_top - left_bottom
    return height / width * ax.get_data_ratio()


def inset_axes(x, y, width=None, height=None, aspect=None, polar=False, vertical=False, ax=None,
               **kwargs):
    """ A function to create an inset axes.

    Parameters
    ----------
    x, y: float
        The x/y coordinate of the center of the inset axes.
    width : float, default None
        The width of the inset axes in the x data coordinates.
    height : float, default None
        The height of the inset axes in the y data coordinates.
    aspect : float or str ('pitch'), default None
        You can specify a combination of height and aspect or width and aspect.
        This will make the axes visually have the given aspect ratio (width/height).
        For example, if you want an inset axes to appear square set aspect = 1.
        For polar plots, this is defaulted to 1.
    polar : bool, default False
        Whether the inset axes if a polar projection.
    vertical : bool, default False
        If the orientation is vertical (True), then the code switches the x and y coordinates.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    **kwargs : All other keyword arguments are passed on to the inset_axes.

    Returns
    --------
    ax : matplotlib.axes.Axes

    Examples
    --------
    >>> from mplsoccer import inset_axes
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> inset_ax = inset_axes(0.5, 0.5, height=0.2, aspect=1, ax=ax)
    """
    validate_ax(ax)
    xlim = kwargs.pop('xlim', (0, 1))
    ylim = kwargs.pop('ylim', (0, 1))
    ax_aspect = ax.get_aspect()
    if not isinstance(polar, bool):
        raise TypeError(f"Invalid 'polar' argument: '{polar}' should be bool.")
    if ax_aspect == 'auto':
        ax_aspect = get_aspect(ax)
    if polar and aspect is not None and aspect != 1:
        warnings.warn('aspect is ignored for polar plots (defaults to 1)', UserWarning)
    if polar:
        aspect = 1
    if vertical:
        x, y = y, x
        width, height = height, width
    if vertical and aspect is not None:
        aspect = 1 / aspect

    if polar and height is not None and width is not None:
        raise TypeError('Invalid argument: for polar axes provide only one of width or height')
    if aspect is not None and width is not None and height is not None:
        raise TypeError('Invalid argument: if using aspect you cannot use both width and height')
    if ((width is not None) + (height is not None) + (aspect is not None)) != 2:
        raise TypeError(
            'Invalid argument: must give the arguments width and height,'
            ' or width and aspect, or height and aspect')

    if aspect is not None and width is None:
        width = height / aspect * ax_aspect
    elif aspect is not None and height is None:
        height = width * aspect / ax_aspect

    bbox = (x - width / 2, y - height / 2, width, height)
    inset_axes = ax.inset_axes(bbox, transform=ax.transData, xlim=xlim, ylim=ylim,
                               polar=polar, **kwargs)
    if polar and vertical:
        inset_axes.set_theta_zero_location('N')
    return inset_axes


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
                 url=('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                      'src/hinted/Roboto-Regular.ttf')):
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

def copy_doc(func):
    """ Decorator to copy a docstring to a new function/method. 
    Inspired by estnani's answer: https://stackoverflow.com/questions/4056983/how-do-i-programmatically-set-the-docstring
    """
    def _doc(new_func):
        new_func.__doc__ = func.__doc__
        return new_func
    return _doc
