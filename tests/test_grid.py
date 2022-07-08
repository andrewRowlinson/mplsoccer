""" Test the grid functions, which create a grid of axes."""

import matplotlib.pyplot as plt
import numpy as np

from mplsoccer import grid, grid_dimensions


def test_figsize():
    for i in range(100):
        ax_aspect = np.random.uniform(0.3, 2)
        nrows = np.random.randint(1, 6)
        ncols = np.random.randint(1, 6)
        figwidth = np.random.uniform(0.5, 10)
        figheight = np.random.uniform(0.5, 10)
        max_grid = np.random.uniform(0.5, 1)
        space = np.random.uniform(0, 0.2)

        grid_width, grid_height = grid_dimensions(ax_aspect=ax_aspect,
                                                  figwidth=figwidth,
                                                  figheight=figheight,
                                                  nrows=nrows,
                                                  ncols=ncols,
                                                  max_grid=max_grid,
                                                  space=space)
        assert np.isclose(grid_height - max_grid, 0) or np.isclose(grid_width - max_grid, 0)

        fig, ax = grid(ax_aspect=ax_aspect,
                       figheight=figheight,
                       nrows=nrows,
                       ncols=ncols,
                       grid_height=grid_height,
                       grid_width=grid_width,
                       space=space,
                       endnote_height=0,
                       title_height=0)
        check_figwidth, check_figheight = fig.get_size_inches()

        assert np.isclose(check_figwidth - figwidth, 0)
        assert np.isclose(check_figheight - figheight, 0)
        plt.close(fig)
