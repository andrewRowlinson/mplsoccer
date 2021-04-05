"""
=======================================
Plot lines with varying width and color
=======================================

This example shows how to plot lines with different colors and linewidths.
This would be useful for pass maps.
"""

from mplsoccer.pitch import Pitch
import numpy as np
from matplotlib.cm import get_cmap
import matplotlib.pyplot as plt
plt.style.use('ggplot')

##############################################################################
# Create a lines plot with varying widths and colors

# setup the pitch
pitch = Pitch(axis=True, label=True, pad_left=5, pad_right=5, pad_top=5, pad_bottom=5)
fig, ax = pitch.draw()
# get the pitch extents
xmin, xmax, ymin, ymax = pitch.extent
# create 10 lines across the pitch
ystart = np.linspace(ymin - 5, ymax + 5, 10)
yend = np.linspace(ymin - 5, ymax + 5, 10)
xstart = np.repeat(xmin + 5, 10)
xend = np.repeat(xmax - 5, 10)
# create linearly increasing linewidths
lw = np.linspace(1, 10, 10)
# create 10 colors from a color map (linearly spaced)
color = get_cmap('plasma')(np.linspace(0, 1, 10))
# plot the lines
pitch.lines(xstart, ystart, xend, yend, color=color, lw=lw, ax=ax)
