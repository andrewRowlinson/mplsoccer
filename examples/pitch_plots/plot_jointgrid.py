"""
=========
Jointgrid
=========

Inspired by the Seaborn jointgrid and `@n_mondon <https://twitter.com/n_mondon>`_ charts,
jointgrid gives a handy way to put marginal axis on each side of the pitch.
"""

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.cm import get_cmap

from mplsoccer import Pitch, VerticalPitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from mplsoccer.utils import FontManager

# get data for a Sevilla versus Barcelona match with a high amount of shots
kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False,
          'tactics_lineup_df': False, 'warn': False}
df = read_event(f'{EVENT_SLUG}/9860.json', **kwargs)['event']

# setup the mplsoccer StatsBomb Pitches
# note not much padding around the pitch so the marginal axis are tight to the pitch
# if you are using a different goal type you will need to increase the padding to see the goals
pitch = Pitch(figsize=(16, 9), pad_top=0.05, pad_right=0.05, pad_bottom=0.05,
              pad_left=0.05, line_zorder=2)
vertical_pitch = VerticalPitch(figsize=(16, 9), half=True,
                               pad_top=0.05, pad_right=0.05, pad_bottom=0.05,
                               pad_left=0.05, line_zorder=2)

# setup a mplsoccer FontManager to download google fonts (Roboto-Regular / SigmarOne-Regular)
fm = FontManager()
fm_rubik = FontManager(('https://github.com/google/fonts/blob/master/ofl/rubikmonoone/'
                        'RubikMonoOne-Regular.ttf?raw=true'))

##############################################################################
# Subset the shots for each team and move Barcelona's shots to the other side of the pitch.

# subset the shots
df_shots = df[df.type_name == 'Shot'].copy()

# subset the shots for each team
team1, team2 = df_shots.team_name.unique()
df_team1 = df_shots[df_shots.team_name == team1].copy()
df_team2 = df_shots[df_shots.team_name == team2].copy()

# Usually in football, the data is collected so the attacking direction is left to right.
# We can shift the coordinates via: new_x_coordinate = right_side - old_x_coordinate
# This is helpful for having one team shots on the left of the pitch and the other on the right
df_team1['x'] = pitch.dim.right - df_team1.x

##############################################################################
# Plotting a standard shot map with step charts
# ---------------------------------------------

fig, axes = pitch.jointgrid(left=0.15,  # pitch axis starts 15% in from the side of the figure
                            bottom=0.075,  # pitch axis starts 7.5% in from the side of the figure
                            marginal_height=0.1,  # marginal axes heights are 10% of figure height
                            space_height=0,  # 0% space between the pitch and the marginal axes
                            pitch_height=0.8)  # the pitch width takes up 80% of the figure height
# we plot a usual scatter plot but the scatter size is based on expected goals
# note that the size is the expected goals * 700
# so any shots with an expected goals = 1 would take a size of 700 (points**2)
sc_team1 = pitch.scatter(df_team1.x, df_team1.y, s=df_team1.shot_statsbomb_xg * 700,
                         ec='black', color='#ba495c', ax=axes[0])
sc_team2 = pitch.scatter(df_team2.x, df_team2.y, s=df_team1.shot_statsbomb_xg * 700,
                         ec='black', color='#697cd4', ax=axes[0])
# (step) histograms on each of the left, top, and right marginal axes
team1_hist_y = sns.histplot(y=df_team1.y, ax=axes[1], element='step', color='#ba495c')
team1_hist_x = sns.histplot(x=df_team1.x, ax=axes[2], element='step', color='#ba495c')
team2_hist_x = sns.histplot(x=df_team2.x, ax=axes[2], element='step', color='#697cd4')
team2_hist_y = sns.histplot(y=df_team2.y, ax=axes[3], element='step', color='#697cd4')
txt1 = axes[0].text(x=15, y=70, s=team1, fontproperties=fm.prop, color='#ba495c',
                    ha='center', va='center', fontsize=30)
