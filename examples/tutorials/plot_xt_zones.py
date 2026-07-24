"""
==========================
Expected threat over zones
==========================

This example shows how to build an expected threat (xT) model over any
zone layout, here the Juego de Posición zones. For the theory behind
expected threat see the :ref:`sphx_glr_gallery_tutorials_plot_xt.py` tutorial,
which models it over a regular grid.

The grid version keeps the transitions in a four-dimensional matrix
(start row, start column, end row, end column). Because the zone statistics
are flat (one value per zone) and each event has a single zone identifier,
the transitions collapse to a simple (num_zones, num_zones) matrix and the
Markov step becomes a matrix product. This is not only easier to reason
about, it also works for irregular layouts (like the merged Juego de
Posición zones) which the four-dimensional grid form cannot represent.
If you use zones that form a regular grid, this method reproduces the
grid version's results.
"""

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mplsoccer import Sbopen, Pitch

parser = Sbopen()
pitch = Pitch(line_zorder=2)

##############################################################################
# Set up the zones
# ----------------
# Rather than a regular grid, we use the 20 Juego de Posición zones.
# You could use any rectangle layout via ``bin_statistic_zones``
# (or even non-rectangular zones via ``zone_statistic_from_binnumber``).
regions, names = pitch.positional_zones('full')
num_zones = len(regions)

##############################################################################
# Get event data
# --------------
# Get event data from the FA Women's Super League 2019/20.
# Here we include only the carries, shots, and passes used to model expected threat.
# You may additionally want to filter out set pieces and counter-attacks.

# first let's get the match file which lists all the match identifiers for
# the 87 games from the FA WSL 2019/20
df_match = parser.match(competition_id=37, season_id=42)
match_ids = df_match.match_id.unique()

# next we create a dataframe of all the events
all_events_df = []
cols = ['match_id', 'id', 'type_name', 'sub_type_name', 'player_name',
        'x', 'y', 'end_x', 'end_y', 'outcome_name', 'shot_statsbomb_xg']
for match_id in match_ids:
    # get carries/ passes/ shots
    event = parser.event(match_id)[0]  # get the first dataframe (events) which has index = 0
    event = event.loc[event.type_name.isin(['Carry', 'Shot', 'Pass']), cols].copy()

    # boolean columns for working out probabilities
    event['goal'] = event['outcome_name'] == 'Goal'
    event['shoot'] = event['type_name'] == 'Shot'
    event['move'] = event['type_name'] != 'Shot'
    all_events_df.append(event)
event = pd.concat(all_events_df)

##############################################################################
# Bin the data
# ------------
# Here we calculate the probability of a shot,
# successful move (pass or carry), and goal (given a shot) per zone.
# We are averaging the boolean columns (True = 1) and (False = 0) to give us the
# probability between zero and one. The 'statistic' keys are flat arrays
# with one value per zone.
shot_probability = pitch.bin_statistic_zones(event['x'], event['y'], regions,
                                             values=event['shoot'], statistic='mean')
move_probability = pitch.bin_statistic_zones(event['x'], event['y'], regions,
                                             values=event['move'], statistic='mean')
goal_probability = pitch.bin_statistic_zones(event.loc[event['shoot'], 'x'],
                                             event.loc[event['shoot'], 'y'], regions,
                                             values=event.loc[event['shoot'], 'goal'],
                                             statistic='mean')

##############################################################################
# Plot shot probability
# ---------------------
path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
fig, ax = pitch.draw()
shot_heatmap = pitch.heatmap_zones(shot_probability, ax=ax)
labels = pitch.label_heatmap(shot_probability, ax=ax, str_format='{:.0%}',
                             color='white', fontsize=12, va='center', ha='center',
                             path_effects=path_eff)

##############################################################################
# Plot move probability
# ---------------------
fig, ax = pitch.draw()
move_heatmap = pitch.heatmap_zones(move_probability, ax=ax)
labels = pitch.label_heatmap(move_probability, ax=ax, str_format='{:.0%}',
                             color='white', fontsize=12, va='center', ha='center',
                             path_effects=path_eff)

##############################################################################
# Plot goal probability
# ---------------------
fig, ax = pitch.draw()
goal_heatmap = pitch.heatmap_zones(goal_probability, ax=ax)
labels = pitch.label_heatmap(goal_probability, ax=ax, str_format='{:.0%}',
                             color='white', fontsize=12, va='center', ha='center',
                             path_effects=path_eff)

