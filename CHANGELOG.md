
Version 0.0.20
-----------

### Fixed
1) Fixed arrows so the arrows scale correctly when the dots per inches (dpi) of the figure is changed. Before the units were in dots so the arrow got smaller as the dots per inches increases. Fixed this so the arrow is in points (1/72th of an inch) so the arrow stays the same size when the dots per inch changes.


Version 0.0.19
-----------

### Fixed
1) Fixed arrows legend to work in recent versions of matplotlib.

Version 0.0.17 / 0.0.18
-----------

### Changed
1) changed the event_type_name/ event_type_id columns in the StatsBomb data to sub_type_name, sub_type_id.


Version 0.0.16
-----------

### Changed
1) combined the StatsBomb technique columns (pass_technique, goalkeeper_technique, shot_technique) into techique_id and technique_name
2) combined the Statsbomb type columns (pass_type, duel_type_id, goalkeeper_type, shot_type) into event_type_name and event_type_id
3) removed StatsBomb columns that repeat other columns: pass_through_ball, pass_outswinging, pass_inswinging, 
clearance_head, clearance_left_foot, clearance_right_foot, pass_straight, clearance_other, goalkeeper_punched_out, 
goalkeeper_shot_saved_off_target, shot_saved_off_target, goalkeeper_shot_saved_to_post, shot_saved_to_post, 
goalkeeper_lost_out, goalkeeper_lost_in_play, goalkeeper_success_out, goalkeeper_success_in_play, goalkeeper_saved_to_post,
shot_kick_off, goalkeeper_penalty_saved_to_post

Version 0.0.15
-----------

### Changed
1) changed Pitch so axes aren't raveled when using subplots, e.g. layout=(2, 2). So colorbar can be used with subplots.


Version 0.0.14
-----------

### Changed
1) changed the internal workings of bin statistics and heatmaps so the results of bin_statistic can be used for other purposes.
2) removed print function from Pitch.

Version 0.0.12
-----------

### Changed
1) changed the wyscout goal posts y locations to 45/ 55 for consistency with [socceraction](https://github.com/ML-KULeuven/socceraction/blob/master/socceraction/spadl/wyscout.py). 

Version 0.0.11
-----------

### Changed
1) fixed the statsbomb module so the event dataset has simplified names for the end coordinates. Previously they were shot_end_x, pass_end_x etc. Now they are under three columns: end_x, end_y, end_z.

Version 0.0.10
-----------

### Fixed
1) fixed the statsbomb module so it works when the json is empty.

Version 0.0.9
-----------

### Added
1) Added Pitch.voronoi() for calculating Voronoi vertices.
2) Added Pitch.goal_angle() for plotting the angle to the goal.
3) Added Pitch.polygon() for plotting polygons on the pitch (e.g. goal angle and Voronoi)
4) Added add_image for adding images to matplotlib figures.

Version 0.0.8
-----------

### Fixed
1) Made the statsbomb module clean the data faster.

Version 0.0.7
-----------

### Fixed
1) fixed Pitch.label_heatmap(). Now filters out labels outside of the pitch extent.


Version 0.0.6
-----------

### Fixed
1) fixed Pitch.bin_statistic(). Now works for ``statistic`` arguments other than 'count'.


Version 0.0.5
-----------

### Fixed
1) fixed Pitch.heatmap() bug. Now returns a mesh in horizontal orientation.


Version 0.0.4
-----------

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

Version 0.0.3
-----------

Minor pep8 fixes.

Version 0.0.2
-----------

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

Version 0.0.1
-----------
### Fixed
1) Fixed the README so it loads pictures from the raw GitHub files.
    
Version 0.0.0
-----------

Initial version. Pitch class with plotting methods: scatter, lines, quiver, kdeplot, hexbin, and joint_plot. Scatter accepts marker='football' to plot footballs.
