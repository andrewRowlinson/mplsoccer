"""
===================
Textured background
===================

This example shows how to plot a pitch with a textured background behind it.
"""

from urllib.request import urlopen

from PIL import Image
import matplotlib.pyplot as plt

from mplsoccer.pitch import Pitch
from mplsoccer.utils import add_image

# opening the background image
# pic by NASA/Expedition 40 crew member
# available at: https://commons.wikimedia.org/wiki/File:ISS-40_Thunderheads_near_Borneo.jpg
IMAGE_URL = ('https://upload.wikimedia.org/wikipedia/commons/'
             '1/1d/ISS-40_Thunderheads_near_Borneo.jpg')
image = Image.open(urlopen(IMAGE_URL))

pitch = Pitch(pitch_color='None')
fig, ax = pitch.draw(tight_layout=False)
# adding the image and the image credits
ax_image = add_image(image, fig, left=0, bottom=0, width=1, height=1)
ax.text(50, 75, 'cloud pic by\nNASA/Expedition 40 crew member', color='white')
# set the pitch to be plotted after the image
# note these numbers can be anything like 0.5, 0.2 as long
# as the image zorder is behind the pitch zorder
ax.set_zorder(1)
ax_image.set_zorder(0)
# save with 'tight' and no padding to avoid borders
# fig.savefig('cloud.png', bbox_inches='tight', pad_inches=0)

plt.show()  # If you are using a Jupyter notebook you do not need this line
