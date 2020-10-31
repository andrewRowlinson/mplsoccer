from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import numpy as np


def grass_cmap():
    cmap = LinearSegmentedColormap.from_list('grass', [(0.25, 0.44, 0.12, 1), (0.48, 1, 0.55, 1)], N=50)
    cmap = cmap(np.linspace(0, 1, 50))
    cmap = np.concatenate((cmap[::-1], cmap))
    cmap = cmap[40: -20]
    cmap = ListedColormap(cmap)
    return cmap
