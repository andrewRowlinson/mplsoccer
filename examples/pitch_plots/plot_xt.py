"""
===============
Expected threat
===============

This example shows how to create expected threat (xT). This was
introduced by Karun Singh in this `great blog post <https://karun.in/blog/expected-threat.html>`_
"""

from mplsoccer import Sbopen, Pitch
import numpy as np
import pandas as pd
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt

parser = Sbopen()
pitch = Pitch(line_zorder=2)
bins = (16, 12)  # 16 cells x 12 cells

##############################################################################
# Get event data
# --------------
# Get event data from the FA Women's Super League 2019/20.
# Here we include only regular play events, which excludes set pieces and also counter attacks.

df_match = parser.match(competition_id=37, season_id=42)  # 87 games from FA WSL 2019/20
match_ids = df_match.match_id.unique()

all_events_df = []
cols = ['match_id', 'id', 'type_name', 'sub_type_name', 'x', 'y', 'end_x', 'end_y', 'outcome_name']
for match_id in match_ids:
    # get carries/ passes/ shots from regular play
    event = parser.event(match_id)[0]
    mask_success_pass = (event['type_name'] == 'Pass') & (event['outcome_name'].isnull())
    mask_carry_shot = event.type_name.isin(['Carry', 'Shot'])
    mask_regular_play = event['play_pattern_name'] == 'Regular Play'
    event = event.loc[(mask_success_pass | mask_carry_shot) & mask_regular_play, cols].copy()
    
    # boolean columns for working out probabilities
    event['goal'] = event['outcome_name'] == 'Goal'
    event['shoot'] = event['type_name'] == 'Shot'
    event['move'] = event['type_name'] != 'Shot'
    all_events_df.append(event)
event = pd.concat(all_events_df)

##############################################################################
# Bin the data
# ------------
# Here we calculate the probability of a shot, successful move (pass or carry), and goal (given a shot).

shot_probability = pitch.bin_statistic(event['x'], event['y'], values=event['shoot'], statistic='mean', bins=bins)
move_probability = pitch.bin_statistic(event['x'], event['y'], values=event['move'], statistic='mean', bins=bins)
goal_probability = pitch.bin_statistic(event.loc[event['shoot'], 'x'], 
                                       event.loc[event['shoot'], 'y'],
                                       event.loc[event['shoot'], 'goal'],
                                       statistic='mean', bins=bins)

##############################################################################
# Plot shot probability
# ---------------------
fig, ax = pitch.draw()
pitch.heatmap(shot_probability, ax=ax)

##############################################################################
# Plot goal probability
# ---------------------
fig, ax = pitch.draw()
pitch.heatmap(goal_probability, ax=ax)


##############################################################################
# Plot move probability
# ---------------------
fig, ax = pitch.draw()
pitch.heatmap(move_probability, ax=ax)

##############################################################################
# Calculate the move transition matrix
# ------------------------------------
move = event[event['move']].copy()

# get bin end location cells as an integer
bin_end_locations = pitch.bin_statistic(move['end_x'], move['end_y'], bins=bins)
move['end_bin'] = bin_end_locations['binnumber'][0] * bins[1] + bin_end_locations['binnumber'][1]

# turn this into dummy columns (1/ 0) for move in the relevant end cell
move_dummies = pd.get_dummies(move.end_bin, sparse=True)
all_bins = np.arange(0, bins[0] * bins[1])
not_included = [col for col in all_bins if col not in move_dummies.columns]
for col in all_bins:
    if col not in move_dummies.columns:
        move_dummies[col] = 0
move_dummies = move_dummies[all_bins]

move_transition = pitch.bin_statistic(move['x'],
                                      move['y'],
                                      move_dummies.values.T.tolist(),
                                      bins=bins,
                                      statistic='mean')

##############################################################################
# Get the matrices
# ----------------
# Get the matrices from the dictionaries and turn nans into zeros
move_transition_matrix = np.nan_to_num(move_transition['statistic'])
move_transition_matrix = np.transpose(move_transition_matrix.reshape(bins[1], bins[0], bins[0], bins[1]), (0, 1, 3, 2))
shot_probability_matrix = np.nan_to_num(shot_probability['statistic'])
move_probability_matrix = np.nan_to_num(move_probability['statistic'])
goal_probability_matrix = np.nan_to_num(goal_probability['statistic'])

##############################################################################
# Bin Start locations
# -------------------
# These lines are not needed for xT just for plotting the transition matrix.
bin_start_locations = pitch.bin_statistic(move['x'], move['y'], bins=bins)
move['start_bin'] = bin_start_locations['binnumber'][0] * bins[1] + bin_start_locations['binnumber'][1]

##############################################################################
# Plot transition matrix
# ----------------------
# Plotting one cell of the move transition matrix first row (x=0) and 6th cell up (y_idx = 5)
x_idx = 0
y_idx = 5
for_plotting = pitch.bin_statistic(event['x'], event['y'], bins=bins)  # new bin statistic for plotting only
for_plotting['statistic'] = move_transition_matrix[y_idx, x_idx, :, :]  # changing statistic to relevant start cell
fig, ax = pitch.draw()
pitch.heatmap(for_plotting, ax=ax)
# overlaying a scatter of the end locations so you can see it's working
mask = move.start_bin == x_idx * bins[1] + y_idx
pitch.scatter(move[mask].end_x, move[mask].end_y, ax=ax, color='red', alpha=0.1)

##############################################################################
# Calculate xT
# ------------
# Calculate xT until convergence

xt = np.multiply(shot_probability_matrix, goal_probability_matrix)
diff = 1
iteration = 0
while np.any(diff > 0.00001):
    xt_copy = xt.copy()
    xt = (np.multiply(shot_probability_matrix, goal_probability_matrix) +
      np.multiply(move_probability_matrix, 
                  np.multiply(move_transition_matrix, np.expand_dims(xt, axis=(0, 1))).sum(axis=(2, 3)))
     )
    diff = (xt - xt_copy)
    iteration += 1
print('Number of iterations:', iteration)

##############################################################################
# Plot xT grid
# ------------
# Another method popularized by `@petermckeever <https://twitter.com/petermckeever>`_.
# is to use hatch patterns to show where something was not-successful versus successful.
# There are lots of different hatch patterns.
# See: matplotlib.org/api/_as_gen/matplotlib.patches.Patch.html#matplotlib.patches.Patch.set_hatch
# This is typically combined with the highlight-text package
# by `@danzn1 <https://twitter.com/danzn1>`_.

path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
for_plotting['statistic'] = xt
fig, ax = pitch.draw(figsize=(14, 9.625))
_ = pitch.heatmap(for_plotting, ax=ax)
_ = pitch.label_heatmap(for_plotting, ax=ax, str_format='{:.2%}', color='white', fontsize=14, va='center', ha='center',
                       path_effects=path_eff)

plt.show()  # If you are using a Jupyter notebook you do not need this line
