"""`mplsoccer.scatterutils` is a python module containing Matplotlib
markers and a function to rotate markers."""

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import inspect

import matplotlib.markers as mmarkers
import matplotlib.path as mpath
import numpy as np
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerPathCollection

__all__ = ['scatter_football', 'scatter_rotation', 'arrowhead_marker',
           'football_shirt_marker', 'football_left_boot_marker',
          'football_right_boot_marker']


# Note that the football-marker arrays are based on the
# in my other repo, but the arrays are copied here
# https://github.com/andrewRowlinson/data-science/blob/master/data_visualization/matplotlib_football_marker.ipynb

# football hexagon arrays
football_hexagon_codes = np.array([1, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 79, 1, 3,
                                   3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 79, 1, 3, 3, 3,
                                   3, 4, 4, 4, 3, 3, 2, 3, 3, 79, 1, 2, 3, 3, 4, 4, 4,
                                   3, 3, 3, 3, 3, 3, 79, 1, 3, 3, 3, 3, 4, 4, 4, 3, 3,
                                   3, 3, 3, 3, 79, 1, 1, 1, 1])
football_hexagon_vertices = np.array([[-0.22499999999999998, -0.3096859321060139],
                                      [-0.3578624191511828, -0.42126390612162967],
                                      [-0.4307248383023656, -0.5928418801372455],
                                      [-0.29662436542138726, -0.7538845585184165],
                                      [-0.22252389254040889, -0.9749272368995876],
                                      [-0.07605800448461039, -1.0083575877001376],
                                      [0.07605800448461039, -1.0083575877001376],
                                      [0.22252389254040889, -0.9749272368995876],
                                      [0.29662436542138726, -0.7538845585184165],
                                      [0.43072483830236563, -0.5928418801372455],
                                      [0.3578624191511828, -0.4212639061216298],
                                      [0.22499999999999987, -0.30968593210601403],
                                      [-0.00000000000000005551115123125783, -0.33968593210601394],
                                      [-0.22499999999999998, -0.3096859321060139],
                                      [-0.22499999999999998, -0.3096859321060139],
                                      [0.22499999999999984, -0.309685932106014],
                                      [0.35786241915118266, -0.42126390612162967],
                                      [0.4307248383023654, -0.5928418801372455],
                                      [0.6745860377099481, -0.5228718813250733],
                                      [0.8584472371175307, -0.5129018825129013],
                                      [0.9355018385938869, -0.38393509178776364],
                                      [0.982508270481868, -0.2392641702247741],
                                      [0.9959745660164324, -0.0896362864490644],
                                      [0.8164509970942311, 0.038404580904486146],
                                      [0.6969274281720299, 0.2264454482580367],
                                      [0.5004925378203781, 0.1423674742424208],
                                      [0.36405764746872626, 0.11828950022680491],
                                      [0.3245288237343631, -0.06569821593960454],
                                      [0.22499999999999984, -0.309685932106014],
                                      [0.22499999999999984, -0.309685932106014],
                                      [0.36405764746872626, 0.11828950022680493],
                                      [0.5004925378203782, 0.14236747424242066],
                                      [0.69692742817203, 0.22644544825803642],
                                      [0.6950004453997567, 0.47219094443542353],
                                      [0.7530734626274834, 0.6579364406128105],
                                      [0.654229937273651, 0.77107265150149],
                                      [0.531165500901059, 0.8604841982111864],
                                      [0.3930222411881726, 0.919528965248744],
                                      [0.22651112059408626, 0.7961609145035808],
                                      [-0.00000000000000005551115123125783, 0.7327928637584178],
                                      [0.00000000000000013877787807814457, 0.3827928637584179],
                                      [0.2120288237343632, 0.28054118199261147],
                                      [0.36405764746872626, 0.11828950022680493],
                                      [0.36405764746872626, 0.11828950022680493],
                                      [0.00000000000000013877787807814457, 0.38279286375841787],
                                      [0.00000000000000016653345369377348, 0.7327928637584178],
                                      [-0.226511120594086, 0.796160914503581],
                                      [-0.3930222411881722, 0.9195289652487442],
                                      [-0.5311655009010592, 0.8604841982111865],
                                      [-0.6542299372736504, 0.771072651501486],
                                      [-0.7530734626274826, 0.6579364406128061],
                                      [-0.6950004453997563, 0.41219094443542137],
                                      [-0.69692742817203, 0.22644544825803659],
                                      [-0.5604925378203782, 0.14236747424242088],
                                      [-0.36405764746872626, 0.1182895002268052],
                                      [-0.21202882373436308, 0.28054118199261147],
                                      [0.00000000000000013877787807814457, 0.38279286375841787],
                                      [0.00000000000000013877787807814457, 0.38279286375841787],
                                      [-0.36405764746872615, 0.11828950022680515],
                                      [-0.560492537820378, 0.142367474242421],
                                      [-0.6969274281720299, 0.2264454482580368],
                                      [-0.8164509970942311, 0.03840458090448631],
                                      [-0.9959745660164324, -0.08963628644906418],
                                      [-0.9825082704818681, -0.23926417022477386],
                                      [-0.9355018385938869, -0.38393509178776364],
                                      [-0.8584472371175307, -0.5129018825129013],
                                      [-0.6145860377099481, -0.5228718813250733],
                                      [-0.43072483830236563, -0.5928418801372455],
                                      [-0.3578624191511829, -0.42126390612162967],
                                      [-0.2250000000000001, -0.30968593210601386],
                                      [-0.3245288237343631, -0.12569821593960442],
                                      [-0.36405764746872615, 0.11828950022680515],
                                      [-0.36405764746872615, 0.11828950022680515],
                                      [-1.0204451903760434, -1.0083575877001376],
                                      [-1.0204451903760434, 1.0268236782504188],
                                      [1.0204451903760436, -1.0083575877001376],
                                      [1.0204451903760436, 1.0268236782504188]])

