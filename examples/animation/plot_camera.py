"""
=============
Camera follow
=============

``AnimationFollow`` slides the view window along the pitch like a
broadcast camera. The camera path is data you supply: here the ball's
x-position, smoothed for inertia and clamped to the pitch.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

from mplsoccer import (Pitch, animate, AnimationFollow, AnimationScatter,
                       AnimationScoreboard)

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
# Build the camera path and a clock, keyed by frame id.
WIDTH = 50
clip = df[df.frame_id.between(100, 850)]
ball = clip[clip.player_id == 'ball'].sort_values('frame_id')
path = np.clip(gaussian_filter1d(ball['x'].to_numpy(), 50),
               -52.5 + WIDTH / 2, 52.5 - WIDTH / 2)
camera = dict(zip(ball['frame_id'], path))
clock = {f: f'{(f - 100) / 25:04.1f}s' for f in ball['frame_id']}

##############################################################################
pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationScatter(ids=home, s=200,
                                             color='#d7191c', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=away, s=200,
                                             color='#2c7bb6', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=['ball'], s=36,
                                             color='yellow', ec='black',
                                             zorder=3),
                            AnimationScoreboard(texts=clock, xy=(0.02, 0.97),
                                                va='top', fontweight='bold'),
                            AnimationFollow(target=camera, width=WIDTH)])
plt.show()

##############################################################################
# In a Jupyter notebook, set the animation display once and end a cell
# with the animation object to get an interactive player, or save the
# clip to a file. Both are commented out so the gallery does not run them.

# plt.rcParams['animation.html'] = 'jshtml'
# anim
# anim.save('animation.gif', writer='mplsoccer_gif', dpi=80)
