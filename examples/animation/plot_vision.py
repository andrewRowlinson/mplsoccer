"""
============
Vision cones
============

An arc showing where each player is looking is just a rotating marker:
a wedge ``Path`` with its point on the player, turned by the same
heading recipe as the orientation example. Tracking data has no eyes —
a heading is movement, not gaze — but it reads well in broadcast-style
graphics.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
from matplotlib.path import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mplsoccer import Pitch, animate, AnimationScatter

ASSETS = ('https://raw.githubusercontent.com/andrewRowlinson/'
          'mplsoccer-assets/main/animation/')
ds = skillcorner.load_tracking(
    raw_data=urlretrieve(ASSETS + 'mock_tracking_extrapolated.jsonl')[0],
    meta_data=urlretrieve(ASSETS + 'mock_match.json')[0])
df = ds.tracking.to_pandas()
players = ds.players.to_pandas()
home_id = ds.teams['team_id'][0]
home = players.loc[players.team_id == home_id, 'player_id'].tolist()
away = players.loc[players.team_id != home_id, 'player_id'].tolist()

##############################################################################
# The heading recipe (see the orientation example: degrees clockwise
# from the direction of play) with a heavier smooth and a higher speed gate, so the cones steer on purposeful runs
# instead of scanning with every wobble. The cone is a sixty-degree
# wedge of the unit circle with its point at the origin, authored
# facing up like all rotation markers.
pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
df = df.sort_values(['player_id', 'frame_id'])
group = df.groupby('player_id', sort=False)
smooth = lambda s: s.rolling(51, center=True, min_periods=1).mean()
u = group['x'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
v = group['y'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
u = u.groupby(df['player_id']).transform(smooth)
v = v.groupby(df['player_id']).transform(smooth)
heading, _ = pitch.calculate_angle_and_distance(df['x'], df['y'],
                                                df['x'] + u, df['y'] + v,
                                                degrees=True)
df['heading'] = np.where(np.hypot(u, v) > 1.5, heading, np.nan)
df['heading'] = df.groupby('player_id')['heading'].ffill()
to_centre, _ = pitch.calculate_angle_and_distance(df['x'], df['y'],
                                                  np.zeros(len(df)),
                                                  np.zeros(len(df)),
                                                  degrees=True)
df['heading'] = df['heading'].fillna(pd.Series(to_centre, index=df.index))

cone = Path.wedge(60, 120)

##############################################################################
clip = df[df.frame_id.between(100, 600)]

fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationScatter(ids=home, rotation='heading',
                                             marker=cone, s=4800,
                                             color='#d7191c', alpha=0.25,
                                             lw=0, zorder=1),
                            AnimationScatter(ids=away, rotation='heading',
                                             marker=cone, s=4800,
                                             color='#2c7bb6', alpha=0.25,
                                             lw=0, zorder=1),
                            AnimationScatter(ids=home, s=100,
                                             color='#d7191c', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=away, s=100,
                                             color='#2c7bb6', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=['ball'], s=30,
                                             color='yellow', ec='black',
                                             zorder=3)])
plt.show()

##############################################################################
# In a Jupyter notebook, set the animation display once and end a cell
# with the animation object to get an interactive player, or save the
# clip to a file. Both are commented out so the gallery does not run them.

# plt.rcParams['animation.html'] = 'jshtml'
# anim
# anim.save('animation.gif', writer='mplsoccer_gif', dpi=80)
