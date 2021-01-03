"""
=====================
Plot football markers
=====================

This example shows how to plot football markers.
"""

from mplsoccer import Pitch
import matplotlib.pyplot as plt
plt.style.use('ggplot')

pitch = Pitch(figsize=(10, 8))
fig, ax = pitch.draw()
# 'edgecolors' sets the color of the pentagons and edges, 'c' sets the color of the hexagons
sc = pitch.scatter([70, 50], [60, 50],
                   marker='football', label='football black and white', ax=ax)
sc2 = pitch.scatter([20, 30], [10, 10],
                    marker='football', s=2000, edgecolors='blue', c='yellow', label='football blue and yellow', ax=ax)
sc3 = pitch.scatter([100, 20], [70, 70],
                    marker='football', s=1500, edgecolors='green', c='red', label='football red and green', ax=ax)
sc4 = pitch.scatter([80, 100], [30, 20],
                    marker='football', s=2500, edgecolors='black', c='purple', label='football black and purple', ax=ax)
leg = ax.legend(borderpad=1, markerscale=0.5, labelspacing=1.5, loc='upper center', fontsize=15)
