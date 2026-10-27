"""
===============
Formation lines
===============

``AnimationLines`` connects groups of players with polylines — here the
defensive lines of Victorious Secret, detected per frame with the
approach from Kuba Michalczyk's 2020 OptaPro Forum project,
`How Impactful Are Line-Breaking Passes?
<https://www.statsperform.com/insights/how-impactful-are-line-breaking-passes/>`_:
Jenks natural breaks on the goal-to-goal coordinate, smoothed in time
so players do not flicker between lines. mplsoccer draws the lines; the
detector below is plain numpy and pandas, so swap in your own.
"""
from urllib.request import urlretrieve

from fastforward import skillcorner
import matplotlib.pyplot as plt
import numpy as np

from mplsoccer import Pitch, animate, AnimationLines, AnimationScatter

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
away_gk = players.loc[(players.team_id != home_id) &
                      (players.position == 'GK'), 'player_id'].tolist()

##############################################################################
# Jenks natural breaks: the optimal split of the outfield players'
# goal-to-goal coordinates into ``k`` contiguous groups, found by dynamic
# programming over the sorted values (minimising the within-group sum of
# squares). Exact and deterministic, and trivial for ten players.


def jenks_labels(x, k=3):
    """Group the values of ``x`` into ``k`` contiguous classes; returns a
    label per value, 0 for the lowest class."""
    x = np.asarray(x, dtype=float)
    n = x.size
    if n <= k:
        return np.argsort(np.argsort(x))     # fewer players than lines
    order = np.argsort(x)
    xs = x[order]
    # prefix sums give the sum of squares of any contiguous run in O(1)
    cs = np.concatenate([[0.], np.cumsum(xs)])
    cs2 = np.concatenate([[0.], np.cumsum(xs ** 2)])

    def sse(i, j):
        s = cs[j] - cs[i]
        return (cs2[j] - cs2[i]) - s * s / (j - i)

    cost = np.full((k + 1, n + 1), np.inf)
    split = np.zeros((k + 1, n + 1), dtype=int)
    cost[0, 0] = 0.
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            for i in range(c - 1, j):
                value = cost[c - 1, i] + sse(i, j)
                if value < cost[c, j]:
                    cost[c, j] = value
                    split[c, j] = i
    sorted_labels = np.empty(n, dtype=int)
    j = n
    for c in range(k, 0, -1):
        i = split[c, j]
        sorted_labels[i:j] = c - 1
        j = i
    labels = np.empty(n, dtype=int)
    labels[order] = sorted_labels
    return labels


##############################################################################
# Detect the lines frame by frame. The goal-to-goal coordinate is smoothed
# over two seconds per player first, and a player's line assignment must
# last at least a second, otherwise it is absorbed into the previous one:
# both stop single-frame jitter reshuffling the lines.
FPS, N_LINES = 25, 3
clip = df[df.frame_id.between(100, 600)]
outfield = (clip[clip.player_id.isin(away) & ~clip.player_id.isin(away_gk)]
            .sort_values(['player_id', 'frame_id']).copy())
outfield['x_smooth'] = (outfield.groupby('player_id')['x']
                        .transform(lambda s: s.rolling(2 * FPS, center=True,
                                                       min_periods=1).mean()))
outfield['line'] = (outfield.groupby('frame_id')['x_smooth']
                    .transform(lambda s: jenks_labels(s.to_numpy(), N_LINES)))


def drop_short_runs(labels, min_frames=FPS):
    """Absorb line assignments shorter than ``min_frames`` into the
    previous assignment (one player's labels, in frame order)."""
    labels = labels.to_numpy().copy()
    change = np.flatnonzero(np.diff(labels)) + 1
    starts, ends = np.concatenate([[0], change]), np.concatenate([change, [labels.size]])
    for start, end in zip(starts, ends):
        if end - start < min_frames and start > 0:
            labels[start:end] = labels[start - 1]
    return labels


outfield['line'] = outfield.groupby('player_id')['line'].transform(drop_short_runs)

##############################################################################
# Fold the assignments into the dict ``AnimationLines`` takes:
# ``{frame id: [ids of line 0, ids of line 1, ...]}``, each line's players
# ordered across the pitch so its polyline does not zigzag.
lines = {}
for frame_id, frame in outfield.sort_values(['frame_id', 'line', 'y']).groupby('frame_id'):
    lines[frame_id] = [grp['player_id'].tolist()
                       for _, grp in frame.groupby('line')]

##############################################################################
pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68,
              goal_type='line')
fig, anim = animate(pitch, clip, frame='frame_id', x='x', y='y',
                    ids='player_id',
                    layers=[AnimationLines(groups=lines, colors='#2c7bb6',
                                           lw=2, alpha=0.6, zorder=1),
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
