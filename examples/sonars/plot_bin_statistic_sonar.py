"""
======
Sonars
======
Sonars were first introduced by `Eliot McKinley <https://x.com/etmckinley>`_.
They show more information than heatmaps by introducing the angle of passes, shots
or other events.
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
# Plot the Pass Sonar
pitch = Pitch()
angle, distance = pitch.calculate_angle_and_distance(df.x, df.y, df.end_x, df.end_y)
bs = pitch.bin_statistic_sonar(df.x, df.y, angle, bins=(6, 4, 4), center=True)
fig, ax = pitch.draw(figsize=(8, 5.5))
axs = pitch.sonar_grid(bs, width=15, fc='cornflowerblue', ec='black', ax=ax)
