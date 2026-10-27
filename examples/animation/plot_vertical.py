"""
==============
Vertical pitch
==============

Every layer works unchanged on a ``VerticalPitch``: positions, trails,
marker rotations and supplied geometry (surfaces, polygons, segments)
all swap automatically. Padding works like the static API — here
``pad_top`` makes room for a clock.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt

from mplsoccer import (VerticalPitch, animate, AnimationScatter,
                       AnimationScoreboard, AnimationTrail)

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
clip = df[df.frame_id.between(100, 475)]
clock = {f: f'{(f - 100) / 25:04.1f}s' for f in df['frame_id'].unique()}

pitch = VerticalPitch(pitch_type='skillcorner', pitch_length=105,
                      pitch_width=68, goal_type='line', pad_top=5)
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id', label=shirts,
                    layers=[AnimationTrail(ids=['ball'], length=75,
                                           color='gold', zorder=1),
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
                            AnimationScoreboard(texts=clock, xy=(0, 0.995),
                                                va='top', fontweight='bold')],
                    draw_kws={'figsize': (5, 7.5)})
plt.show()

##############################################################################
# In a Jupyter notebook, set the animation display once and end a cell
# with the animation object to get an interactive player, or save the
# clip to a file. Both are commented out so the gallery does not run them.

# plt.rcParams['animation.html'] = 'jshtml'
# anim
# anim.save('animation.gif', writer='mplsoccer_gif', dpi=80)
