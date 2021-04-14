"""
============
Pizza Plots
============

* ``mplsoccer``, ``py_pizza`` module helps one to plot pizza charts in a few lines of code.

* The design idea is inspired by `Tom Worville <https://twitter.com/Worville>`_, `Football Slices <https://twitter.com/FootballSlices>`_ and `Soma Zero FC <https://twitter.com/somazerofc>`_

* Here we will show some examples of how to use ``mplsoccer`` to plot pizza-charts.

We have re-written `Soumyajit Bose's <https://twitter.com/Soumyaj15209314>`_  pizza chart code 
to enable greater customisation.
"""

from mplsoccer import PyPizza, add_image, FontManager
import matplotlib.pyplot as plt
from highlight_text import fig_text
from PIL import Image
from urllib.request import urlopen

##############################################################################
# Load some fonts
# ---------------
# We will use mplsoccer's FontManager to load some fonts from Google Fonts.
# We borrowed the FontManager from the excellent
# `ridge_map library <https://github.com/ColCarroll/ridge_map>`_.

font_normal = FontManager("https://github.com/google/fonts/blob/main/apache/roboto/static/Roboto-Regular.ttf?raw=true")
font_italic = FontManager("https://github.com/google/fonts/blob/main/apache/roboto/static/Roboto-Italic.ttf?raw=true")
font_bold = FontManager("https://github.com/google/fonts/blob/main/apache/roboto/static/Roboto-Medium.ttf?raw=true")

##############################################################################
# Load Images
# ---------------
# We will using these images in our examples. You can find all the images `here <https://github.com/andrewRowlinson/mplsoccer-assets>`_.

putellas_cropped = Image.open(
    urlopen("https://github.com/andrewRowlinson/mplsoccer-assets/blob/main/putellas_cropped.png?raw=true")
)
lewa_cropped = Image.open(
    urlopen("https://github.com/andrewRowlinson/mplsoccer-assets/blob/main/lewa_cropped.png?raw=true")
)
fdj_cropped = Image.open(
    urlopen("https://github.com/andrewRowlinson/mplsoccer-assets/blob/main/fdj_cropped.png?raw=true")
)

##############################################################################
# Plotting A Simple Pizza-Plot
# ----------------------------
# To plot we need a parameter list and corresponding values list.

# parameter list
params = [
    "Non-Penalty Goals", "npxG", "npxG per Shot", "xA", "Open Play\nShot Creating Actions",
    "\nPenalty Area\nEntries", "Progressive Passes", "Progressive Carries",
    "Successful Dribbles", "\nTouches\nper Turnover", "pAdj\nPress Regains", "Aerials Won"
]

# values for corresponding parameters
values = [99, 99, 87, 51, 62, 58, 45, 40, 27, 74, 77, 73]

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    straight_line_color="#000000",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=1,               # linewidth of last circle
    other_circle_lw=1,              # linewidth for other circles
    other_circle_ls="-."            # linestyle for other circles
)

# plot pizza
fig, ax = baker.make_pizza(
    values,             # list of values
    figsize=(8,8),      # adjust figsize according to your need
    param_location=110, # where the parameters will be added
    kwargs_slices=dict(
        facecolor="cornflowerblue", edgecolor="#000000", 
        zorder=2, linewidth=1
    ),                  # values to be used when plotting slices                
    kwargs_params=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, va="center"
    ),                  # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue", 
            boxstyle="round,pad=0.2", lw=1
        )
    )                   # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.97, "Robert Lewandowski - FC Bayern Munich", size=18,
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

plt.show()

##############################################################################
# Adding Image
# ----------------------------
# One can add image to the pizza plot. The process is like this: first increase the size of the
# center circle by using ``inner_circle_size`` argument inside ``PyPizza`` and then using ``add_image`` 
# method to plot the image at the center.
#
# Hack: You can use `Image-Online.co <https://crop-circle.imageonline.co/>`_ to crop a circle in image online and
# then use that image for plotting.

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of params
    straight_line_color="#000000",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=1,               # linewidth of last circle
    other_circle_lw=1,              # linewidth for other circles
    other_circle_ls="-.",           # linestyle for other circles
    inner_circle_size=20            # increase the circle size           
)

