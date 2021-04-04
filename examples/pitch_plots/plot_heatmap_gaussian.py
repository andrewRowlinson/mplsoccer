"""
================
Heatmap smoothed
================

Tom Decroos, author of matplotsoccer (https://github.com/TomDecroos/matplotsoccer),
asked whether it was possible to plot a Gaussian smoothed heatmaps,
which are available in matplotsoccer.
Here is an example demonstrating this.
"""

import matplotlib.pyplot as plt
import pandas as pd
from scipy.ndimage import gaussian_filter

from mplsoccer import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG

plt.style.use('dark_background')

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
pitch = Pitch(pitch_type='statsbomb', line_zorder=2, line_color='white')
# draw
fig, ax = pitch.draw(figsize=(16, 9))
bin_statistic = pitch.bin_statistic(df.x, df.y, statistic='count', bins=(25, 25))
bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')
cbar = fig.colorbar(pcm, ax=ax)
TITLE_STR = 'Location of pressure events - 3 home games for Chelsea FC Women'
title = fig.suptitle(TITLE_STR, x=0.4, y=0.98, fontsize=23)

plt.show()  # If you are using a Jupyter notebook you do not need this line
