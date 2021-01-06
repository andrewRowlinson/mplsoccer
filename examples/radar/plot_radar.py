"""
============
Radar Charts
============

* ``mplsoccer``, ``radar_chart`` module helps one to plot radar charts in a few lines of code.

* The radar-chart theme is inspired by `StatsBomb <https://twitter.com/StatsBomb/>`_
  and `Rami Moghadam <https://cargocollective.com/ramimo/2013-NBA-All-Stars>`_ 

* Here we will show some examples on how to use ``mplsoccer`` to plot radar charts.

First we import the Radar class
"""

from mplsoccer import Radar
import matplotlib.pyplot as plt

##############################################################################
# Making a simple Radar Chart
# ---------------------------
# Here we will make a very simple radar chart using ``mplsoccer`` module ``radar_chart``. 
# We will be making use of ``ranges``, ``params``, ``values`` and ``radar_color`` parameter.

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]

# instantiate object
radar = Radar()

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=params, values=values, figsize=(12,12),
  radar_color=['#B6282F', '#FFFFFF']
)

##############################################################################
# Label And Range Fontsize
# ---------------------------
# Here we will see how we can use ``label_fontsize`` and ``range_fontsize`` parameter. 
# We will here increase the values of these two parameters and you will see that the ranges and labels now are larger than the previous output. 

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]

# instantiate object
radar = Radar(
  label_fontsize=12, range_fontsize=7.5
)

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=params, values=values, figsize=(12,12),
  radar_color=['#B6282F', '#FFFFFF']
)
fig.tight_layout()

##############################################################################
# Adding Title
# ---------------------------
# Here we will create a dictionary to specify title values and will pass it to ``plot_radar`` method.
# We will also be using ``fontfamily`` as ``serif``.

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]


## title values
title = dict(
    title_name="Bruno Fernandes",        # title on left side
    subtitle_name="Manchester United",   # subtitle on left side
    subtitle_color='#B6282F',
    title_name_2='Radar Chart',          # title on right side
    subtitle_name_2="Midfielder",        # subtitle on right side
    subtitle_color_2='#B6282F',
    title_fontsize=18,                   # same fontsize for both title
    subtitle_fontsize=15,                # same fontsize for both subtitle
)

# instantiate object
radar = Radar(fontfamily="serif")

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=params, values=values, title=title, figsize=(12,12),
  radar_color=['#B6282F', '#FFFFFF']
)
fig.tight_layout()

##############################################################################
# Adding Title (2)
# ---------------------------
# The user can also change the fontsize for top-right title and subtitle. The below code shows how to do it.

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]


## title values
title = dict(
    title_name="Bruno Fernandes",        # title on left side
    subtitle_name="Manchester United",   # subtitle on left side
    subtitle_color='#B6282F',
    title_name_2='Radar Chart',          # title on right side
    subtitle_name_2="Midfielder",        # subtitle on right side
    subtitle_color_2='#B6282F',
    title_fontsize=18,                   # fontsize for left-title
    subtitle_fontsize=15,                # fontsize for left-subtitle
    title_fontsize_2=14,                 # fontsize for right-title
    subtitle_fontsize_2=14               # fontsize for right-subtitle
)

# instantiate object
radar = Radar(fontfamily="serif")

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=params, values=values, title=title, figsize=(12,12),
  radar_color=['#B6282F', '#FFFFFF']
)
fig.tight_layout()

##############################################################################
# Adding Endnote
# ---------------------------
# The Inspired By endnote is there to thank those who developed and popularized it.
# One can also pass ``end_color`` and ``end_size`` argument to ``plot_radar`` method to change color and size of the end-note respectively.

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]


## title values
title = dict(
    title_name="Bruno Fernandes",        # title on left side
    subtitle_name="Manchester United",   # subtitle on left side
    subtitle_color='#B6282F',
    title_name_2='Radar Chart',          # title on right side
    subtitle_name_2="Midfielder",        # subtitle on right side
    subtitle_color_2='#B6282F',
    title_fontsize=18,                   # fontsize for left-title
    subtitle_fontsize=15,                # fontsize for left-subtitle
    title_fontsize_2=14,                 # fontsize for right-title
    subtitle_fontsize_2=14               # fontsize for right-subtitle
)

## endnote 
endnote = "graphic: @slothfulwave612)\ncreated using mplsoccer"

# instantiate object
radar = Radar(fontfamily="serif")

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=params, values=values, title=title, figsize=(12,12),
  radar_color=['#B6282F', '#FFFFFF'], endnote=endnote
)
fig.tight_layout()

