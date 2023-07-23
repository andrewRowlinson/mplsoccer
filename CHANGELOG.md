:rocket: Version 1.2.0
----------------------

### Added
* :heart_eyes: Added the ``formation`` method, which plots formations as text, images, inset axes, \
scatter plots or pitches.
* :new: Added the ability to return a dataframe for all the formations and player positions with the \
``Pitch.formations_dataframe`` attribute and the ``Pitch.get_positions()`` method.
* :new: Added the ``inset_axes`` and ``inset_image`` methods/functions for plotting \
inset axes and images.
* :new: Added the ``Pitch.text`` wrapper for Axes.text, which automatically flips \
the x and y coordinates.
* :new: Added the ``xoffset`` and ``yoffset``arguments to the label_heatmap method \
for plotting a heatmap's labels off-center.

### Breaking Changes
* :x: Fixed the Matplotlib dependency to version 3.6 or higher.
* :x: The StatsBomb ``tactics_formation`` is changed from a numeric dtype to a string dtype, \
e.g. 442 changed to '442'

### Changes
* :ok: Added the new pitch attributes ``positional_alpha`` and ``shade_alpha`` for \
controlling the transparency of the positional lines and shaded block in the middle of the pitch. \
Previously, the alpha was controlled by the ``line_alpha`` attribute.

### Fixes
* Fixed some deprecation warnings for Matplotlib (get_cmap) and Seaborn (kdeplot).

:rocket: Version 1.1.12
----------------------

### Fixes
* Fixed the timestamp conversion for match data.

:rocket: Version 1.1.11
----------------------

