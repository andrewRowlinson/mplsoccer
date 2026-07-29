"""
===========
Sonar Zones
===========
The ``bin_statistic_sonar_zones`` method bins angles within any
rectangular tiling and ``sonar_zones`` plots a sonar at
the centre of each zone. Here we use the Juego de Posición zones.

More information is available on how to customize the segments in
:ref:`sphx_glr_gallery_sonars_plot_bin_statistic_sonar.py` and on the
zone layouts in :ref:`sphx_glr_gallery_pitch_plots_plot_heatmap_zones.py`.
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import Pitch, Sbopen

##############################################################################
# Load the first game that Messi played as a false-9.
parser = Sbopen()
df = parser.event(69249)[0]  # 0 index is the event file
df_pass = df[(df.type_name == 'Pass') & (df.team_name == 'Barcelona') &
             (~df.sub_type_name.isin(['Free Kick', 'Throw-in',
                                      'Goal Kick', 'Kick Off', 'Corner']))].copy()
df_pass['success'] = df_pass['outcome_name'].isnull()

##############################################################################
# Calculate the angle and distance and create the zone statistics
pitch = Pitch(line_color='#f0eded', line_zorder=2)
angle, distance = pitch.calculate_angle_and_distance(df_pass.x, df_pass.y, df_pass.end_x,
                                                     df_pass.end_y)
zones, names = pitch.positional_zones('full')
bs_count = pitch.bin_statistic_sonar_zones(df_pass.x, df_pass.y, angle, zones,
                                           names=names, angle_bins=5, center=True)
bs_success = pitch.bin_statistic_sonar_zones(df_pass.x, df_pass.y, angle, zones,
                                             values=df_pass.success, statistic='mean',
                                             names=names, angle_bins=5, center=True)

##############################################################################
# Plot a sonar in each Juego de Posición zone with the number of passes as
# the slice length and the success rate of the passes for the color.
fig, ax = pitch.draw(figsize=(8, 5.5))
axs = pitch.sonar_zones(bs_count,
                        # here we set the color of the slices based on the % success
                        stats_color=bs_success, cmap='viridis', ec='#202020',
                        # we set the color map to be mapped from 0% to 100%
                        # rather than the default min/max of the values
                        vmin=0, vmax=1,
                        zorder=3,  # slices appear above the axis lines
                        # the size of the sonar axis in data coordinates
                        width=13,
                        ax=ax)

##############################################################################
# The zone statistics also work with ``heatmap_zones``, so you can shade
# each zone by its total number of passes underneath the sonars.
pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                       ['#15242e', '#4393c4'], N=10)
fig, ax = pitch.draw(figsize=(8, 5.5))
zones_count = pitch.bin_statistic_zones(df_pass.x, df_pass.y, zones)
pc = pitch.heatmap_zones(zones_count, ax=ax, cmap=pearl_earring_cmap, edgecolor='#202020')
axs = pitch.sonar_zones(bs_count, ec='#202020', fc='cornflowerblue',
                        zorder=3, width=13, ax=ax)

plt.show()  # If you are using a Jupyter notebook you do not need this line
