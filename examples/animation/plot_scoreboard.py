"""
==========
Scoreboard
==========

``AnimationScoreboard`` pins per-frame text to a fixed screen position:
a scoreboard and running clock here, but any per-frame string works —
phase labels, possession, narration. Pass an array aligned with the
frames, a dict keyed by frame id, or a callable.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt

from mplsoccer import Pitch, animate, AnimationScatter, AnimationScoreboard

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
# The score is a dict keyed by frame id that changes at the goal frames.
# The mock match has no events, so two goals are made up here; with real
# data take the goal frames from the events and the same loop covers a
# full match (one short string per frame).
goals = {250: 'home', 420: 'away'}           # frame id -> scoring team
home_goals = away_goals = 0
score = {}
for f in sorted(df['frame_id'].unique()):
    home_goals += goals.get(f) == 'home'
    away_goals += goals.get(f) == 'away'
    score[f] = f'Rolos Rejects {home_goals} - {away_goals} Victorious Secret'


##############################################################################
# The clock is the callable form instead: it is called each frame with
# the clip and the frame position, and reads the frame id back from the
# clip. Nothing is stored up front, so it costs the same for 90 minutes.
def clock(frames, i):
    seconds = (frames.frame_index[i] - 100) / 25
    return f'{seconds // 60:02.0f}:{seconds % 60:04.1f}'


##############################################################################
clip = df[df.frame_id.between(100, 600)]

pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line', pad_top=5)   # room above the pitch
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationScatter(ids=home, s=150,
                                             color='#d7191c', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=away, s=150,
                                             color='#2c7bb6', ec='black',
                                             zorder=2),
                            AnimationScatter(ids=['ball'], s=30,
                                             color='yellow', ec='black',
                                             zorder=3),
                            AnimationScoreboard(texts=score, xy=(0, 0.99),
                                                va='top', fontweight='bold'),
                            AnimationScoreboard(texts=clock, xy=(1, 0.99),
                                                ha='right', va='top',
                                                fontweight='bold')])
plt.show()

##############################################################################
# In a Jupyter notebook, set the animation display once and end a cell
# with the animation object to get an interactive player, or save the
# clip to a file. Both are commented out so the gallery does not run them.

# plt.rcParams['animation.html'] = 'jshtml'
# anim
# anim.save('animation.gif', writer='mplsoccer_gif', dpi=80)