# football pentagon arrays
football_pentagon_codes = np.array([1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 79, 1, 3, 3, 4, 4,
                                    4, 3, 3, 79, 1, 3, 3, 4, 4, 4, 3, 3, 79, 1, 3, 3, 4,
                                    4, 4, 3, 3, 79, 1, 3, 3, 4, 4, 4, 3, 3, 79, 1, 3, 3,
                                    4, 4, 4, 3, 3, 79, 1, 1, 1, 1])
football_pentagon_vertices = np.array([[0.000000000000000023439302766909766, 0.38279286375841787],
                                       [-0.21202882373436308, 0.28054118199261147],
                                       [-0.3640576474687262, 0.11828950022680507],
                                       [-0.3245288237343631, -0.12569821593960442],
                                       [-0.22499999999999998, -0.3096859321060139],
                                       [-0.00000000000000005551115123125783, -0.33968593210601394],
                                       [0.22499999999999987, -0.30968593210601403],
                                       [0.3245288237343631, -0.06569821593960454],
                                       [0.36405764746872626, 0.11828950022680493],
                                       [0.2120288237343632, 0.28054118199261147],
                                       [0.00000000000000011719651383454883, 0.38279286375841787],
                                       [0.00000000000000011719651383454883, 0.38279286375841787],
                                       [0.43072483830236563, -0.5928418801372455],
                                       [0.29662436542138726, -0.7538845585184165],
                                       [0.22252389254040889, -0.9749272368995876],
                                       [0.48867813807221294, -0.9141784174079514],
                                       [0.7184254914884021, -0.7472571944544121],
                                       [0.8584472371175307, -0.5129018825129013],
                                       [0.6745860377099481, -0.5228718813250733],
                                       [0.43072483830236563, -0.5928418801372455],
                                       [0.43072483830236563, -0.5928418801372455],
                                       [0.6969274281720299, 0.2264454482580367],
                                       [0.8164509970942311, 0.038404580904486146],
                                       [0.9959745660164324, -0.0896362864490644],
                                       [1.0204451903760436, 0.18226386071471035],
                                       [0.9326895101963948, 0.4523480728972359],
                                       [0.7530734626274834, 0.6579364406128105],
                                       [0.6950004453997567, 0.47219094443542353],
                                       [0.6969274281720299, 0.2264454482580367],
                                       [0.6969274281720299, 0.2264454482580367],
                                       [-0.00000000000000005551115123125783, 0.7327928637584178],
                                       [0.22651112059408626, 0.7961609145035808],
                                       [0.3930222411881726, 0.919528965248744],
                                       [0.1419916732365391, 1.0268236782504185],
                                       [-0.14199167323653866, 1.0268236782504188],
                                       [-0.3930222411881722, 0.9195289652487442],
                                       [-0.226511120594086, 0.796160914503581],
                                       [-0.00000000000000005551115123125783, 0.7327928637584178],
                                       [-0.00000000000000005551115123125783, 0.7327928637584178],
                                       [-0.69692742817203, 0.22644544825803659],
                                       [-0.6950004453997563, 0.41219094443542137],
                                       [-0.7530734626274826, 0.6579364406128061],
                                       [-0.9326895101963917, 0.452348072897233],
                                       [-1.0204451903760434, 0.18226386071470885],
                                       [-0.9959745660164324, -0.08963628644906418],
                                       [-0.8164509970942311, 0.03840458090448631],
                                       [-0.69692742817203, 0.22644544825803659],
                                       [-0.69692742817203, 0.22644544825803659],
                                       [-0.43072483830236563, -0.5928418801372455],
                                       [-0.6145860377099481, -0.5228718813250733],
                                       [-0.8584472371175307, -0.5129018825129013],
                                       [-0.7184254914884021, -0.7472571944544121],
                                       [-0.48867813807221294, -0.9141784174079514],
                                       [-0.22252389254040889, -0.9749272368995876],
                                       [-0.29662436542138726, -0.7538845585184165],
                                       [-0.43072483830236563, -0.5928418801372455],
                                       [-0.43072483830236563, -0.5928418801372455],
                                       [-1.0204451903760434, -1.0083575877001376],
                                       [-1.0204451903760434, 1.0268236782504188],
                                       [1.0204451903760436, -1.0083575877001376],
                                       [1.0204451903760436, 1.0268236782504188]])