##############################################################################
# Calculate the move transition matrix
# ------------------------------------
# The move transition matrix takes into account the success probability of
# carrying out the transitions. It is the probability of moving the ball
# successfully from one zone to another. As each event belongs to a single
# zone (the 'binnumber' key), the transitions are a simple
# (num_zones, num_zones) matrix rather than the grid version's
# four-dimensional matrix.

# get a dataframe of move events with their start/ end zones and filter it
# so the dataframe only contains actions starting inside the pitch
move = event[event['move']].copy()
start_zones = pitch.bin_statistic_zones(move['x'], move['y'], regions)
move['start_zone'] = start_zones['binnumber']
move = move[start_zones['inside']].copy()

# get the successful moves, which filters out the events that ended outside
# the pitch or were not successful (null)
end_zones = pitch.bin_statistic_zones(move['end_x'], move['end_y'], regions)
move['end_zone'] = end_zones['binnumber']
move_success = move[end_zones['inside'] & move['outcome_name'].isnull()].copy()

# the number of successful moves between the zones
move_transition_matrix = np.zeros((num_zones, num_zones))
np.add.at(move_transition_matrix,
          (move_success['start_zone'].to_numpy(), move_success['end_zone'].to_numpy()), 1)

# and divide by the starting locations for all moves (including unsuccessful)
# to get the probability of moving the ball successfully between zones
start_counts = np.bincount(move['start_zone'], minlength=num_zones)
move_transition_matrix = np.divide(move_transition_matrix,
                                   start_counts[:, np.newaxis],
                                   out=np.zeros_like(move_transition_matrix),
                                   where=start_counts[:, np.newaxis] != 0,
                                   )

##############################################################################
# Get the matrices
# ----------------
# Get the flat arrays from the dictionaries and turn nans into zeros
move_transition_matrix = np.nan_to_num(move_transition_matrix)
shot_probability_matrix = np.nan_to_num(shot_probability['statistic'])
move_probability_matrix = np.nan_to_num(move_probability['statistic'])
goal_probability_matrix = np.nan_to_num(goal_probability['statistic'])

##############################################################################
# Calculate xT
# ------------
# Calculate xT until convergence. Initially the expected threat is set to the
# shot probability multiplied by the goal probability. With flat zones the
# Markov step is a matrix product: the transition matrix times the expected
# threat of the end zones.
xt = np.multiply(shot_probability_matrix, goal_probability_matrix)
diff = 1
iteration = 0
while np.any(diff > 0.00001):  # iterate until the differences between the old and new xT is small
    xt_copy = xt.copy()  # keep a copy for comparing the differences
    # calculate the new expected threat
    xt = (np.multiply(shot_probability_matrix, goal_probability_matrix) +
          np.multiply(move_probability_matrix, move_transition_matrix @ xt))
    diff = (xt - xt_copy)
    iteration += 1
print('Number of iterations:', iteration)

##############################################################################
# Plot xT zones
# -------------
# The 'statistic' key is a plain array so we can assign our computed
# expected threat to a zone statistics dictionary for plotting.
for_plotting = pitch.bin_statistic_zones(event['x'], event['y'], regions, names=names)
for_plotting['statistic'] = xt
fig, ax = pitch.draw(figsize=(14, 9.625))
_ = pitch.heatmap_zones(for_plotting, ax=ax)
_ = pitch.label_heatmap(for_plotting, ax=ax, str_format='{:.2%}',
                        color='white', fontsize=14, va='center', ha='center',
                        path_effects=path_eff)
# sphinx_gallery_thumbnail_path = 'gallery/tutorials/images/sphx_glr_plot_xt_zones_004'

##############################################################################
# Scoring events
# --------------
# We score each successful move as the additional expected threat gained from
# moving from one zone to another. With flat zones this is a simple lookup
# with the zone identifiers.
start_xt = xt[move_success['start_zone']]
end_xt = xt[move_success['end_zone']]
move_success['xt'] = end_xt - start_xt

# show players with top 5 total expected threat
move_success.groupby('player_name')['xt'].sum().sort_values(ascending=False).head(5)

plt.show()  # If you are using a Jupyter notebook you do not need this line