##############################################################################
# Making Clean Radar Charts
# ---------------------------
# A clean radar chart is one where the final plot does not include the range and param values only showing the shape of the polygon.

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]


## title values
title = dict(
    title_name="Bruno Fernandes",        # title on left side
    subtitle_name="Manchester United",   # subtitle on left side
    subtitle_color='#B6282F',
    title_name_2='Radar Chart',          # title on right side
    subtitle_name_2="Midfielder",        # subtitle on right side
    subtitle_color_2='#B6282F',
    title_fontsize=18,                   # fontsize for left-title
    subtitle_fontsize=15,                # fontsize for left-subtitle
    title_fontsize_2=14,                 # fontsize for right-title
    subtitle_fontsize_2=14               # fontsize for right-subtitle
)

## endnote 
endnote = "graphic: @slothfulwave612)\ncreated using mplsoccer"

# instantiate object
radar = Radar(fontfamily="serif")

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=None, values=values, title=title, plot_range=False, figsize=(12,12),
  radar_color=['#B6282F', '#FFFFFF'], endnote=endnote
)
fig.tight_layout()

##############################################################################
# Dark Theme
# ---------------------------
# The user can update the colors by passing ``background_color``, ``patch_color``, ``label_color`` and ``range_color`` argument to the ``Radar``.

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54]


## title values
title = dict(
    title_name="Bruno Fernandes",        
    title_color="#F2F2F2",
    subtitle_name="Manchester United",   
    subtitle_color='#F2A365',
    title_name_2='Radar Chart',   
    title_color_2="#F2F2F2",
    subtitle_name_2="Midfielder",        
    subtitle_color_2='#F2A365',
    title_fontsize=18,                   
    subtitle_fontsize=15,                
    title_fontsize_2=14,                 
    subtitle_fontsize_2=14               
)

## endnote 
endnote = "graphic: @slothfulwave612)\ncreated using mplsoccer"

# instantiate object
radar = Radar(
    background_color="#222222", patch_color="#2D2A32", label_color="#F2F2F2", range_color="#FFFFFF", fontfamily="serif"
)

# plot radar
fig, ax = radar.plot_radar(
  ranges=ranges, params=params, values=values, title=title, figsize=(12,12),
  radar_color=["#30475E", "#F2A365"], endnote=endnote
)
fig.tight_layout()

##############################################################################
# Making comparison radar chart
# ---------------------------
# The code snippet:

# parameter names
params = [
    "npxG", "Non-Penalty Goals", "xA", 
    "Key Passes", "Through Balls", "Progressive Passes", 
    "Shot-Creating Actions", "Goal-Creating Actions", 
    "Dribbles Completed", "Pressure Regains", "Touches In Box"
]

# range values
ranges = [
    (0.08, 0.37), (0.0, 0.6), (0.1, 0.6), (1, 4), (0.6, 1.2),
    (4, 10), (3, 8), (0.3, 1.3), (0.3, 1.5), (2, 5.5), (2, 5)
]

# parameter value
values = [
    [0.25, 0.42, 0.42, 3.47, 1.04, 8.06, 5.62, 0.97, 0.56, 5.14, 3.54],  ## bruno
    [0.32, 0.0, 0.43, 3.5, 0.98, 7.72, 6.18, 0.98, 1.71, 4.88, 4.96],    ## KDB
]

## title values
title = dict(
    title_name="Bruno Fernandes",        
    title_color="#C2495D",
    subtitle_name="Manchester United",   
    subtitle_color="#F2F2F2",
    title_name_2="Kevin de Bruyne",   
    title_color_2="#3282B8",
    subtitle_name_2="Manchester City",        
    subtitle_color_2="#F2F2F2",
    title_fontsize=18,                   
    subtitle_fontsize=15             
)

## endnote 
endnote = "graphic: @slothfulwave612)\ncreated using mplsoccer"

# instantiate object
radar = Radar(
    background_color="#222222", patch_color="#2D2A32", label_color="#F2F2F2", range_color="#FFFFFF", fontfamily="serif"
)
    
# plot radar              
fig, ax = radar.plot_radar(
    ranges=ranges, params=params, values=values, title=title, figsize=(12,12),
    radar_color=["#C2495D", "#3282B8"], alphas=[0.55, 0.5],
    endnote=endnote, end_color="#C0C0C0", compare=True
)
fig.tight_layout()