football_hexagon_marker = mpath.Path(football_hexagon_vertices, football_hexagon_codes)
football_pentagon_marker = mpath.Path(football_pentagon_vertices, football_pentagon_codes)

arrowhead_marker = mpath.Path(np.array([[0., 1.], [-1., -1.], [0., -0.4], [1., -1.], [0., 1.]]),
                              np.array([1, 2, 2, 2, 79], dtype=np.uint8))

football_boot_vertices = np.array([[11.9551887, 1.64724906],
                                   [13.0388887, 4.29835906],
                                   [12.4334887, 4.52243906],
                                   [11.8301887, 4.75621906],
                                   [11.2365887, 4.99914906],
                                   [10.8450887, 5.15932906],
                                   [10.4393887, 5.33267906],
                                   [10.0229887, 5.51681906],
                                   [8.8023887, 2.53105906],
                                   [8.5577887, 1.93254906],
                                   [7.8635887, 1.64142906],
                                   [7.2518887, 1.88083906],
                                   [6.6401887, 2.12024906],
                                   [6.3426887, 2.79950906],
                                   [6.5873887, 3.39801906],
                                   [7.8630887, 6.51862906],
                                   [6.8373887, 7.01355906],
                                   [5.7852887, 7.54510906],
                                   [4.7501887, 8.08365906],
                                   [3.4345887, 4.86542906],
                                   [3.1899887, 4.26690906],
                                   [2.4957887, 3.97579906],
                                   [1.8840887, 4.21520906],
                                   [1.2723887, 4.45460906],
                                   [0.9748887, 5.13387906],
                                   [1.2195887, 5.73238906],
                                   [2.6382887, 9.20296906],
                                   [1.2238887, 9.96542906],
                                   [-0.0946113, 10.70036306],
                                   [-1.1909113, 11.32159006],
                                   [-2.6552113, 12.15141106],
                                   [-4.5038113, 11.27153206],
                                   [-5.1810113, 9.75406906],
                                   [-6.3274113, 7.18525906],
                                   [-8.0250113, 3.39801906],
                                   [-14.7263113, 2.86714906],
                                   [-18.5412113, 2.56492906],
                                   [-24.3930513, 5.45474906],
                                   [-26.2132213, 7.90301906],
                                   [-26.6775713, 8.52759906],
                                   [-27.5250613, 9.22750906],
                                   [-28.3099713, 9.14591906],
                                   [-30.1683813, 8.95273906],
                                   [-31.5836513, 8.65034906],
                                   [-32.4782793, 6.89956906],
                                   [-32.6844363, 4.97499906],
                                   [-32.7074253, 4.76042906],
                                   [-32.7508903, 4.47421906],
                                   [-32.8032913, 4.12915906],
                                   [-33.0248933, 2.66983906],
                                   [-33.4063123, 0.15795906],
                                   [-33.0747013, -2.43784094],
                                   [-32.2546573, -8.85744094],
                                   [-28.6015313, -9.44094094],
                                   [-28.6015313, -9.44094094],
                                   [-26.2904113, -9.44094094],
                                   [-25.4206313, -12.35894094],
                                   [-23.4325513, -12.35894094],
                                   [-22.5628113, -9.44094094],
                                   [-19.1333113, -9.44094094],
                                   [-18.2635113, -12.35894094],
                                   [-16.2755113, -12.35894094],
                                   [-15.4057113, -9.44094094],
                                   [3.5306887, -9.44094094],
                                   [4.4004887, -12.35894094],
                                   [6.3885887, -12.35894094],
                                   [7.2583887, -9.44094094],
                                   [10.6877887, -9.44094094],
                                   [11.5575887, -12.35894094],
                                   [13.5455887, -12.35894094],
                                   [14.4153887, -9.44094094],
                                   [17.8447887, -9.44094094],
                                   [18.7145887, -12.35894094],
                                   [20.7026887, -12.35894094],
                                   [21.5724887, -9.44094094],
                                   [22.8670887, -9.44094094],
                                   [24.4402887, -9.44094094],
                                   [26.0146887, -9.16924094],
                                   [27.4328887, -8.50314094],
                                   [30.0262887, -7.28504094],
                                   [30.8977887, -6.26694094],
                                   [30.7858887, -3.78044094],
                                   [30.5856887, -1.62544094],
                                   [28.6549887, -0.10354094],
                                   [24.3231887, 1.00225906],
                                   [24.3231887, 1.00225906],
                                   [20.0385887, 1.92940906],
                                   [15.2862887, 3.51041906],
                                   [14.1701887, 0.78025906],
                                   [13.9255887, 0.18175906],
                                   [13.2313887, -0.10934094],
                                   [12.6196887, 0.13005906],
                                   [12.0079887, 0.36945906],
                                   [11.7104887, 1.04875906],
                                   [11.9551887, 1.64724906],
                                   [11.9551887, 1.64724906]])
