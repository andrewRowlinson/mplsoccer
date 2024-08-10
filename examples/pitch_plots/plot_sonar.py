"""
=====
Sonar
=====

This example shows how to plot sonars.
"""
from mplsoccer import Pitch
from mplsoccer import Sbopen

parser = Sbopen()
df = parser.event(19789)[0] # 0 index is the event file
df = df[(df.team_name == 'Chelsea FCW') & (df.type_name == 'Pass') & (df.outcome_name.isnull())].copy()

##############################################################################
# Calculate binned statistics
# ---------------------------

pitch = Pitch()
angle, distance = pitch.calculate_angle_and_distance(df.x, df.y, df.end_x, df.end_y)
bin_statistic = pitch.bin_statistic_sonar(df.x, df.y, angle)
print(bin_statistic.keys())