### Added
* Added the pitch type ``impect`` for plotting [impect data](https://www.impect.com/en/).

:rocket: Version 1.1.10
----------------------

### Fixes
* Fixed the StatsBomb lineup parsers so when the player_nickname is missing \
the parsers still work.

:rocket: Version 1.1.9
----------------------

### Fixes
* Fixed positional pitch marking to remove extraneous lines when ``Pitch`` is created with 
``positional=True`` 

:rocket: Version 1.1.8
----------------------

### Fixes
* Fixed goal width dimensions for ``opta_dims`` definitions from (44.62,55.38) to (45.2,54.8)

:rocket: Version 1.1.7
----------------------

### Fixes
* Fixed the ``PyPizza`` class so that ``linewidths`` of zero are allowed values. \
see: https://github.com/andrewRowlinson/mplsoccer/issues/71
* Fixed the ``HandlerFootball`` class so the football scatter method is compatible with \
Matplotlib 3.6 where transOffset was replaced with offset_transform. \
see: https://github.com/andrewRowlinson/mplsoccer/issues/72

### Docs
* Added a wedges example to the tutorials as an alternative to comet lines.

:rocket: Version 1.1.5/1.1.6
----------------------------

### Fixes
* Fixes the ``FontManager`` URLs so that they can be imported in JupyterLite.

### Changes
* We now use hatch rather than setuptools for the mplsoccer build.

:rocket: Version 1.1.4
----------------------

### Fixes
* Fixed the ``Pitch.bin_statistic`` method so that it returns consistent binnumber results for \
the different pitch types. Now the binnumber indexing starts in the top-left hand corner \
as index 0, 0. Previously it depended on whether the pitch had an inverted y-axes whether the \
indexing started at the top or bottom left corner. This change is consistent with how indexing \
on a numpy array works (0, 0) is the top-left corner so this enables the bin statistics \
to be reconstructed from the binnumber via numpy indexing.

### Changes
* Bin numbers from ``Pitch.bin_statistic`` start in the top-left corner at index 0,0.
* Statistics from ``Pitch.bin_statistic``, now mirror the horizontal pitch layout, i.e. they match \
the output from ``Pitch.label_heatmap``. The y coordinate center and edges have been flipped \
for inverted y-axis to allow this change (previously the statistic was flipped instead).

:rocket: Version 1.1.3
----------------------

### Fixes
* Fixed the broken links for the Roboto fonts in the docs and ``FontManager`` class.

:rocket: Version 1.1.2
----------------------

### Fixes
* Fixed the error message for ``Radar`` when min_range > max_range so that it notifies you \
to use the argument ``lower_is_better`` rather than ``greater_is_better``.

### Docs
* :page_with_curl: Added an example of layering turbines and radar charts.

:rocket: Version 1.1.1
----------------------

### Breaking Changes
* :x: The ``statsbomb`` module is completely overhauled to make it easier to use. \
The module now contains three classes ``Sbopen``, ``Sbapi`` and ``Sblocal`` for retrieving data \
from the StatsBomb open-data, API, and local files.
* :x: Added the ``lower_is_better`` argument to ``Radar``. If any of ``lower_is_better`` \
strings are in the parameter list then the radar object will flip the statistic. \
Previously you had to manually switch the order of the ``min_range`` and ``max_range`` \
to flip the statistic. In soccer, this is useful for parameters like miss-controls \
where fewer miss-controls is better than more. \
The default (None) does not flip any of the parameters.
* :new: Added the ``grid`` module, which allows the ``grid``  function to be \
used with other types of charts.
* :x: The ``grid`` method is changed so if there is no endnote or title then the axes \
(or numpy array of axes) are returned rather than a dictionary.
* :x: Renamed ``calculate_grid_dimensions`` to ``grid_dimensions``.

### Added
* :heart_eyes: Added a turbine chart, which is a Radar plot with multiple kernel density \
estimators  plotted to show where in the distribution a person's skill falls. \
Inspired by [Soumyajit Bose](https://twitter.com/Soumyaj15209314)
* :heart_eyes: Delaunay triangulation added to Pitch classes by \
[Matthew Williamson]( https://twitter.com/photomattic) using the ``triplot`` method.
* :heart_eyes: Binnumbers added to the ``bin_statistic`` methods to give \
the bin indices for each event. If the event has a null coordinate or a coordinate \
outside the pitch the indices are set to negative one.
* :icecream: ``corner_arcs`` Boolean argument added to pitches by \
[Devin Pleuler]( https://twitter.com/devinpleuler) for plotting corner arcs.
* :icecream: Added the ``linestyle``, ``goal_linestyle``, and ``line_alpha`` \
arguments for styling of the pitches.
* :icecream: Added ``spoke`` method to the Radar class for drawing lines from the center \
of the radar to the edges for each plotted statistic.
* :new: Added the ``statistic=circmean`` argument to bin_statistic, which uses \
a nan safe version of scipy circmean.
* :new: Added the ``draw_radar_solid`` method to ``Radar`` to more easily plot multiple radars \
on the same chart.

### Changes
* :ok: ``polygon`` method of the Pitch class changed to plot multiple of \
matplotlib.patches.Polygon rather than one matplotlib.collections.PatchCollection \
so they can be clipped more easily to the shape of other patches.
* :ok: Removed warnings for ``figsize``, ``tight_layout``, ``contrained_layout``, \
``layout``, ``view``, and ``orientation`` as the arguments are deprecated.
* :ok:  Changed how pitch lines are drawn from one continuous line to plotting some \
lines separately. The one continuous line way of plotting caused problems \
as the dotted linestyle was plotted incorrectly when the lines overlapped.
* :ok: Changed how the ``box`` goal is drawn from a rectangle to a line to allow \
``goal_linestyle`` to work without it overlapping with the pitch
* :ok: Changed ``bin_statistic`` to use the nan safe versions of mean, std, median, \
sum, min, and max.

### Docs
* :page_with_curl: Added a new tutorial section and the first tutorial expected threat. \
Expected threat is based on the methods popularised by \
[Karun Singh](https://twitter.com/karun1710) and [Sarah Rudd](https://twitter.com/srudd_ok).
* :page_with_curl: Removed the matplotlib sub_plot_mosaic function from the docs. \
Many people reported that they had problems because it was not available in their \
version of matplotlib. It has been replaced with the new ``grid`` functions.

:rocket: Version 1.0.7
----------------------

### Fixes
* Fixed a memory leak in pitch.lines and pitch.quiver associated with assigning \
those collections to class-level legend handler map, so they never deallocated.
* Fixed read_lineup so it works from reading from a local file.

:rocket: Version 1.0.6
----------------------

### Fixes
* Removed deprecated set indexer in statsbomb event reader.
* Fixes for docs: simplified StatsBomb section, fixed broken StatsBomb logos, \
and fixed the standardizer example so that it works with the lastest version of kloppy.

:rocket: Version 1.0.5
----------------------
  
### Fixes
* Fixed the install process (setup.py) so it does not import mplsoccer. The version number is now \
contained in the _version.py file.

:rocket: Version 1.0.4
----------------------

### Added
* Added ``convexhull`` method to the Pitch classes. This creates a polygon with the smallest \
shape that contains the points.

:rocket: Version 1.0.3
----------------------

### Added
* Added ``**kwargs`` to ``Bumpy.plot()`` method. \
All the keyword arguments are passed for setting ticklabels and labels.
* It is now possible to adjust the text in Pizza comparison charts if \
the the text overlaps through ``get_compare_value_texts``. \
Four new methods have been added to ``PyPizza`` to enable this:
  * ``get_param_texts()`` : To fetch list of ``axes.text`` for params.
  * ``get_value_texts()`` : To fetch list of ``axes.text`` for values. 
  * ``get_compare_value_texts()`` : To fetch list of ``axes.text`` for comparison-values.
  * ``get_theta()`` : To fetch list containing theta values (``float``) (x-coordinate for each text).
* added line_alpha to control the transparency of the pitch lines.
* added a cyberpunk example with glowing pitch lines.
  
### Changes
* increased the ``goal_alpha`` default to 1. ``goal_alpha`` can now be used with all goal_types.

### Fixes
* fixed the Pitch.grid method ``axis`` argument default to True to match the docstrings.

:rocket: Version 1.0.2
----------------------

This release is a major refactor of mplsoccer and a merger with 
[soccerplots](https://github.com/Slothfulwave612/soccerplots) for plotting Radars.

---

### Breaking Changes
* :x: ``orientation`` argument is removed. \
To plot on a vertical pitch use the new ``VerticalPitch`` class.
* :x: ``layout`` argument is removed. Use the Matplotlib style ``nrows`` and ``ncols`` instead. \
For example, Pitch(layout=(4, 5)) becomes pitch = Pitch() and pitch.draw(nrows=4, ncols=5).
* :x: ``view`` argument is removed. Use half=True to display half-a-pitch. \
For example, Pitch(view='half') becomes Pitch(half=True).
* :x: ``pitch_type=stats`` pitch_type option removed.
* :x: removed ``jointplot`` method and replaced with the more flexible ``jointgrid`` method.

---

### Changes
* :white_check_mark: ``hexbin`` now clips to the sides of the soccer pitch for a more \
attractive visualization.
* :heavy_exclamation_mark: ``wyscout`` goal width increased to 12 units (from 10 units) \
to align with ggsoccer. This matters as the new ``Standardizer`` \
class uses the goalpost dimensions.
* :heavy_exclamation_mark: fixed  the``bin_statistic_positional`` and ``heatmap_positional`` \
so the heatmaps are created consistently at the heatmap edges \
i.e. grid cells are created from the bottom to the top of the pitch, where the top edge \
always belongs to the cell above.

---

### Added
* :heart_eyes: Merged mplsoccer with [soccerplots](https://github.com/Slothfulwave612/soccerplots) \
for wonderful radar charts and  bumpy charts.
* :strawberry: Added Nightingale Rose Charts (also known as pizza charts).
* :strawberry: Added a ``jointgrid`` method to draw optional marginal axes on the four-sides \
of a soccer pitch. This replaces the old ``jointplot``, which did not allow non-square pitches.
* :strawberry: Added the ``grid`` method to create a grid of pitches with more control \
than plt.subplots.
* :strawberry: Added ``FontManager`` from [ridge_map](https://github.com/colcarroll/ridge_map) \
by [Colin Carroll](https://twitter.com/colindcarroll) for downloading and using google fonts.
* :strawberry: Added ``Standardizer`` for changing from one provider data format to another. \
For example, StatsBomb to Tracab.
* :icecream: Added new pitch_types: ``skillcorner``, ``secondspectrum``, and a ``custom`` \
pitch type where the length and width can vary.
* :icecream: Added ``goal_alpha`` for controlling the transparency of ``goal_type='box'`` goals.
* :icecream: Added ``goal_type='circle'`` to plot the goalposts as circles.
* :new: Added ``degrees=True`` option so calculate_angle_and_degrees can output the angle \
in degrees clockwise.
* :new: Added ``create_transparent_cmap`` to create colormaps that vary from high transparency \
to low transparency.
* :new: Added ``normalize`` option to ``bin_statistic`` and ``bin_statistic_positional`` \
so the results are divided by the total.
* Added ``str_format`` option to ``label_heatmap`` to enable formatting of heatmap labels, \
e.g. % or rounding.
* Added ``exclude_zeros`` option (default False) to ``label_heatmap`` to enable you to \
exclude drawing any labels equal to zero.

---

### Fixes
* :ok: Changed ``Seaborn`` x and y from arguments to keyword arguments. \
This fixes a FutureWarning from Seaborn that the only valid positional argument will be data.
* :ok: Changed imports so that you do not need to reference the module. \
For example, you can now use: from mplsoccer import Pitch.
* :ok: Added repr methods for string representations of classes.
* :ok: Stopped the storage of the Matplotlib figure and axes in the pitch class attributes.
* :ok: Fixed a FutureWarning from Pandas that the lookup method will be deprecated.

---

### Docs
* :page_with_curl: Added examples for custom colormaps
* :page_with_curl: Tweaked the StatsBomb data example to only update files if the \
JSON file has changed.
* :page_with_curl: Added more beautiful scatter examples and chart titles.
* :page_with_curl: Added examples for ``grid`` and ``jointgrid``.

---

### Refactoring
The pitch class has been split into multiple modules and classes to simplify the code.
This helps reduce the number of conditional if/else switches.
* pitch.py contains the new classes for plotting/ drawing pitches. The ``Pitch`` class is for a \
horizontally orientated soccer pitch, and the new ``VerticalPitch`` is for the \
vertical orientation. A change from the old API of Pitch(orientation='vertical').
* The ``Pitch`` and ``VerticalPitch`` classes inherit their \
plotting methods from ``BasePitchPlot``. While ``BasePitchPlot`` inherits attributes and methods \
for drawing a soccer pitch from ``BasePitch``.
* The soccer pitch dimensions are in a separate module (dimensions.py) for reuse within \
a new ``Standardizer`` class.
* The code for heatmaps, arrows, lines, scatter_rotation, and scatter_football are now \
in separate modules (heatmap.py, quiver.py, linecollection.py, and scatterutils.py).

---

:rocket: Version 0.0.23
-----------------------

### Hot fix
Fixed the statsbomb module to allow a requests response to be used in read_event, read_match, read_competition and read_lineup. This should allow the statsbomb module to be used with the StatsBomb API via the requests library.


:rocket: Version 0.0.22
-----------------------

### Hot fix
Fixed statsbomb read_event to read the z location, as StatsBomb recently changed their data so it also records the shot impact height 'z' location.


:rocket: Version 0.0.21
-----------------------

### Changed
1) changed the name of the 'statsperform' pitch_type to 'uefa'
2) changed the background zorder from 0.8 -> 0.6 so it defaults to below the new Juego de posición pitch markings
3) changed the center circle size for the opta, wyscout, statsbomb, and stats pitches to align with the edge of the six-yard box

### Fixed
1) amended the fbref plotting example to work for all five of the leagues.
2) arrows can now take *args to allow colors to be set using C via a cmap.
3) fixed a bug for the metricasports pitch so the center circle and arcs plot when the pitch_width and pitch_length are the same size
4) fixed a bug for the Voronoi plot where the wyscout, opta, and metricasports data wasn't scaled appropriately to a full-sized pitch
5) fixed bin_statistic so the binning of data is always consistent from the bottom to the top of the pitch. Previously pitches with an inverted axis were binned top to bottom. This does not currently apply to bin_statistic_positional.