football_left_boot_vertices = np.array(football_boot_vertices, copy=True)
football_left_boot_vertices[:, 0] = -football_left_boot_vertices[:, 0]
football_boot_codes = np.array([1, 2, 4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 4, 4, 4, 2, 4,
                                4, 4, 2, 4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 4, 4, 4, 4,
                                4, 4, 4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 4, 4, 4, 4, 4,
                                4, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                                2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4,
                                4, 4, 4, 2, 4, 4, 4, 4, 4, 4, 79], dtype=np.uint8)
football_left_boot_marker = mpath.Path(football_left_boot_vertices, football_boot_codes)
football_right_boot_marker = mpath.Path(football_boot_vertices, football_boot_codes)

football_shirt_vertices = np.array([[-8.64393778, 14.7593703],
                                    [-8.77813778, 15.2513343],
                                    [-9.21703778, 15.6196988],
                                    [-9.72483778, 15.57899907],
                                    [-15.15703778, 15.1436583],
                                    [-20.29153778, 12.9982823],
                                    [-24.25958778, 9.4671423],
                                    [-29.17980778, 5.0886723],
                                    [-22.91111778, -5.1666277],
                                    [-17.34803778, -1.7286277],
                                    [-16.52063778, -1.2173277],
                                    [-15.40623778, -1.6929277],
                                    [-15.29353778, -2.6104277],
                                    [-14.93573778, -5.5230277],
                                    [-14.26743778, -11.1554277],
                                    [-13.78753778, -16.3456277],
                                    [-13.10193778, -23.7606277],
                                    [-14.37273778, -36.4179277],
                                    [-14.37273778, -36.4179277],
                                    [15.17886222, -36.4179277],
                                    [15.17886222, -36.4179277],
                                    [13.90806222, -23.7606277],
                                    [14.59366222, -16.3456277],
                                    [15.07356222, -11.1554277],
                                    [15.74186222, -5.5230277],
                                    [16.09966222, -2.6104277],
                                    [16.21236222, -1.6929277],
                                    [17.32676222, -1.2173277],
                                    [18.15416222, -1.7286277],
                                    [23.83906222, -5.2418277],
                                    [29.82026222, 5.2360723],
                                    [25.06576222, 9.4671423],
                                    [21.09766222, 12.9982823],
                                    [15.96316222, 15.1436583],
                                    [10.53096222, 15.57899916],
                                    [10.02316222, 15.6196988],
                                    [9.58426222, 15.2513353],
                                    [9.45006222, 14.7593713],
                                    [8.42436222, 11.0015323],
                                    [4.76276222, 8.2215623],
                                    [0.40306222, 8.2215623],
                                    [-3.95663778, 8.2215623],
                                    [-7.61823778, 11.0015323],
                                    [-8.64393778, 14.7593703],
                                    [-8.64393778, 14.7593703]])
