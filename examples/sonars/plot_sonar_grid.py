"""
==========
Sonar Grid
==========
Sonars were first introduced by `Eliot McKinley <https://x.com/etmckinley>`_.
They show more information than heatmaps by introducing the angle of passes, shots
or other events.

The following examples show how to use the ``sonar_grid`` method to plot
a grid of sonars. There is more information on how to customize the grid cells
and segments in :ref:`sphx_glr_gallery_sonars_plot_bin_statistic_sonar.py`.
"""
from mplsoccer import Pitch, VerticalPitch, Sbopen
import numpy as np
import matplotlib.pyplot as plt

##############################################################################
# Load the first game that Messi played as a false-9.
parser = Sbopen()
df = parser.event(69249)[0]  # 0 index is the event file
df = df[((df.type_name == 'Pass') & (df.outcome_name.isnull()) & # succesful passes
         (df.team_name == 'Barcelona')
        )].copy()

plt.show()  # If you are using a Jupyter notebook you do not need this line