### Added
1) added a method calculate_angles_and_distance to calculate the angle and distance from start and end locations.
2) added an example for plotting a pass network contributed by DymondFormation.
3) added parameters to shade the middle section of the pitch and draw Juego de posición pitch markings. 
4) added a method flow to plot a pass flow map and a new example using this method

:rocket: Version 0.0.20
-----------------------

### Fixed
1) Fixed arrows so the arrows scale correctly when the dots per inches (dpi) of the figure is changed. Before the units were in dots so the arrow got smaller as the dots per inches increases. Fixed this so the arrow is in points (1/72th of an inch) so the arrow stays the same size when the dots per inch changes.


:rocket: Version 0.0.19
-----------------------

### Fixed
1) Fixed arrows legend to work in recent versions of matplotlib.

:rocket: Version 0.0.17 / 0.0.18
----------------------------------------

### Changed
1) changed the event_type_name/ event_type_id columns in the StatsBomb data to sub_type_name, sub_type_id.


:rocket: Version 0.0.16
-----------------------

### Changed
1) combined the StatsBomb technique columns (pass_technique, goalkeeper_technique, shot_technique) into techique_id and technique_name
2) combined the Statsbomb type columns (pass_type, duel_type_id, goalkeeper_type, shot_type) into event_type_name and event_type_id
3) removed StatsBomb columns that repeat other columns: pass_through_ball, pass_outswinging, pass_inswinging, 
clearance_head, clearance_left_foot, clearance_right_foot, pass_straight, clearance_other, goalkeeper_punched_out, 
goalkeeper_shot_saved_off_target, shot_saved_off_target, goalkeeper_shot_saved_to_post, shot_saved_to_post, 
goalkeeper_lost_out, goalkeeper_lost_in_play, goalkeeper_success_out, goalkeeper_success_in_play, goalkeeper_saved_to_post,
shot_kick_off, goalkeeper_penalty_saved_to_post

