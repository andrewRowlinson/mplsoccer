"""
=========================
Heatmap Juego de Posición
=========================

This example shows how to plot all pressure events from three matches as a Juego de Posición heatmap.
See: https://spielverlagerung.com/2014/11/26/juego-de-posicion-a-short-explanation/
"""

from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import os
import pandas as pd
import numpy as np

# get data
match_files = ['19789.json', '19794.json', '19805.json']
kwargs = {'related_event_df': False,'shot_freeze_frame_df': False, 'tactics_lineup_df': False, 'warn': False}
df = pd.concat([read_event(f'{EVENT_SLUG}/{file}', **kwargs)['event'] for file in match_files])
# filter chelsea pressure events
mask_chelsea_pressure = (df.team_name == 'Chelsea FCW') & (df.type_name == 'Pressure')
df = df.loc[mask_chelsea_pressure,['x','y']]

##############################################################################
# Plot the heatmaps

# setup pitch
pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 9), layout = (1,3), line_zorder=2,
              pitch_color= '#22312b', line_color = 'white',orientation='vertical')
# draw
fig, ax = pitch.draw()
positions = ['full','horizontal','vertical']
for i, pos in enumerate(positions):
    bin_statistic = pitch.bin_statistic_positional(df.x, df.y,statistic='count',positional=pos)
    pitch.heatmap_positional(bin_statistic, ax=ax[i], cmap='coolwarm', edgecolors='#22312b')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=ax[i])
    # replace raw counts with percentages and add percentage sign (note immutable named tuple so used _replace)
    for bs in bin_statistic:
        bs['statistic'] = (pd.DataFrame((bs['statistic'] / bs['statistic'].sum()))
                           .applymap(lambda x: '{:.0%}'.format(x))
                           .values)
    pitch.label_heatmap(bin_statistic, color = 'white', fontsize = 18, ax = ax[i], ha = 'center', va = 'bottom')
title = fig.suptitle('Location of pressure events - 3 home games for Chelsea FC Women', x=0.5, y=0.98, fontsize=30,);
