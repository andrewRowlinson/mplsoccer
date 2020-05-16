"""
==============================
Pass plot using lines and cmap
==============================

This example shows how to plot all passes leading to shots from a team using a colormap (cmap).
"""

from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from matplotlib import rcParams

rcParams['text.color'] = '#c7d5cc'  # set the default text color

# get event dataframe for game 7478, create a dataframe of the passes, and a boolean mask for the outcome
df = read_event(f'{EVENT_SLUG}/7478.json',
                related_event_df=False, shot_freeze_frame_df=False, tactics_lineup_df=False)['event']

##############################################################################
# Filter datasets to only include passes leading to shots, and goals

team1 = 'Seattle Reign'
team2 = 'Houston Dash'
df_pass = df.loc[(df.pass_assisted_shot_id.notnull()) & (df.team_name == team1),
                 ['x', 'y', 'pass_end_x', 'pass_end_y', 'pass_assisted_shot_id']]

df_shot = df.loc[(df.type_name == 'Shot') & (df.team_name == team1),
                 ['id', 'outcome_name', 'shot_statsbomb_xg']].rename({'id': 'pass_assisted_shot_id'}, axis=1)

df_pass = df_pass.merge(df_shot, how='left').drop('pass_assisted_shot_id', axis=1)

mask_goal = df_pass.outcome_name == 'Goal'

##############################################################################
# View the pass dataframe.

df_pass

##############################################################################
# Plotting

# Setup the pitch
pitch = Pitch(pitch_type='statsbomb', orientation='vertical', pitch_color='#22312b', line_color='#c7d5cc',
              figsize=(16, 11), view='half', pad_top=2, tight_layout=True)
fig, ax = pitch.draw()

# Plot the completed passes
pitch.lines(df_pass.x, df_pass.y, df_pass.pass_end_x, df_pass.pass_end_y,
            lw=10, transparent=True, comet=True, cmap='jet',
            label='pass leading to shot', ax=ax)

# Plot the goals
pitch.scatter(df_pass[mask_goal].pass_end_x, df_pass[mask_goal].pass_end_y, s=700,
              marker='football', edgecolors='black', c='white', zorder=2,
              label='goal', ax=ax)
pitch.scatter(df_pass[~mask_goal].pass_end_x, df_pass[~mask_goal].pass_end_y,
              edgecolors='white', c='#22312b', s=700, zorder=2,
              label='shot', ax=ax)
# Set the title
ax.set_title(f'{team1} passes leading to shots \n vs {team2}', fontsize=30)

# set legend
ax.legend(facecolor='#22312b', edgecolor='None', fontsize=20, loc='lower center', handlelength=4)

# Set the figure facecolor
fig.set_facecolor('#22312b')
