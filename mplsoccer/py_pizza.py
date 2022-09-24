"""A Python module for plotting pizza-plots.

Author: Anmol_Durgapal(@slothfulwave612)

The idea is inspired by Tom Worville, Football Slices, Soma Zero FC and Soumyajit Bose.
"""

import matplotlib.pyplot as plt
import numpy as np

__all__ = ["PyPizza"]


class PyPizza:
    """A class for plotting pizza charts in Matplotlib.

    Parameters
    ----------
    params : sequence of str
        The name of parameters (e.g. 'Key Passes')
    min_range, max_range : sequence of floats, default None
        Minimum and maximum range for each parameter
    background_color : str, default "#F2F2F2"
        The background-color of the plot.
    inner_circle_size : float, default 5.0
        Size of the inner circle.
    straight_line_limit : float, default 100.0
        Limit till which straight line will go.
    straight_line_color : str, default "#808080"
        Color for the straight-lines.
    straight_line_lw : float, default 2.0
        Linewidth for the straight-lines.
    straight_line_ls : str, default '-'
        Linestyle for the straight-lines.
    last_circle_color : str, default "#000000"
        Color for the last circle.
    last_circle_lw : float, default 2.0
        Linewidth for the last circle.
    last_circle_ls : str, default '-'
        Linestyle for the last circle.
    other_circle_color : str, default "#808080"
        Color for other circles.
    other_circle_lw : float, default 2.0
        Linewidth for other circle.
    other_circle_ls : str, default "--"
        Linestyle for other circle.
    """

    def __init__(self, params, min_range=None, max_range=None,
                 background_color="#F2F2F2", inner_circle_size=5.0, straight_line_limit=100.0,
                 straight_line_color="#808080", straight_line_lw=2.0, straight_line_ls='-',
                 last_circle_color="#000000", last_circle_lw=2.0, last_circle_ls='-',
                 other_circle_color="#808080", other_circle_lw=2.0, other_circle_ls="--"):
        self.params = params
        self.min_range = min_range
        self.max_range = max_range
        self.background_color = background_color
        self.inner_circle_size = inner_circle_size
        self.straight_line_limit = straight_line_limit
        self.straight_line_color = straight_line_color
        self.straight_line_lw = straight_line_lw
        # if any of the linewidths are zero set the linestyle to solid
        # to prevent https://github.com/andrewRowlinson/mplsoccer/issues/71
        if straight_line_lw == 0:
            self.straight_line_ls = 'solid'
        else:
            self.straight_line_ls = straight_line_ls
        self.last_circle_color = last_circle_color
        self.last_circle_lw = last_circle_lw
        if last_circle_lw == 0:
            self.last_circle_ls = 'solid'
        else:
            self.last_circle_ls = last_circle_ls
        self.other_circle_color = other_circle_color
        self.other_circle_lw = other_circle_lw
        if other_circle_lw == 0:
            self.other_circle_ls = 'solid'
        else:
            self.other_circle_ls = other_circle_ls
        self.param_texts = []
        self.value_texts = []
        self.compare_value_texts = []
        self.theta = None  # filled-in by make_pizza method

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'params={self.params}, '
                f'min_range={self.min_range}, '
                f'max_range={self.max_range}, '
                f'background_color={self.background_color}, '
                f'inner_circle_size={self.inner_circle_size}, '
                f'straight_line_limit={self.straight_line_limit}, '
                f'straight_line_color={self.straight_line_color}, '
                f'straight_line_lw={self.straight_line_lw}, '
                f'straight_line_ls={self.straight_line_ls}, '
                f'last_circle_color={self.last_circle_color}, '
                f'last_circle_lw={self.last_circle_lw}, '
                f'last_circle_ls={self.last_circle_ls}, '
                f'other_circle_color={self.other_circle_color}, '
                f'other_circle_lw={self.other_circle_lw}, '
                f'other_circle_ls={self.other_circle_ls}, ')

    def make_pizza(self, values, compare_values=None, bottom=0.0, figsize=(24, 16),
                   ax=None, param_location=108, slice_colors=None, value_colors=None,
                   compare_colors=None, value_bck_colors=None, compare_value_colors=None,
                   compare_value_bck_colors=None, color_blank_space=None, blank_alpha=0.5,
                   kwargs_slices=None, kwargs_compare=None, kwargs_params=None, kwargs_values=None,
                   kwargs_compare_values=None):
        """To make the pizza plot.

            Parameters
            ----------
            values : sequence of floats/int
                Values for each parameter.
            compare_values : sequence of floats/int, default None
                Comparison Values for each parameter.
            bottom : float, default 0.0
                Start value for the bar.
            figsize : tuple of floats, default (24, 16)
                The figure size in inches (width, height).
            ax : matplotlib axis, default None
                matplotlib.axes.Axes.
                If None is specified the pitch is plotted on a new figure.
            param_location : float, default 108
                Location where params will be added.
            slice_colors : sequence of str, default None
                Color for individual slices.
            value_colors : sequence of str, default None
                Color for the individual values-text.
            compare_colors : sequence of str, default None
                Color for the individual comparison-slices.
            value_bck_colors : sequence of str, default None
                Color for background text-box for individual value-text.
            compare_value_colors : sequence of str, default None
                Color for the individual comparison-values-text.
            compare_value_bck_colors : sequence of str, default None
                Color for background text-box for individual comparison-value-text.
            color_blank_space : str/sequence of str, default None.
                To color the blank space area in the plot.
                        if "same" --> same color as main-slices
                        if sequence of str --> colors from the defined sequence
            blank_alpha : float, default 0.5
                Alpha value for blank-space-colors

            **kwargs_slices : All keyword arguments are passed on to axes.Axes.bar for slices.
            **kwargs_compare : All keyword arguments are passed on to axes.Axes.bar
                               for comparison-slices.
            **kwargs_params : All keyword arguments are passed on to axes.Axes.text
                              for adding parameters.
            **kwargs_values : All keyword arguments are passed on to axes.Axes.text
                              for adding values.
            **kwargs_compare_values : All keyword arguments are passed on to axes.Axes.text
                              for adding comparison-values.

            Returns
            -------
            If ax=None returns a matplotlib Figure and Axes.
            Else the settings are applied on an existing axis and returns None.
        """
        if len(self.params) != len(values):
            raise Exception("Length of params and values are not equal!!!")
        if slice_colors is not None and len(slice_colors) != len(self.params):
            raise Exception("Length of slice_colors and params are not equal!!!")
        if value_colors is not None and len(value_colors) != len(self.params):
            raise Exception("Length of text_colors and params are not equal!!!")
        if value_bck_colors is not None and len(value_bck_colors) != len(self.params):
            raise Exception("Length of text_bck_colors and params are not equal!!!")
        if compare_value_bck_colors is not None and len(compare_value_bck_colors) != len(values):
            raise Exception("Length of compare_value_bck_colors and values are not equal!!!")
        if value_bck_colors is not None and len(value_bck_colors) != len(self.params):
            raise Exception("Length of text_bck_colors and params are not equal!!!")
        if self.min_range is not None and len(self.min_range) != len(self.max_range):
            raise Exception("Length of min_range and max_range are not equal!!!")
        if self.min_range is not None and len(self.min_range) != len(values):
            raise Exception("Length of min_range and values are not equal!!!")
        if isinstance(color_blank_space, list) and len(color_blank_space) != len(self.params):
            raise Exception("Length of color_blank_space and params are not equal!!!")

        # set empty dict if None
        if kwargs_slices is None:
            kwargs_slices = dict()
        if kwargs_compare is None:
            kwargs_compare = dict()
        if kwargs_params is None:
            kwargs_params = dict()
        if kwargs_values is None:
            kwargs_values = dict()
        if kwargs_compare_values is None:
            kwargs_compare_values = dict()

        if ax is None:
            fig, ax = plt.subplots(
                figsize=figsize, facecolor=self.background_color,
                subplot_kw={'projection': 'polar'}
            )
            ax.set_facecolor(self.background_color)

            return_fig_ax = True
        else:
            return_fig_ax = False

        # total number of attributes
        total_params = len(self.params)

        # calculate theta value and width of the bar
        self.theta, width = np.linspace(
            0.0, 2 * np.pi, total_params, endpoint=False, retstep=True
        )

        if self.min_range is not None and self.max_range is not None:
            self.min_range = np.array(self.min_range)
            self.max_range = np.array(self.max_range)
            temp_values = self.__get_value(values)
        else:
            temp_values = values

        # plot slice for values
        main_slice = ax.bar(
            x=self.theta, height=temp_values, width=width,
            bottom=bottom, **kwargs_slices
        )

        # color individual slices
        if slice_colors is not None:
            for index, slices in enumerate(main_slice):
                slices.set_facecolor(slice_colors[index])

        # color blank area
        if color_blank_space is not None:
            blank_space = ax.bar(
                self.theta, height=self.straight_line_limit,
                width=width,
                bottom=bottom,
                zorder=main_slice[0].get_zorder()-1
            )

            if color_blank_space == "same":
                for index, (blank, slice_) in enumerate(zip(blank_space, main_slice)):
                    blank.set_facecolor(slice_.get_facecolor())
                    blank.set_alpha(blank_alpha)
            else:
                for blank, color in zip(blank_space, color_blank_space):
                    blank.set_facecolor(color)
                    blank.set_alpha(blank_alpha)

        # add comparison values
        if compare_values is not None:

            if self.min_range is not None and self.max_range is not None:
                temp_compare_values = self.__get_value(compare_values)
            else:
                temp_compare_values = compare_values

            compare_slice = ax.bar(
                x=self.theta, height=temp_compare_values, width=width,
                bottom=bottom, **kwargs_compare
            )

            for idx, (slice_c, slice_m) in enumerate(zip(compare_slice, main_slice)):
                if temp_values[idx] <= temp_compare_values[idx]:
                    slice_c.set_zorder(slice_m.get_zorder() - 0.1)
                if temp_values[idx] > temp_compare_values[idx]:
                    slice_c.set_zorder(slice_m.get_zorder() + 0.1)

            # color individual slices
            if compare_colors is not None:
                for index, slices in enumerate(compare_slice):
                    slices.set_facecolor(compare_colors[index])

        else:
            temp_compare_values = None

        # setup-pizza
        self.__setup_pizza(ax, width)

        # add text
        self.__add_texts(
            ax, values, param_location,
            value_colors=value_colors, value_bck_colors=value_bck_colors,
            compare_values=compare_values, compare_value_colors=compare_value_colors,
            temp_values=temp_values, temp_compare_values=temp_compare_values,
            compare_value_bck_colors=compare_value_bck_colors,
            kwargs_params=kwargs_params, kwargs_values=kwargs_values,
            kwargs_compare_values=kwargs_compare_values
        )

        if return_fig_ax:
            return fig, ax
        return None

    def __setup_pizza(self, ax, width):
        """To set up the pizza plot.

            Parameters
            ----------
            ax : matplotlib axis.
                matplotlib.axes.Axes.
            width : sequence of float.
                width of the slices.
        """
        # degrees gone
        ax.tick_params(labelbottom=False)

        # inner circle size
        ax.set_rorigin(-self.inner_circle_size)

        # values off
        ax.set_yticklabels([])
        ax.set_xticklabels([])

        # start from top and to the right
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)

        # set up line for each bar
        ax.set_thetagrids((self.theta+width/2) * 180 / np.pi)

        # last circle off
        ax.spines['polar'].set_visible(False)

        # set limit for straight line
        ax.set_rmax(self.straight_line_limit)

        # for last circle
        index = -1
        gridlines = ax.yaxis.get_gridlines()
        gridlines[index].set_color(self.last_circle_color)
        gridlines[index].set_linewidth(self.last_circle_lw)

        gridlines[index].set_linestyle(self.last_circle_ls)

        # for other circles excluding last circle
        for i in list(ax.yaxis.get_gridlines())[:-1]:
            i.set_color(self.other_circle_color)
            i.set_linewidth(self.other_circle_lw)
            i.set_linestyle(self.other_circle_ls)

        # for other straight-line
        for i in list(ax.xaxis.get_gridlines()):
            i.set_color(self.straight_line_color)
            i.set_linewidth(self.straight_line_lw)
            i.set_linestyle(self.straight_line_ls)

    def __add_texts(self, ax, values, param_location,
                    temp_values=None, temp_compare_values=None,
                    value_colors=None, value_bck_colors=None,
                    compare_values=None, compare_value_colors=None,
                    compare_value_bck_colors=None,
                    kwargs_params=None, kwargs_values=None, kwargs_compare_values=None):
        """To make the pizza plot.

            Parameters
            ----------
            ax : matplotlib axis.
                matplotlib.axes.Axes.
            values : sequence of floats/int
                Values for each parameter.
            param_location : float, default 108
                Location where params will be added.
            temp_values : sequence of floats/int
                Values for each parameter (if ranges are specified)
            temp_compare_values : sequence of floats/int
                Comparison-Values for each parameter (if ranges are specified)
            value_colors : sequence of str, default None
                Color for the individual values-text.
            value_bck_colors : sequence of str, default None
                Color for background text-box for individual value-text.
            compare_values : sequence of floats/int, default None
                Comparison Values for each parameter.
            compare_value_colors : sequence of str, default None
                Color for the individual comparison-values-text.
            compare_value_bck_colors : sequence of str, default None
                Color for background text-box for individual comparison-value-text.

            **kwargs_params : All keyword arguments are passed on to axes.Axes.text
                              for adding parameters.
            **kwargs_values : All keyword arguments are passed on to axes.Axes.text
                              for adding values.
            **kwargs_compare_values : All keyword arguments are passed on to axes.Axes.text
                              for adding comparison-values.

            Returns
            -------
            If ax=None returns a matplotlib Figure and Axes.
            Else the settings are applied on an existing axis and returns None.
        """
        # set to empty dict if None
        if kwargs_params is None:
            kwargs_params = dict()
        if kwargs_values is None:
            kwargs_values = dict()
        if kwargs_compare_values is None:
            kwargs_compare_values = dict()

        # total length of parameters
        total_params = len(self.params)

        # get the rotation angles
        rotation = (2 * np.pi / total_params) * np.arange(total_params)

        # flip the rotation if the label is in lower half
        mask_flip_label = (rotation > np.pi / 2) & (rotation < np.pi / 2 * 3)
        rotation[mask_flip_label] = rotation[mask_flip_label] + np.pi
        rotation_degrees = -np.rad2deg(rotation)

        # plot params
        for x, rotation, label in zip(self.theta, rotation_degrees, self.params):
            temp_text = ax.text(
                x, param_location, label,
                rotation=rotation, rotation_mode="anchor",
                ha="center", **kwargs_params
            )

            self.param_texts.append(temp_text)

        # plot values
        for i, (x, value, rotation) in enumerate(zip(self.theta, values, rotation_degrees)):
            if value_colors is not None:
                kwargs_values["color"] = value_colors[i]
            if value_bck_colors is not None and kwargs_values.get("bbox") is not None:
                kwargs_values["bbox"]["facecolor"] = value_bck_colors[i]

            temp_text = ax.text(
                x, temp_values[i], value, ha="center", **kwargs_values
            )

            self.value_texts.append(temp_text)

        # plot comparison values
        if compare_values is not None:
            for i, (x, value, rotation) in enumerate(zip(self.theta, compare_values,
                                                         rotation_degrees)):
                if compare_value_colors is not None:
                    kwargs_compare_values["color"] = compare_value_colors[i]
                if compare_value_bck_colors is not None and kwargs_values.get("bbox") is not None:
                    kwargs_compare_values["bbox"]["facecolor"] = compare_value_bck_colors[i]

                if temp_compare_values is not None:
                    value_1 = temp_compare_values[i]
                    value_2 = value
                else:
                    value_1 = value_2 = value

                temp_text = ax.text(
                    x, value_1, value_2, ha="center", **kwargs_compare_values
                )

                self.compare_value_texts.append(temp_text)

    def __get_value(self, values):
        """To get values if ranges are passed."""
        label_range = np.abs(self.max_range - self.min_range)
        range_min = np.minimum(self.min_range, self.max_range)
        range_max = np.maximum(self.min_range, self.max_range)
        values_clipped = np.minimum(np.maximum(values, range_min), range_max)
        proportion = np.abs(values_clipped - self.min_range) / label_range
        vertices = (proportion * 100)

        return vertices

    def adjust_texts(self, params_offset, offset=0.0, adj_comp_values=False):
        """ To adjust the value-texts. (if they are overlapping)

        Parameters
        ----------
        params_offset : sequence of bool
            Pass True for parameter whose value are to be adjusted.
        offset : float, default 0.0
            The value will define how much adjustment will be made.
        adj_comp_values : bool, defaults False
            To make adjustment for comparison-values-text.
        """
        if len(params_offset) != len(self.params):
            raise Exception("Length of params_offset and params are not equal!!!")

        # fetch index where value is True
        idx_value = [i for i, x in enumerate(params_offset) if x]

        if adj_comp_values:
            texts = self.get_compare_value_texts()
        else:
            texts = self.get_value_texts()

        # iterate over text objects and adjust the text for which params_offset is True
        for count, (temp_text, theta) in enumerate(
            zip(texts, self.get_theta())
        ):
            # fetch the value
            adj_val = offset if count in idx_value else 0.0

            # adjust the position
            # add some value to x-coordinate and keep y-coordinate same
            temp_text.set_position((
                theta+adj_val, temp_text.get_position()[1]
            ))

    def get_param_texts(self):
        """To fetch list of axes.text for params."""
        return self.param_texts

    def get_value_texts(self):
        """To fetch list of axes.text for values."""
        return self.value_texts

    def get_compare_value_texts(self):
        """To fetch list of axes.text for comparison-values."""
        return self.compare_value_texts

    def get_theta(self):
        """To fetch list containing theta values (x-coordinate for each text)."""
        return self.theta

    # __str__ is the same as __repr__
    __str__ = __repr__
