"""
==============================
Comparison Pizza (Percentiles)
==============================

* Author: `slothfulwave612 <https://twitter.com/slothfulwave612>`_

* ``mplsoccer``, ``py_pizza`` module helps one to plot pizza charts in a few lines of code.

* The design idea is inspired by `Tom Worville <https://twitter.com/Worville>`_, \
`Football Slices <https://twitter.com/FootballSlices>`_ and \
`Soma Zero FC <https://twitter.com/somazerofc>`_

* We have re-written `Soumyajit Bose's <https://twitter.com/Soumyaj15209314>`_  pizza chart code \
to enable greater customisation.

Here we plot a pizza chart for comparing two players.
"""

import matplotlib.pyplot as plt
from highlight_text import fig_text

from mplsoccer import PyPizza, FontManager

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
# Comparison Chart
# ----------------
# To plot comparison chart one have to pass list of values to ``compare_values`` argument.

# parameter and values list
# The values are taken from the excellent fbref website (supplied by StatsBomb)
params = [
    "Non-Penalty Goals", "npxG", "npxG per Shot", "xA",
    "Open Play\nShot Creating Actions", "\nPenalty Area\nEntries",
    "Progressive Passes", "Progressive Carries", "Successful Dribbles",
    "\nTouches\nper Turnover", "pAdj\nPress Regains", "Aerials Won"
]
values = [99, 99, 87, 51, 62, 58, 45, 40, 27, 74, 77, 73]    # for Robert Lewandowski
values_2 = [83, 75, 55, 62, 72, 92, 92, 79, 64, 92, 68, 31]  # for Mohamed Salah

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    background_color="#EBEBE9",     # background color
    straight_line_color="#222222",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=1,               # linewidth of last circle
    last_circle_color="#222222",    # color of last circle
    other_circle_ls="-.",           # linestyle for other circles
    other_circle_lw=1               # linewidth for other circles
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                     # list of values
    compare_values=values_2,    # comparison values
    figsize=(8, 8),             # adjust figsize according to your need
    kwargs_slices=dict(
        facecolor="#1A78CF", edgecolor="#222222",
        zorder=2, linewidth=1
    ),                          # values to be used when plotting slices
    kwargs_compare=dict(
        facecolor="#FF9300", edgecolor="#222222",
        zorder=2, linewidth=1,
    ),
    kwargs_params=dict(
        color="#000000", fontsize=12,
        fontproperties=font_normal.prop, va="center"
    ),                          # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12,
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    ),                          # values to be used when adding parameter-values labels
    kwargs_compare_values=dict(
        color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
        bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
    ),                          # values to be used when adding parameter-values labels
)

# add title
fig_text(
    0.515, 0.99, "<Robert Lewandowski> vs <Mohamed Salah>", size=17, fig=fig,
    highlight_textprops=[{"color": '#1A78CF'}, {"color": '#EE8900'}],
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.942,
    "Percentile Rank vs Top-Five League Forwards | Season 2020-21",
    size=15,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add credits
CREDIT_1 = "data: statsbomb viz fbref"
CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

plt.show()

##############################################################################
# Adjust Overlapping Values
# -------------------------
# To adjust overlapping values one can use ``adjust_texts()`` method.
# The user have to pass ``params_offset`` list
# which will contain bool values denoting which parameter's text is to be adjusted,
# an ``offset`` value denoting how much adjustment will be made,
# and if the user wants to adjust the comparison-text then can pass
# ``adj_comp_values=True`` to the ``adjust_texts()`` method. Below is an example code.

# parameter and values list
params = [
    "Non-Penalty Goals", "npxG", "npxG per Shot", "xA",
    "Open Play\nShot Creating Actions", "\nPenalty Area\nEntries",
    "Progressive Passes", "Progressive Carries", "Successful Dribbles",
    "\nTouches\nper Turnover", "pAdj\nPress Regains", "Aerials Won"
]

# dummy values
values = [15, 7, 57, 86, 63, 51, 11, 32, 85, 69, 90, 54]    # for Player 1
values_2 = [31, 41, 43, 42, 47, 24, 60, 60, 28, 70, 92, 64]  # for Player 2

# pass True in that parameter-index whose values are to be adjusted
# here True values are passed for "\nTouches\nper Turnover" and "pAdj\nPress Regains" params
params_offset = [
    False, False, False, False, False, False,
    False, False, False, True, True, False
]

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    background_color="#EBEBE9",     # background color
    straight_line_color="#222222",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=1,               # linewidth of last circle
    last_circle_color="#222222",    # color of last circle
    other_circle_ls="-.",           # linestyle for other circles
    other_circle_lw=1               # linewidth for other circles
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                     # list of values
    compare_values=values_2,    # comparison values
    figsize=(8, 8),             # adjust figsize according to your need
    kwargs_slices=dict(
        facecolor="#1A78CF", edgecolor="#222222",
        zorder=2, linewidth=1
    ),                          # values to be used when plotting slices
    kwargs_compare=dict(
        facecolor="#FF9300", edgecolor="#222222",
        zorder=2, linewidth=1,
    ),
    kwargs_params=dict(
        color="#000000", fontsize=12,
        fontproperties=font_normal.prop, va="center"
    ),                          # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12,
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    ),                          # values to be used when adding parameter-values labels
    kwargs_compare_values=dict(
        color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
        bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
    ),                          # values to be used when adding parameter-values labels
)


# adjust text for comparison-values-text
baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)

# add title
fig_text(
    0.515, 0.99, "<Player 1> vs <Player 2>", size=17, fig=fig,
    highlight_textprops=[{"color": '#1A78CF'}, {"color": '#EE8900'}],
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.942,
    "Percentile Rank Chart",
    size=15,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add credits
CREDIT_1 = "dummy-data"
CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{CREDIT_1}\n{CREDIT_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

plt.show()