football_shirt_codes = np.array([1, 4, 4, 4, 4, 4, 4, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4,
                                 4, 4, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 2, 2, 4, 4,
                                 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 79], dtype=np.uint8)
football_shirt_marker = mpath.Path(football_shirt_vertices, football_shirt_codes)


def _mscatter(x, y, markers=None, ax=None, **kwargs):
    """ Helper function to allow rotation of scatter points."""
    # based on:
    # https://stackoverflow.com/questions/52303660/iterating-markers-in-plots/52303895#52303895
    scatter_plot = ax.scatter(x, y, **kwargs)
    if markers is not None:
        paths = []
        for marker in markers:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(marker_obj.get_transform())
            paths.append(path)
        scatter_plot.set_paths(paths)
    return scatter_plot


def scatter_rotation(x, y, rotation_degrees, marker=None, ax=None, vertical=False, **kwargs):
    """ Scatter plot with points rotated by rotation_degrees clockwise.

    Parameters
    ----------
    x, y : array-like or scalar.
        Commonly, these parameters are 1D arrays.
    rotation_degrees: array-like or scalar, default None.
        Rotates the marker in degrees, clockwise. 0 degrees is facing the direction of play.
        In a horizontal pitch, 0 degrees is this way →
    marker: MarkerStyle, optional
        The marker style. marker can be either an instance of the class or the
        text shorthand for a particular marker. Defaults to None, in which case it takes
        the value of rcParams["scatter.marker"] (default: 'o') = 'o'.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    vertical : bool, default False
        Rotates the markers correctly for the orientation. If using a vertical setup
        where the x and y-axis are flipped set vertical=True.
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.

    Returns
    -------
    paths : matplotlib.collections.PathCollection
    """
    rotation_degrees = np.ma.ravel(rotation_degrees)
    if x.size != rotation_degrees.size:
        raise ValueError("x and rotation_degrees must be the same size")
    # rotated counterclockwise - this makes it clockwise with zero facing the direction of play
    rotation_degrees = - rotation_degrees
    # if horizontal rotate by 90 degrees so 0 degrees is this way →
    if vertical is False:
        rotation_degrees = rotation_degrees - 90
    markers = []
    for degrees in rotation_degrees:
        marker_style = mmarkers.MarkerStyle(marker=marker)
        marker_style._transform = marker_style.get_transform().rotate_deg(degrees)
        markers.append(marker_style)

    return _mscatter(x, y, markers=markers, ax=ax, **kwargs)


