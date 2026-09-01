"""
=====================
Pitch control surface
=====================

This example shows how to overlay a dense model-generated surface on the pitch
with ``overlay_surface``: here a simple pitch-control model, where each cell is
the probability that the attacking team arrives first, based on player
distances. The same method works for any grid — expected threat surfaces,
xG models, or the output of your own control model.
"""

import matplotlib.pyplot as plt
import numpy as np

from mplsoccer import Pitch, VerticalPitch

np.random.seed(42)

# two teams of ten outfield players
attack = np.column_stack([np.random.uniform(20, 110, 10), np.random.uniform(5, 75, 10)])
defence = np.column_stack([np.random.uniform(30, 115, 10), np.random.uniform(5, 75, 10)])

# a naive control model: logistic difference of the distance
# to the nearest player of each team, evaluated on a dense grid
x = np.linspace(0, 120, 240)
y = np.linspace(0, 80, 160)
xx, yy = np.meshgrid(x, y)


def nearest_distance(players):
    dist = np.dstack([np.hypot(xx - px, yy - py) for px, py in players])
    return dist.min(axis=2)


control = 1 / (1 + np.exp(-(nearest_distance(defence) - nearest_distance(attack)) / 4))

##############################################################################
# Overlay the surface on a horizontal pitch

pitch = Pitch(pitch_type='statsbomb', line_zorder=2, line_color='white')
fig, ax = pitch.draw(figsize=(9, 6))
mesh = pitch.overlay_surface(control, cmap='RdBu_r', vmin=0, vmax=1, alpha=0.8, ax=ax)
pitch.scatter(attack[:, 0], attack[:, 1], c='#d60000', s=80,
              edgecolors='black', zorder=3, ax=ax)
pitch.scatter(defence[:, 0], defence[:, 1], c='#0044cc', s=80,
              edgecolors='black', zorder=3, ax=ax)
cbar = fig.colorbar(mesh, ax=ax, shrink=0.7)
cbar.set_label('probability the red team controls the location')

##############################################################################
# The same surface on a vertical pitch: ``overlay_surface`` switches the
# coordinates for you, so the array does not need to be transposed.

pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, line_color='white', half=True)
fig, ax = pitch.draw(figsize=(6, 6))
mesh = pitch.overlay_surface(control, cmap='RdBu_r', vmin=0, vmax=1, alpha=0.8, ax=ax)
pitch.scatter(attack[:, 0], attack[:, 1], c='#d60000', s=80,
              edgecolors='black', zorder=3, ax=ax)
pitch.scatter(defence[:, 0], defence[:, 1], c='#0044cc', s=80,
              edgecolors='black', zorder=3, ax=ax)

plt.show()  # If you are using a Jupyter notebook this is not needed
