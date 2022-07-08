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
    # get carries/ passes/ shots
    event = parser.event(match_id)[0]
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

# get a dataframe of move events and filter out events starting outside the pitch (-1 binnumber)
move = event[event['move']].copy()
bin_start_locations = pitch.bin_statistic(move['x'], move['y'], bins=bins)
move = move[np.all(bin_start_locations['binnumber'] != -1, axis=0)].copy()

# get the successful moves and filter out the events that ended outside the pitch
bin_end_locations = pitch.bin_statistic(move['end_x'], move['end_y'], bins=bins)
move_success = move[(np.all(bin_end_locations['binnumber'] != -1, axis=0) &
                     move['outcome_name'].isnull())].copy()

# get a dataframe of the bin start and end locations
bin_success_start = pitch.bin_statistic(move_success['x'], move_success['y'], bins=bins)
bin_success_end = pitch.bin_statistic(move_success['end_x'], move_success['end_y'], bins=bins)
df_bin = pd.DataFrame({'x': bin_success_start['binnumber'][0],
                       'y': bin_success_start['binnumber'][1],
                       'end_x': bin_success_end['binnumber'][0],
                       'end_y': bin_success_end['binnumber'][1]})

# calculate the bin counts for the succesful moves
bin_counts = df_bin.value_counts().reset_index(name='bin_counts')
move_transition_matrix = np.zeros((bins[1], bins[0], bins[1], bins[0]))
move_transition_matrix[bin_counts['y'], bin_counts['x'],
                       bin_counts['end_y'], bin_counts['end_x']] = bin_counts.bin_counts.values

# and divide by the starting locations for all moves (including unsuccessful)
bin_start_locations = pitch.bin_statistic(move['x'], move['y'], bins=bins)
bin_start_locations = np.expand_dims(bin_start_locations['statistic'], (2, 3))
move_transition_matrix = np.divide(move_transition_matrix,
                                   bin_start_locations,
                                   out=np.zeros_like(move_transition_matrix),
                                   where=bin_start_locations!=0,
                                  )

##############################################################################
# Get the matrices
# ----------------
# Get the matrices from the dictionaries and turn nans into zeros
move_transition_matrix = np.nan_to_num(move_transition_matrix)
shot_probability_matrix = np.nan_to_num(shot_probability['statistic'])
move_probability_matrix = np.nan_to_num(move_probability['statistic'])
goal_probability_matrix = np.nan_to_num(goal_probability['statistic'])

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
# Plot the xT grid

path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
for_plotting = pitch.bin_statistic(event['x'], event['y'], bins=bins)  # new bin statistic for plotting only
for_plotting['statistic'] = xt
fig, ax = pitch.draw(figsize=(14, 9.625))
_ = pitch.heatmap(for_plotting, ax=ax)
_ = pitch.label_heatmap(for_plotting, ax=ax, str_format='{:.2%}', color='white', fontsize=14, va='center', ha='center',
                       path_effects=path_eff)

plt.show()  # If you are using a Jupyter notebook you do not need this line
