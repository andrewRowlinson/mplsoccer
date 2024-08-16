"""
==========
Sonar Grid
==========
StatsBomb has a great
`blog <https://statsbomb.com/articles/soccer/a-sneak-peak-at-iq-tactics-a-brief-history-of-radials-sonars-wagon-wheels-in-soccer/>`_
on the history of Sonars. Sonars show more information than heatmaps
by introducing the angle of passes, shots or other events.

The following examples show how to use the ``sonar_grid`` method to plot
a grid of sonars. I have copied a layout by `Ted Knutson <https://x.com/mixedknuts>`_ the founder
of StatsBomb. However, I encourage you to try out your variations as the API
allows you to mix and match different metrics for setting the slice length
and colors. Given the huge array of possible combinations, you should also
add a key to explain the viz because there isn’t a single standard for Sonars.

More information is available on how to customize the grid cells and segments in
:ref:`sphx_glr_gallery_sonars_plot_bin_statistic_sonar.py`.
"""
import matplotlib.pyplot as plt
import numpy as np

from mplsoccer import Pitch, Sbopen

##############################################################################
# Load the first game that Messi played as a false-9.
parser = Sbopen()
df = parser.event(69249)[0]  # 0 index is the event file
df_pass = df[(df.type_name == 'Pass') & (df.team_name == 'Barcelona') &
             (~df.sub_type_name.isin(['Free Kick', 'Throw-in',
                                      'Goal Kick', 'Kick Off', 'Corner']))].copy()
df_pass['success'] = df_pass['outcome_name'].isnull()
# There aren't that many throw-ins in this match so we will plot the data from both teams
df_throw = df[df.sub_type_name == 'Throw-in'].copy()
df_throw['success'] = df_throw['outcome_name'].isnull()

##############################################################################
# Calculate the angle and distance and create the binned statistics
pitch = Pitch(line_color='#f0eded')
angle, distance = pitch.calculate_angle_and_distance(df_pass.x, df_pass.y, df_pass.end_x,
                                                     df_pass.end_y)
throw_angle, throw_distance = pitch.calculate_angle_and_distance(df_throw.x, df_throw.y,
                                                                 df_throw.end_x, df_throw.end_y)
# stats for passes
bins = (6, 4, 5)
bs_count_all = pitch.bin_statistic_sonar(df_pass.x, df_pass.y, angle, bins=bins, center=True)
bs_success = pitch.bin_statistic_sonar(df_pass.x, df_pass.y, angle, values=df_pass.success,
                                       statistic='mean', bins=bins, center=True)
bs_distance = pitch.bin_statistic_sonar(df_pass.x, df_pass.y, angle, values=distance,
                                        statistic='mean', bins=bins, center=True)
# note we do not center the throw-in segments as throw-ins generally don't go backwards :D
throw_bins = (6, 5, 12)
bs_throw_success = pitch.bin_statistic_sonar(df_throw.x, df_throw.y, throw_angle,
                                             values=df_throw.success, statistic='mean',
                                             bins=throw_bins, center=False)
bs_throw_distance = pitch.bin_statistic_sonar(df_throw.x, df_throw.y, throw_angle,
                                              values=throw_distance, statistic='mean',
                                              bins=throw_bins, center=False)

##############################################################################
# Here, we plot a Sonar grid that copies the style of StatsBomb IQ with
# average distance for the slice length and the success rate of the passes for the color.
fig, ax = pitch.draw(figsize=(8, 5.5))
axs = pitch.sonar_grid(bs_distance,
                       # here we set the color of the slices based on the % success of the pass
                       stats_color=bs_success, cmap='viridis', ec='#202020',
                       # we set the color map to be mapped from 0% to 100%
                       # rather than the default min/max of the values
                       vmin=0, vmax=1,
                       # the axis minimum and maximum are set automatically to the min/max
                       # here we set it explicity to 0 and 50 units
                       rmin=0, rmax=50,
                       zorder=3,  # slices appear above the axis lines
                       width=15,
                       # the size of the sonar axis in data coordinates. Can use height instead
                       ax=ax)

# you can turn on the axis and labels with axis=True and label=True in sonar_grid
# here, we manually make changes so we can change the styling
for ax in axs.flatten():
    ax.grid(False, axis='x')  # Turn off x-axis spokes
    ax.grid(True, axis='y', lw=1, ls='--',
            color='#969696')  # Turn on y-axis rings and change line style
    ax.set_yticks(np.arange(0, 51, 10))  # y-axis rings every 10 distance (0, 10, 20, 30, 40, 50)
    ax.spines['polar'].set_visible(True)
    ax.spines['polar'].set_color('#202020')

##############################################################################
# Another popular variation is to have the number of passes as the slice
# length and another metric as the color (e.g. success rate or pass distance).
fig, ax = pitch.draw(figsize=(8, 5.5))
axs = pitch.sonar_grid(bs_count_all,
                       stats_color=bs_distance, cmap='Blues', vmin=0, vmax=50,
                       width=15,
                       # set the axis to the next multiple of 5
                       rmin=0, rmax=np.ceil(bs_count_all['statistic'].max() / 5) * 5,
                       ax=ax)

##############################################################################
# Here, we plot a Sonar grid for throw-ins.
# The method's defaults do not plot the Sonar grid cell if all the values are numpy_nan
# (``exclude_nan=True``) or all the values are zero (``exclude_zeros=True``).
fig, ax = pitch.draw(figsize=(8, 5.5))
axs = pitch.sonar_grid(bs_throw_distance,
                       # here we set the color of the slices based on the % success of the pass
                       stats_color=bs_throw_success, cmap='viridis', ec='#202020',
                       exclude_zeros=True,
                       # we set the color map to be mapped from 0% to 100%
                       # rather than the default min/max of the values
                       vmin=0, vmax=1,
                       # the axis minimum and maximum are set automatically to the min/max
                       # here we set it explicity to 0 and 50 units
                       rmin=0, rmax=50,
                       zorder=3,  # slices appear above the axis lines
                       width=15,
                       # the size of the sonar axis in data coordinates. Can use height instead
                       ax=ax)

# you can turn on the axis and labels with axis=True and label=True in sonar_grid
# here, we manually make changes so we can change the styling
for ax in axs.flatten():
    if ax is not None:  # a lot of the axis are None as there are no values in the middle of the pitch
        ax.grid(True, axis='y', lw=1, ls='--',
                color='#969696')  # Turn on y-axis rings and change line style
        ax.set_yticks(
            np.arange(0, 51, 10))  # y-axis rings every 10 distance (0, 10, 20, 30, 40, 50)
        ax.spines['polar'].set_visible(True)
        ax.spines['polar'].set_color('#202020')

plt.show()  # If you are using a Jupyter notebook you do not need this line
