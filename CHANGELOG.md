Version 0.0.2
-----------
    - Default pitch_type is now 'statsbomb'. It was 'opta'.
    - Fixed 'wyscout' pitch type. The 0,0 coordinate is meant to be top left.
    - Fixed jointplot to clip to pitch outline.
    - Added support for 'statsperform' and 'metricasports' pitch types.
    - Added support for grass texture with pitch_color='grass', e.g. Pitch(pitch_color='grass').
    - Added Pitch.heatmap() to allow plotting of heatmaps over pitches.
    - Added an arrowhead_marker. Example use: from mplsoccer.utils import arrowhead_marker; Pitch.scatter(x,y,marker='arrowhead_marker).
    - Added support for marker rotation, e.g. Pitch.scatter(x,y,rotation_degrees=rotation_degrees). The rotation is in degrees and clockwise. Zero degrees is aligned with the direction of play, i.e. left to right in the horizontal orientation and bottom to top in vertical orientation.
    - Fixed the Pitch.lines() method to take a non-sequence (e.g. one line).
    - Fixed the Pitch.lines() method so that when transparent=True its consistent across pitch types. It is more transparent at the line start and more opaque at the line end.
    - Added data checks around how padding is used so that you can't accidentally remove the pitch or flip the axis by setting pad_left, pad_right, pad_top,pad_bottom too negative in the Pitch class.
    - Added Statsbomb data support to read data from the open-data repo (https://github.com/statsbomb/open-data).
    - Fixed how dimensions are represented in the Pitch class internally (left, right, bottom, top) so they match the horizontal pitch orientation.
    - Pitch backgrounds now plotted internally with the method Pitch._set_background().
    - Renamed Pitch.joint_plot() to Pitch.jointplot() to align with Seaborn.
    - Added various ValueErrors to ensure that the size of input arrays for plots are the same.

Version 0.0.1
-----------
    - Fixed the README so it loads pictures from the raw GitHub files.
    
Version 0.0.0
-----------

    - Initial version. Pitch class with plotting methods: scatter, lines, quiver, kdeplot, hexbin, and joint_plot. Scatter accepts marker='football' to plot footballs.
