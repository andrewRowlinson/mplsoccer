""" Functions to plot a grid of axes with an endnote and title."""

import matplotlib.pyplot as plt
import numpy as np

__all__ = ['_grid_dimensions', '_draw_grid', 'grid', 'grid_dimensions']


def _grid_dimensions(ax_aspect=1, figheight=9, nrows=1, ncols=1,
                     grid_height=0.715, grid_width=0.95, space=0.05,
                     left=None, bottom=None,
                     endnote_height=0, endnote_space=0.01,
                     title_height=0, title_space=0.01,
                     ):
    """ A helper to calculate the grid dimensions.

    Parameters
    ----------
    ax_aspect : float, default 1
        The aspect ratio of the grid's axis (width divided by height).
    figheight : float, default 9
        The figure height in inches.
    nrows, ncols : int, default 1
        Number of rows/columns of axes in the grid.
    grid_height : float, default 0.715
        The height of the grid in fractions of the figure height.
        The default is the grid height is 71.5% of the figure height.
    grid_width : float, default 0.95
        The width of the grid in fractions of the figure width.
        The default is the grid is 95% of the figure width.
    space : float, default 0.05
        The total amount of the grid height reserved for spacing between the grid axes.
        Expressed as a fraction of the grid_height. The default is 5% of the grid height.
        The spacing across the grid width is automatically calculated to maintain even spacing.
    left : float, default None
        The location of the left-hand side of the axes in fractions of the figure width.
        The default of None places the axes in the middle of the figure.
    bottom : float, default None
        The location of the bottom endnote axes in fractions of the figure height.
        The default of None places the axes in the middle of the figure.
        If the endnote_height=0 then the grid is located at the bottom coordinate instead.
    endnote_height: float, default 0
        The height of the endnote axes in fractions of the figure height.
        For, example 0.07 means the endnote axis is 7% of the figure height.
        If endnote_height=0 (default), then the endnote axes is not plotted.
    endnote_space : float, default 0.01
        The space between the grid and endnote axis in fractions of the figure height.
        The default space is 1% of the figure height.
        If endnote_height=0, then the endnote_space is set to zero.
    title_height : float, default 0
        The height of the title axis in fractions of the figure height.
        For, example 0.15 means the title axis is 15% of the figure height.
        If title_height=0 (default), then the title axes is not plotted.
    title_space : float, default 0.01
        The space between the grid and title axis in fractions of the figure height.
        The default space is 1% of the figure height.
        If title_height=0, then the title_space is set to zero.

    Returns
    -------
    dimensions : dict[dimension, value]
        A dictionary holding the axes and figure dimensions.
    """

    # dictionary for holding dimensions
    dimensions = {'figheight': figheight, 'nrows': nrows, 'ncols': ncols,
                  'grid_height': grid_height, 'grid_width': grid_width,
                  'title_height': title_height, 'endnote_height': endnote_height,
                  }

    if left is None:
        left = (1 - grid_width) / 2

    if title_height == 0:
        title_space = 0

    if endnote_height == 0:
        endnote_space = 0

    error_msg_height = ('The axes extends past the figure height. '
                        'Reduce one of the bottom, endnote_height, endnote_space, grid_height, '
                        'title_space or title_height so the total is ≤ 1.')
    error_msg_width = ('The grid axes extends past the figure width. '
                       'Reduce one of the grid_width or left so the total is ≤ 1.')

    axes_height = (endnote_height + endnote_space + grid_height +
                   title_height + title_space)
    if axes_height > 1:
        raise ValueError(error_msg_height)

    if bottom is None:
        bottom = (1 - axes_height) / 2

    if bottom + axes_height > 1:
        raise ValueError(error_msg_height)

    if left + grid_width > 1:
        raise ValueError(error_msg_width)

    dimensions['left'] = left
    dimensions['bottom'] = bottom
    dimensions['title_space'] = title_space
    dimensions['endnote_space'] = endnote_space

    if (nrows > 1) and (ncols > 1):
        dimensions['figwidth'] = figheight * grid_height / grid_width * (((1 - space) * ax_aspect *
                                                                          ncols / nrows) +
                                                                         (space * (ncols - 1) / (
                                                                                 nrows - 1)))
        dimensions['spaceheight'] = grid_height * space / (nrows - 1)
        dimensions['spacewidth'] = dimensions['spaceheight'] * figheight / dimensions['figwidth']
        dimensions['axheight'] = grid_height * (1 - space) / nrows

    elif (nrows > 1) and (ncols == 1):
        dimensions['figwidth'] = figheight * grid_height / grid_width * (
                1 - space) * ax_aspect / nrows
        dimensions['spaceheight'] = grid_height * space / (nrows - 1)
        dimensions['spacewidth'] = 0
        dimensions['axheight'] = grid_height * (1 - space) / nrows

    elif (nrows == 1) and (ncols > 1):
        dimensions['figwidth'] = figheight * grid_height / grid_width * (space + ax_aspect * ncols)
        dimensions['spaceheight'] = 0
        dimensions['spacewidth'] = grid_height * space * figheight / dimensions['figwidth'] / (
                ncols - 1)
        dimensions['axheight'] = grid_height

    else:  # nrows=1, ncols=1
        dimensions['figwidth'] = figheight * grid_height * ax_aspect / grid_width
        dimensions['spaceheight'] = 0
        dimensions['spacewidth'] = 0
        dimensions['axheight'] = grid_height

    dimensions['axwidth'] = dimensions['axheight'] * ax_aspect * figheight / dimensions['figwidth']

    return dimensions