# plot pizza
fig, ax = baker.make_pizza(
    values,              # list of values
    figsize=(8,8),       # adjust figsize according to your need
    param_location=110,  # where the parameters will be added
    kwargs_slices=dict(
        facecolor="cornflowerblue", edgecolor="#000000", 
        zorder=2, linewidth=1
    ),                  # values to be used when plotting slices                
    kwargs_params=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, va="center"
    ),                  # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue", 
            boxstyle="round,pad=0.2", lw=1
        )
    )                   # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.97, "Robert Lewandowski - FC Bayern Munich", size=18,
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

# add image
ax_image = add_image(
    lewa_cropped, fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
)   # these values might differ when you are plotting

plt.show()

##############################################################################
# Adding Colors To Blank Spaces
# -----------------------------
# One can even add colors to blank spaces, ``color_blank_space`` is used for specifying the colors. There are two options 
# that users can use. If ``color_blank_space="same"`` is passed then the slice-color with lower alpha value will be used
# to color the blank space. If a list of color is passed to ``color_blank_space`` then those colors will be used. The user
# can set the alpha for blank-space using ``blank_alpha`` argument.

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    straight_line_color="#F2F2F2",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=0,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                     # list of values
    figsize=(8,8),              # adjust figsize according to your need
    color_blank_space="same",   # use same color to fill blank space
    blank_alpha=0.4,            # alpha for blank-space colors
    kwargs_slices=dict(
        facecolor="cornflowerblue", edgecolor="#F2F2F2", 
        zorder=2, linewidth=1
    ),                          # values to be used when plotting slices                
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
    )                           # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.97, "Robert Lewandowski - FC Bayern Munich", size=18,
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

plt.show()

##############################################################################
# Adding Colors To Blank Spaces (2)
# ---------------------------------
# Here we will pass a list of color to fill the blank spaces.

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    straight_line_color="#F2F2F2",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=0,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                                      # list of values
    figsize=(8,8),                               # adjust figsize according to your need
    color_blank_space=["#C5C5C5"]*len(params),   # use same color to fill blank space
    blank_alpha=0.4,                             # alpha for blank-space colors
    kwargs_slices=dict(
        facecolor="cornflowerblue", edgecolor="#F2F2F2", 
        zorder=2, linewidth=1
    ),                                           # values to be used when plotting slices                
    kwargs_params=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, va="center"
    ),                                           # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue", 
            boxstyle="round,pad=0.2", lw=1
        )
    )                                            # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.97, "Robert Lewandowski - FC Bayern Munich", size=18,
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

plt.show()

##############################################################################
# Multiple Slice Colors
# ---------------------------------
# The users can also use multiple colors for individual slices.

# parameter list
params = [
    "Non-Penalty Goals", "npxG", "xA", 
    "Open Play\nShot Creating Actions", "\nPenalty Area\nEntries",
    "Touches\nper Turnover", "Progressive\nPasses", "Progressive\nCarries", 
    "Final 1/3 Passes", "Final 1/3 Carries",
    "pAdj\nPressure Regains", "pAdj\nTackles Made", 
    "pAdj\nInterceptions", "Recoveries", "Aerial Win %"
]

# value list
values = [
    70, 77, 74, 68, 60, 
    96, 89, 97, 92, 94,
    16, 19, 56, 53, 94
]

# color for the slices and text
slice_colors = ["#1A78CF"] * 5 + ["#FF9300"] * 5 + ["#D70232"] * 5
text_colors = ["#000000"] * 10 + ["#F2F2F2"] * 5

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    background_color="#EBEBE9",     # background color
    straight_line_color="#EBEBE9",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=0,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
    inner_circle_size=20            # size of inner circle
)   

# plot pizza
fig, ax = baker.make_pizza(
    values,                          # list of values
    figsize=(8,8.5),                   # adjust figsize according to your need
    color_blank_space="same",        # use same color to fill blank space
    slice_colors=slice_colors,       # color for individual slices 
    value_colors=text_colors,        # color for the value-text
    value_bck_colors=slice_colors,   # color for the blank spaces
    blank_alpha=0.4,                 # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="#F2F2F2", zorder=2, linewidth=1
    ),                               # values to be used when plotting slices                
    kwargs_params=dict(
        color="#000000", fontsize=11, 
        fontproperties=font_normal.prop, va="center"
    ),                               # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=11, 
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue", 
            boxstyle="round,pad=0.2", lw=1
        )
    )                                # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.975, "Frenkie de Jong - FC Barcelona", size=16,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.955, 
    "Percentile Rank vs Top-Five League Midfielders | Season 2020-21", 
    size=13,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add credits
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.02, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

