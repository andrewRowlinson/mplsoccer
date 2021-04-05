"""
==============
Pass flow plot
==============

This example shows how to plot the passes from a team as a pass flow plot.
"""

from matplotlib import rcParams
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG

rcParams['text.color'] = '#c7d5cc'  # set the default text color

# get event dataframe for game 7478, create a dataframe of the passes,
# and a boolean mask for the outcome
df = read_event(f'{EVENT_SLUG}/7478.json',
                related_event_df=False, shot_freeze_frame_df=False,
                tactics_lineup_df=False)['event']

##############################################################################
# Boolean mask for filtering the dataset by team

team1, team2 = df.team_name.unique()
mask_team1 = (df.type_name == 'Pass') & (df.team_name == team1)

##############################################################################
# Filter dataset to only include one teams passes and get boolean mask for the completed passes

df_pass = df.loc[mask_team1, ['x', 'y', 'end_x', 'end_y', 'outcome_name']]
mask_complete = df_pass.outcome_name.isnull()

##############################################################################
# Setup the pitch and number of bins
pitch = Pitch(pitch_type='statsbomb',  line_zorder=2, line_color='#c7d5cc', pitch_color='#22312b')
bins = (6, 4)

##############################################################################
# Plotting using a single color and length
fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
# plot the heatmap - darker colors = more passes originating from that square
bs_heatmap = pitch.bin_statistic(df_pass.x, df_pass.y, statistic='count', bins=bins)
hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Blues')
# plot the pass flow map with a single color ('black') and length of the arrow (5)
fm = pitch.flow(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y,
                color='black', arrow_type='same',
                arrow_length=5, bins=bins, ax=ax)
ax.set_title(f'{team1} pass flow map vs {team2}', fontsize=30, pad=-20)
fig.set_facecolor('#22312b')

##############################################################################
# Plotting using a cmap and scaled arrows

fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
# plot the heatmap - darker colors = more passes originating from that square
bs_heatmap = pitch.bin_statistic(df_pass.x, df_pass.y, statistic='count', bins=bins)
hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Reds')
# plot the pass flow map with a custom color map and the arrows scaled by the average pass length
# the longer the arrow the greater the average pass length in the cell
grey = LinearSegmentedColormap.from_list('custom cmap', ['#DADADA', 'black'])
fm = pitch.flow(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y, cmap=grey,
                arrow_type='scale', arrow_length=15, bins=bins, ax=ax)
ax.set_title(f'{team1} pass flow map vs {team2}', fontsize=30, pad=-20)
fig.set_facecolor('#22312b')

##############################################################################
# Plotting with arrow lengths equal to average distance

fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
# plot the heatmap - darker colors = more passes originating from that square
bs_heatmap = pitch.bin_statistic(df_pass.x, df_pass.y, statistic='count', bins=bins)
hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Greens')
# plot the pass flow map with a single color and the
# arrow length equal to the average distance in the cell
fm = pitch.flow(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y, color='black',
                arrow_type='average', bins=bins, ax=ax)
ax.set_title(f'{team1} pass flow map vs {team2}', fontsize=30, pad=-20)
fig.set_facecolor('#22312b')

plt.show()  # If you are using a Jupyter notebook you do not need this line
