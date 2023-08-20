"""
===========
How quickly the team produced a shot after a player passed the ball?
===========

The following script associates each pass to a different color, based
on how quickly a shot was produced after that pass.
"""

from mplsoccer import Pitch, Sbopen
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import rcParams
import matplotlib.pyplot as plt

rcParams['font.family'] = 'montserrat'
rcParams['text.color'] = 'black'

# Get event dataframe for game 7478
parser = Sbopen()
df, related, freeze, tactics = parser.event(7478)

##############################################################################
# Boolean mask for filtering all the passes from a single player

team1, team2 = df.team_name.unique()
player = "Megan Anna Rapinoe"
mask_player = (df.type_name == 'Pass') & (df.team_name == team1) & (df.player_name == player)

##############################################################################
# Filter the dataset to only include passes from one player, then get the 
# boolean mask for the completed passes.

df_pass = df.loc[mask_player, ['x', 'y', 'end_x', 'end_y', 'outcome_name']]
mask_complete = df_pass.outcome_name.isnull()

##############################################################################
# Find the temporal distance between the pass and the subsequent shot 
# (if present), checking that there is no possession loss in the build 
# up to the shot.

df['distance_to_shot'] = -1

for idx, row in df.iterrows():
    if row['type_name'] == 'Pass':
        current_team = row['possession_team_name']
        current_team_name = row['team_name']
        
        next_shot_idx = idx + 1
        while next_shot_idx < len(df):
            next_event = df.iloc[next_shot_idx]
            if (next_event['type_name'] == 'Shot' and
                next_event['possession_team_name'] == current_team and
                next_event['team_name'] == current_team_name):
                time_distance = (next_event['minute'] - row['minute'])*60 + (next_event['second'] - row['second'])
                df.at[idx, 'distance_to_shot'] = time_distance
                break
            elif next_event['possession_team_name'] != current_team:
                break
            next_shot_idx += 1

##############################################################################
# Filter the dataset to only include passes from one player, then get the 
# boolean mask for the completed passes leading to a shot at the end of
# the build up.

df_pass = df.loc[mask_player, ['x', 'y', 'end_x', 'end_y', 'outcome_name', 'distance_to_shot']]
mask_shot_complete = (df_pass.outcome_name.isnull()) & (df_pass.distance_to_shot >= 0)
df_pass_leading_to_shot = df_pass[mask_shot_complete]

##############################################################################
# Create the cmap and find min/max time values.

time_min = df_pass_leading_to_shot['distance_to_shot'].min()
time_max = df_pass_leading_to_shot['distance_to_shot'].max()

cmap = LinearSegmentedColormap.from_list("Nord Palette - Nord10 to Nord11", ['#bf616a', '#5e81ac'], N=100)

##############################################################################
# Plotting

# Set up the pitch
pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='#4C566A')
fig, ax = pitch.draw(figsize=(12, 10), constrained_layout=True, tight_layout=True)
fig.set_facecolor('white')

# Find the color of each pass
def assign_color(row):
    normalized_distance = (row['distance_to_shot'] - time_min) / (time_max - time_min)
    color = cmap(normalized_distance)
    return color

pass_color = df_pass_leading_to_shot.apply(assign_color, axis=1)

# Plot the completed passes leading to a shot
pitch.arrows(df_pass_leading_to_shot.x, df_pass_leading_to_shot.y,
             df_pass_leading_to_shot.end_x, df_pass_leading_to_shot.end_y,
             width=3, headwidth=5, headlength=5,
             color=pass_color, ax=ax)

# Create the cbar and the endnotes
scm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=time_min, vmax=time_max))
scm.set_array([])
cax = ax.inset_axes([0.25, 1.02, 0.5, 0.04])
cbar = plt.colorbar(scm, cax=cax, orientation='horizontal')
cbar.set_label('Time distance to the following shot (seconds)', fontsize=12, labelpad=10)
cbar.ax.xaxis.set_label_position('top')
cbar.ax.xaxis.set_ticks_position('bottom')
cbar.ax.tick_params(labelsize=10)

ax.text(99.5, 82, "@your_twitter_handle", fontsize=12, va="center")
ax.text(
    0,
    82,
    f"{team1} vs {team2} ~ All {player} passes part of a shot build up.",
    fontsize=11,
    va="center",
    ha="left",
)
ax.text(
    0,
    84,
    f"Statsbomb open data.",
    fontsize=11,
    va="center",
    ha="left",
)

plt.show()