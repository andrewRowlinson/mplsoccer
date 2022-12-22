"""
=======================
Plotting position locations on the pitch with FormationHelper
=======================

The Pitch classes provide a dictionary of positions and their location on the pitch.

This is provided in two flavours, for lines of 5 players and for lines of 4 players, to better control spacing.

"""

from mplsoccer import VerticalPitch

# Get the enum that specifies whether you want locations using the 4 or 5 player lines
from mplsoccer import PositionLineType


##############################################################################
# You can retrieve the position coordinates using the ``dim.positions`` attribute.
# Whether you want the coordinates for the 4 or 5 player lines is specified by the ``PositionLineType`` enum.

pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white', line_alpha=0.5)

striker_coordinates = pitch.dim.positions[PositionLineType.FIVE_PER_LINE]['ST']
cdm_coordinates = pitch.dim.positions[PositionLineType.FIVE_PER_LINE]['CDM']
rcm_coordinates = pitch.dim.positions[PositionLineType.FIVE_PER_LINE]['RCM']
lcm_coordinates = pitch.dim.positions[PositionLineType.FIVE_PER_LINE]['LCM']


##############################################################################
# You can then use these coordinates in scatter plots or any other type of normal 
# mplsoccer plots
fig, ax = pitch.draw(figsize=(8, 6), constrained_layout=True, tight_layout=False)

# Get the coordinates for a striker, central defensive midfielder and central midfielders


# Plot the positions
pitch.scatter(striker_coordinates['x'], striker_coordinates['y'], s=100, ax=ax, color='red')
pitch.scatter(cdm_coordinates['x'], cdm_coordinates['y'], s=100, ax=ax, color='blue')
pitch.scatter(rcm_coordinates['x'], rcm_coordinates['y'], s=100, ax=ax, color='blue')
pitch.scatter(lcm_coordinates['x'], lcm_coordinates['y'], s=100, ax=ax, color='blue')

##############################################################################
# As an extra resource, the ``FormationHelper`` class can be used to get a list of 
# tuples of position name and PositionLineType enum value for each position in every common formation.
# The following formations have been provided

from mplsoccer import FormationHelper
print(sorted(FormationHelper.formations))

##############################################################################
# Below is a showcase of all available formations and their positions

#Create a grid of pitch
p = VerticalPitch('opta',line_alpha=0.5, pitch_color='grass', line_color='white')
cols = 5
rows = len(FormationHelper.formations) // cols 

fig, axes = p.grid(nrows=rows, ncols=cols, title_height=0, endnote_height=0, figheight=20, space=0.08)
axes = axes.flatten()

for i, formation in enumerate(sorted(FormationHelper.formations)):
    position_list = FormationHelper.get_formation(formation)
    for position, four_or_five_player_line in position_list:
        x, y = p.dim.positions[four_or_five_player_line][position]['x'], p.dim.positions[four_or_five_player_line][position]['y']
        p.scatter(x,y, color='black', s=350, ax=axes[i])
        p.annotate(xy=(x,y), text=position, color='white', fontsize=8, ha='center', va='center', ax=axes[i])
    axes[i].set_title(formation, fontsize=10)