"""
======
Basics
======

First we import the Pitch class and set the matplotlib style sheet.
"""
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
plt.style.use('ggplot')

##############################################################################
# Draw a pitch on a new axis
# --------------------------
# Let's plot on a new axis first.

pitch = Pitch(figsize=(8, 4))  # specifying figure size is optional (width, height)
fig, ax = pitch.draw()

##############################################################################
# Draw on an existing axis
# ------------------------
# mplsoccer also plays nicely with other matplotlib figures. To draw a pitch on an
# existing matplotlib axis specify an ``ax`` in the ``draw`` method.

fig, ax = plt.subplots(nrows=1, ncols=2)
pitch = Pitch()
pitch.draw(ax=ax[1])

##############################################################################
# Supported data providers
# ------------------------
# mplsoccer supports 7 pitch types by specifying the ``pitch_type`` argument:
# 'statsbomb', 'opta', 'tracab', 'stats', 'wyscout', 'statsperform', and 'metricasports'. 
# If you are using tracking data ('metricasports' or 'tracab'), you also need to specify the 
# ``pitch_length`` and ``pitch_width``, which are typically 105 and 68 respectively.

pitch = Pitch(pitch_type='statsperform')  # example plotting a statsperform pitch
fig, ax = pitch.draw()

##############################################################################

pitch = Pitch(pitch_type='tracab', pitch_length=105, pitch_width=68,  # example plotting a tracab pitch
              axis=True, label=True)  # showing axis labels is optional
fig, ax = pitch.draw()

##############################################################################
# Adjusting the plot layout
# -------------------------
# mplsoccer also plots on grids by specifying ``layout``: a tuple of (rows, columns).
# The default is to use
# tight_layout. See: https://matplotlib.org/3.2.1/tutorials/intermediate/tight_layout_guide.html.

pitch = Pitch(layout=(2, 3))
fig, ax = pitch.draw()

##############################################################################
# But you can also use constrained layout
# by setting ``constrained_layout=True`` and ``tight_layout=False``, which may look better.
# See: https://matplotlib.org/3.2.1/tutorials/intermediate/constrainedlayout_guide.html.

pitch = Pitch(layout=(2, 3), tight_layout=False, constrained_layout=True)
fig, ax = pitch.draw()

##############################################################################
# Pitch orientation
# -----------------
# There are four basic pitch orientations controlled by ``orientation`` and ``view`` arguments.
# 
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
# You can also adjust the pitch orientations with the ``pad_left``, ``pad_right``,
# ``pad_bottom`` and ``pad_top`` arguments to make arbitrary pitch shapes.

pitch = Pitch(orientation='vertical', view='half',
              pad_left=-10,  # bring the left axis in 10 data units (reduce the size)
              pad_right=-10,  # bring the right axis in 10 data units (reduce the size)
              pad_top=10,  # extend the top axis 10 data units
              pad_bottom=20)  # extend the bottom axis 20 data units
fig, ax = pitch.draw()

##############################################################################
# Pitch appearance
# ----------------
# The pitch appearance is adjustable.
# Use ``pitch_color`` and ``line_color``, and ``stripe_color`` (if ``stripe=True``) to adjust the colors.

pitch = Pitch(pitch_color='#aabb97', line_color='white',
              stripe_color='#c2d59d', stripe=True)  # optional stripes
fig, ax = pitch.draw()

##############################################################################
# mplsoccer can also plot grass pitches by setting ``pitch_color='grass'``.

pitch = Pitch(pitch_color='grass', line_color='white',
              stripe=True)  # optional stripes
fig, ax = pitch.draw()

##############################################################################
# Two goal types are included ``goal_type='line'`` and ``goal_type='box'``.

pitch = Pitch(goal_type='box')
fig, ax = pitch.draw()

##############################################################################
#  The line markings and spot size can be adjusted via ``linewidth`` and ``spot_scale``.

pitch = Pitch(linewidth=3, 
              spot_scale=0.01)  # the size of the penalty and center spots relative to the pitch_length
fig, ax = pitch.draw()

##############################################################################
# If you need to lift the pitch markings above other elements of the chart.
# You can do this via ``line_zorder`` and ``background_zorder``.

pitch = Pitch(line_zorder=2, background_zorder=1)  # e.g. useful if you want to plot pitch lines over heatmaps
fig, ax = pitch.draw()

##############################################################################
# Axis
# ----
# By default mplsoccer turns of the axis (border), ticks, and labels.
# You can use them by setting the ``axis``, ``label`` and ``tick`` arguments.

pitch = Pitch(axis=True, label=True, tick=True)
fig, ax = pitch.draw()

##############################################################################
# xkcd
# ----
# Finally let's use matplotlib's xkcd theme.

plt.xkcd()
pitch = Pitch(pitch_color='grass', stripe=True, figsize=(8, 4))
fig, ax = pitch.draw()
annotation = ax.annotate('Who can resist this?', (60, 10), fontsize=30, ha='center')
