"""
======
Photos
======

This example shows how to plot photos in your charts.
"""

from mplsoccer.pitch import Pitch
from PIL import Image
import numpy as np
from urllib.request import urlopen
import matplotlib.pyplot as plt
plt.style.use('dark_background')

##############################################################################
# Setup a figure size and get the aspect ratio
# ############################################

# set a figure size and get the figure aspect ratio (width/height)
figsize = (16, 9)  # 16 by 9 is a good ratio for twitter images
fig_aspect = figsize[0] / figsize[1]

##############################################################################
# Load an image of Messi and get the aspect ratio
# ###############################################

# load the image and get the image aspect ratio (width/height)
image_url = 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Messi_vs_Nigeria_2018.jpg'
image = np.array(Image.open(urlopen(image_url)))
image_height, image_width, _ = image.shape
image_aspect = image_width / image_height

##############################################################################
# Plotting an image over a pitch
# ##############################
# 
# To plot images you use ``Axes.imshow()`` in matplotlib.
# We are going to draw a pitch and then overlay ontop an image of Messi on a new axis.

# draw the pitch
pitch = Pitch(figsize=figsize, tight_layout=False, line_zorder=2)
fig, ax = pitch.draw()

# set the image display width to 20% (0.2) of the total figure
# and calculate the image display height based on the aspect ratios of the image and figure
image_display_width = 0.2
image_display_height = image_display_width / image_aspect * fig_aspect

# add a new axis for the Messi image
ax_image = fig.add_axes((0.55,  # 55% in from the left of the image
                         0.2,  # 20% in from the bottom of the image
                         image_display_width, image_display_height))
ax_image.axis('off')  # axis off so no labels/ ticks
img = ax_image.imshow(image, alpha=0.9,  # slightly transparent so lines show through
                      interpolation='hanning')  # hanning interpolation is used as downsampling image

##############################################################################
# Photo from: https://en.wikipedia.org/wiki/Lionel_Messi#/media/File:Messi_vs_Nigeria_2018.jpg;
# License: https://creativecommons.org/licenses/by-sa/3.0/;
# Creator: Кирилл Венедиктов

##############################################################################
# More control over the images and axis
# #####################################
# 
# For more control over where the images are placed, you can create a blank figure with ``plt.figure()``
# and then use ``Figure.add_axes()`` to add seperate axes for each of the plot elements.

# setup a blank figure
fig = plt.figure(figsize=figsize)

# setup a Pitch object
pitch = Pitch(figsize=figsize, tight_layout=False, pad_bottom=0.5, pad_top=0.5, pad_left=0.5, pad_right=0.5,
              line_zorder=2)

# we are going to add an axis for the pitch
# the width will be 65% (0.65) of the total figure
# we then calculate the pitch display height and draw the pitch on the new axis
pitch_display_width = 0.65
pitch_display_height = pitch_display_width / pitch.ax_aspect * fig_aspect
ax1 = fig.add_axes((0.05,  # 5% in from the left of the image
                    0.05,  # 5% in from the bottom of the image
                    pitch_display_width, pitch_display_height))
pitch.draw(ax=ax1)

# we are also going to add the Messi image to the top of the figure as a new axis
# but this time the width will be 8% of the figure
image_display_width = 0.08
image_display_height = image_display_width / image_aspect * fig_aspect
ax2 = fig.add_axes((0.054,  # slightly right from the pitch position as accounts for the pitch padding
                    0.84,  # near the top of the figure
                    image_display_width, image_display_height))
ax2.imshow(image, interpolation='hanning')  # hanning interpolation is used as we are downsampling the image
ax2.axis('off')

# and the Messi image to the bottom right of the figure on a new axis
# but this time the width will be 20% of the figure
image_display_width = 0.2
image_display_height = image_display_width / image_aspect * fig_aspect
ax3 = fig.add_axes((0.75,  # 75% in from the left of the figure
                    0.054,  # slightly up from pitch position as accounts for pitch padding
                    image_display_width, image_display_height))
ax3.imshow(image, interpolation='hanning')  # hanning interpolation is used as we are downsampling the image
ax3.axis('off')

# add a title
title = fig.suptitle("Messi's greatest hits", x=0.42, y=0.9, va='center', ha='center', fontsize=60)

##############################################################################
# Photo from: https://en.wikipedia.org/wiki/Lionel_Messi#/media/File:Messi_vs_Nigeria_2018.jpg;
# License: https://creativecommons.org/licenses/by-sa/3.0/;
# Creator: Кирилл Венедиктов

