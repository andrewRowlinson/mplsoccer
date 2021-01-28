from collections import namedtuple

import matplotlib.docstring as docstring
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import rcParams
from matplotlib.collections import PatchCollection
from scipy.spatial import Voronoi
from scipy.stats import circmean, gaussian_kde

from mplsoccer._pitch_base import BasePitch
from mplsoccer.heatmap import bin_statistic, bin_statistic_positional, heatmap, heatmap_positional
from mplsoccer.linecollection import lines
from mplsoccer.quiver import arrows
from mplsoccer.scatterutils import scatter_football, scatter_rotation
from mplsoccer.utils import validate_ax

_BinnedStatisticResult = namedtuple('BinnedStatisticResult',
                                    ('statistic', 'x_grid', 'y_grid', 'cx', 'cy'))


class BasePitchPlot(BasePitch):
    """ This class adds the plotting methods to the Pitch classes"""

    def plot(self, x, y, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.plot,
        which automatically flips the x and y coordinates if the pitch is vertical.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.plot.

        Returns
        -------
        lines : A list of Line2D objects representing the plotted data.
        """
        validate_ax(ax)
        x, y = self._reverse_if_vertical(x, y)
        return ax.plot(x, y, **kwargs)

    def scatter(self, x, y, rotation_degrees=None, marker=None, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.scatter,
        which automatically flips the x and y coordinates if the pitch is vertical.
        Can optionally use a football marker with marker='football'.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        rotation_degrees: array-like or scalar, default None.
            Rotates the marker in degrees, clockwise. 0 degrees is facing the direction of play.
            In a horizontal pitch, 0 degrees is this way →, in a vertical pitch,
            0 degrees is this way ↑
        marker: MarkerStyle, optional
            The marker style. marker can be either an instance of the class or the
            text shorthand for a particular marker. Defaults to None, in which case it takes
            the value of rcParams["scatter.marker"] (default: 'o') = 'o'.
            If marker='football' plots a football shape with the pentagons the color
            of the edgecolors and hexagons the color of the 'c' argument; 'linewidths'
            also sets the linewidth of the football marker.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.

        Returns
        -------
        paths : matplotlib.collections.PathCollection
                or a tuple of (paths, paths) if marker='football'

        """
        validate_ax(ax)

        x = np.ma.ravel(x)
        y = np.ma.ravel(y)

        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        x, y = self._reverse_if_vertical(x, y)

        if marker is None:
            marker = rcParams['scatter.marker']

        if marker == 'football' and rotation_degrees is not None:
            raise NotImplementedError("rotated football markers are not implemented.")

        if marker == 'football':
            scatter_plot = scatter_football(x, y, ax=ax, **kwargs)
        elif rotation_degrees is not None:
            scatter_plot = scatter_rotation(x, y, rotation_degrees, marker=marker,
                                            vertical=self.vertical, ax=ax, **kwargs)
        else:
            scatter_plot = ax.scatter(x, y, marker=marker, **kwargs)
        return scatter_plot

    def _reflect_2d(self, x, y, standardized=False):
        x = np.ravel(x)
        y = np.ravel(y)
        if standardized:
            x_limits, y_limits = [0, 105], [0, 68]
        else:
            x_limits, y_limits = [self.dim.left, self.dim.right], [self.dim.bottom, self.dim.top]
        reflected_data_x = np.r_[x, 2 * x_limits[0] - x, 2 * x_limits[1] - x, x, x]
        reflected_data_y = np.r_[y, y, y, 2 * y_limits[0] - y, 2 * y_limits[1] - y]
        return reflected_data_x, reflected_data_y

    def kdeplot(self, x, y, ax=None, reflect=True, **kwargs):
        """ Routine to perform kernel density estimation using seaborn kdeplot and plot
         the result on the given ax.
        The method used here includes a simple reflection method for boundary correction,
         so that probability mass is not assigned to areas outside the pitch.
        Automatically flips the x and y coordinates if the pitch is vertical.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        reflect : bool, default True
            Whether to reflect the coordinates for boundary correction
        **kwargs : All other keyword arguments are passed on to seaborn.kdeplot.

        Returns
        -------
        contour : matplotlib.contour.ContourSet
        """
        validate_ax(ax)

        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        weights = kwargs.pop('weights', None)
        bw_method = kwargs.pop('bw_method', 'scott')

        if reflect:
            scip_kde = gaussian_kde(np.vstack([x, y]), bw_method='scott', weights=weights)
            bw_method = scip_kde.scotts_factor() / 4.
            x, y = self._reflect_2d(x, y)

        x, y = self._reverse_if_vertical(x, y)

        contour_plot = sns.kdeplot(x=x, y=y, ax=ax, weights=weights, bw_method=bw_method,
                                   clip=self.kde_clip, **kwargs)
        return contour_plot

    def hexbin(self, x, y, ax=None, **kwargs):
        """ Utility wrapper around matplotlib.axes.Axes.hexbin,
        which automatically flips the x and y coordinates if the pitch is vertical and
         clips to the pitch boundaries.

        Parameters
        ----------
        x, y : array-like or scalar.
            Commonly, these parameters are 1D arrays.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        mincnt : int > 0, default: 1
            If not None, only display cells with more than mincnt number of points in the cell.
        gridsize : int or (int, int), default: (17, 8) for Pitch/ (17, 17) for VerticalPitch
            If a single int, the number of hexagons in the x-direction. The number of hexagons
            in the y-direction is chosen such that the hexagons are approximately regular.
            Alternatively, if a tuple (nx, ny), the number of hexagons in the x-direction
            and the y-direction.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.hexbin.

        Returns
        -------
        polycollection : matplotlib.collections.PolyCollection
        """
        validate_ax(ax)
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        # according to seaborn hexbin isn't nan safe so filter out nan
        mask = np.isnan(x) | np.isnan(y)
        x = x[~mask]
        y = y[~mask]

        x, y = self._reverse_if_vertical(x, y)
        mincnt = kwargs.pop('mincnt', 1)
        gridsize = kwargs.pop('gridsize', self.hexbin_gridsize)
        extent = kwargs.pop('extent', self.hex_extent)
        hexbin = ax.hexbin(x, y, mincnt=mincnt, gridsize=gridsize, extent=extent, **kwargs)
        rect = patches.Rectangle((self.visible_pitch[0], self.visible_pitch[2]),
                                 self.visible_pitch[1] - self.visible_pitch[0],
                                 self.visible_pitch[3] - self.visible_pitch[2],
                                 fill=False)
        ax.add_patch(rect)
        hexbin.set_clip_path(rect)
        return hexbin

    def polygon(self, verts, ax=None, **kwargs):
        """ Plot polygons using a PathCollection.
        See: https://matplotlib.org/3.1.1/api/collections_api.html.
        Valid Collection keyword arguments: edgecolors, facecolors, linewidths, antialiaseds,
        transOffset, norm, cmap
        Automatically flips the x and y vertices if the pitch is vertical.

        Parameters
        ----------
        verts: verts is a sequence of (verts0, verts1, ...)
            where verts_i is a numpy array of shape (number of vertices, 2).
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to
            matplotlib.collections.PatchCollection.

        Returns
        -------
        PathCollection : matplotlib.collections.PatchCollection
        """
        validate_ax(ax)
        verts = np.asarray(verts)
        patch_list = []
        for vert in verts:
            vert = self._reverse_vertices_if_vertical(vert)
            polygon = patches.Polygon(vert, closed=True)
            patch_list.append(polygon)
        p = PatchCollection(patch_list, **kwargs)
        p = ax.add_collection(p)
        return p

    def goal_angle(self, x, y, ax=None, goal='right', **kwargs):
        """ Plot a polygon with the angle to the goal using PathCollection.
        See: https://matplotlib.org/3.1.1/api/collections_api.html.
        Valid Collection keyword arguments: edgecolors, facecolors, linewidths, antialiaseds,
        transOffset, norm, cmap

        Parameters
        ----------
        x, y: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the coordinates on the pitch.
        goal: str default 'right'.
            The goal to plot, either 'left' or 'right'.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to
             matplotlib.collections.PathCollection.

        Returns
        -------
        PathCollection : matplotlib.collections.PathCollection
        """
        validate_ax(ax)
        valid_goal = ['left', 'right']
        if goal not in valid_goal:
            raise TypeError(f'Invalid argument: goal should be in {valid_goal}')
        x = np.ravel(x)
        y = np.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        if goal == 'right':
            goal_coordinates = self.goal_right
        else:
            goal_coordinates = self.goal_left
        verts = np.zeros((x.size, 3, 2))
        verts[:, 0, 0] = x
        verts[:, 0, 1] = y
        verts[:, 1:, :] = np.expand_dims(goal_coordinates, 0)
        p = self.polygon(verts, ax=ax, **kwargs)
        return p

    def annotate(self, text, xy, xytext=None, ax=None, **kwargs):
        """ Utility wrapper around ax.annotate
        which automatically flips the xy and xytext coordinates if the pitch is vertical.

        Annotate the point xy with text.
        See: https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html

        Parameters
        ----------
        text : str
            The text of the annotation.
        xy : (float, float)
            The point (x, y) to annotate.
        xytext : (float, float), optional
            The position (x, y) to place the text at. If None, defaults to xy.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.annotate.

        Returns
        -------
        annotation : matplotlib.text.Annotation
        """
        validate_ax(ax)
        xy = self._reverse_annotate_if_vertical(xy)
        if xytext is not None:
            xytext = self._reverse_annotate_if_vertical(xytext)
        return ax.annotate(text, xy, xytext, **kwargs)

    @docstring.copy(bin_statistic)
    def bin_statistic(self, x, y, values=None, statistic='count', bins=(5, 4), standardized=False):
        stats = bin_statistic(x, y, values=values, dim=self.dim, statistic=statistic,
                              bins=bins, standardized=standardized)
        return stats

    @docstring.copy(heatmap)
    def heatmap(self, stats, ax=None, **kwargs):
        mesh = heatmap(stats, ax=ax, vertical=self.vertical, **kwargs)
        return mesh

    @docstring.copy(bin_statistic_positional)
    def bin_statistic_positional(self, x, y, values=None, positional='full', statistic='count'):
        stats = bin_statistic_positional(x, y, values=values,
                                         dim=self.dim, positional=positional, statistic=statistic)
        return stats

    @docstring.copy(heatmap_positional)
    def heatmap_positional(self, stats, ax=None, **kwargs):
        mesh = heatmap_positional(stats, ax=ax, vertical=self.vertical, **kwargs)
        return mesh

    def label_heatmap(self, stats, ax=None, **kwargs):
        """ Labels the heatmaps and automatically flips the coordinates if the pitch is vertical.

        Parameters
        ----------
        stats : A dictionary or list of dictionaries.
            This should be calculated via bin_statistic_positional() or bin_statistic().
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.annotate.

        Returns
        ----------
        annotations : A list of matplotlib.text.Annotation.
        """
        validate_ax(ax)

        if not isinstance(stats, list):
            stats = [stats]

        annotation_list = []
        for bs in stats:
            # remove labels outside the plot extents
            mask_x_outside1 = bs['cx'] < self.dim.pitch_extent[0]
            mask_x_outside2 = bs['cx'] > self.dim.pitch_extent[1]
            mask_y_outside1 = bs['cy'] < self.dim.pitch_extent[2]
            mask_y_outside2 = bs['cy'] > self.dim.pitch_extent[3]
            mask_clip = mask_x_outside1 | mask_x_outside2 | mask_y_outside1 | mask_y_outside2
            mask_clip = np.ravel(mask_clip)

            text = np.ravel(bs['statistic'])[~mask_clip]
            cx = np.ravel(bs['cx'])[~mask_clip]
            cy = np.ravel(bs['cy'])[~mask_clip]
            for i in range(len(text)):
                annotation = self.annotate(text[i], (cx[i], cy[i]), ax=ax, **kwargs)
                annotation_list.append(annotation)

        return annotation_list

    @docstring.copy(arrows)
    def arrows(self, xstart, ystart, xend, yend, *args, ax=None, **kwargs):
        validate_ax(ax)
        q = arrows(xstart, ystart, xend, yend, *args, ax=ax, vertical=self.vertical, **kwargs)
        return q

    @docstring.copy(lines)
    def lines(self, xstart, ystart, xend, yend, color=None, n_segments=100,
              comet=False, transparent=False, alpha_start=0.01,
              alpha_end=1, cmap=None, ax=None, **kwargs):
        validate_ax(ax)
        lc = lines(xstart, ystart, xend, yend, color=color, n_segments=n_segments, comet=comet,
                   transparent=transparent, alpha_start=alpha_start, alpha_end=alpha_end,
                   cmap=cmap, ax=ax, vertical=self.vertical, reverse_cmap=self.reverse_cmap,
                   **kwargs)
        return lc

    def voronoi(self, x, y, teams):
        """ Get Voronoi vertices for a set of coordinates.
        Uses a trick by Dan Nichol (@D4N__ on Twitter) where points are reflected in the pitch lines
        before calculating the Voronoi. This means that the Voronoi extends to
        the edges of the pitch. See:
        https://github.com/ProformAnalytics/tutorial_nbs/blob/master/notebooks/Voronoi%20Reflection%20Trick.ipynb

        Players outside of the pitch dimensions are assumed to be standing on the pitch edge.
        This means that their coordinates are clipped to the pitch edges
        before calculating the Voronoi.

        Parameters
        ----------
        x, y: array-like or scalar.
            Commonly, these parameters are 1D arrays. These should be the coordinates on the pitch.

        teams: array-like or scalar.
            This splits the results into the Voronoi vertices for each team.
            This can either have integer (1/0) values or boolean (True/False) values.
            team1 is where team==1 or team==True
            team2 is where team==0 or team==False

        Returns
        -------
        team1 : a 1d numpy array (length number of players in team 1) of 2d arrays
            Where the individual 2d arrays are coordinates of the Voronoi vertices.

        team2 : a 1d numpy array (length number of players in team 2) of 2d arrays
            Where the individual 2d arrays are coordinates of the Voronoi vertices.
        """
        x = np.ravel(x)
        y = np.ravel(y)
        teams = np.ravel(teams)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")
        if teams.size != x.size:
            raise ValueError("x and team must be the same size")

        if self.dim.aspect != 1:
            standardized = True
            x, y = self.standardizer.transform(x, y)
            extent = np.array([0, 105, 0, 68])
        else:
            standardized = False
            extent = self.dim.pitch_extent

        # clip outside to pitch extents
        x = x.clip(min=extent[0], max=extent[1])
        y = y.clip(min=extent[2], max=extent[3])

        # reflect in pitch lines
        reflect_x, reflect_y = self._reflect_2d(x, y, standardized=standardized)
        reflect = np.vstack([reflect_x, reflect_y]).T

        # create Voronoi
        vor = Voronoi(reflect)

        # get region vertices
        regions = vor.point_region[:x.size]
        regions = np.array(vor.regions, dtype='object')[regions]
        region_vertices = []
        for region in regions:
            verts = vor.vertices[region]
            verts[:, 0] = np.clip(verts[:, 0], a_min=extent[0], a_max=extent[1])
            verts[:, 1] = np.clip(verts[:, 1], a_min=extent[2], a_max=extent[3])
            # convert back to coordinates if previously standardized
            if standardized:
                x_std, y_std = self.standardizer.transform(verts[:, 0], verts[:, 1], reverse=True)
                verts[:, 0] = x_std
                verts[:, 1] = y_std
            region_vertices.append(verts)
        region_vertices = np.array(region_vertices, dtype='object')

        # seperate team1/ team2 vertices
        team1 = region_vertices[teams == 1]
        team2 = region_vertices[teams == 0]

        return team1, team2

    def calculate_angle_and_distance(self, xstart, ystart, xend, yend, standardized=False):
        """ Calculates the angle in radians counter-clockwise between a start and end
        location and the distance. Where the angle 0 is this way →
        (the straight line from left to right) in a horizontally orientated pitch
        and this way ↑ in a vertically orientated pitch.
        The angle goes from 0 to 2pi. To convert the angle to degrees use np.degrees(angle).

        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays.
            These should be the start and end coordinates to calculate the angle between.
        standardized : bool, default False
            Whether the x, y values have been standardized to the 'uefa'
            pitch coordinates (105m x 68m)

        Returns
        -------
        angle: ndarray
            Array of angles in radians counter-clockwise in the range [0, 2pi].
            Where 0 is the straight line left to right in a horizontally orientated pitch
            and the straight line bottom to top in a vertically orientated pitch.
        distance: ndarray
            Array of distances.
        """
        xstart = np.ravel(xstart)
        ystart = np.ravel(ystart)
        xend = np.ravel(xend)
        yend = np.ravel(yend)

        if xstart.size != ystart.size:
            raise ValueError("xstart and ystart must be the same size")
        if xstart.size != xend.size:
            raise ValueError("xstart and xend must be the same size")
        if ystart.size != yend.size:
            raise ValueError("ystart and yend must be the same size")

        x_dist = xend - xstart
        if self.dim.invert_y and standardized is False:
            y_dist = ystart - yend
        else:
            y_dist = yend - ystart

        angle = np.arctan2(y_dist, x_dist)
        # if negative angle make positive angle, so goes from 0 to 2 * pi
        angle[angle < 0] = 2 * np.pi + angle[angle < 0]

        distance = (x_dist ** 2 + y_dist ** 2) ** 0.5

        return angle, distance

    def flow(self, xstart, ystart, xend, yend, bins=(5, 4), arrow_type='same', arrow_length=5,
             color=None, ax=None, **kwargs):
        """ Create a flow map by binning  the data into cells and calculating the average
        angles and distances. The colors of each arrow are

        Parameters
        ----------
        xstart, ystart, xend, yend: array-like or scalar.
            Commonly, these parameters are 1D arrays.
            These should be the start and end coordinates to calculate the angle between.
        bins : int or [int, int] or array_like or [array, array], optional
            The bin specification for binning the data to calculate the angles/ distances.
              * the number of bins for the two dimensions (nx = ny = bins),
              * the number of bins in each dimension (nx, ny = bins),
              * the bin edges for the two dimensions (x_edge = y_edge = bins),
              * the bin edges in each dimension (x_edge, y_edge = bins).
                If the bin edges are specified, the number of bins will be,
                (nx = len(x_edge)-1, ny = len(y_edge)-1).
        arrow_type : str, default 'same'
            The supported arrow types are: 'same', 'scale', and 'average'.
            'same' makes the arrows the same size (arrow_length).
            'scale' scales the arrow length by the average distance
                in the cell (up to a max of arrow_length).
            'average' makes the arrow size the average distance in the cell.
        arrow_length : float, default 5
            The arrow_length for the flow map. If the arrow_type='same',
            all the arrows will be arrow_length. If the arrow_type='scale',
            the arrows will be scaled by the average distance.
            If the arrow_type='average', the arrows_length is ignored
            This is automatically multipled by 100 if using a 'tracab' pitch
            (i.e. the default is 500).
        color : A matplotlib color, defaults to None.
            Defaults to None. In that case the marker color is
            determined by the cmap (default 'viridis').
            and the counts of the starting positions in each bin.
        ax : matplotlib.axes.Axes, default None
            The axis to plot on.
        **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.quiver.

        Returns
        -------
        PolyCollection : matplotlib.quiver.Quiver
        """
        validate_ax(ax)
        if self.dim.aspect != 1:
            standardized = True
            xstart, ystart = self.standardizer.transform(xstart, ystart)
            xend, yend = self.standardizer.transform(xend, yend)
        else:
            standardized = False

        # calculate  the binned statistics
        angle, distance = self.calculate_angle_and_distance(xstart, ystart, xend, yend,
                                                            standardized=standardized)
        bs_distance = self.bin_statistic(xstart, ystart, values=distance,
                                         statistic='mean', bins=bins, standardized=standardized)
        bs_angle = self.bin_statistic(xstart, ystart, values=angle,
                                      statistic=circmean, bins=bins, standardized=standardized)

        # calculate the arrow length
        if self.pitch_type == 'tracab':
            arrow_length = arrow_length * 100
        if arrow_type == 'scale':
            new_d = (bs_distance['statistic'] * arrow_length /
                     np.nan_to_num(bs_distance['statistic']).max(initial=None))
        elif arrow_type == 'same':
            new_d = arrow_length
        elif arrow_type == 'average':
            new_d = bs_distance['statistic']
        else:
            valid_arrows = ['scale', 'same', 'average']
            raise TypeError(f'Invalid argument: arrow_type should be in {valid_arrows}')

        # calculate the end positions of the arrows
        endx = bs_angle['cx'] + (np.cos(bs_angle['statistic']) * new_d)
        if self.dim.invert_y and standardized is False:
            endy = bs_angle['cy'] - (np.sin(bs_angle['statistic']) * new_d)  # invert_y
        else:
            endy = bs_angle['cy'] + (np.sin(bs_angle['statistic']) * new_d)

        # get coordinates and convert back to the pitch coordinates if necessary
        cx, cy = bs_angle['cx'], bs_angle['cy']
        if standardized:
            cx, cy = self.standardizer.transform(cx, cy, reverse=True)
            endx, endy = self.standardizer.transform(endx, endy, reverse=True)

        # plot arrows
        if color is None:
            bs_count = self.bin_statistic(xstart, ystart, statistic='count',
                                          bins=bins, standardized=standardized)
            flow = self.arrows(cx, cy, endx, endy, bs_count['statistic'], ax=ax, **kwargs)
        else:
            flow = self.arrows(cx, cy, endx, endy, color=color, ax=ax, **kwargs)

        return flow

    def jointgrid(self, pitch_height=0.5, marginal_height=0.1, space_height=0,
                  left=0.1, bottom=0.1, ax_left=True, ax_top=True, ax_right=True, ax_bottom=False):
        """ Create a grid with a pitch at the center and axes on the
         top and right handside of the pitch.

        Parameters
        ----------
        pitch_height : float, default 0.5
            The height of the pitch in fractions of the figure height.
            The default is 50% of the figure.
        marginal_height : float, default 0.1
            The height of the marginal axes (either side of the pitch) in fractions
             of the figure height.
            The default is 10% of the figure.
        space_height : float, default 0
            The space between the pitch and the other axes in fractions of the figure height.
            The default is no space (note it will still look like there is space
            if the pitch has padding).
        left : float, default 0.1
            The location of the left hand side of the pitch in fractions of the figure width.
            The default means that the pitch is located 10% in from the left of the figure.
        bottom : float, default 0.1
            The location of the bottom side of the pitch in fractions of the figure height.
            The default means that the pitch is located 10% in from the bottom of the figure.
        ax_left, ax_top, ax_right : bool, default True
            Whether to include a Matplotlib Axes on the left/top/right side of the pitch.
        ax_bottom : bool, default False
            Whether to include a Matplotlib Axes on the bottom side of the pitch.
        Returns
        -------
        fig : matplotlib.figure.Figure
        ax : a 1d numpy array (length 5) of matplotlib.axes.Axes
            format = array([pitch, marginal axes in order left, top, right, bottom])
            if marginal axes is not present then axes replaced by None
        """
        if bottom + pitch_height + ((space_height + marginal_height) * ax_top) > 1.:
            error_msg = ('The jointplot axes extends past the figure height. '
                         'Reduce one of the pitch_height, space_height, marginal_height, '
                         'or bottom so the total is ≤ 1')
            raise ValueError(error_msg)
            
        if bottom - ((space_height + marginal_height) * ax_bottom) < 0.:
            error_msg = ('The jointplot axes extends past the figure bottom border. '
                         'Increase the bottom argument so it is more than the space_height + marginal_height.')
            raise ValueError(error_msg)
            
        fig_aspect = self.figsize[0] / self.figsize[1]
        pitch_width = pitch_height * self.ax_aspect / fig_aspect
        marginal_width = marginal_height / fig_aspect
        space_width = space_height / fig_aspect
        if left + pitch_width + ((space_width + marginal_width) * ax_right) > 1.:
            error_msg = ('The jointplot axes extends past the figure width. '
                         'Reduce one of the pitch_height, space_height, marginal_height, '
                         'or left.')
            raise ValueError(error_msg)
            
        if left - ((space_width + marginal_width) * ax_left) < 0.:
            error_msg = ('The jointplot axes extends past the figure left border. '
                         'Increase the left argument so there is space for the left marginal axis.')
            raise ValueError(error_msg)
            

        left_pad = (np.abs(self.visible_pitch - self.extent)[0] /
                    np.abs(self.extent[1] - self.extent[0]))
        right_pad = (np.abs(self.visible_pitch - self.extent)[1] /
                     np.abs(self.extent[1] - self.extent[0]))
        bottom_pad = (np.abs(self.visible_pitch - self.extent)[2] /
                      np.abs(self.extent[3] - self.extent[2]))
        top_pad = (np.abs(self.visible_pitch - self.extent)[3] /
                   np.abs(self.extent[3] - self.extent[2]))
        
        # add axes and draw pitch
        fig = plt.figure(figsize=self.figsize)
        
        # set axes limits
        x0, x1, y0, y1 = self.visible_pitch
        
        axes = []
        
        if ax_left:
            ax_0 = fig.add_axes((left - space_width - marginal_width,
                                 bottom + (bottom_pad * pitch_height),
                                 marginal_width,
                                 pitch_height - (bottom_pad + top_pad) * pitch_height))
            ax_0.set_ylim(y0, y1)
            ax_0.invert_xaxis()
            for spine in ['left', 'bottom', 'top']:
                ax_0.spines[spine].set_visible(False)
            axes.append(ax_0)
        else:
            axes.append(None)
            
        if ax_top:
            ax_1 = fig.add_axes((left + (left_pad * pitch_width),
                                 bottom + pitch_height + space_height,
                                 pitch_width - (left_pad + right_pad) * pitch_width,
                                 marginal_height))
            for spine in ['left', 'right', 'top']:
                ax_1.spines[spine].set_visible(False)
            ax_1.set_xlim(x0, x1)
            axes.append(ax_1)
        else:
            axes.append(None)
        
        if ax_right:
            ax_2 = fig.add_axes((left + pitch_width + space_width,
                                 bottom + (bottom_pad * pitch_height),
                                 marginal_width,
                                 pitch_height - (bottom_pad + top_pad) * pitch_height))
            ax_2.set_ylim(y0, y1)
            for spine in ['right', 'bottom', 'top']:
                ax_2.spines[spine].set_visible(False)
            axes.append(ax_2)
        else:
            axes.append(None)
            
        if ax_bottom:
            ax_3 = fig.add_axes((left + (left_pad * pitch_width),
                                 bottom - space_height - marginal_height,
                                 pitch_width - (left_pad + right_pad) * pitch_width,
                                 marginal_height))
            for spine in ['left', 'right', 'bottom']:
                ax_3.spines[spine].set_visible(False)
            ax_3.set_xlim(x0, x1)
            ax_3.invert_yaxis()
            axes.append(ax_3)
        else:
            axes.append(None)
                
        ax_pitch = fig.add_axes((left, bottom, pitch_width, pitch_height))
        self.draw(ax=ax_pitch)
        axes.insert(0, ax_pitch)
       
        for ax in axes[1:]:
            if ax is not None:
                plt.setp(ax.get_xticklabels(), visible=False)
                plt.setp(ax.get_yticklabels(), visible=False)
                ax.set_xticks([])
                ax.set_yticks([])
        
        axes = np.array(axes)

        return fig, axes

    # The methods below for drawing/ setting attributes for some of the pitch elements
    # are defined in pitch.py (Pitch/ VerticalPitch classes)
    # as they differ for horizontal/ vertical pitches
    def _scale_pad(self):
        pass

    def _set_extent(self):
        pass

    def _draw_rectangle(self, ax, x, y, width, height, **kwargs):
        pass

    def _draw_line(self, ax, x, y, **kwargs):
        pass

    def _draw_ellipse(self, ax, x, y, width, height, **kwargs):
        pass

    def _draw_arc(self, ax, x, y, width, height, theta1, theta2, **kwargs):
        pass

    def _draw_stripe(self, ax, i):
        pass

    def _draw_stripe_grass(self, pitch_color):
        pass

    @staticmethod
    def _reverse_if_vertical(x, y):
        pass

    @staticmethod
    def _reverse_vertices_if_vertical(vert):
        pass

    @staticmethod
    def _reverse_annotate_if_vertical(annotate):
        pass
