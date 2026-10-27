"""
==================
Player orientation
==================

``AnimationScatter(rotation=...)`` rotates markers to face a per-frame
orientation column. Tracking providers with body orientation (e.g. NFL
data's ``o``) supply it directly; soccer data usually does not, so here
we derive a heading from the movement — note a heading is not a true
facing (a backpedalling defender points the wrong way).
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mplsoccer import (Pitch, animate, AnimationScatter, halfcircle_marker)

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
shirts = dict(zip(players.player_id, players.jersey_number))

##############################################################################
# Derive a heading column: smoothed velocity, masked below walking pace
# so stationary players hold their last confident angle. The angle is in
# the same convention as ``pitch.scatter(rotation_degrees=)``: degrees
# clockwise, 0 = the direction of play, which
# ``pitch.calculate_angle_and_distance`` gives from a start and end point.
pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
df = df.sort_values(['player_id', 'frame_id'])
group = df.groupby('player_id', sort=False)
smooth = lambda s: s.rolling(13, center=True, min_periods=1).mean()
u = group['x'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
v = group['y'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
u = u.groupby(df['player_id']).transform(smooth)
v = v.groupby(df['player_id']).transform(smooth)
heading, _ = pitch.calculate_angle_and_distance(df['x'], df['y'],
                                                df['x'] + u, df['y'] + v,
                                                degrees=True)
df['heading'] = np.where(np.hypot(u, v) > 0.7, heading, np.nan)
df['heading'] = df.groupby('player_id')['heading'].ffill()
# anyone yet to move (the keepers) faces the centre spot
to_centre, _ = pitch.calculate_angle_and_distance(df['x'], df['y'],
                                                  np.zeros(len(df)),
                                                  np.zeros(len(df)),
                                                  degrees=True)
df['heading'] = df['heading'].fillna(pd.Series(to_centre, index=df.index))

##############################################################################
# Markers rotate to the ``heading`` column; the half-circle's flat edge
# is the front. The numbers stay upright.
clip = df[df.frame_id.between(100, 600)]

fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id', label=shirts,
                    layers=[AnimationScatter(ids=home, rotation='heading',
                                             marker=halfcircle_marker, s=640,
                                             color='#d7191c', label=True,
                                             labelcolor='white', fontsize=7,
                                             zorder=2),
                            AnimationScatter(ids=away, rotation='heading',
                                             marker=halfcircle_marker, s=640,
                                             color='#2c7bb6', label=True,
                                             labelcolor='white', fontsize=7,
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