:rocket: Version 0.0.15
-----------------------

### Changed
1) changed Pitch so axes aren't raveled when using subplots, e.g. layout=(2, 2). So colorbar can be used with subplots.


:rocket: Version 0.0.14
-----------------------

### Changed
1) changed the internal workings of bin statistics and heatmaps so the results of bin_statistic can be used for other purposes.
2) removed print function from Pitch.

:rocket: Version 0.0.12
-----------------------

### Changed
1) changed the wyscout goal posts y locations to 45/ 55 for consistency with [socceraction](https://github.com/ML-KULeuven/socceraction/blob/master/socceraction/spadl/wyscout.py). 

:rocket: Version 0.0.11
-----------------------

### Changed
1) fixed the statsbomb module so the event dataset has simplified names for the end coordinates. Previously they were shot_end_x, pass_end_x etc. Now they are under three columns: end_x, end_y, end_z.

:rocket: Version 0.0.10
-----------------------

### Fixed
1) fixed the statsbomb module so it works when the json is empty.

:rocket: Version 0.0.9
----------------------

### Added
1) Added Pitch.voronoi() for calculating Voronoi vertices.
2) Added Pitch.goal_angle() for plotting the angle to the goal.
3) Added Pitch.polygon() for plotting polygons on the pitch (e.g. goal angle and Voronoi)
4) Added add_image for adding images to matplotlib figures.