txt2 = axes[0].text(x=105, y=70, s=team2, fontproperties=fm.prop, color='#697cd4',
                    ha='center', va='center', fontsize=30)
_ = axes[1].axis('off')
_ = axes[2].axis('off')
_ = axes[3].axis('off')

##############################################################################
# Plotting a standard shot map with rug plots
# -------------------------------------------

# increased the size of the pitch_height and decreased the marginal height
# as rug plots are only lines, we don't need as much space taken up by the marginal axes
fig, axes = pitch.jointgrid(left=0.15, bottom=0.075, pitch_height=0.8, marginal_height=0.02)
sc_team1 = pitch.scatter(df_team1.x, df_team1.y, s=df_team1.shot_statsbomb_xg * 700,
                         ec='black', color='#ba495c', ax=axes[0])
sc_team2 = pitch.scatter(df_team2.x, df_team2.y, s=df_team1.shot_statsbomb_xg * 700,
                         ec='black', color='#697cd4', ax=axes[0])
# note height=1 means that the whole of the marginal axes are taken up by the rugplots
team1_rug_y = sns.rugplot(y=df_team1.y, ax=axes[1], color='#ba495c', height=1)
team1_rug_y = sns.rugplot(y=df_team2.y, ax=axes[3], color='#697cd4', height=1)
team1_rug_x = sns.rugplot(x=df_team1.x, ax=axes[2], color='#ba495c', height=1)
team2_rug_x = sns.rugplot(x=df_team2.x, ax=axes[2], color='#697cd4', height=1)
txt1 = axes[0].text(x=15, y=70, s=team1, fontproperties=fm.prop, color='#ba495c',
                    ha='center', va='center', fontsize=30)
txt2 = axes[0].text(x=105, y=70, s=team2, fontproperties=fm.prop, color='#697cd4',
                    ha='center', va='center', fontsize=30)
_ = axes[1].axis('off')
_ = axes[2].axis('off')
_ = axes[3].axis('off')

##############################################################################
# Get more shot data for additional games

# sevilla versus barcelona 2014/2015 to 2019/2020
sevilla_games = ['265835.json', '266142.json', '265839.json', '266989.json', '266280.json',
                 '9673.json', '9860.json', '16029.json', '16190.json', '303473.json', '303674.json']
df_list = [read_event(f'{EVENT_SLUG}/{file}', **kwargs)['event'] for file in sevilla_games]

df = pd.concat(df_list)

# subset the shots
df_shots = df[df.type_name == 'Shot'].copy()

# subset the shots for each team
team1, team2 = df_shots.team_name.unique()
df_team1 = df_shots[df_shots.team_name == team1].copy()
df_team2 = df_shots[df_shots.team_name == team2].copy()

# move the team1 coordinate to the left hand side
df_team1['x'] = pitch.dim.right - df_team1.x

##############################################################################
# Get colors
# We are using Reds and Blues colormaps below and select a color just over half
# way (60%) through the colormap for use in the charts.

red = get_cmap('Reds')(np.linspace(0, 1, 100))[60]
blue = get_cmap('Blues')(np.linspace(0, 1, 100))[60]

##############################################################################
# Hexbin shot map with kdeplot marginal axes
# ------------------------------------------

fig, axes = pitch.jointgrid(left=0.15, bottom=0.075, pitch_height=0.8)
# plot the hexbins
hex1 = pitch.hexbin(df_team1.x, df_team1.y, ax=axes[0], edgecolors=pitch.line_color, cmap='Reds')
hex2 = pitch.hexbin(df_team2.x, df_team2.y, ax=axes[0], edgecolors=pitch.line_color, cmap='Blues')
# normalize the values so the colors depend on the minimum/ value for both teams
# this ensures that darker colors mean more shots relative to both teams
vmin = min(hex1.get_array().min(), hex2.get_array().min())
vmax = max(hex1.get_array().max(), hex2.get_array().max())
hex1.set_clim(vmin=vmin, vmax=vmax)
hex2.set_clim(vmin=vmin, vmax=vmax)
# plot kdeplots on the marginals
team1_hist_y = sns.kdeplot(y=df_team1.y, ax=axes[1], color=red, shade=True)
team1_hist_x = sns.kdeplot(x=df_team1.x, ax=axes[2], color=red, shade=True)
team2_hist_x = sns.kdeplot(x=df_team2.x, ax=axes[2], color=blue, shade=True)
team2_hist_y = sns.kdeplot(y=df_team2.y, ax=axes[3], color=blue, shade=True)
txt1 = axes[0].text(x=15, y=70, s=team1, fontproperties=fm.prop, color=red,
                    ha='center', va='center', fontsize=30)
