"""
=================================
Plotting formations and positions
=================================

The Pitch classes provide a dictionary of positions and their location on the pitch.

This is provided in two flavours, for lines of 5 players and for lines of 4 players,
to better control spacing.
"""

from mplsoccer import VerticalPitch

##############################################################################
# You can retrieve the position coordinates from ``pitch.dim`` using either
# the ``position_line5`` or the ``position_line4`` data class.

pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white', line_alpha=0.5)

# Get the coordinates for a striker, central defensive midfielder and central midfielders
striker_coordinates = pitch.dim.position_line5.ST
cdm_coordinates = pitch.dim.position_line5.CDM
rcm_coordinates = pitch.dim.position_line4.RCM
lcm_coordinates = pitch.dim.position_line4.LCM

##############################################################################
# You can then use these coordinates in scatter plots or any other type of normal
# mplsoccer plots

fig, ax = pitch.draw(figsize=(8, 6), constrained_layout=True, tight_layout=False)
# Plot the positions
pitch.scatter(striker_coordinates.x, striker_coordinates.y, s=100, ax=ax, color='red')
pitch.scatter(cdm_coordinates.x, cdm_coordinates.y, s=100, ax=ax, color='blue')
pitch.scatter(rcm_coordinates.x, rcm_coordinates.y, s=100, ax=ax, color='blue')
pitch.scatter(lcm_coordinates.x, lcm_coordinates.y, s=100, ax=ax, color='blue')

##############################################################################
# Below is a showcase of all available formations and their positions

# Create a grid of pitch
p = VerticalPitch('opta', line_alpha=0.5, pitch_color='grass', line_color='white')
COLS = 5
rows = len(p.formations) // COLS

fig, axes = p.grid(nrows=rows, ncols=COLS, title_height=0, endnote_height=0, figheight=20,
                   space=0.08)
axes = axes.flatten()

for i, formation in enumerate(sorted(p.formations)):
    position_dict = p.get_formation(formation)
    for position in position_dict:
        x, y = position_dict[position].x, position_dict[position].y
        p.scatter(x, y, color='black', s=350, ax=axes[i])
        p.annotate(xy=(x, y), text=position, color='white', fontsize=8, ha='center', va='center',
                   ax=axes[i])
    axes[i].set_title(formation, fontsize=10)
