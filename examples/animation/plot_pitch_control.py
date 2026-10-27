"""
=============
Pitch control
=============

``AnimationSurface`` animates a grid of values over the pitch. Here a
minimal time-to-intercept pitch control model: Laurie Shaw's
approximation from his tracking-data tutorials (react, then run at top
speed) plus the turning penalty from Devin Pleuler's
`analytics handbook <https://github.com/devinpleuler/analytics-handbook>`_.
mplsoccer draws the surface; the model is yours: compute any
(n_frames, ny, nx) stack and pass it in.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import numpy as np

from mplsoccer import Pitch, animate, AnimationScatter, AnimationSurface

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
# The model: each cell's value is the difference between how fast the
# two teams can reach it. A player reacts for 0.7 s (drifting with their
# current velocity), then runs at 5 m/s; on top, a running player is
# charged for how far they must turn towards the cell (speed times the
# turn as a fraction of a half circle), so space behind a sprinting
# defender counts less as theirs. Velocities come from the usual pandas
# recipe; positions and velocities pivot to (n_frames, n_players, 2) arrays.
df = df.sort_values(['player_id', 'frame_id'])
group = df.groupby('player_id', sort=False)
df['u'] = group['x'].diff().shift(-1).groupby(df['player_id']).ffill() * 25
df['v'] = group['y'].diff().shift(-1).groupby(df['player_id']).ffill() * 25

clip = df[df.frame_id.between(100, 350)]
grids = {col: clip.pivot(index='frame_id', columns='player_id', values=col)
         for col in ('x', 'y', 'u', 'v')}


def team_arrays(ids):
    xy = np.stack([grids['x'][ids], grids['y'][ids]], axis=-1)
    uv = np.stack([grids['u'][ids], grids['v'][ids]], axis=-1)
    return xy, uv


def time_to_intercept(xy, uv, points, reaction=0.7, vmax=5.0):
    to_point = points[:, :, None] - xy               # (ny, nx, players, 2)
    speed = np.linalg.norm(uv, axis=-1)              # (players,)
    distance = np.linalg.norm(to_point, axis=-1)
    # a stationary player, or a cell underfoot, has nothing to turn
    # (cosine 1); the clip stops rounding pushing a cosine past 1
    denominator = distance * speed
    cosine = np.divide((to_point * uv).sum(axis=-1), denominator,
                       out=np.ones_like(denominator), where=denominator > 0)
    turn = np.arccos(np.clip(cosine, -1, 1))
    arrive = xy + uv * reaction
    run = np.linalg.norm(points[:, :, None] - arrive, axis=-1)
    seconds = speed * turn / np.pi + reaction + run / vmax
    return np.nanmin(seconds, axis=-1)               # fastest player

gx, gy = np.meshgrid(np.linspace(-52.5, 52.5, 84), np.linspace(-34, 34, 54))
points = np.stack([gx, gy], axis=-1)
home_xy, home_uv = team_arrays(home)
away_xy, away_uv = team_arrays(away)
control = np.stack([time_to_intercept(home_xy[i], home_uv[i], points)
                    - time_to_intercept(away_xy[i], away_uv[i], points)
                    for i in range(len(home_xy))])

##############################################################################
# Keep the values smooth and band with ``BoundaryNorm`` — banding the
# data itself would show the compute grid's staircase.
pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line', line_color='0.3')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationSurface(
                                values=control, extent=(-52.5, 52.5, -34, 34),
                                cmap='RdBu',
                                norm=BoundaryNorm(np.linspace(-1, 1, 11),
                                                  256, extend='both'),
                                alpha=0.5, zorder=0.7,
                                interpolation='bilinear',
                                interpolation_stage='data'),
                            AnimationScatter(ids=home, s=150,
                                             color='#d7191c', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=away, s=150,
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
