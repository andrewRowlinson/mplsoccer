"""
=====================
Animate tracking data
=====================

Animate tracking data by passing a long-form dataframe (one row per
player per frame) and a list of layers saying what to draw. Here we
load mock SkillCorner-format data with
`fast-forward <https://fast-forward.readthedocs.io/>`_.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt

from mplsoccer import Pitch, animate, AnimationScatter

ASSETS = ('https://raw.githubusercontent.com/andrewRowlinson/'
          'mplsoccer-assets/main/animation/')
ds = skillcorner.load_tracking(
    raw_data=urlretrieve(ASSETS + 'mock_tracking_extrapolated.jsonl')[0],
    meta_data=urlretrieve(ASSETS + 'mock_match.json')[0])
df = ds.tracking.to_pandas()
players = ds.players.to_pandas()

##############################################################################
# Get the team line-ups and shirt numbers from the players dataframe.
home_id = ds.teams['team_id'][0]
home = players.loc[players.team_id == home_id, 'player_id'].tolist()
away = players.loc[players.team_id != home_id, 'player_id'].tolist()
shirts = dict(zip(players.player_id, players.jersey_number))

##############################################################################
# Slice a clip with pandas (the dataframe you pass is the clip) and
# animate it: one scatter layer per team plus one for the ball.
clip = df[df.frame_id.between(100, 475)]

pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id', label=shirts,
                    layers=[AnimationScatter(ids=home, s=250, color='#d7191c',
                                             ec='black', label=True,
                                             labelcolor='white', zorder=2),
                            AnimationScatter(ids=away, s=250, color='#2c7bb6',
                                             ec='black', label=True,
                                             labelcolor='white', zorder=2),
                            AnimationScatter(ids=['ball'], s=40,
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
