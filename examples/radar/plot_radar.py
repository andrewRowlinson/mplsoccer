"""
============
Radar Charts
============

* ``mplsoccer``, ``radar_chart`` module helps one to plot radar charts in a few lines of code.

* The radar-chart theme is inspired by `StatsBomb <https://twitter.com/StatsBomb/>`_
  and `Rami Moghadam <https://cargocollective.com/ramimo/2013-NBA-All-Stars>`_ 

* Here we will show some examples on how to use ``mplsoccer`` to plot radar charts.

First we import the Radar class
"""

from mplsoccer import Radar

##############################################################################
# Making a simple Radar Chart
# ---------------------------
# Here we will make a very simple radar chart using ``mplsoccer`` module ``radar_chart``. 
# We will be making use of ``ranges``, ``params``, ``values`` and ``radar_color`` parameter.

# parameter names
params = ['xAssist', 'Key Passes', 'Crosses Into Box', 'Cross Completion %', 'Deep Completions',
          'Progressive Passes', 'Prog. Pass Accuracy', 'Dribbles', 'Progressive Runs',
          'PADJ Interceptions', 'Succ. Def. Actions', 'Def Duel Win %']

# range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 6.3), (19.51, 50.0), (0.35, 1.61),
          (6.45, 11.94), (62.9, 79.4), (0.43, 4.08), (0.6, 2.33),
          (4.74, 7.2), (8.59, 12.48), (50.66, 66.67)]

# parameter value
values = [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29]

# instantiate object
radar = Radar()

# plot radar
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                                 radar_color=['#B6282F', '#FFFFFF'])
fig.tight_layout()

