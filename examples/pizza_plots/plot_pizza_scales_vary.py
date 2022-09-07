"""
======================
Different Scales Pizza
======================

* Author: `slothfulwave612 <https://twitter.com/slothfulwave612>`_

* ``mplsoccer``, ``py_pizza`` module helps one to plot pizza charts in a few lines of code.

* The design idea is inspired by `Tom Worville <https://twitter.com/Worville>`_, \
`Football Slices <https://twitter.com/FootballSlices>`_ and \
`Soma Zero FC <https://twitter.com/somazerofc>`_

* We have re-written `Soumyajit Bose's <https://twitter.com/Soumyaj15209314>`_  pizza chart code \
to enable greater customisation.

Here we plot a pizza chart where each parameters has a different
maximum and minimum value.
"""

from urllib.request import urlopen

import matplotlib.pyplot as plt
from PIL import Image

from mplsoccer import PyPizza, add_image, FontManager

##############################################################################
# Load some fonts
# ---------------
# We will use mplsoccer's FontManager to load some fonts from Google Fonts.
# We borrowed the FontManager from the excellent
# `ridge_map library <https://github.com/ColCarroll/ridge_map>`_.

font_normal = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/roboto/'
                          'Roboto%5Bwdth,wght%5D.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/roboto/'
                          'Roboto-Italic%5Bwdth,wght%5D.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                        'RobotoSlab%5Bwght%5D.ttf')

##############################################################################
# Load Image
# ----------
# Load a cropped image of Alexia Putellas.

URL = "https://raw.githubusercontent.com/andrewRowlinson/mplsoccer-assets/main/putellas_cropped.png"
putellas_cropped = Image.open(urlopen(URL))

##############################################################################
# Slices With Different Scales
# ----------------------------
# Let's say you want to plot values for parameters with different range,
# e.g. for pass % parameter you have lower limit as 72 and upper limit as 92,
# for npxG you have lower limit as 0.05 and upper limit as 0.25 so on.
# In order to plot parameter and values like this see below example.
# We will pass min-range-value and max-range-value for each parameter.

# parameter and value list
# The values are taken from the excellent fbref website (supplied by StatsBomb)
params = [
    "Passing %", "Deep Progression", "xG Assisted", "xG Buildup",
    "Successful Dribbles", "Fouls Won", "Turnovers", "Pressure Regains",
    "pAdj Tackles", "pAdj Interceptions"
]
values = [82, 9.94, 0.22, 1.58, 1.74, 1.97, 2.43, 2.81, 3.04, 0.92]

# minimum range value and maximum range value for parameters
min_range = [74, 3.3, 0.03, 0.28, 0.4, 0.7, 2.6, 2.4, 1.1, 0.7]
max_range = [90, 9.7, 0.20, 0.89, 2.1, 2.7, 0.4, 5.1, 3.7, 2.5]

# instantiate PyPizza class
baker = PyPizza(
    params=params,
    min_range=min_range,        # min range values
    max_range=max_range,        # max range values
    background_color="#222222", straight_line_color="#000000",
    last_circle_color="#000000", last_circle_lw=2.5, straight_line_lw=1,
    other_circle_lw=0, other_circle_color="#000000", inner_circle_size=20,
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                     # list of values
    figsize=(8, 8),             # adjust figsize according to your need
    color_blank_space="same",   # use same color to fill blank space
    blank_alpha=0.4,            # alpha for blank-space colors
    param_location=110,         # where the parameters will be added
    kwargs_slices=dict(
        facecolor="#1A78CF", edgecolor="#000000",
        zorder=1, linewidth=1
    ),                          # values to be used when plotting slices
    kwargs_params=dict(
        color="#F2F2F2", fontsize=12, zorder=5,
        fontproperties=font_normal.prop, va="center"
    ),                          # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12,
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="#1A78CF",
            boxstyle="round,pad=0.2", lw=1
        )
    )                           # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.97, "Alexia Putellas - FC Barcelona Femení", size=18,
    ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
)

# add subtitle
fig.text(
    0.515, 0.942,
    "Primera División Femenina | Season 2020-21 | 90s Played: 13.2",
    size=15,
    ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
)

# add credits
CREDIT_1 = "data: statsbomb viz fbref"
CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
    fontproperties=font_italic.prop, color="#F2F2F2",
    ha="right"
)

# add image
ax_image = add_image(
    putellas_cropped, fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
)   # these values might differ when you are plotting

plt.show()