txt2 = axes[0].text(x=105, y=70, s=team2, fontproperties=fm.prop, color=blue,
                    ha='center', va='center', fontsize=30)
_ = axes[1].axis('off')
_ = axes[2].axis('off')
_ = axes[3].axis('off')

##############################################################################
# Heatmap shot map with histogram/ kdeplot on the marginal axes
# -------------------------------------------------------------

fig, axes = pitch.jointgrid(left=0.15, bottom=0.075, pitch_height=0.8)
bs1 = pitch.bin_statistic(df_team1.x, df_team1.y, bins=(18, 12))
bs2 = pitch.bin_statistic(df_team2.x, df_team2.y, bins=(18, 12))
# get the min/ max values for normalizing across both teams
vmax = max(bs2['statistic'].max(), bs1['statistic'].max())
vmin = max(bs2['statistic'].min(), bs1['statistic'].min())
# set values where zero shots to nan values so it does not show up in the heatmap
# i.e. zero values take the background color
bs1['statistic'][bs1['statistic'] == 0] = np.nan
bs2['statistic'][bs2['statistic'] == 0] = np.nan
# set the vmin/ vmax so the colors depend on the minimum/maximum value for both teams
hm1 = pitch.heatmap(bs1, ax=axes[0], cmap='Reds', vmin=vmin, vmax=vmax, edgecolor='#f9f9f9')
hm2 = pitch.heatmap(bs2, ax=axes[0], cmap='Blues', vmin=vmin, vmax=vmax, edgecolor='#f9f9f9')
# histograms with kdeplot
team1_hist_y = sns.histplot(y=df_team1.y, ax=axes[1], color=red, linewidth=1, kde=True)
team1_hist_x = sns.histplot(x=df_team1.x, ax=axes[2], color=red, linewidth=1, kde=True)
team2_hist_x = sns.histplot(x=df_team2.x, ax=axes[2], color=blue, linewidth=1, kde=True)
team2_hist_y = sns.histplot(y=df_team2.y, ax=axes[3], color=blue, linewidth=1, kde=True)
txt1 = axes[0].text(x=15, y=70, s=team1, fontproperties=fm.prop, color=red,
                    ha='center', va='center', fontsize=30)
txt2 = axes[0].text(x=105, y=70, s=team2, fontproperties=fm.prop, color=blue,
                    ha='center', va='center', fontsize=30)
_ = axes[1].axis('off')
_ = axes[2].axis('off')
_ = axes[3].axis('off')

##############################################################################
# Kdeplot shot map with kdeplot on the marginal axes
# --------------------------------------------------

fig, axes = pitch.jointgrid(left=0.15, bottom=0.075, pitch_height=0.8)
# increase number of levels for a smoother looking heatmap
kde1 = pitch.kdeplot(df_team1.x, df_team1.y, ax=axes[0], cmap='Reds', levels=75, shade=True)
kde2 = pitch.kdeplot(df_team2.x, df_team2.y, ax=axes[0], cmap='Blues', levels=75, shade=True)
# kdeplot on marginal axes
team1_hist_y = sns.kdeplot(y=df_team1.y, ax=axes[1], color=red, shade=True)
team1_hist_x = sns.kdeplot(x=df_team1.x, ax=axes[2], color=red, shade=True)
team2_hist_x = sns.kdeplot(x=df_team2.x, ax=axes[2], color=blue, shade=True)
team2_hist_y = sns.kdeplot(y=df_team2.y, ax=axes[3], color=blue, shade=True)
txt1 = axes[0].text(x=15, y=70, s=team1, fontproperties=fm.prop, color=red,
                    ha='center', va='center', fontsize=30)