:rocket: Version 0.0.8
----------------------

### Fixed
1) Made the statsbomb module clean the data faster.

:rocket: Version 0.0.7
----------------------

### Fixed
1) fixed Pitch.label_heatmap(). Now filters out labels outside of the pitch extent.


:rocket: Version 0.0.6
----------------------

### Fixed
1) fixed Pitch.bin_statistic(). Now works for ``statistic`` arguments other than 'count'.


:rocket: Version 0.0.5
----------------------

### Fixed
1) fixed Pitch.heatmap() bug. Now returns a mesh in horizontal orientation.


:rocket: Version 0.0.4
----------------------

### Added
1) Docs and gallery added.
2) Added option to change the penalty and center spot size via spot_scale.
3) Added legend handlers for plotting footballs in the scatter method, arrows in the arrows method, and lines in the lines method of the Pitch class.

### Changed
1) utils module renamed scatterutils
2) Pitch.quiver() renamed Pitch.arrows()
3) Default color of Pitch.lines() changed to rcparams['lines.color']
4) Default hexbin cmap changed to viridis
5) Pitch.lines() now takes alpha_start and alpha_end arguments. The line linearly increases in opacity from alpha_start to alpha_end if transparent=True. Previously these were hard coded as 0.1 and 0.5. The new defaults are 0.01 and 1.
6) Pitch.lines() not takes cmap as an argument. You can either select cmap or color, but not both.
7) Pitch.bin_statistic_positional() and Pitch.bin_statistic() return dictionaries rather than named tuples.
8) Pitch defaults changed to tight_layout=True and constrained_layout=False.
9) Default penalty and center spot size now smaller and can be adjusted.
10) Pitch default colors changed, pitch_color is now not plotted by default ('None') and pitch lines are taken from the rcParams 'grid.color'.  

