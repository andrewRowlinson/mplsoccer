# Radar Charts

## Content

* [Overview](#Overview)
* [Documentation](#soccerplotsradar_chartplot_radar)
* [Examples](#examples)
  * [Making A Simple Radar Chart](#making-a-simple-radar-chart)  
  * [Label And Range Fontsize](#label-and-range-fontsize)
  * [Adding Title To The Plot](#adding-title-to-the-plot)
  * [Player Comparison](#player-comparison)
  * [Saving The PLot](#saving-the-plot)

## Overview

* `soccerplots`, `radar_chart` module helps you plot cool radar charts in a few lines of code.

* The radar-chart theme is inspired from [Statsbomb](https://twitter.com/StatsBomb).

* Here we will look at the documentation and some examples on how to use `soccerplot` to plot radar charts.

* **Note**:
  * You should have `numpy` and `matplotlib` packages installed on your system.
  
  * `Python v3.7.7` has been used with `numpy v1.18.5` and `matplotlib v3.3.0` while coding out the radar_chart module.
  
  * If something won't work try updating Python or your packages. And if you are facing any problem using `soccerplots` ping me [here](https://twitter.com/slothfulwave612).
  
## soccerplots.radar_chart.plot_radar  

```python
soccerplots.radar_chart.plot_radar(ranges, params, values, radar_color, label_fontsize=10, range_fontsize=6.5, 
                                   filename=None, dpi=300, title=dict(), alpha=[0.6, 0.6], compare=False, 
                                   fontname='Liberation Serif', credit_size=13)
```

|  No.  |  Parameter  |  About Parameter  |
|-------|-------------|-------------------|
|  1.   |   ranges    | list of tuples containing min and max value for each parameter.    |
|  2.   |   params    | list of string values containing the name of parameters.|
|  3.   |   values    | list of float values for each parameters. <br> can be nested list as well when making comparison charts.|
|  4.   | radar_color | list of two color values.|
|  5.   | label_fontsize| float, fontsize for the labels around the radar-chart <br> Default: 10|
|  6.   | range_fontsize| float, fontsize for the range values plotted within radar chart <br> Default: 6.5| 
|  7.   | filename | str, the name per which the file will be saved(you have to add extension as well with the filename) <br> Default: None|
|  8.   | dpi  | int, dots per inch value <br> Default: 300 |
|  9.   | title | dict, containing information of title and subtitle. <br> To know more see examples. <br> Default: empty-dict|
| 10.   | alpha | list of alpha values, to be used when plotting comparison radars. <br> Range: [0,1] <br> Default: [0.6, 0.6]|
| 11.   | compare | bool, True: if comparison radars will be made. <br> False: otherwise|
| 12.   | fontname | str, font-name to be used for the entire radar chart <br> For more info on fonts click [here](https://twitter.com/joriki/status/1291981791578865664). <br> Default: Liberation Serif|
| 13.   | credit_size | float, the font-size for the credit string. <br> Credit given to [Statsbomb](https://twitter.com/StatsBomb). <br> Default: 13

|  No.  |  Returns  |  About  |
|-------|-----------|---------|
|  1.   |  fig      | figure object |
|  2.   |  ax       | axis object |

## Examples

* Here we will look into some of the examples that can help in making radar-charts using `soccerplots`.

* **Example Tutorial Content:**
    1. [Making A Simple Radar Chart](#making-a-simple-radar-chart)  
    2. [Label And Range Fontsize](#label-and-range-fontsize)
    3. [Adding Title To The Plot](#adding-title-to-the-plot)
    4. [Player Comparison](#player-comparison)
    5. [Saving The PLot](#saving-the-plot)
    
### Making A Simple Radar Chart    

* Here we will make a very simple radar chart using `soccerplots` module `radar_chart`. 

* We will be making use of `ranges`, `params`, `values` and `radar_color` parameter.

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssist', 'Key Passes', 'Crosses Into Box', 'Cross Completion %', 'Deep Completions',
          'Progressive Passes', 'Prog. Pass Accuracy', 'Dribbles', 'Progressive Runs',
          'PADJ Interceptions', 'Succ. Def. Actions', 'Def Duel Win %']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 6.3), (19.51, 50.0), (0.35, 1.61),
          (6.45, 11.94), (62.9, 79.4), (0.43, 4.08), (0.6, 2.33),
          (4.74, 7.2), (8.59, 12.48), (50.66, 66.67)]

## parameter value
values = [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29]

## plot radar chart
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#FFFFFF'])
```

![fig](https://user-images.githubusercontent.com/33928040/89763650-955bc300-db10-11ea-97eb-2dde9d587bb7.jpg)


### Label And Range Fontsize

* Here we will see how we can use `label_fontsize` and `range_fontsize` parameter. We will here increase the values of these two parameters and you will see that the ranges and labels now are larger than the previous output.

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssist', 'Key Passes', 'Crosses Into Box', 'Cross Completion %', 'Deep Completions',
          'Progressive Passes', 'Prog. Pass Accuracy', 'Dribbles', 'Progressive Runs',
          'PADJ Interceptions', 'Succ. Def. Actions', 'Def Duel Win %']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 6.3), (19.51, 50.0), (0.35, 1.61),
          (6.45, 11.94), (62.9, 79.4), (0.43, 4.08), (0.6, 2.33),
          (4.74, 7.2), (8.59, 12.48), (50.66, 66.67)]

## parameter value
values = [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29]

## plot radar chart: label_fontsize=13 and range_fontsize=7.5
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#FFFFFF'],
                                 label_fontsize=13, range_fontsize=7.5)
```

![fig](https://user-images.githubusercontent.com/33928040/89764280-ba9d0100-db11-11ea-9785-87ffcd4507a4.jpg)


### Adding Title To The Plot

* Let's see how we can add titles to the radar-chart.

* `title` parameter takes a dictionary having these keys:
   1. title_name -- The title of your plot, displayed at top left corner.
   2. title_color -- The color of the title(displayed at top left corner). Default Value: '#000000'.
   3. subtitle_name -- The info to be displayed below the tilte at top left corner.
   4. subtitle_color -- The color of the subtitle(displayed at top left corner). Default Value: '#000000'.
   5. title_name_2 -- The title to be displayed at top right corner.
   6. title_color_2 -- The color of the title(displaed at top right corner). Default Value: '#000000'.
   7. subtitle_name_2 -- The info to be displayed below the tilte at top right corner.
   8. subtitle_color_2 -- The color of the subtitile(displayed at top right corner). Default Value: '#000000'.
   9. title_fontsize -- The fontsize of the title. Default: 20.
   10. subtitle_fontsize -- The fontsize of the subtitle. Default: 15
   
* **Example 01:**

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssist', 'Key Passes', 'Crosses Into Box', 'Cross Completion %', 'Deep Completions',
          'Progressive Passes', 'Prog. Pass Accuracy', 'Dribbles', 'Progressive Runs',
          'PADJ Interceptions', 'Succ. Def. Actions', 'Def Duel Win %']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 6.3), (19.51, 50.0), (0.35, 1.61),
          (6.45, 11.94), (62.9, 79.4), (0.43, 4.08), (0.6, 2.33),
          (4.74, 7.2), (8.59, 12.48), (50.66, 66.67)]

## parameter value
values = [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29]

## title values
title = dict(
    title_name='Sergiño Dest',
    title_color='#000000',
    subtitle_name='AFC Ajax',
    subtitle_color='#B6282F',
    title_fontsize=18,
    subtitle_fontsize=15,
)

## plot radar chart
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#FFFFFF'], title=title)
```

![fig](https://user-images.githubusercontent.com/33928040/89776568-cf848f00-db27-11ea-9eb6-c93acb758a09.jpg)


* **Example 02:**

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssist', 'Key Passes', 'Crosses Into Box', 'Cross Completion %', 'Deep Completions',
          'Progressive Passes', 'Prog. Pass Accuracy', 'Dribbles', 'Progressive Runs',
          'PADJ Interceptions', 'Succ. Def. Actions', 'Def Duel Win %']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 6.3), (19.51, 50.0), (0.35, 1.61),
          (6.45, 11.94), (62.9, 79.4), (0.43, 4.08), (0.6, 2.33),
          (4.74, 7.2), (8.59, 12.48), (50.66, 66.67)]

## parameter value
values = [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29]

## title values
title = dict(
    title_name='Sergiño Dest',
    subtitle_name='AFC Ajax',
    subtitle_color='#B6282F',
    title_name_2='Radar Chart',
    subtitle_name_2='Fullback',
    subtitle_color_2='#B6282F',
    title_fontsize=18,
    subtitle_fontsize=15,
)

## plot radar chart
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#FFFFFF'], title=title)
```

![fig](https://user-images.githubusercontent.com/33928040/89776630-e88d4000-db27-11ea-96e9-cda5fed8b9c6.jpg)


### Player Comparison

* Now here we will plot a radar chart where we will compare two players.

* For player comparison `values` will now be a nested list and we have to pass `compare=True` to tell the function that we want to plot a comparison radar chart.

* **Example 01:**

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssists', 'Key Passes', 'Crosses Into Box', 'Cross Competion', 'Deep Completions', 
          'Progressive Passes', 'Prog. Passes Accuracy%', 'Dribbles', 'Progressive Runs', 
          'PADJ Interceptions', 'Succ. Def Actions', 'Def Duel Win%']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 0.63), (19.51, 50.0), (0.35, 1.61), (6.45, 11.94), (62.94, 79.46), (0.43, 4.08), (0.6, 2.33), (5.01, 7.2), (9.02, 12.48),
          (52.44, 66.67)]

## parameter value
values = [
    [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29],   ## for Sergino Dest
    [0.07, 0.36, 0.16, 32.14, 1.04, 7.37, 74.46, 3.68, 2.40, 6.87, 8.97, 61.14]    ## for Nelson Semedo
]

## title
title = dict(
    title_name='Sergiño Dest',
    title_color='#B6282F',
    subtitle_name='AFC Ajax',
    subtitle_color='#B6282F',
    title_name_2='Nelson Semedo',
    title_color_2='#344D94',
    subtitle_name_2='Barcelona',
    subtitle_color_2='#344D94',
    title_fontsize=18,
    subtitle_fontsize=15,
)

## plot radar chart
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#344D94'], title=title, compare=True)
```

![fig](https://user-images.githubusercontent.com/33928040/89775607-d27e8000-db25-11ea-9fd0-ec2f1367b7fa.jpg)


* **Example 02:**

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssists', 'Key Passes', 'Crosses Into Box', 'Cross Competion', 'Deep Completions', 
          'Progressive Passes', 'Prog. Passes Accuracy%', 'Dribbles', 'Progressive Runs', 
          'PADJ Interceptions', 'Succ. Def Actions', 'Def Duel Win%']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 0.63), (19.51, 50.0), (0.35, 1.61), (6.45, 11.94), (62.94, 79.46), (0.43, 4.08), (0.6, 2.33), (5.01, 7.2), (9.02, 12.48),
          (52.44, 66.67)]

## parameter value
values = [
    [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29],   ## for Sergino Dest
    [0.07, 0.36, 0.16, 32.14, 1.04, 7.37, 74.46, 3.68, 2.40, 6.87, 8.97, 61.14]    ## for Nelson Semedo
]

## title
title = dict(
    title_name='Sergiño Dest',
    title_color='#B6282F',
    subtitle_name='AFC Ajax',
    subtitle_color='#B6282F',
    title_name_2='Nelson Semedo',
    title_color_2='#344D94',
    subtitle_name_2='Barcelona',
    subtitle_color_2='#344D94',
    title_fontsize=18,
    subtitle_fontsize=15,
)

## plot radar chart -- alpha values
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#344D94'], 
                                 alpha=[0.8, 0.6], title=title, compare=True)
```

![fig](https://user-images.githubusercontent.com/33928040/89775828-386b0780-db26-11ea-995f-a476c7a518d7.jpg)


### Saving The Plot

* In order to save the plot we have to use `filename` parameter, here we will pass the name of the file with added extension.

* Another parameter we can use here is `dpi` by default it is set to `300`. If you want to have save high quality plot you can increase the value.

```python
from soccerplots import radar_chart

## parameter names
params = ['xAssists', 'Key Passes', 'Crosses Into Box', 'Cross Competion', 'Deep Completions', 
          'Progressive Passes', 'Prog. Passes Accuracy%', 'Dribbles', 'Progressive Runs', 
          'PADJ Interceptions', 'Succ. Def Actions', 'Def Duel Win%']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 0.63), (19.51, 50.0), (0.35, 1.61), (6.45, 11.94), (62.94, 79.46), (0.43, 4.08), (0.6, 2.33), (5.01, 7.2), (9.02, 12.48),
          (52.44, 66.67)]

## parameter value
values = [
    [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29],   ## for Sergino Dest
    [0.07, 0.36, 0.16, 32.14, 1.04, 7.37, 74.46, 3.68, 2.40, 6.87, 8.97, 61.14]    ## for Nelson Semedo
]

## title
title = dict(
    title_name='Sergiño Dest',
    title_color='#B6282F',
    subtitle_name='AFC Ajax',
    subtitle_color='#B6282F',
    title_name_2='Nelson Semedo',
    title_color_2='#344D94',
    subtitle_name_2='Barcelona',
    subtitle_color_2='#344D94',
    title_fontsize=18,
    subtitle_fontsize=15,
)

## plot radar chart -- the plot will be saved to your present working directory
fig, ax = radar_chart.plot_radar(ranges=ranges, params=params, values=values, radar_color=['#B6282F', '#344D94'], 
                                 alpha=[0.8, 0.6], filename='compare.jpg', dpi=500, title=title, compare=True)
```