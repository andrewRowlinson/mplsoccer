"""
==================================
Event distribution using jointplot 
==================================

This example shows how to plot the location of events occurring in a match 
using a joint plot.
"""

from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import os

##############################################################################
# load the first game that Messi played as a false-9

kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False, 'tactics_lineup_df': False, 'warn': False}
df_false9 = read_event(f'{EVENT_SLUG}/69249.json', **kwargs)['event']
# filter messi's actions (starting positions)
df_false9 = df_false9.loc[df_false9.player_id == 5503, ['x', 'y']]

##############################################################################
# Plot the joint plot
# Note that the axis of joint plots is always square, so here we make the pitch square by setting ``pad_left``
pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', stripe=True, view='half', pad_left=20)
joint_kws = {'shade': False, 'color': 'green', 'cmap': "plasma", 'linewidths': 3}
g = pitch.jointplot(df_false9.x, df_false9.y, height=9, kind='kde', **joint_kws)
g.fig.subplots_adjust(top=0.9)
title = g.fig.suptitle("Messi's first game as a false 9", fontsize=25, ha='center', va='center')
