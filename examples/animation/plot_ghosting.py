"""
========
Ghosting
========

Ghosts — model-predicted alternative positions drawn beside the real
players — are just more entities in the dataframe. This example fakes a
"league-average defense" by delaying each defender by a second
(real ghosting uses a learned model: Le, Carr, Yue & Lucey, "Data-Driven
Ghosting", Sloan 2017).
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
import pandas as pd

from mplsoccer import Pitch, animate, AnimationScatter, AnimationTrail

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
# The toy ghost model: each away player delayed by a second. Ghost rows
# get their own entity ids and concatenate onto the real data.
ghosts = df[df.player_id.isin(away)].copy()
ghosts['frame_id'] += 25
ghosts['player_id'] = 'ghost_' + ghosts['player_id']
ghost_ids = ghosts['player_id'].unique().tolist()
df = pd.concat([df, ghosts])

##############################################################################
clip = df[df.frame_id.between(125, 625)]

pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationTrail(ids=away, length=50,
                                           color='#2c7bb6', zorder=1),
                            AnimationTrail(ids=ghost_ids, length=50,
                                           color='0.6', zorder=1),
                            AnimationScatter(ids=ghost_ids, s=150,
                                             color='0.8', ec='0.5',
                                             zorder=2),
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
