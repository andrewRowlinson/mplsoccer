"""
===================
Customize colormaps
===================

This example shows how to use cmasher colormaps and
also how to make a custom colormap (cmap) in Matplotlib. Colormaps are used to
map from a value to a color in a chart.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import VerticalPitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from mplsoccer.utils import FontManager

# get data
match_files = ['19789.json', '19794.json', '19805.json']
kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False,
          'tactics_lineup_df': False, 'warn': False}
df = pd.concat([read_event(f'{EVENT_SLUG}/{file}', **kwargs)['event'] for file in match_files])
# filter chelsea pressure events
mask_chelsea_pressure = (df.team_name == 'Chelsea FCW') & (df.type_name == 'Pressure')
df = df.loc[mask_chelsea_pressure, ['x', 'y']]

##############################################################################
# Create colormaps using LinearSegmentedColormap
# ----------------------------------------------
# In these examples we will use a list of two colours and the colormaps will
# linearly increase between these two colors (note you can do more such as use 3 colors).
#
# For dark theme backgrounds, I prefer going from dark to light colors. This is so the null values
# which will take the dark background color are not mistaken for high values.
# Likewise, I prefer to go from light to dark colors when using a lighter background.
pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                       ['#15242e', '#4393c4'], N=10)
el_greco_violet_cmap = LinearSegmentedColormap.from_list("El Greco Violet - 10 colors",
                                                         ['#332a49', '#8e78a0'], N=10)
el_greco_yellow_cmap = LinearSegmentedColormap.from_list("El Greco Yellow - 10 colors",
                                                         ['#7c2e2a', '#f2dd44'], N=10)
flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 10 colors",
                                                  ['#e3aca7', '#c03a1d'], N=10)
# same color maps but with 100 colors
pearl_earring_cmap_100 = LinearSegmentedColormap.from_list("Pearl Earring - 100 colors",
                                                           ['#15242e', '#4393c4'], N=100)
el_greco_violet_cmap_100 = LinearSegmentedColormap.from_list("El Greco Violet - 100 colors",
                                                             ['#3b3154', '#8e78a0'], N=100)
el_greco_yellow_cmap_100 = LinearSegmentedColormap.from_list("El Greco Yellow - 100 colors",
                                                             ['#7c2e2a', '#f2dd44'], N=100)
flamingo_cmap_100 = LinearSegmentedColormap.from_list("Flamingo - 100 colors",
                                                      ['#e3aca7', '#c03a1d'], N=100)

##############################################################################
# Show the colormaps
# ------------------
#
# The below colormaps are inspired by art and nature: Girl with a Pearl by Johannes Vermeer,
# The Disrobing of Christ by El Greco, and flamingos.
#
# With heatmaps and hexbins, I prefer to use fewer colors (N=10)
# so the values are mapped to fewer colors.
# While for smoother heatmaps when using kdeplot go for more colors (e.g. N=100).
fig, axes = plt.subplots(figsize=(12, 5), nrows=8, ncols=2, constrained_layout=True)
gradient = np.linspace(0, 1, 256)
gradient = np.repeat(np.expand_dims(gradient, axis=0), repeats=10, axis=0)
cmaps = [pearl_earring_cmap, flamingo_cmap,
         el_greco_violet_cmap, el_greco_yellow_cmap,
         pearl_earring_cmap_100, flamingo_cmap_100,
         el_greco_violet_cmap_100, el_greco_yellow_cmap_100]
fm = FontManager()
for i, cmap in enumerate(cmaps):
    axes[i, 0].axis('off')
    axes[i, 1].axis('off')
    axes[i, 0].imshow(gradient, cmap=cmap)
    axes[i, 1].text(0, 0.5, cmap.name, va='center', fontsize=20, fontproperties=fm.prop)

##############################################################################
# Cyan colormap heatmap
pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#122c3d')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
bs = pitch.bin_statistic(df.x, df.y, bins=(12, 8))
heatmap = pitch.heatmap(bs, edgecolors='#122c3d', ax=ax, cmap=pearl_earring_cmap)

##############################################################################
# Cyan colormap hexbin
fig, ax = pitch.draw()
hexmap = pitch.hexbin(df.x, df.y, ax=ax, edgecolors='#122c3d', gridsize=(8, 8),
                      cmap=pearl_earring_cmap)

##############################################################################
# Cyan colormap kdeplot
pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#15242e')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
# note use the colormap with 100 colors for a smoother finish
# sphinx_gallery_thumbnail_path = 'gallery/pitch_plots/images/sphx_glr_plot_cmap_004.png'
kdeplot = pitch.kdeplot(df.x, df.y, ax=ax, cmap=pearl_earring_cmap_100, shade=True, levels=100)

##############################################################################
# Flamingo colormap heatmap
pitch = VerticalPitch(line_color='#000009', line_zorder=2, pitch_color='white')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
bs = pitch.bin_statistic(df.x, df.y, bins=(12, 8))
heatmap = pitch.heatmap(bs, ax=ax, edgecolors='#f4f4f4', cmap=flamingo_cmap)

##############################################################################
# Flamingo colormap hexbin
fig, ax = pitch.draw()
hexmap = pitch.hexbin(df.x, df.y, ax=ax, edgecolors='#f4f4f4', gridsize=(8, 8), cmap=flamingo_cmap)

##############################################################################
# Flamingo colormap kdeplot
pitch = VerticalPitch(line_color='#000009', line_zorder=2, pitch_color='#e3aca7')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
kdeplot = pitch.kdeplot(df.x, df.y, ax=ax, cmap=flamingo_cmap_100, shade=True, levels=100)

##############################################################################
# Violet colormap heatmap
pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#20143f')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
bs = pitch.bin_statistic(df.x, df.y, bins=(12, 8))
heatmap = pitch.heatmap(bs, ax=ax, edgecolors='#20143f', cmap=el_greco_violet_cmap)

##############################################################################
# Violet colormap hexbin
fig, ax = pitch.draw()
hexbin = pitch.hexbin(df.x, df.y, ax=ax, edgecolors='#20143f',
                      gridsize=(8, 8), cmap=el_greco_violet_cmap)

##############################################################################
# Violet colormap kdeplot
pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#332a49')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
kdeplot = pitch.kdeplot(df.x, df.y, ax=ax, cmap=el_greco_violet_cmap_100, shade=True, levels=100)

##############################################################################
# Yellow colormap heatmap
pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#471c15')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
bs = pitch.bin_statistic(df.x, df.y, bins=(12, 8))
heatmap = pitch.heatmap(bs, ax=ax, edgecolors='#471c15', cmap=el_greco_yellow_cmap)

##############################################################################
# Yellow colormap hexbin
fig, ax = pitch.draw()
hexbin = pitch.hexbin(df.x, df.y, ax=ax, edgecolors='#443d07',
                      gridsize=(8, 8), cmap=el_greco_yellow_cmap)

##############################################################################
# Yellow colormap kdeplot
pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#7c2e2a')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
kdeplot = pitch.kdeplot(df.x, df.y, ax=ax, cmap=el_greco_yellow_cmap_100, shade=True, levels=100)
