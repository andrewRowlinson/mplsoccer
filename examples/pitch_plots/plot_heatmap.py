"""
=======
Heatmap
=======

This example shows how to plot all pressure events from three matches as a heatmap.
"""

import pandas as pd
import matplotlib.pyplot as plt

from mplsoccer import VerticalPitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG

# get data
match_files = ['19789.json', '19794.json', '19805.json']
kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False,
          'tactics_lineup_df': False, 'warn': False}
df = pd.concat([read_event(f'{EVENT_SLUG}/{file}', **kwargs)['event'] for file in match_files])
# filter chelsea pressure events
mask_chelsea_pressure = (df.team_name == 'Chelsea FCW') & (df.type_name == 'Pressure')
df = df.loc[mask_chelsea_pressure, ['x', 'y']]

##############################################################################
# Plot the heatmaps

# setup pitch
pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2,
                      pitch_color='#22312b', line_color='white')
# draw
fig, ax = pitch.draw(figsize=(16, 9), ncols=3, nrows=1,)
# heatmap specified by (nx, ny) for horizontal pitch
bins = [(6, 5), (1, 5), (6, 1)]
for i, bin_dimension in enumerate(bins):
    bin_statistic = pitch.bin_statistic(df.x, df.y, statistic='count', bins=bin_dimension)
    # draw
    pitch.heatmap(bin_statistic, ax=ax[i], cmap='coolwarm', edgecolors='#22312b')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=ax[i])
    # replace raw counts with percentages and add percentage sign
    # (note immutable named tuple so used _replace)
    bin_statistic['statistic'] = ((pd.DataFrame((bin_statistic['statistic'] /
                                                 bin_statistic['statistic'].sum())))
                                  .applymap(lambda x: '{:.0%}'.format(x))
                                  .values)
    pitch.label_heatmap(bin_statistic, color='white', fontsize=18,
                        ax=ax[i], ha='center', va='bottom')
TITLE_STR = 'Location of pressure events - 3 home games for Chelsea FC Women'
title = fig.suptitle(TITLE_STR, x=0.5, y=0.98, fontsize=30)

plt.show()  # If you are using a Jupyter notebook you do not need this line
