"""
====================
Plot rotated markers
====================

This example shows how to plot rotated markers.

> ! Warning: The rotation angle is in degrees and assumes the original marker is pointing upwards ↑.
> Rotates the marker in degrees, clockwise. 0 degrees is facing the direction of play (left to right).
> In a horizontal pitch, 0 degrees is this way →, in a vertical pitch, 0 degrees is this way ↑
"""

from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
from mplsoccer.scatterutils import arrowhead_marker
import numpy as np
plt.style.use('ggplot')

pitch = Pitch(figsize=(10,8), axis=True, label=True)
fig, ax = pitch.draw()
n=15
x = np.linspace(0, 120, n)
y = np.linspace(0, 80, n)
rotate = np.linspace(0, 360, n).round(0).astype(np.int32)
pitch.scatter(x, y, rotation_degrees=rotate, marker=arrowhead_marker, edgecolors='black', s=3500, ax=ax)
for i in range(n):
    pitch.annotate(f'{rotate[i]}°', (x[i], y[i]), ha='center', va='center', fontsize=15, color='white', ax=ax)
    