:rocket: Version 0.0.3
----------------------

Minor pep8 fixes.

:rocket: Version 0.0.2
----------------------

### Added
1) Added constrained_layout option for Pitch class
2) Added line_zorder so can raise or lower pitch markings in a plot. This was necessary so you could plot the pitch lines over a heatmap.
3) Added support for 'statsperform' and 'metricasports' pitch types.
4) Added support for grass texture with pitch_color='grass', e.g. Pitch(pitch_color='grass').
5) Added heatmap and methods to bin data and create statistics to allow plotting of heatmaps over pitches.
6) Added an arrowhead_marker. Example use: from mplsoccer.utils import arrowhead_marker; Pitch.scatter(x,y,marker='arrowhead_marker).
7) Added support for marker rotation, e.g. Pitch.scatter(x,y,rotation_degrees=rotation_degrees). The rotation is in degrees and clockwise. Zero degrees is aligned with the direction of play, i.e. left to right in the horizontal orientation and bottom to top in vertical orientation.
8) Added data checks around how padding is used so that you can't accidentally remove the pitch or flip the axis by setting pad_left, pad_right, pad_top,pad_bottom too negative in the Pitch class.
9) Added Statsbomb data support to read data from the open-data repo (https://github.com/statsbomb/open-data).
10) Added various ValueErrors to ensure that the size of input arrays for plots are the same.

### Changed
1) Default pitch_type is now 'statsbomb'. It was 'opta'.
2) Changed defaults for Pitch class: tight_layout=False and constrained_layout=True
3) Renamed Pitch.joint_plot() to Pitch.jointplot() to align with Seaborn.
4) Pitch backgrounds now plotted internally with the method Pitch._set_background().

### Fixed
1) Fixed jointplot to clip to pitch outline.
2) Fixed 'wyscout' pitch type. The 0,0 coordinate is meant to be top left.
3) Fixed the Pitch.lines() method to take a non-sequence (e.g. one line).
4) Fixed the Pitch.lines() method so that when transparent=True its consistent across pitch types. It is more transparent at the line start and more opaque at the line end.
5) Fixed how dimensions are represented in the Pitch class internally (left, right, bottom, top) so they match the horizontal pitch orientation.

:rocket: Version 0.0.1
----------------------
### Fixed
1) Fixed the README so it loads pictures from the raw GitHub files.
    
:rocket: Version 0.0.0
----------------------

Initial version. Pitch class with plotting methods: scatter, lines, quiver, kdeplot, hexbin, and joint_plot. Scatter accepts marker='football' to plot footballs.
