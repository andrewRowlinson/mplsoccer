"""
==============
mplsoccer logo
==============
"""
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from matplotlib import rcParams
plt.style.use('ggplot')
plt.xkcd()

# plot the mplsoccer logo
pitch = Pitch(pitch_color='grass', stripe=True,
              figsize=(1280/rcParams['figure.dpi'], 640/rcParams['figure.dpi']),
              pad_left=8, pad_top=8, pad_bottom=8, pad_right=8)
fig, ax = pitch.draw()
annotation = ax.annotate('mplsoccer', (60, 40), fontsize=120, ha='center', va='center')
