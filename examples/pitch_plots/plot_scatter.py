"""
============
Plot scatter
============

This example shows how to plot a scatter chart.
"""

from mplsoccer import Pitch
import matplotlib.pyplot as plt
plt.style.use('ggplot')

pitch = Pitch(figsize=(10, 8))
fig, ax = pitch.draw()
sc = pitch.scatter([70, 50, 20, 60, 90], [60, 50, 20, 10, 30],
                   c=['red', 'blue', 'green', 'yellow', 'orange'],
                   s=200, label='scatter', ax=ax)
leg = ax.legend(borderpad=1, markerscale=0.5, labelspacing=1.5, loc='upper center', fontsize=15)
