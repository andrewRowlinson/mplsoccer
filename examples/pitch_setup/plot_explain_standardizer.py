"""
========================
Explain the Standardizer
========================

This example is used to explain why you should use mplsoccer's standardization technique.
It shows how pitches stretch to fit pitches of a fixed dimension.
More details are available in the Standardize data example.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from mplsoccer import Pitch, VerticalPitch, FontManager
from mplsoccer.quiver import arrows

FIGWIDTH, FIGHEIGHT = 14, 10
FIGSIZE = (FIGWIDTH, FIGHEIGHT)
FIG_ASPECT = FIGWIDTH / FIGHEIGHT
fig = plt.figure(figsize=FIGSIZE)

fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                       'rubikmonoone/RubikMonoOne-Regular.ttf')

# layout specifications
PAD = 1
pitch_spec = {'pad_left': PAD, 'pad_right': PAD,
              'pad_bottom': PAD, 'pad_top': PAD, 'pitch_color': 'None'}
pitch_width, pitch_length = 80, 105
pitch_width3, pitch_length3 = 60, 105
pitch_length4, pitch_width4 = 120, 68
pitch_length6, pitch_width6 = 85, 68

# define pitches (top left, top middle, top right, bottom left, bottom middle, bottom right)
pitch1 = Pitch(pitch_type='custom', pitch_width=pitch_width, pitch_length=pitch_length,
               line_color='#b94e45', **pitch_spec)
pitch2 = Pitch(pitch_type='statsbomb', **pitch_spec)
pitch3 = Pitch(pitch_type='custom', pitch_width=pitch_width3, pitch_length=pitch_length3,
               line_color='#56ae6c', **pitch_spec)
pitch4 = VerticalPitch(pitch_type='custom', pitch_length=pitch_length4, pitch_width=pitch_width4,
                       line_color='#bc7d39', **pitch_spec)
pitch5 = VerticalPitch(pitch_type='statsbomb', **pitch_spec)
pitch6 = VerticalPitch(pitch_type='custom', pitch_length=pitch_length6, pitch_width=pitch_width6,
                       line_color='#677ad1', **pitch_spec)

TITLE_HEIGHT = 0.1  # title axes are 10% of the figure height

#  width of pitch axes as percent of the figure width
TOP_WIDTH = 0.27
BOTTOM_WIDTH = 0.18

# calculate the horizontal space between axes (and figure sides) in percent of the figure width
TOP_SPACE = (1 - (TOP_WIDTH * 3)) / 4
BOTTOM_SPACE = (1 - (BOTTOM_WIDTH * 3)) / 4

# calculate the height of the pitch axes in percent of the figure height
height1 = TOP_WIDTH / pitch1.ax_aspect * FIG_ASPECT
height2 = TOP_WIDTH / pitch2.ax_aspect * FIG_ASPECT
height3 = TOP_WIDTH / pitch3.ax_aspect * FIG_ASPECT
height4 = BOTTOM_WIDTH / pitch4.ax_aspect * FIG_ASPECT
height5 = BOTTOM_WIDTH / pitch5.ax_aspect * FIG_ASPECT
height6 = BOTTOM_WIDTH / pitch6.ax_aspect * FIG_ASPECT

# calculate pitch offsets from center / title locations
vertical_axes_space = (1 - (height1 + height4 + TITLE_HEIGHT + TITLE_HEIGHT)) / 5
bottom_offset = ((1 - height4) / 2) - vertical_axes_space
title1_bottom = 1 - vertical_axes_space - TITLE_HEIGHT
title2_bottom = 1 - (vertical_axes_space * 3) - (TITLE_HEIGHT * 2) - height1
top_offset = (1 - title1_bottom - title2_bottom - TITLE_HEIGHT) / 2

# draw pitches

# top left
LEFT1 = TOP_SPACE
bottom1 = (1 - height1) / 2 - top_offset
ax1 = fig.add_axes((LEFT1, bottom1, TOP_WIDTH, height1))
pitch1.draw(ax=ax1)

# top middle
left2 = (TOP_SPACE * 2) + TOP_WIDTH
bottom2 = (1 - height2) / 2 - top_offset
ax2 = fig.add_axes((left2, bottom2, TOP_WIDTH, height2))
pitch2.draw(ax=ax2)

# top right
left3 = (TOP_SPACE * 3) + (TOP_WIDTH * 2)
bottom3 = (1 - height3) / 2 - top_offset
ax3 = fig.add_axes((left3, bottom3, TOP_WIDTH, height3))
pitch3.draw(ax=ax3)

# bottom left
LEFT4 = BOTTOM_SPACE
bottom4 = (1 - height4) / 2 - bottom_offset
ax4 = fig.add_axes((LEFT4, bottom4, BOTTOM_WIDTH, height4))
pitch4.draw(ax=ax4)

# bottom middle
left5 = (BOTTOM_SPACE * 2) + BOTTOM_WIDTH
bottom5 = (1 - height5) / 2 - bottom_offset
ax5 = fig.add_axes((left5, bottom5, BOTTOM_WIDTH, height5))
pitch5.draw(ax=ax5)

# bottom right
left6 = (BOTTOM_SPACE * 3) + (BOTTOM_WIDTH * 2)
bottom6 = (1 - height6) / 2 - bottom_offset
ax6 = fig.add_axes((left6, bottom6, BOTTOM_WIDTH, height6))
pitch6.draw(ax=ax6)

# draw titles

font_kwargs = {'size': 20, 'va': 'center', 'ha': 'center', 'fontproperties': fm_rubik.prop}
# title

ax_title1 = fig.add_axes((0, title1_bottom, 1, TITLE_HEIGHT))
ax_title1.axis('off')
ax_title1.text(LEFT1 + TOP_WIDTH / 2, 0.5,
               f'{pitch_length}m X {pitch_width}m\nWide pitch',
               color='#b94e45', **font_kwargs)
ax_title1.text(left2 + TOP_WIDTH / 2, 0.5, 'StatsBomb\n(120 X 80)',
               color=pitch2.line_color, **font_kwargs)
ax_title1.text(left3 + TOP_WIDTH / 2, 0.5,
               f'{pitch_length3}m X {pitch_width3}m\nNarrow pitch',
               color='#56ae6c', **font_kwargs)
ax_title1.set_xlim(0, 1)
ax_title1.set_ylim(0, 1)
arrows(LEFT1 + TOP_WIDTH / 2, 0.1, left2 + TOP_WIDTH / 2, 0.1, color='#b94e45', ax=ax_title1)
arrows(left3 + TOP_WIDTH / 2, 0.1, left2 + TOP_WIDTH / 2, 0.1, color='#56ae6c', ax=ax_title1)

ax_title2 = fig.add_axes((0, title2_bottom, 1, TITLE_HEIGHT))
ax_title2.axis('off')
ax_title2.text(LEFT4 + BOTTOM_WIDTH / 2, 0.5,
               f'{pitch_length4}m X {pitch_width4}m\nLong pitch',
               color='#bc7d39', **font_kwargs)
ax_title2.text(left5 + BOTTOM_WIDTH / 2, 0.5,
               'StatsBomb\n(120 X 80)', color=pitch5.line_color, **font_kwargs)
ax_title2.text(left6 + BOTTOM_WIDTH / 2, 0.5,
               f'{pitch_length6}m X {pitch_width6}m\nShort pitch',
               color='#677ad1', **font_kwargs)
ax_title2.set_xlim(0, 1)
ax_title2.set_ylim(0, 1)
arrows(LEFT4 + BOTTOM_WIDTH / 2, 0.1, left5 + BOTTOM_WIDTH / 2, 0.1, color='#bc7d39', ax=ax_title2)
arrows(left6 + BOTTOM_WIDTH / 2, 0.1, left5 + BOTTOM_WIDTH / 2, 0.1, color='#677ad1', ax=ax_title2)

ax_all = fig.add_axes((0, 0, 1, 1))
ax_all.set_facecolor('None')
ax_all.axis('off')

# hatch boxes

hatch_kwargs = {'facecolor': 'None', 'hatch': '///', 'edgecolor': pitch2.line_color}
pitch2._draw_rectangle(ax2, pitch2.dim.left, pitch2.dim.penalty_area_bottom,
                       pitch2.dim.penalty_area_length, pitch2.dim.penalty_area_width,
                       **hatch_kwargs)
pitch2._draw_rectangle(ax2, pitch2.dim.penalty_area_right, pitch2.dim.penalty_area_bottom,
                       pitch2.dim.penalty_area_length, pitch2.dim.penalty_area_width,
                       **hatch_kwargs)
pitch5._draw_rectangle(ax5, pitch5.dim.left, pitch5.dim.penalty_area_bottom,
                       pitch5.dim.penalty_area_length, pitch5.dim.penalty_area_width,
                       **hatch_kwargs)
pitch5._draw_rectangle(ax5, pitch5.dim.penalty_area_right, pitch5.dim.penalty_area_bottom,
                       pitch5.dim.penalty_area_length, pitch5.dim.penalty_area_width,
                       **hatch_kwargs)

# fixed box text

# top
penalty_area_coordinates2 = [pitch2.dim.penalty_area_length / 2,
                             pitch2.dim.length - pitch2.dim.penalty_area_length / 2]
for coordinate in penalty_area_coordinates2:
    pitch2.annotate('Fixed\nsize', (coordinate, pitch2.dim.center_width),
                    rotation=90, color='#6f706f',
                    bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5, 'edgecolor': 'None'},
                    ax=ax2, **font_kwargs)

# bottom
penalty_area_coordinates5 = [pitch5.dim.penalty_area_length / 2,
                             pitch5.dim.length - pitch5.dim.penalty_area_length / 2]
for coordinate in penalty_area_coordinates5:
    pitch5.annotate('Fixed\nsize', (coordinate, pitch5.dim.center_width), color='#6f706f',
                    bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5, 'edgecolor': 'None'},
                    ax=ax5, **font_kwargs)

# shaded areas

# top left
rect1_width = (pitch1.dim.width - pitch1.dim.penalty_area_width) / 2
rect1_length = pitch1.dim.length
pitch1._draw_rectangle(ax1, pitch1.dim.left, pitch1.dim.bottom,
                       rect1_length, rect1_width, color='#b94e45', alpha=0.5)
pitch1._draw_rectangle(ax1, pitch1.dim.left, pitch1.dim.penalty_area_top,
                       rect1_length, rect1_width, color='#b94e45', alpha=0.5)

# top middle
rect2_width = (pitch2.dim.width - pitch2.dim.penalty_area_width) / 2
rect2_length = pitch2.dim.length / 2
pitch2._draw_rectangle(ax2, pitch2.dim.left, pitch2.dim.bottom,
                       rect2_length, rect2_width, color='#b94e45', alpha=0.5)
pitch2._draw_rectangle(ax2, pitch2.dim.left, pitch2.dim.penalty_area_left,
                       rect2_length, rect2_width, color='#b94e45', alpha=0.5)
pitch2._draw_rectangle(ax2, pitch2.dim.center_length, pitch2.dim.penalty_area_left,
                       rect2_length, rect2_width, color='#56ae6c', alpha=0.5)
pitch2._draw_rectangle(ax2, pitch2.dim.center_length, pitch2.dim.bottom,
                       rect2_length, rect2_width, color='#56ae6c', alpha=0.5)

# top right
rect3_width = (pitch3.dim.width - pitch3.dim.penalty_area_width) / 2
rect3_length = pitch3.dim.length
pitch3._draw_rectangle(ax3, pitch3.dim.left, pitch3.dim.bottom,
                       rect3_length, rect3_width, color='#56ae6c', alpha=0.5)
pitch3._draw_rectangle(ax3, pitch3.dim.left, pitch3.dim.penalty_area_top,
                       rect3_length, rect3_width, color='#56ae6c', alpha=0.5)

# bottom left
rect4_width = pitch4.dim.length - pitch4.dim.penalty_area_length * 2
rect4_length = pitch4.dim.penalty_area_width
pitch4._draw_rectangle(ax4, pitch4.dim.penalty_area_left, pitch4.dim.penalty_area_bottom,
                       rect4_width, rect4_length, color='#bc7d39', alpha=0.5)

# bottom middle
rect5_width = pitch5.dim.length - pitch5.dim.penalty_area_length * 2
rect5_length = pitch5.dim.penalty_area_width / 2
pitch5._draw_rectangle(ax5, pitch5.dim.penalty_area_left, pitch5.dim.penalty_area_bottom,
                       rect5_width, rect5_length, color='#677ad1', alpha=0.5)
pitch5._draw_rectangle(ax5, pitch5.dim.penalty_area_left, pitch5.dim.center_width,
                       rect5_width, rect5_length, color='#bc7d39', alpha=0.5)

# bottom right
rect6_width = pitch6.dim.length - pitch6.dim.penalty_area_length * 2
rect6_length = pitch6.dim.penalty_area_width
pitch6._draw_rectangle(ax6, pitch6.dim.penalty_area_left, pitch6.dim.penalty_area_bottom,
                       rect6_width, rect6_length, color='#677ad1', alpha=0.5)

# polys connecting

bbox1 = ax1.get_position()
bbox2 = ax2.get_position()
bbox3 = ax3.get_position()
bbox4 = ax4.get_position()
bbox5 = ax5.get_position()
bbox6 = ax6.get_position()


def poly(first_pitch, second_pitch, text, text_kwargs, left_ax, right_ax, ax, bbox_left, bbox_right,
         pos1x, pos1y, pos2x, pos2y, pos3x, pos3y, pos4x, pos4y):
    """ Helper method to plot polygons between the pitches."""
    poly_pos1 = first_pitch._to_ax_coord(left_ax, left_ax.transAxes,
                                         (getattr(first_pitch.dim, pos1x),
                                          getattr(first_pitch.dim, pos1y)))
    poly_pos1 = poly_pos1 * np.array([bbox_left.width, bbox_left.height]) + np.array(
        [bbox_left.x0, bbox_left.y0])
    poly_pos2 = second_pitch._to_ax_coord(right_ax, right_ax.transAxes,
                                          (getattr(second_pitch.dim, pos2x),
                                           getattr(second_pitch.dim, pos2y)))
    poly_pos2 = poly_pos2 * np.array([bbox_right.width, bbox_right.height]) + np.array(
        [bbox_right.x0, bbox_right.y0])
    poly_pos3 = second_pitch._to_ax_coord(right_ax, right_ax.transAxes,
                                          (getattr(second_pitch.dim, pos3x),
                                           getattr(second_pitch.dim, pos3y)))
    poly_pos3 = poly_pos3 * np.array([bbox_right.width, bbox_right.height]) + np.array(
        [bbox_right.x0, bbox_right.y0])
    poly_pos4 = first_pitch._to_ax_coord(left_ax, left_ax.transAxes,
                                         (getattr(first_pitch.dim, pos4x),
                                          getattr(first_pitch.dim, pos4y)))
    poly_pos4 = poly_pos4 * np.array([bbox_left.width, bbox_left.height]) + np.array(
        [bbox_left.x0, bbox_left.y0])
    poly_points = np.vstack([poly_pos1, poly_pos2, poly_pos3, poly_pos4])
    polygon = Polygon(poly_points, linestyle='--', linewidth=2, facecolor='None',
                      edgecolor='#b94e45')
    ax.annotate(text, poly_points.mean(axis=0), color='#6f706f', **text_kwargs)
    ax.add_artist(polygon)


# polys top - connect left and middle
poly(pitch1, pitch2, 'Squeeze', font_kwargs, ax1, ax2, ax_all, bbox1, bbox2,
     pos1x='right', pos1y='top', pos2x='left', pos2y='top',
     pos3x='left', pos3y='penalty_area_top', pos4x='right', pos4y='penalty_area_top')
poly(pitch1, pitch2, 'Squeeze', font_kwargs, ax1, ax2, ax_all, bbox1, bbox2,
     pos1x='right', pos1y='penalty_area_bottom', pos2x='left', pos2y='penalty_area_bottom',
     pos3x='left', pos3y='bottom', pos4x='right', pos4y='bottom')

# poly top - connect middle and right
poly(pitch2, pitch3, 'Expand', font_kwargs, ax2, ax3, ax_all, bbox2, bbox3,
     pos1x='right', pos1y='top', pos2x='left', pos2y='top',
     pos3x='left', pos3y='penalty_area_top', pos4x='right', pos4y='penalty_area_top')
poly(pitch2, pitch3, 'Expand', font_kwargs, ax2, ax3, ax_all, bbox2, bbox3,
     pos1x='right', pos1y='penalty_area_bottom', pos2x='left', pos2y='penalty_area_bottom',
     pos3x='left', pos3y='bottom', pos4x='right', pos4y='bottom')

# poly bottom - connect left and middle
poly(pitch4, pitch5, 'Squeeze', font_kwargs, ax4, ax5, ax_all, bbox4, bbox5,
     pos1x='penalty_area_bottom', pos1y='penalty_area_right',
     pos2x='penalty_area_top', pos2y='penalty_area_right',
     pos3x='penalty_area_top', pos3y='penalty_area_left',
     pos4x='penalty_area_bottom', pos4y='penalty_area_left')

# poly bottom - connect middle and right
poly(pitch5, pitch6, 'Expand', font_kwargs, ax5, ax6, ax_all, bbox5, bbox6,
     pos1x='penalty_area_bottom', pos1y='penalty_area_right',
     pos2x='penalty_area_top', pos2y='penalty_area_right',
     pos3x='penalty_area_top', pos3y='penalty_area_left',
     pos4x='penalty_area_bottom', pos4y='penalty_area_left')

plt.show()  # If you are using a Jupyter notebook you do not need this line
