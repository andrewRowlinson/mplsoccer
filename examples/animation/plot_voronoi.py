"""
=======
Voronoi
=======

``AnimationPolygon`` draws supplied polygons per frame — here each
team's Voronoi cells from ``pitch.voronoi``, the region of the pitch
each player is closest to.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

from mplsoccer import Pitch, animate, AnimationPolygon, AnimationScatter

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
# ``pitch.voronoi`` returns each team's cells for one frame; collect
# them into dicts keyed by frame id.
pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
clip = df[df.frame_id.between(100, 600)]
home_cells, away_cells = {}, {}
for frame_id, frame in clip[clip.player_id != 'ball'].groupby('frame_id'):
    team1, team2 = pitch.voronoi(frame['x'], frame['y'],
                                 frame['player_id'].isin(home))
    home_cells[frame_id] = list(team1)
    away_cells[frame_id] = list(team2)

##############################################################################
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationPolygon(polys=home_cells,
                                             facecolor=to_rgba('#d7191c', 0.2),
                                             edgecolor='white', lw=1.5,
                                             zorder=1),
                            AnimationPolygon(polys=away_cells,
                                             facecolor=to_rgba('#2c7bb6', 0.2),
                                             edgecolor='white', lw=1.5,
                                             zorder=1),
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
