"""
======
Basics
======

These examples show how to setup plots in mplsoccer.
"""
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
plt.style.use('ggplot')

##############################################################################
# Draw a pitch on a new axis
# --------------------------
# Plot a pitch on a new matplotlib figure and axis.

pitch = Pitch(figsize=(8, 4))  # specifying figure size is optional (width, height)
fig, ax = pitch.draw()

##############################################################################
# Draw on an existing axis
# ------------------------
# mplsoccer also plays nicely with matplotlib. You can draw a pitch on any existing matplotlib axis by
# specifying the `ax` in pitch.draw().

fig, ax = plt.subplots(nrows=1, ncols=2)
pitch = Pitch()
pitch.draw(ax=ax[1])

##############################################################################
# Supported data providers
# ------------------------
# mplsoccer supports seven pitch types by specifying the `pitch_type` parameter. The supported pitch types are 
# 'statsbomb', 'opta', 'tracab', 'stats', 'wyscout', 'statsperform', 'metricasports'. 
# If you are using tracking data ('metricasports' and 'tracab'), you also need to specify the 
# `pitch_length` and `pitch_width`, which are typically 105 and 68 respectively.

pitch = Pitch(pitch_type='statsperform')  # example plotting a statsperform pitch
fig, ax = pitch.draw()

##############################################################################

pitch = Pitch(pitch_type='tracab', pitch_length=105, pitch_width=68,  # example plotting a tracab pitch
              axis=True, label=True)  # showing axis labels is optional
fig, ax = pitch.draw()

##############################################################################
# Adjusting the plot layout
# -------------------------
# mplsoccer supports basic matplotlib grids by specifying `layout`: a tuple of (rows, columns). The default is to use
# [tight_layout](https://matplotlib.org/3.2.1/tutorials/intermediate/tight_layout_guide.html).

pitch = Pitch(layout=(2, 3))
fig, ax = pitch.draw()

##############################################################################
# You can also use [constrained layout](https://matplotlib.org/3.2.1/tutorials/intermediate/constrainedlayout_guide.html)
# by setting `constrained_layout=True` and `tight_layout=False`, which may look better.

pitch = Pitch(layout=(2, 3), tight_layout=False, constrained_layout=True)
fig, ax = pitch.draw()

##############################################################################
# Pitch orientation
# -----------------
# There are four basic pitch orientations controlled by `orientation` and `view` arguments.
# Horizontal full

pitch = Pitch(orientation='horizontal', view='full')
fig, ax = pitch.draw()

##############################################################################
# Vertical full

pitch = Pitch(orientation='vertical', view='full')
fig, ax = pitch.draw()

##############################################################################
# Horizontal half
pitch = Pitch(orientation='horizontal', view='half')
fig, ax = pitch.draw()

##############################################################################
# Vertical half
pitch = Pitch(orientation='vertical', view='half')
fig, ax = pitch.draw()

##############################################################################
# You can adjust the pitch orientation with the `pad_left`, `pad_right`, `pad_bottom` and `pad_top` arguments to make abritary pitch appearances.

pitch = Pitch(orientation='vertical', view='half',
              pad_left=-10,  # bring the left axis in 10 data units (reduce the size)
              pad_right=-10,  # bring the right axis in 10 data units (reduce the size)
              pad_top=10, # extend the top axis 10 data units
              pad_bottom=20) # extend the bottom axis 20 data units
fig, ax = pitch.draw()

##############################################################################
# Pitch appearance
# ----------------
# The pitch apperance is adjustable including the colors, goal types, and linewidths. Use `pitch_color` and `line_color`, and `stripe_color` (if `stripe=True`).

pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)  # optional stripes
fig, ax = pitch.draw()

##############################################################################
# mplsoccer can also plot grass pitches by setting `pitch_color='grass'`.

pitch = Pitch(pitch_color='grass', line_color='white',
              stripe=True)  # optional stripes
fig, ax = pitch.draw()

##############################################################################
# Two goal types are included `goal_type='line'` and `goal_type='box'`.

pitch = Pitch(goal_type='box')
fig, ax = pitch.draw()

##############################################################################
#  The line markings and spot size can be adjusted via `linewidth` and `spot_scale`.

pitch = Pitch(linewidth=3, 
              spot_scale=0.01)  # the size of the penalty and center spots relative to the pitch_length
fig, ax = pitch.draw()

##############################################################################
# You might need to lift the pitch markings above other elements of the chart.
# You can do this via `line_zorder` and `background_zorder`.

pitch = Pitch(line_zorder = 2, background_zorder = 1)  # e.g. useful if you want to plot pitch lines over heatmaps
fig, ax = pitch.draw()

##############################################################################
# Axis
# ----
# By default mplsoccer turns of the axis, ticks, and labels. You can add them back with `axis`, `label` and `tick` arguments.

pitch = Pitch(axis=True, label=True, tick=True)
fig, ax = pitch.draw()

##############################################################################
# xkcd
# ----
# Finally if you want a bit of fun matplotlib comes with a xkcd theme.

plt.xkcd()
pitch = Pitch(pitch_color='grass', stripe=True, figsize=(8, 4))
fig, ax = pitch.draw()
ax.annotate('Who can resist this?', (60, 10), fontsize=30, ha='center');