def _draw_grid(dimensions, left_pad=0, right_pad=0, axis=True, grid_key='grid'):
    """ A helper to create a grid of axes in a specified location

    Parameters
    ----------
    dimensions : dict[dimension, value]
        A dictionary holding the axes and figure dimensions.
        This is created via the _grid_dimensions function.
    left_pad, right_pad : float, default 0
        The padding for the title and endnote. Usually the endnote and title
        are flush to the sides of the axes grid. With the padding option you can
        indent the title and endnote so that there is a gap between the grid axes
        and the title/endnote. The padding units are fractions of the figure width.
    axis : bool, default True
        Whether the endnote and title axes are 'on'.
    grid_key : str, default grid
        The dictionary key for the main axes in the grid.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axs : dict[label, Axes]
        A dictionary mapping the labels to the Axes objects.
    """
    dims = dimensions
    bottom_coordinates = np.tile(dims['spaceheight'] + dims['axheight'],
                                 reps=dims['nrows'] - 1).cumsum()
    bottom_coordinates = np.insert(bottom_coordinates, 0, 0.)
    bottom_coordinates = np.repeat(bottom_coordinates, dims['ncols'])
    grid_bottom = dims['bottom'] + dims['endnote_height'] + dims['endnote_space']
    bottom_coordinates = bottom_coordinates + grid_bottom
    bottom_coordinates = bottom_coordinates[::-1]

    left_coordinates = np.tile(dims['spacewidth'] + dims['axwidth'],
                               reps=dims['ncols'] - 1).cumsum()
    left_coordinates = np.insert(left_coordinates, 0, 0.)
    left_coordinates = np.tile(left_coordinates, dims['nrows'])
    left_coordinates = left_coordinates + dims['left']

    fig = plt.figure(figsize=(dims['figwidth'], dims['figheight']))
    axs = []
    for idx, bottom_coord in enumerate(bottom_coordinates):
        axs.append(fig.add_axes((left_coordinates[idx], bottom_coord,
                                 dims['axwidth'], dims['axheight'])))
    axs = np.squeeze(np.array(axs).reshape((dims['nrows'], dims['ncols'])))
    if axs.size == 1:
        axs = axs.item()
    result_axes = {grid_key: axs}

    title_left = dims['left'] + left_pad
    title_width = dims['grid_width'] - left_pad - right_pad

    if dims['title_height'] > 0:
        ax_title = fig.add_axes(
            (title_left, grid_bottom + dims['grid_height'] + dims['title_space'],
             title_width, dims['title_height']))
        if axis is False:
            ax_title.axis('off')
        result_axes['title'] = ax_title

    if dims['endnote_height'] > 0:
        ax_endnote = fig.add_axes((title_left, dims['bottom'],
                                   title_width, dims['endnote_height']))
        if axis is False:
            ax_endnote.axis('off')
        result_axes['endnote'] = ax_endnote

    if dims['title_height'] == 0 and dims['endnote_height'] == 0:
        return fig, result_axes[grid_key]  # no dictionary if just grid
    return fig, result_axes  # else dictionary


