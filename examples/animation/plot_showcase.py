"""
=======================
Putting it all together
=======================

Layers compose: team convex hulls under velocity arrows under labelled
markers, with a clock on top.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt

from mplsoccer import (Pitch, animate, AnimationArrows, AnimationHull,
                       AnimationScatter, AnimationScoreboard)

ASSETS = ('https://raw.githubusercontent.com/andrewRowlinson/'
          'mplsoccer-assets/main/animation/')
ds = skillcorner.load_tracking(
    raw_data=urlretrieve(ASSETS + 'mock_tracking_extrapolated.jsonl')[0],
    meta_data=urlretrieve(ASSETS + 'mock_match.json')[0])
df = ds.tracking.to_pandas()
players = ds.players.to_pandas()
home_id = ds.teams['team_id'][0]
outfield = players[players.position != 'GK']
home = players.loc[players.team_id == home_id, 'player_id'].tolist()
away = players.loc[players.team_id != home_id, 'player_id'].tolist()
home_out = outfield.loc[outfield.team_id == home_id, 'player_id'].tolist()
away_out = outfield.loc[outfield.team_id != home_id, 'player_id'].tolist()
shirts = dict(zip(players.player_id, players.jersey_number))

##############################################################################
# Velocity columns for the arrows (one diff per player) and a clock.
df = df.sort_values(['player_id', 'frame_id'])
group = df.groupby('player_id', sort=False)
df['u'] = group['x'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
df['v'] = group['y'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
clock = {f: f'{(f - 100) / 25:04.1f}s' for f in df['frame_id'].unique()}

##############################################################################
clip = df[df.frame_id.between(100, 600)]

pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id', label=shirts,
                    layers=[AnimationHull(ids=home_out, facecolor='#d7191c',
                                          edgecolor='#d7191c', alpha=0.15,
                                          zorder=1),
                            AnimationHull(ids=away_out, facecolor='#2c7bb6',
                                          edgecolor='#2c7bb6', alpha=0.15,
                                          zorder=1),
                            AnimationArrows(u='u', v='v', ids=home + away,
                                            color='0.3', width=1.5,
                                            zorder=1.5),
                            AnimationScatter(ids=home, s=220,
                                             color='#d7191c', ec='black',
                                             label=True, labelcolor='white',
                                             fontsize=8, zorder=2),
                            AnimationScatter(ids=away, s=220,
                                             color='#2c7bb6', ec='black',
                                             label=True, labelcolor='white',
                                             fontsize=8, zorder=2),
                            AnimationScatter(ids=['ball'], s=36,
                                             color='yellow', ec='black',
                                             zorder=3),
                            AnimationScoreboard(texts=clock, xy=(0.02, 0.97),
                                                va='top',
                                                fontweight='bold')])
plt.show()

##############################################################################
# In a Jupyter notebook, set the animation display once and end a cell
# with the animation object to get an interactive player, or save the
# clip to a file. Both are commented out so the gallery does not run them.

# plt.rcParams['animation.html'] = 'jshtml'
# anim
# anim.save('animation.gif', writer='mplsoccer_gif', dpi=80)
