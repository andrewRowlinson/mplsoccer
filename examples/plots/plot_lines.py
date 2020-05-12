"""
=====================
Pass plot using lines
=====================

This example shows how to plot all passes from a team in a match as lines.
"""

from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from matplotlib import rcParams

rcParams['text.color'] = '#c7d5cc'  # set the default text color

# get event dataframe for game 7478, create a dataframe of the passes, and a boolean mask for the outcome
df = read_event(f'{EVENT_SLUG}/7478.json',
                related_event_df=False, shot_freeze_frame_df=False, tactics_lineup_df=False)['event']

##############################################################################
# Boolean mask for filtering the dataset by team

team1, team2 = df.team_name.unique()
mask_team1 = (df.type_name == 'Pass') & (df.team_name == team1)

##############################################################################
# Filter dataset to only include one teams passes and get boolean mask for the completed passes

df_pass = df.loc[mask_team1, ['x', 'y', 'pass_end_x', 'pass_end_y', 'outcome_name']]
mask_complete = df_pass.outcome_name.isnull()

##############################################################################
# View the pass dataframe.

df_pass.head()

##############################################################################
# Plotting

# Setup the pitch
pitch = Pitch(pitch_type='statsbomb', orientation='horizontal',
              pitch_color='#22312b', line_color='#c7d5cc', figsize=(16, 11),
              constrained_layout=False, tight_layout=True)
fig, ax = pitch.draw()

# Plot the completed passes
lc1 = pitch.lines(df_pass[mask_complete].x, df_pass[mask_complete].y,
                  df_pass[mask_complete].pass_end_x, df_pass[mask_complete].pass_end_y,
                  lw=5, transparent=True, comet=True,
                  color='#ad993c', ax=ax)

# Plot the other passes
lc2 = pitch.lines(df_pass[~mask_complete].x, df_pass[~mask_complete].y,
                  df_pass[~mask_complete].pass_end_x, df_pass[~mask_complete].pass_end_y,
                  lw=5, transparent=True, comet=True,
                  color='#ba4f45', ax=ax)

# Plot the legend
ax.legend(facecolor='#22312b', edgecolor='None', fontsize=20, loc='upper left', handlelength=4)

# Set the title
ax.set_title(f'{team1} passes vs {team2}', fontsize=30)

# Set the figure facecolor
fig.set_facecolor('#22312b')