def scatter_football(x, y, ax=None, **kwargs):
    """ Scatter plot of football markers.
    Plots two scatter plots one for the hexagons and one for the pentagons of the football.

    Parameters
    ----------
    x, y : array-like or scalar.
        Commonly, these parameters are 1D arrays.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.scatter.

    Returns
    -------
    (paths, paths) : a tuple of matplotlib.collections.PathCollection
    """
    linewidths = kwargs.pop('linewidths', 0.5)
    hexcolor = kwargs.pop('c', 'white')
    pentcolor = kwargs.pop('edgecolors', 'black')
    s = kwargs.pop('s', 500)
    sc_hex = ax.scatter(x, y, edgecolors=pentcolor, c=hexcolor, linewidths=linewidths,
                        marker=football_hexagon_marker, s=s, **kwargs)

    if 'label' in kwargs:
        Legend.update_default_handler_map({sc_hex: HandlerFootball()})
        del kwargs['label']

    sc_pent = ax.scatter(x, y, edgecolors=pentcolor, c=pentcolor, linewidths=linewidths,
                         marker=football_pentagon_marker, s=s, **kwargs)

    return sc_hex, sc_pent


class HandlerFootball(HandlerPathCollection):
    """Automatically generated by scatter_football() if label is a keyword
    to allow use of football marker in legend."""

    if 'transOffset' in inspect.signature(HandlerPathCollection.create_collection).parameters.keys():
        def create_collection(self, orig_handle, sizes, offsets, transOffset):
            edgecolor = orig_handle.get_edgecolor()[0]
            facecolor = orig_handle.get_facecolor()[0]
            sizes = [size * 0.249 for size in sizes]
            return type(orig_handle)([football_hexagon_marker, football_pentagon_marker],
                                     sizes=sizes,
                                     offsets=offsets,
                                     transOffset=transOffset,
                                     facecolors=[facecolor, edgecolor],
                                     edgecolors=edgecolor,
                                     )
    else:
        def create_collection(self, orig_handle, sizes, offsets, offset_transform):
            edgecolor = orig_handle.get_edgecolor()[0]
            facecolor = orig_handle.get_facecolor()[0]
            sizes = [size * 0.249 for size in sizes]
            return type(orig_handle)([football_hexagon_marker, football_pentagon_marker],
                                     sizes=sizes,
                                     offsets=offsets,
                                     offset_transform=offset_transform,
                                     facecolors=[facecolor, edgecolor],
                                     edgecolors=edgecolor,
                                     )

    def _default_update_prop(self, legend_handle, orig_handle):
        facecolor = legend_handle.get_facecolor()
        edgecolor = legend_handle.get_edgecolor()
        legend_handle.update_from(orig_handle)
        legend_handle.set_facecolor(facecolor)
        legend_handle.set_edgecolor(edgecolor)
