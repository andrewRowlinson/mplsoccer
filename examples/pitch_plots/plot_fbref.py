"""
==============
FBRef Pressure
==============

This example shows how to scrape pressure events from FBRef.com and plot them as a heatmap.
"""
from urllib.request import urlopen

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from mplsoccer import Pitch, add_image

##############################################################################
# Scrape the data via a link to a specific table.
# To get the link for a different league,
# find the table you want from the website. Then click "Share & more" and copy the link from
# the option "Modify & Share Table". Then "click url for sharing" and get the table as a url.
URL = 'https://fbref.com/en/share/eDK2O'
df = pd.read_html(URL)[0]
# select a subset of the columns (Squad and pressure columns)
df = df[['Unnamed: 0_level_0', 'Pressures']].copy()
df.columns = df.columns.droplevel()  # drop the top-level of the multi-index

##############################################################################
# Get the league average percentages
pressure_cols = ['Def 3rd', 'Mid 3rd', 'Att 3rd']
df_total = pd.DataFrame(df[pressure_cols].sum())
df_total.columns = ['total']
df_total = df_total.T
df_total = df_total.divide(df_total.sum(axis=1), axis=0) * 100

##############################################################################
# Calculate the percentages for each team and sort so that the teams which press higher are last
df[pressure_cols] = df[pressure_cols].divide(df[pressure_cols].sum(axis=1), axis=0) * 100.
df.sort_values(['Att 3rd', 'Def 3rd'], ascending=[True, False], inplace=True)

##############################################################################
# Plot the percentages

# setup a mplsoccer pitch
pitch = Pitch(line_zorder=2, line_color='black')

# mplsoccer calculates the binned statistics usually from raw locations, such as pressure events
# for this example we will create a binned statistic dividing
# the pitch into thirds for one point (0, 0)
# we will fill this in a loop later with each team's statistics from the dataframe
bin_statistic = pitch.bin_statistic([0], [0], statistic='count', bins=(3, 1))

# Plot
fig, axes = pitch.draw(figsize=(16, 9), ncols=5, nrows=4,
                       tight_layout=False, constrained_layout=True)
axes = axes.ravel()
teams = df['Squad'].values
vmin = df[pressure_cols].min().min()  # we normalise the heatmaps with the min / max values
vmax = df[pressure_cols].max().max()
for i, ax in enumerate(axes[:len(teams)]):
    ax.set_title(teams[i], fontsize=20)
    # fill in the bin statistics from df and plot the heatmap
    bin_statistic['statistic'] = df.loc[df.Squad == teams[i], pressure_cols].values
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax)
    # format and plot labels
    bin_statistic['statistic'] = (pd.DataFrame(bin_statistic['statistic'])
                                  .round(0)
                                  .astype(np.int32)
                                  .applymap(lambda x: '{:d}%'.format(x)).values)
    annotate = pitch.label_heatmap(bin_statistic, color='white',
                                   fontsize=20, ax=ax, ha='center', va='center')
    # set a black path effect around the labels
    for label in annotate:
        label.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'),
                                path_effects.Normal()])
axes = axes.reshape(4, 5)
cbar = fig.colorbar(heatmap, ax=axes[:, 4], shrink=0.85)
cbar.ax.tick_params(labelsize=20)
# if its the Bundesliga remove the two spare pitches
if len(teams) == 18:
    for ax in axes[-1, 3:]:
        ax.remove()
# load the StatsBomb logo and add it to the plot
LOGO_URL = 'https://raw.githubusercontent.com/statsbomb/open-data/master/img/statsbomb-logo.jpg'
sb_logo = Image.open(urlopen(LOGO_URL))
add_image(sb_logo, fig, left=0.9, bottom=0.975, width=0.1)
title = fig.suptitle('Pressure events %, Bundesliga, 2019/20', fontsize=20)

##############################################################################
# Plot the percentage point difference

# Calculate the percentage point difference from the league average
df[pressure_cols] = df[pressure_cols].values - df_total.values

# plot the percentage point difference
pitch = Pitch(line_zorder=2, line_color='black')
fig, axes = pitch.draw(figsize=(16, 9), ncols=5, nrows=4,
                       tight_layout=False, constrained_layout=True)
axes = axes.ravel()
teams = df['Squad'].values
vmin = df[pressure_cols].min().min()
vmax = df[pressure_cols].max().max()
for i, ax in enumerate(axes[:len(teams)]):
    ax.set_title(teams[i], fontsize=20)
    bin_statistic['statistic'] = df.loc[df.Squad == teams[i], pressure_cols].values
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax)
    bin_statistic['statistic'] = (pd.DataFrame(bin_statistic['statistic'])
                                  .round(0)
                                  .astype(np.int32))
    annotate = pitch.label_heatmap(bin_statistic, color='white',
                                   fontsize=30, ax=ax, ha='center', va='center')
    for label in annotate:
        label.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'),
                                path_effects.Normal()])
axes = axes.reshape(4, 5)
cbar = fig.colorbar(heatmap, ax=axes[:, 4], shrink=0.85, format='%d')
cbar.ax.tick_params(labelsize=20)
# if its the Bundesliga remove the two spare pitches
if len(teams) == 18:
    for ax in axes[-1, 3:]:
        ax.remove()
# load the StatsBomb logo and add it to the plot
sb_logo = Image.open(urlopen(LOGO_URL))
add_image(sb_logo, fig, left=0.9, bottom=0.975, width=0.1)
TITLE_STR = 'Pressure events, percentage point difference from the Bundesliga average 2019/20'
title = fig.suptitle(TITLE_STR, fontsize=20)

plt.show()  # If you are using a Jupyter notebook you do not need this line
