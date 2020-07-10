"""
==============
Pass flow plot
==============

This example shows how to plot the passes from a team as a pass flow plot.
"""

from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from matplotlib import rcParams
from scipy.stats import circmean
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')

rcParams['text.color'] = '#c7d5cc'  # set the default text color

# get event dataframe for game 7478, create a dataframe of the passes, and a boolean mask for the outcome
df = read_event(f'{EVENT_SLUG}/7478.json',
                related_event_df=False, shot_freeze_frame_df=False, tactics_lineup_df=False)['event']

##############################################################################
# Boolean mask for filtering the dataset by team

team1, team2 = df.team_name.unique()
mask_team1 = (df.type_name == 'Pass') & (df.team_name == team1)

##############################################################################
# Filter dataset to only include one teams passes and get boolean mask for the completed passes

df_pass = df.loc[mask_team1, ['x', 'y', 'end_x', 'end_y', 'outcome_name']]
mask_complete = df_pass.outcome_name.isnull()

##############################################################################
# Plotting

# Setup the pitch
pitch = Pitch(pitch_type='statsbomb', orientation='horizontal', figsize=(16, 11), line_zorder=2,
              line_color='#c7d5cc', constrained_layout=True, tight_layout=False)
fig, ax = pitch.draw()

# plot the heatmap - darker colors = more passes originating from that square
bs_heatmap = pitch.bin_statistic(df_pass.x, df_pass.y, statistic='count', bins=(6, 4))
hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Blues')

# calculate the angle of the passes
angle = pitch.calculate_angle(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y)  
# calculate the average angle for each grid cell using the circmean.
bs = pitch.bin_statistic(x=df_pass.x, y=df_pass.y, values=angle, statistic=circmean, bins=(6, 4))
# plot the pass flow arrows with a common length (d).
d = 3
endx = bs['cx'] + (np.cos(bs['statistic']) * d) # calculate the endx position of the arrow
endy = bs['cy'] - (np.sin(bs['statistic']) * d) # calculate the endy position of the arrow
flow = pitch.arrows(bs['cx'], bs['cy'], endx, endy, ax=ax, zorder=3)