txt2 = axes[0].text(x=105, y=70, s=team2, fontproperties=fm.prop, color=blue,
                    ha='center', va='center', fontsize=30)
_ = axes[1].axis('off')
_ = axes[2].axis('off')
_ = axes[3].axis('off')

##############################################################################
# Vertical shot map with kdeplot marginals
# ----------------------------------------
# The jointgrid is flexible. You can filter the marginal axes with
# ax_left, ax_top, ax_left, ax_right. Here we set the bottom and right
# marginal axes to display for a single team.

# we leave enough room here for the bottom marginal axes
# the pitch starts at 15% of the figure height. The bottom marginal axes is 10% of the figure height
# therefore 5% of the figure height is left as a margin at the bottom of the plot
fig, axes = vertical_pitch.jointgrid(left=0.2, bottom=0.15, pitch_height=0.8, marginal_height=0.1,
                                     # here we filter out the left and top marginal axes
                                     ax_top=False, ax_bottom=True, ax_left=False, ax_right=True)
# typical shot map where the scatter points vary by the expected goals value
# using alpha for transparency as there are a lot of shots stacked around the six-yard box
sc_team2 = vertical_pitch.scatter(df_team2.x, df_team2.y, s=df_team2.shot_statsbomb_xg * 700,
                                  alpha=0.5, ec='black', color='#697cd4', ax=axes[0])
# kdeplots on the marginals
# remember to flip the coordinates y=x, x=y for the marginals when using vertical orientation
team2_hist_x = sns.kdeplot(y=df_team2.x, ax=axes[3], color='#697cd4', shade=True)
team2_hist_y = sns.kdeplot(x=df_team2.y, ax=axes[4], color='#697cd4', shade=True)
txt1 = axes[0].text(x=40, y=80, s=team2, fontproperties=fm_rubik.prop, color=pitch.line_color,
                    ha='center', va='center', fontsize=60)
_ = axes[3].axis('off')
_ = axes[4].axis('off')

##############################################################################
# Crop the pitch
# --------------
# The jointgrid also works with arbritary padding.
# So you can crop the pitc and still have the marginal axes to plot on.

vertical_pitch = VerticalPitch(figsize=(16, 9), half=True,
                               # here we remove some of the pitch on the left/ right/ bottom
                               pad_top=0.05, pad_right=-15, pad_bottom=-20, pad_left=-15,
                               goal_type='line')

# we leave enough room here for the bottom marginal axes
# the pitch starts at 15% of the figure height. The bottom marginal axes is 10% of the figure height
# therefore 5% of the figure height is left as a margin at the bottom of the plot
fig, axes = vertical_pitch.jointgrid(left=0.2, bottom=0.15, pitch_height=0.8, marginal_height=0.1,
                                     # here we filter out the left and top marginal axes
                                     ax_top=False, ax_bottom=True, ax_left=False, ax_right=True)
# typical shot map where the scatter points vary by the expected goals value
# using alpha for transparency as there are a lot of shots stacked around the six-yard box
sc_team2 = vertical_pitch.scatter(df_team2.x, df_team2.y, s=df_team2.shot_statsbomb_xg * 700,
                                  alpha=0.5, ec='black', color='#697cd4', ax=axes[0])
# kdeplots on the marginals
# remember to flip the coordinates y=x, x=y for the marginals when using vertical orientation
team2_hist_x = sns.kdeplot(y=df_team2.x, ax=axes[3], color='#697cd4', shade=True)
team2_hist_y = sns.kdeplot(x=df_team2.y, ax=axes[4], color='#697cd4', shade=True)
txt1 = axes[0].text(x=40, y=85, s=team2, fontproperties=fm_rubik.prop, color=pitch.line_color,
                    ha='center', va='center', fontsize=60)
_ = axes[3].axis('off')
_ = axes[4].axis('off')
