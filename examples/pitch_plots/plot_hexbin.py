"""
===========
Hexbin plot
===========

This example shows how to plot the location of events occurring in a match
 using hexbins.
"""

import matplotlib.pyplot as plt

from mplsoccer import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG

##############################################################################
# load first game that Messi played as a false-9 and the match before
kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False,
          'tactics_lineup_df': False, 'warn': False}
df_false9 = read_event(f'{EVENT_SLUG}/69249.json', **kwargs)['event']
df_before_false9 = read_event(f'{EVENT_SLUG}/69251.json', **kwargs)['event']
# filter messi's actions (starting positions)
df_false9 = df_false9.loc[df_false9.player_id == 5503, ['x', 'y']]
df_before_false9 = df_before_false9.loc[df_before_false9.player_id == 5503, ['x', 'y']]

##############################################################################
# plotting
pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', stripe=False, line_zorder=2)
fig, ax = pitch.draw(figsize=(16, 9), nrows=1, ncols=2,)
pitch.hexbin(df_before_false9.x, df_before_false9.y, ax=ax[0], cmap='Blues')
pitch.hexbin(df_false9.x, df_false9.y, ax=ax[1], cmap='Blues')
TITLE_STR1 = 'Messi in the game directly before \n playing in the false 9 role'
TITLE_STR2 = 'The first Game Messi \nplayed in the false 9 role'
title1 = ax[0].set_title(TITLE_STR1, fontsize=25, pad=20)
title2 = ax[1].set_title(TITLE_STR2, fontsize=25, pad=20)

plt.show()  # If you are using a Jupyter notebook you do not need this line
