"""
==========================
Broadcast camera footprint
==========================

``AnimationPolygon`` draws supplied polygons per frame. Its original
use: the part of the pitch the broadcast camera can see, which
SkillCorner ships with every frame as ``image_corners_projection``.
Frames without a projection (replays, close-ups) draw nothing.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mplsoccer import Pitch, animate, AnimationPolygon, AnimationScatter

ASSETS = ('https://raw.githubusercontent.com/andrewRowlinson/'
          'mplsoccer-assets/main/animation/')
raw_path = urlretrieve(ASSETS + 'mock_tracking_extrapolated.jsonl')[0]
ds = skillcorner.load_tracking(
    raw_data=raw_path,
    meta_data=urlretrieve(ASSETS + 'mock_match.json')[0])
df = ds.tracking.to_pandas()
players = ds.players.to_pandas()
home_id = ds.teams['team_id'][0]
home = players.loc[players.team_id == home_id, 'player_id'].tolist()
away = players.loc[players.team_id != home_id, 'player_id'].tolist()

##############################################################################
# fast-forward keeps the tracking table lean, so read the camera quad
# straight from the raw file into a dict keyed by frame id.
raw = pd.read_json(raw_path, lines=True)
footprint = {
    frame: [np.array([[c['x_top_left'], c['y_top_left']],
                      [c['x_top_right'], c['y_top_right']],
                      [c['x_bottom_right'], c['y_bottom_right']],
                      [c['x_bottom_left'], c['y_bottom_left']]])]
    for frame, c in zip(raw['frame'], raw['image_corners_projection'])
    if c is not None}

##############################################################################
clip = df[df.frame_id.between(100, 600)]

pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationPolygon(polys=footprint,
                                             facecolor='0.6', alpha=0.25,
                                             zorder=0.5),
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
