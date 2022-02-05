"""
==============
Turbine Charts
==============

Here we jazz up radar charts by putting the distributions inside the
radar chart. You can mix and match the various elements of the Radar
class to create your own version.

Each blade of the turbine represents the statistics for the skill.
While the blade is split at the point of the individual player's skill level.

If you like this idea give `Soumyajit Bose <https://twitter.com/Soumyaj15209314>`_ a follow
on Twitter, as I borrowed some of his ideas for this chart.
"""
import pandas as pd
from mplsoccer import Radar, FontManager
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

##############################################################################
# Creating some random data
# -------------------------
# Here we create some random data from a truncated normal distribution
lower, upper, mu, sigma = 0, 1, 0.35, 0.25
X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
# for 1000 people and 11 skills
values = X.rvs((1000, 11))
# the names of the skills
params = ['Expected goals', 'Total shots',
          'Touches in attacking penalty area', 'Pass completion %',
          'Crosses into the 18-yard box (excluding set pieces)',
          'Expected goals assisted', 'Fouls drawn', 'Successful dribbles',
          'Successful pressures', 'Non-penalty expected goals per shot',
          'Miscontrols/ Dispossessed']
# set up a dataframe with the random values
df = pd.DataFrame(values)
df.columns = params
# in real-life you'd probably have a string column for the player name
# but we will use numbers here
df['player_name'] = np.arange(1000)

##############################################################################
# Instantiate the Radar Class
# ---------------------------
# We will instantiate a radar object and set the lower and upper bounds.

# create the radar object with an upper and lower bound of the 5% and 95% quantiles
low = df[params].quantile(0.05).values
high = df[params].quantile(0.95).values
radar = Radar(params, low, high, num_rings=4)

##############################################################################
# Load a font
# -----------
# We will use mplsoccer's FontManager to load the default Robotto font.
fm = FontManager()

##############################################################################
# Making a Simple Turbine Chart
# -----------------------------
# Here we will make a very simple turbine chart using the ``radar_chart`` module.

# get the player's values (usually the 23 would be a string)
# so for example you might put
# df.loc[df.player_name == 'Martin Ødegaard', params].values[0].tolist()
player_values = df.loc[df.player_name == 23, params].values[0]

# plot the turbine plot
fig, ax = radar.setup_axis()  # format axis as a radar
# plot the turbine blades. Here we give the player_Values and the
# value for all players shape=(1000, 11)
turbine_output = radar.turbine(player_values, df[params].values, ax=ax,
                               kwargs_inner={'edgecolor': 'black'},
                               kwargs_inner_gradient={'cmap': 'Blues'},
                               kwargs_outer={'facecolor': '#b2b2b2', 'edgecolor': 'black'})
# plot some dashed rings and the labels for the values and parameter names
rings_inner = radar.draw_circles(ax=ax, facecolor='None', edgecolor='black', linestyle='--')
range_labels = radar.draw_range_labels(ax=ax, fontsize=15, fontproperties=fm.prop, zorder=2)
param_labels = radar.draw_param_labels(ax=ax, fontsize=15, fontproperties=fm.prop, zorder=2)

##############################################################################
# Sub Plot Mosaic
# ---------------
# Here we create a function to plot a radar flanked with a title and an endnote axes.


def radar_mosaic(radar_height=0.915, title_height=0.06, figheight=14):
    """ Create a Radar chart flanked by a title and endnote axes.

    Parameters
    ----------
    radar_height: float, default 0.915
        The height of the radar axes in fractions of the figure height (default 91.5%).
    title_height: float, default 0.06
        The height of the title axes in fractions of the figure height (default 6%).
    figheight: float, default 14
        The figure height in inches.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axs : dict[label, Axes]
    """
    if title_height + radar_height > 1:
        error_msg = 'Reduce one of the radar_height or title_height so the total is ≤ 1.'
        raise ValueError(error_msg)
    endnote_height = 1 - title_height - radar_height
    figwidth = figheight * radar_height
    figure, axes = plt.subplot_mosaic([['title'], ['radar'], ['endnote']],
                                      gridspec_kw={'height_ratios': [title_height, radar_height,
                                                                     endnote_height],
                                                   # the grid takes up the whole of the figure 0-1
                                                   'bottom': 0, 'left': 0, 'top': 1,
                                                   'right': 1, 'hspace': 0},
                                      figsize=(figwidth, figheight))
    axes['title'].axis('off')
    axes['endnote'].axis('off')
    return figure, axes


##############################################################################
# Adding a title and endnote
# --------------------------
# Here we will add an endnote and title to the Radar. We will use a subplot_mosaic to create
# the figure and pass the axs['radar'] axes to the Radar's methods.

# creating the figure using the function defined above:
fig, axs = radar_mosaic(radar_height=0.915, title_height=0.06, figheight=14)

# plot the turbine plot
radar.setup_axis(ax=axs['radar'])
# plot the turbine blades. Here we give the player_Values and
# the value for all players shape=(1000, 11)
turbine_output = radar.turbine(player_values, df[params].values, ax=axs['radar'],
                               kwargs_inner={'edgecolor': 'black'},
                               kwargs_inner_gradient={'cmap': 'plasma'},
                               kwargs_outer={'facecolor': '#b2b2b2', 'edgecolor': 'black'})
# plot some dashed rings and the labels for the values and parameter names
rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='None',
                                 edgecolor='black', linestyle='--')
range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=15,
                                       fontproperties=fm.prop, zorder=2)
param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=15,
                                       fontproperties=fm.prop, zorder=2)

# adding a title and endnote
title1_text = axs['title'].text(0.01, 0.65, 'Random player', fontsize=25,
                                fontproperties=fm.prop, ha='left', va='center')
title2_text = axs['title'].text(0.01, 0.25, 'Team', fontsize=20,
                                fontproperties=fm.prop,
                                ha='left', va='center', color='#B6282F')
title3_text = axs['title'].text(0.99, 0.65, 'Turbine Chart', fontsize=25,
                                fontproperties=fm.prop, ha='right', va='center')
title4_text = axs['title'].text(0.99, 0.25, 'Position', fontsize=20,
                                fontproperties=fm.prop,
                                ha='right', va='center', color='#B6282F')
endnote_text = axs['endnote'].text(0.99, 0.5, 'Inspired By StatsBomb', fontsize=15,
                                   fontproperties=fm.prop, ha='right', va='center')

plt.show()  # not needed in Jupyter notebooks