def grid(ax_aspect=1, figheight=9, nrows=1, ncols=1,
         grid_height=0.715, grid_width=0.95, space=0.05,
         left=None, bottom=None,
         endnote_height=0, endnote_space=0.01,
         title_height=0, title_space=0.01, axis=True, grid_key='grid'):
    """ Create a grid of axes in a specified location

    Parameters
    ----------
    ax_aspect : float, default 1
        The aspect ratio of the grid's axis (width divided by height).
    figheight : float, default 9
        The figure height in inches.
    nrows, ncols : int, default 1
        Number of rows/columns of axes in the grid.
    grid_height : float, default 0.715
        The height of the grid in fractions of the figure height.
        The default is the grid height is 71.5% of the figure height.
    grid_width : float, default 0.95
        The width of the grid in fractions of the figure width.
        The default is the grid is 95% of the figure width.
    space : float, default 0.05
        The total amount of the grid height reserved for spacing between the grid axes.
        Expressed as a fraction of the grid_height. The default is 5% of the grid height.
        The spacing across the grid width is automatically calculated to maintain even spacing.
    left : float, default None
        The location of the left-hand side of the axes in fractions of the figure width.
        The default of None places the axes in the middle of the figure.
    bottom : float, default None
        The location of the bottom endnote axes in fractions of the figure height.
        The default of None places the axes in the middle of the figure.
        If the endnote_height=0 then the grid is located at the bottom coordinate instead.
    endnote_height: float, default 0
        The height of the endnote axes in fractions of the figure height.
        For, example 0.07 means the endnote axis is 7% of the figure height.
        If endnote_height=0 (default), then the endnote axes is not plotted.
    endnote_space : float, default 0.01
        The space between the grid and endnote axis in fractions of the figure height.
        The default space is 1% of the figure height.
        If endnote_height=0, then the endnote_space is set to zero.
    title_height : float, default 0
        The height of the title axis in fractions of the figure height.
        For, example 0.15 means the title axis is 15% of the figure height.
        If title_height=0 (default), then the title axes is not plotted.
    title_space : float, default 0.01
        The space between the grid and title axis in fractions of the figure height.
        The default space is 1% of the figure height.
        If title_height=0, then the title_space is set to zero.
    axis : bool, default True
        Whether the endnote and title axes are 'on'.
    grid_key : str, default grid
        The dictionary key for the main axes in the grid.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axs : dict[label, Axes]
        A dictionary mapping the labels to the Axes objects.
    """
    dimensions = _grid_dimensions(ax_aspect=ax_aspect, figheight=figheight, nrows=nrows,
                                  ncols=ncols,
                                  grid_height=grid_height, grid_width=grid_width, space=space,
                                  left=left, bottom=bottom,
                                  endnote_height=endnote_height, endnote_space=endnote_space,
                                  title_height=title_height, title_space=title_space,
                                  )
    fig, ax = _draw_grid(dimensions, axis=axis, grid_key=grid_key)
    return fig, ax


def grid_dimensions(ax_aspect, figwidth, figheight, nrows, ncols, max_grid, space):
    """ Propose a grid_width and grid_height for grid based on the inputs.

    Parameters
    ----------
    ax_aspect : float, default 1
        The aspect ratio of the grid's axis (width divided by height).
    figwidth, figheight : float
        The figure width/height in inches.
    nrows, ncols : int
        Number of rows/columns of axes in the grid.
    max_grid : float
        The longest side of the grid in fractions of the figure width / height.
        Should be between zero and one.
    space : float
        The total amount of the grid height reserved for spacing between the grid axes.
        Expressed as a fraction of the grid_height.

    Returns
    -------
    grid_width, grid_height : the suggested grid_width and grid_height
    """
    # grid1 = calculate the grid_width given the max_grid as grid_height
    # grid2 = calculate grid_height given the max_grid as grid_width

    if ncols > 1 and nrows == 1:
        grid1 = max_grid * figheight / figwidth * (space + ax_aspect * ncols)
        grid2 = max_grid / figheight * figwidth / (space + ax_aspect * ncols)
    elif ncols > 1 or nrows > 1:
        extra = space * (ncols - 1) / (nrows - 1)
        grid1 = max_grid * figheight / figwidth * (((1 - space) * ax_aspect *
                                                    ncols / nrows) + extra)
        grid2 = max_grid / figheight * figwidth / (((1 - space) * ax_aspect *
                                                    ncols / nrows) + extra)
    else:  # nrows=1, ncols=1
        grid1 = max_grid * figheight / figwidth * ax_aspect
        grid2 = max_grid / figheight * figwidth / ax_aspect

    # decide whether the max_grid is the grid_width or grid_height and set the other value
    if (grid1 > 1) | ((grid2 >= grid1) & (grid2 <= 1)):
        return max_grid, grid2
    return grid1, max_grid
