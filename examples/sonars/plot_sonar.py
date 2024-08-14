"""
=====
Sonar
=====
There is a great blog on the history of Sonars by
`StatsBomb <https://statsbomb.com/articles/soccer/a-sneak-peak-at-iq-tactics-a-brief-history-of-radials-sonars-wagon-wheels-in-soccer/>`_.
Sonars show more information than heatmaps by introducing the angle of passes, shots
or other events.

The following examples show how to use the ``sonar`` method to plot
a single sonar. There is more information on how to customize the 
segments in :ref:`sphx_glr_gallery_sonars_plot_bin_statistic_sonar.py`.
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
