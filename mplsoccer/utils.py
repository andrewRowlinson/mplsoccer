"""
__author__: Anmol_Durgapal(@slothfulwave612)

Python module containing helper functions.
"""

# necessary packages/modules
import numpy as np
from PIL import Image

__all__ = ['add_image', 'validate_ax', 'get_indices_between', 'get_coordinates']


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
    """
    Adds an image to a figure using fig.add_axes and ax.imshow

    Args:
        image (str): image path.
        fig (matplotlib.figure.Figure): figure object
        left (float): The left dimension of the new axes.
        bottom (float): The bottom dimension of the new axes.
        width (float, optional): The width of the new axes. Defaults to None.
        height (float, optional): The height of the new axes. Defaults to None.
        **kwargs: All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.

    Returns:
        matplotlib.figure.Figure: figure object.
    """
    # open image
    image = Image.open(image)

    # height, width, channel of shape
    shape = np.array(image).shape

    image_height, image_width = shape[0], shape[1]
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
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w) / (r - l)
    figh = float(h) / (t - b)

    # set size
    ax.figure.set_size_inches(figw, figh)


def validate_ax(ax):
    if ax is None:
        raise TypeError("Missing 1 required argument: ax. A Matplotlib axis is required for plotting.")

