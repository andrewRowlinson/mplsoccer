"""
=======
Markers
=======

This example shows how to plot special football markers
designed by the wonderful Kalle Yrjänä.
"""

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt

from mplsoccer import Pitch, football_left_boot_marker, football_right_boot_marker, \
    football_shirt_marker, FontManager, VerticalPitch

fm_jersey = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                        'jersey15/Jersey15-Regular.ttf')
path_eff = [path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()]

##############################################################################
# Plot football markers on a pitch
pitch = Pitch()
fig, ax = pitch.draw(figsize=(8, 5.5))
pitch.scatter(27.5, 30, marker=football_shirt_marker, s=20000,
              ec='black', fc='#DA291C', ax=ax)
pitch.scatter(15, 60, marker=football_left_boot_marker, s=5000,
              ec='#f66e90', fc='#2377c0', ax=ax)
pitch.scatter(40, 60, marker=football_right_boot_marker, s=5000,
              ec='#f66e90', fc='#2377c0', ax=ax)
pitch.text(27.5, 35, '22', va='center', ha='center', color='white', fontproperties=fm_jersey.prop,
           path_effects=path_eff, fontsize=50, ax=ax)

##############################################################################
# Plot a formation of football shirts
pitch = VerticalPitch(pitch_type='opta')
fig, ax = pitch.draw(figsize=(9, 6))
sc = pitch.formation('442', kind='scatter', marker=football_shirt_marker, s=5000, ec='black',
                     fc='#DA291C', ax=ax)
texts = pitch.formation('442', kind='text',
                        text=[1, 2, 5, 6, 3, 7, 4, 8, 11, 10, 9],
                        va='center', ha='center', fontproperties=fm_jersey.prop,
                        path_effects=path_eff, fontsize=32, color='white',
                        positions=[1, 2, 5, 6, 3, 7, 4, 8, 11, 10, 9],
                        xoffset=-3, ax=ax)

plt.show()  # If you are using a Jupyter notebook you do not need this line
