"""
====================
Heatmap wedge zones
====================

Zones do not have to be rectangles. ``zone_statistic_from_binnumber`` is the
second half of ``bin_statistic_zones`` exposed publicly: you assign each point
to a zone yourself (the binnumber), build a matplotlib patch for each zone,
and mplsoccer computes the statistics and plots the zones as a single
collection. This example bins shots into polar wedges around the goal.

Note that when computing angles, the wrap-around at 2*pi is your
responsibility: shift the angles with ``numpy.mod`` (the same trick as the
pass sonars use) so a zone does not straddle the 0/2*pi boundary.
"""

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Wedge

from mplsoccer import VerticalPitch, FontManager, Sbopen

# get shots from a Women's Super League match
parser = Sbopen()
df = parser.event(19789)[0]  # 0 index is the event file
df = df[df.type_name == 'Shot'].copy()

# fontmanager for google font (robotto) and path effects
robotto_regular = FontManager()
path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
night_cmap = LinearSegmentedColormap.from_list("Night - 100 colors",
                                               ['#15242e', '#4393c4'], N=100)

##############################################################################
# Assign the shots to wedge zones
# -------------------------------
# We split the area in front of the goal at (120, 40) into six 30 degree
# wedges. The angle from the goal to each shot is computed with
# ``numpy.arctan2``, which returns angles between -pi and pi. Angles facing
# into the pitch straddle the wrap-around at pi, so we shift them into the
# 0 to 2*pi range with ``numpy.mod`` before binning them with
# ``numpy.digitize``. Shots further than 42 units from the goal are marked
# as outside the zones with binnumber -1.
num_wedges = 6
radius = 42
theta = np.linspace(np.pi / 2, 3 * np.pi / 2, num_wedges + 1)  # wedge edges in radians
angle = np.mod(np.arctan2(df.y - 40, df.x - 120), 2 * np.pi)
distance = np.hypot(df.x - 120, df.y - 40)
binnumber = np.digitize(angle, theta) - 1
binnumber[(binnumber < 0) | (binnumber >= num_wedges) | (distance > radius)] = -1

##############################################################################
# Build the wedge patches
# -----------------------
# The patches are authored in pitch coordinates and mplsoccer handles the
# vertical pitch by transforming the whole collection. Only you know where
# text should sit on a wedge (its visual centre is at mid-radius/ mid-angle,
# not the polygon centroid), so supply the annotation centres cx/ cy.
theta_degrees = np.degrees(theta)
patches = [Wedge((120, 40), radius, theta_degrees[i], theta_degrees[i + 1])
           for i in range(num_wedges)]
theta_mid = 0.5 * (theta[:-1] + theta[1:])
cx = 120 + 0.6 * radius * np.cos(theta_mid)
cy = 40 + 0.6 * radius * np.sin(theta_mid)

##############################################################################
# Plot the wedge zones
# --------------------
# ``zone_statistic_from_binnumber`` computes the statistics per zone and
# ``heatmap_zones`` plots the patches as one collection, so the colorbar
# and labels work exactly like they do for rectangular zones. The collection
# is clipped to the pitch boundaries (like hexbin and kdeplot), so the wedges
# that extend past the pitch edges are snapped to the pitch.
pitch = VerticalPitch(pitch_type='statsbomb', half=True, line_zorder=2,
                      pitch_color='#15242e', line_color='white')
fig, ax = pitch.draw(figsize=(6.6, 6))
fig.set_facecolor('#15242e')
stats = pitch.zone_statistic_from_binnumber(binnumber, patches=patches, cx=cx, cy=cy)
pc = pitch.heatmap_zones(stats, ax=ax, cmap=night_cmap, edgecolor='#15242e', alpha=0.85)
pitch.scatter(df.x, df.y, c='#f4edf0', s=20, alpha=0.5, ax=ax)
labels = pitch.label_heatmap(stats, color='#f4edf0', fontsize=18,
                             ax=ax, ha='center', va='center',
                             str_format='{:.0f}', path_effects=path_eff)
ax.set_title('Shot counts by angle to goal', color='#f4edf0', fontsize=20,
             fontproperties=robotto_regular.prop)

plt.show()  # If you are using a Jupyter notebook you do not need this line
