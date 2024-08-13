"""
===================
Bin Statistic Sonar
===================
Sonars were first introduced by `Eliot McKinley <https://x.com/etmckinley>`_.
They show more information than heatmaps by introducing the angle of passes, shots
or other events.

The following example shows how to use `bin_statistic_sonar`, which bins data by
the pitch grid cells (e.g. 4 by 4) and angles within the grid cell, e.g. 0-180 degrees.
"""
from mplsoccer import Pitch, Sbopen

##############################################################################
# Load the first game that Messi played as a false-9.
parser = Sbopen()
df = parser.event(69249)[0]  # 0 index is the event file
df = df[((df.type_name == 'Pass') & (df.outcome_name.isnull()) & # succesful passes
         (df.team_name == 'Barcelona')
        )].copy()

##############################################################################
# Plot a Pass Sonar
# -----------------
# The follow example calculates the angle and distance for each pass.
# The data is then binned into 6 by 4 grid cells. Within each grid cell, the
# angles are binned into 4 segments (360 / 4 = 90 degrees each).
# The default counts the number of actions (passes) in each segment.
pitch = Pitch()
angle, distance = pitch.calculate_angle_and_distance(df.x, df.y, df.end_x, df.end_y)
bs = pitch.bin_statistic_sonar(df.x, df.y, angle,
                               bins=(6, 4, 4), # x, y, angle binning
                               # center the first angle, so it starts at -45 degrees
                               center=True)
fig, ax = pitch.draw(figsize=(8, 5.5))
axs = pitch.sonar_grid(bs, width=15, fc='cornflowerblue', ec='black', ax=ax)
