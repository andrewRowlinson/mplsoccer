"""
================================
Event distribution using kdeplot 
================================

This example shows how to plot the location of events occurring in a match 
using kernel density estimation (KDE).
"""

from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG

##############################################################################
# load first game that Messi played as a false-9 and the match before as dataframes

kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False, 'tactics_lineup_df': False}
df_false9 = read_event(f'{EVENT_SLUG}/69249.json', **kwargs)['event']
df_before_false9 = read_event(f'{EVENT_SLUG}/69251.json', **kwargs)['event']

##############################################################################
# Filter the dataframes to only include Messi's events and the starting positions

df_false9 = df_false9.loc[df_false9.player_id == 5503, ['x', 'y']]
df_before_false9 = df_before_false9.loc[df_before_false9.player_id == 5503, ['x', 'y']]

##############################################################################
# View a dataframe

df_false9.head()

##############################################################################
# Plotting Messi's first game as a False-9

pitch = Pitch(pitch_type='statsbomb', figsize=(16, 11),
              pitch_color='grass', stripe=True, constrained_layout=False)
fig, ax = pitch.draw()

# plotting
ax.set_title('The first Game Messi played in the false 9 role', fontsize=30, pad=20)

# plot the kernel density estimation
pitch.kdeplot(df_false9.x, df_false9.y, ax=ax, cmap='plasma', linewidths=3)

# annotate
pitch.annotate('6-2 thrashing \nof Real Madrid', (25, 10), color='white',
               fontsize=25, ha='center', va='center', ax=ax)
pitch.annotate('more events', (70, 30), (20, 30), ax=ax, color='white', ha='center', va='center',
               fontsize=20, arrowprops=dict(facecolor='white', edgecolor='None'))
pitch.annotate('fewer events', (51, 20), (20, 20), ax=ax, color='white', ha='center', va='center',
               fontsize=20, arrowprops=dict(facecolor='white', edgecolor='None'))

fig.tight_layout()

##############################################################################
# Plotting both Messi's first game as a False-9 and the game directly before

# Setup the pitches
pitch = Pitch(pitch_type='statsbomb', figsize=(16, 7), layout=(1, 2),
              pitch_color='grass', stripe=True, constrained_layout=False)
fig, ax = pitch.draw()

# set the titles
ax[0].set_title('Messi in the game directly before \n playing in the false 9 role', fontsize=25, pad=20)
ax[1].set_title('The first Game Messi \nplayed in the false 9 role', fontsize=25, pad=20)

# plot the kernel density estimation
pitch.kdeplot(df_before_false9.x, df_before_false9.y, ax=ax[0], cmap='plasma', linewidths=3)
pitch.kdeplot(df_false9.x, df_false9.y, ax=ax[1], cmap='plasma', linewidths=3)

# annotations
pitch.annotate('6-2 thrashing \nof Real Madrid', (25, 10), color='white',
               fontsize=25, ha='center', va='center', ax=ax[1])
pitch.annotate('2-2 draw \nagainst Valencia', (25, 10), color='white',
               fontsize=25, ha='center', va='center', ax=ax[0])
pitch.annotate('more events', (90, 68), (30, 68), ax=ax[0], color='white', ha='center', va='center',
               fontsize=20, arrowprops=dict(facecolor='white', edgecolor='None'))
pitch.annotate('fewer events', (80, 17), (80, 5), ax=ax[0], color='white', ha='center', va='center',
               fontsize=20, arrowprops=dict(facecolor='white', edgecolor='None'))

fig.tight_layout()

