Version 0.0.4
-----------

### Added
1) Docs and gallery added.
2) Added option to change penalty and center spot size.
3) Added legend handlers for plotting footballs in Pitch's scatter method, arrows in the quiver method, and lines in the lines method.

### Changed
1) utils module renamed scatterutils
2) default color of Pitch.lines() changed to rcparams['lines.color']
3) Pitch.lines() now takes alpha_start and alpha_end arguments. The line linearly increases in opacity from alpha_start to alpha_end if transparent=True. Previously these were hard coded as 0.1 and 0.5. The new defaults are 0.01 and 1.
4) Pitch.lines() not takes cmap as an argument. You can either select cmap or color, but not both.
5) Pitch.bin_statistic_positional() and Pitch.bin_statistic() return dictionaries rather than named tuples.
6) Pitch defaults changed to tight_layout=True and constrained_layout=False.
7) Default penalty and center spot size smaller.

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