# add text
fig.text(
    0.34, 0.93, "Attacking        Possession       Defending", size=14,
    fontproperties=font_bold.prop, color="#000000"
)

# add rectangles
fig.patches.extend([
    plt.Rectangle(
        (0.31,0.9225),0.025,0.021, fill=True, color="#1a78cf",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.462,0.9225),0.025,0.021, fill=True, color="#ff9300",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.632,0.9225),0.025,0.021, fill=True, color="#d70232",
        transform=fig.transFigure, figure=fig
    ),
])

# add image
ax_image = add_image(
    fdj_cropped, fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
)   # these values might differ when you are plotting

plt.show()

##############################################################################
# Comparison Chart
# ---------------------------------
# To plot comparison chart one have to pass list of values to ``compare_values`` argument.

# parameter and values list
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
    figsize=(8,8),              # adjust figsize according to your need
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
    ),                          # values to be used when adding parameter-values
    kwargs_compare_values=dict(
        color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
        bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
    ),                          # values to be used when adding parameter-values
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#000000",
    ha="right"
)

plt.show()


##############################################################################
# Dark Theme
# ----------
# Below is an example code for dark theme.

# parameter list
params = [
    "Non-Penalty Goals", "npxG", "xA", 
    "Open Play\nShot Creating Actions", "\nPenalty Area\nEntries",
    "Touches\nper Turnover", "Progressive\nPasses", "Progressive\nCarries", 
    "Final 1/3 Passes", "Final 1/3 Carries",
    "pAdj\nPressure Regains", "pAdj\nTackles Made", 
    "pAdj\nInterceptions", "Recoveries", "Aerial Win %"
]

# value list
values = [
    70, 77, 74, 68, 60, 
    96, 89, 97, 92, 94,
    16, 19, 56, 53, 94
]

# color for the slices and text
slice_colors = ["#1A78CF"] * 5 + ["#FF9300"] * 5 + ["#D70232"] * 5
text_colors = ["#000000"] * 10 + ["#F2F2F2"] * 5

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    background_color="#222222",     # background color
    straight_line_color="#000000",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_color="#000000",    # color for last line
    last_circle_lw=1,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
    inner_circle_size=20            # size of inner circle
)   

# plot pizza
fig, ax = baker.make_pizza(
    values,                          # list of values
    figsize=(8,8.5),                   # adjust figsize according to your need
    color_blank_space="same",        # use same color to fill blank space
    slice_colors=slice_colors,       # color for individual slices 
    value_colors=text_colors,        # color for the value-text
    value_bck_colors=slice_colors,   # color for the blank spaces
    blank_alpha=0.4,                 # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="#000000", zorder=2, linewidth=1
    ),                               # values to be used when plotting slices                
    kwargs_params=dict(
        color="#F2F2F2", fontsize=11, 
        fontproperties=font_normal.prop, va="center"
    ),                               # values to be used when adding parameter
    kwargs_values=dict(
        color="#F2F2F2", fontsize=11, 
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue", 
            boxstyle="round,pad=0.2", lw=1
        )
    )                                # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.975, "Frenkie de Jong - FC Barcelona", size=16,
    ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
)

# add subtitle
fig.text(
    0.515, 0.955, 
    "Percentile Rank vs Top-Five League Midfielders | Season 2020-21", 
    size=13,
    ha="center", fontproperties=font_bold.prop, color="#F2F2F2"
)

# add credits
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.02, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#F2F2F2",
    ha="right"
)

# add text
fig.text(
    0.34, 0.93, "Attacking        Possession       Defending", size=14,
    fontproperties=font_bold.prop, color="#F2F2F2"
)

# add rectangles
fig.patches.extend([
    plt.Rectangle(
        (0.31,0.9225),0.025,0.021, fill=True, color="#1a78cf",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.462,0.9225),0.025,0.021, fill=True, color="#ff9300",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.632,0.9225),0.025,0.021, fill=True, color="#d70232",
        transform=fig.transFigure, figure=fig
    ),
])

# add image
ax_image = add_image(
    fdj_cropped, fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
)   # these values might differ when you are plotting

plt.show()

##############################################################################
# Different Units
# ---------------
# Till now we were plotting a percentile chart where the upper limit was 100. Let's take another example where
# the lower limit is 0 and upper limit is 5. The below code shows how to plot pizza-chart for such case.

