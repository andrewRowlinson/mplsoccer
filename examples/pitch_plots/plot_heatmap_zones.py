"""
====================
Heatmap custom zones
====================

This example shows how to plot heatmaps for a custom zone layout:
axis-aligned rectangles of different sizes that together tile the pitch.
Unlike ``bin_statistic``, the zones do not have to form a regular grid,
so you can merge areas (e.g. a whole third) while splitting others
into channels and halfspaces. The zones are drawn as a single
matplotlib collection so a colorbar works without any syncing.
"""

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import Pitch, FontManager, Sbopen

# get data from three matches of Chelsea FC Women
parser = Sbopen()
match_files = [19789, 19794, 19805]
df = pd.concat([parser.event(file)[0] for file in match_files])  # 0 index is the event file
# filter chelsea pressure events
mask_chelsea_pressure = (df.team_name == 'Chelsea FCW') & (df.type_name == 'Pressure')
df = df.loc[mask_chelsea_pressure, ['x', 'y', 'duration']]

##############################################################################
# Custom colormap, font, and path effects

flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                  ['#e3aca7', '#c03a1d'], N=100)

# fontmanager for google font (robotto)
robotto_regular = FontManager()

path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]

##############################################################################
# Define the zones
# ----------------
# Each zone is a rectangle (x0, x1, y0, y1) in pitch coordinates and together
# the rectangles must exactly tile the pitch (no gaps or overlaps).
# Here we merge the whole defensive third into one zone, split the middle
# third into two halves, and split the attacking third into wings,
# halfspaces and the centre. Zone k of the results always corresponds
# to regions[k]/ names[k] so you can safely join the results to a dataframe.
regions = [(0, 40, 0, 80),      # defensive third
           (40, 80, 0, 40),     # middle third: left half
           (40, 80, 40, 80),    # middle third: right half
           (80, 120, 0, 18),    # attacking third: left wing
           (80, 120, 18, 30),   # attacking third: left halfspace
           (80, 120, 30, 50),   # attacking third: centre
           (80, 120, 50, 62),   # attacking third: right halfspace
           (80, 120, 62, 80)]   # attacking third: right wing
names = ['defensive third', 'middle: left', 'middle: right',
         'wing: left', 'halfspace: left', 'centre',
         'halfspace: right', 'wing: right']

##############################################################################
# Plot a custom zone heatmap
# --------------------------
# The zones are plotted with ``heatmap_zones`` as one
# ``matplotlib.collections.PatchCollection``, so ``fig.colorbar`` works
# directly and ``label_heatmap`` labels the zone centres.
pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0')
fig, ax = pitch.draw(figsize=(6.6, 4.125))
fig.set_facecolor('#f4edf0')
stats = pitch.bin_statistic_zones(df.x, df.y, regions, names=names, normalize=True)
pc = pitch.heatmap_zones(stats, ax=ax, cmap=flamingo_cmap, edgecolor='#f9f9f9')
labels = pitch.label_heatmap(stats, color='#f4edf0', fontsize=18,
                             ax=ax, ha='center', va='center',
                             str_format='{:.0%}', path_effects=path_eff)
cbar = fig.colorbar(pc, ax=ax, shrink=0.6)
cbar.outline.set_edgecolor('#efefef')
cbar.ax.yaxis.set_tick_params(color='#efefef')

##############################################################################
# Join the zones to a dataframe
# -----------------------------
# The 'binnumber' key gives the zone each event belongs to
# (-1 if outside the pitch), so the zones also work for
# dataframe aggregations beyond plotting.
df['zone'] = stats['binnumber']
df['zone_name'] = df['zone'].map(dict(enumerate(stats['names'])))
df.groupby('zone_name', sort=False).agg(num_pressures=('zone', 'size'),
                                        mean_duration=('duration', 'mean'))

##############################################################################
# Statistics on small samples
# ---------------------------
# The 'count' key is always populated regardless of the requested statistic,
# so you can mask out zones with a small sample in one line.
# Here we plot the mean pressure duration per zone
# and exclude zones with fewer than 50 pressure events.
pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0')
fig, ax = pitch.draw(figsize=(6.6, 4.125))
fig.set_facecolor('#f4edf0')
stats = pitch.bin_statistic_zones(df.x, df.y, regions, names=names,
                                  values=df.duration, statistic='mean')
stats['statistic'][stats['count'] < 50] = np.nan  # mask small samples
pc = pitch.heatmap_zones(stats, ax=ax, cmap=flamingo_cmap, edgecolor='#f9f9f9')
labels = pitch.label_heatmap(stats, color='#f4edf0', fontsize=15,
                             ax=ax, ha='center', va='center', exclude_nan=True,
                             str_format='{:.2f}s', path_effects=path_eff)

plt.show()  # If you are using a Jupyter notebook you do not need this line