# parameter and value list
params = ['Speed', 'Agility', 'Strength', 'Passing', 'Dribbles']
values = [5, 2, 4, 3, 1]

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    straight_line_color="#F2F2F2",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    straight_line_limit=5.0,        # max limit of straight lines
    last_circle_lw=0,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
    inner_circle_size=0.4,          # size of inner circle
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                     # list of values
    figsize=(8,8),              # adjust figsize according to your need
    color_blank_space="same",   # use same color to fill blank space
    blank_alpha=0.4,            # alpha for blank-space colors
    param_location=5.5,         # where the parameters will be added
    kwargs_slices=dict(
        facecolor="cornflowerblue", edgecolor="#F2F2F2", 
        zorder=2, linewidth=1
    ),                          # values to be used when plotting slices                
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
    )                           # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.97, "Player Name - Team Name", size=18,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.942, 
    "Rank vs Player's Position | Season Name", 
    size=15,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

plt.show()

##############################################################################
# Slices With Different Scales
# ----------------------------
# Let's say you want to plot values for parameters with different range, e.g. for pass % parameter you have
# lower limit as 72 and upper limit as 92, for npxG you have lower limit as 0.05 and upper limit as 0.25 so on.
# In order to plot parameter and values like this see below example. We will pass min-range-value and 
# max-range-value for each parameter.

# parameter and value list
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
    figsize=(8,8),              # adjust figsize according to your need
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#F2F2F2",
    ha="right"
)

# add image
ax_image = add_image(
    putellas_cropped, fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
)   # these values might differ when you are plotting

plt.show()


##############################################################################
# Comparison Chart With Different Scales
# --------------------------------------

# parameter and value list
params = [
    "Passing %", "Deep Progression", "xG Assisted", "xG Buildup",
    "Successful Dribbles", "Fouls Won", "Turnovers", "Pressure Regains",
    "pAdj Tackles", "pAdj Interceptions"
]
values = [82, 9.94, 0.22, 1.58, 1.74, 1.97, 2.43, 2.81, 3.04, 0.92]    # Putellas
values_2 = [76, 4.56, 0.09, 0.46, 1.08, 1.28, 1.84, 3.16, 2.66, 1.51]  # League Average

# minimum range value and maximum range value for parameters
min_range = [74, 3.3, 0.03, 0.28, 0.4, 0.7, 2.6, 2.4, 1.1, 0.7]
max_range = [90, 9.7, 0.20, 0.89, 2.1, 2.7, 0.4, 5.1, 3.7, 2.5]

# instantiate PyPizza class
baker = PyPizza(
    params=params,
    min_range=min_range,        # min range values 
    max_range=max_range,        # max range values
    background_color="#222222", straight_line_color="#000000",
    last_circle_color="#000000", last_circle_lw=2.5, other_circle_lw=0,
    other_circle_color="#000000", straight_line_lw=1
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                     # list of values
    compare_values=values_2,    # passing comparison values
    figsize=(8,8),              # adjust figsize according to your need
    color_blank_space="same",   # use same color to fill blank space
    blank_alpha=0.4,            # alpha for blank-space colors
    param_location=110,         # where the parameters will be added
    kwargs_slices=dict(
        facecolor="#1A78CF", edgecolor="#000000",
        zorder=1, linewidth=1
    ),                          # values to be used when plotting slices                
    kwargs_compare=dict(
        facecolor="#ff9300", edgecolor="#222222", zorder=3, linewidth=1,
    ),                          # values to be used when plotting comparison slices
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
    ),                           # values to be used when adding parameter-values
    kwargs_compare_values=dict(
        color="#000000", fontsize=12, 
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="#FF9300", 
            boxstyle="round,pad=0.2", lw=1
        )
    )                            # values to be used when adding comparison-values
)

# add title
fig_text(
    0.515, 0.99, "<Alexia Putellas> vs <League Average>", 
    size=16, fig=fig,
    highlight_textprops=[{"color": '#1A78CF'}, {"color": '#FF9300'}],
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
credit_1 = "data: statsbomb viz fbref"
credit_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

fig.text(
    0.99, 0.005, f"{credit_1}\n{credit_2}", size=9,
    fontproperties=font_italic.prop, color="#F2F2F2",
    ha="right"
)

plt.show()