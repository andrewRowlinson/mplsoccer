# Radar Charts

## Content

* [Overview](#overview)
* [Documentation](#mplsoccerradar_chartradar)
* [Examples](#examples)
* [Dark Theme Template](#dark-theme-template)
* [Some More Templates](#some-more-templates)

## Overview

* `mplsoccer`, `radar_chart` module helps one to plot radar charts in a few lines of code.

* The radar-chart theme is inspired from [Statsbomb](https://twitter.com/StatsBomb)/Rami Moghadam.

* Here we will look at the documentation and some examples on how to use `mplsoccer` to plot radar charts.
  
## mplsoccer.radar_chart.Radar

```python
mplsoccer.radar_chart.Radar(
    background_color="#FFFFFF", patch_color="#D6D6D6", fontfamily="Liberation Serif", 
    label_fontsize=10, range_fontsize=6.5, label_color="#000000", range_color="#000000"
)
```

|  No.  |  Parameter  |  About Parameter  |
|-------|-------------|-------------------|
|1.|background_color| (str, optional) the background color of the plot. Defaults to "#FFFFFF".|
|2.|patch_color| (str, optional) the color for our circle. Defaults to "#D6D6D6".|
|3.|fontfamily| (str, optional) fontfamily available in matplotlib. Defaults to "Liberation Serif".|
|4.|label_fontsize| (float, optional) the fontsize of label. Defaults to 10.|
|5.|range_fontsize| (float, optional) the fontsize for range values. Defaults to 6.5.|
|6.|label_color| (str, optional) color value for labels. Defaults to "#000000".|
|7.|range_color| (str, optional): color value for ranges. Defaults to "#000000".|         
      
## mplsoccer.radar_chart.Radar.plot_radar      
      
```python
mplsoccer.radar_chart.Radar.plot_radar(
     ranges, params, values, radar_color, plot_range=True, filename=None, dpi=300,
     title=dict(), alphas=[0.6, 0.6], compare=False, endnote=None, 
     end_size=9, end_color="#95919B", image=None, image_coord=None, figax=None, **kwargs
)
```

|  No.  |  Parameter  |  About Parameter  |
|-------|-------------|-------------------|
|1.|ranges| (list) list of tuples containing min and max value for each parameter.|
|2.|params| (list) list of string values containing the name of parameters. Pass None to plot clean-radar-chart|
|3.|values| (list) list of float values for each parameters/ nested list when making comparison charts.|
|4.|radar_color| (list) list of two color values.|
|5.|plot_range| (bool, optional) to plot the range values. Defaults to True.|
|6.|filename| (str, optional) the name per which the file will be saved added extension. Defaults to None.|
|7.|dpi| (int, optional) dots per inch value. Defaults to 300.|
|8.|title| (str, optional) containing information of title and subtitle. Defaults to dict().|
|9.|alphas| (list, optional) alpha value for color. Defaults to [0.6, 0.6].|
|10.|compare| (bool, optional) True, if comparison charts are to be made. Defaults to False.|
|11.|endnote| (str, optional) the endnote of the plot. Defaults to None.|
|12.|end_size| (int, optional) the font-size for the endnote string. Defaults to 9.|
|13.|end_color| (str, optional) color of the endnote. Defaults to "#95919B".|
|14.|image| (str, optional) image name to be added. Defaults to None.|
|15.|image_coord| (list, optional) containing left, bottom, width, height for image. Defaults to None.|
|16.|figax| (tuple, optional) figure and axis object. Defaults to None.|
|17.|\*\*kwargs| All other keyword arguments are passed on to matplotlib.axes.Axes.imshow.|


|  No.  |  Returns  |  About  |
|-------|-----------|---------|
|  1.   |  fig      | (matplotlib.figure.Figure) figure object |
|  2.   |  ax       | (axes.Axes) axis object |


## Examples

* Here we will look into some of the examples that can help in making radar-charts using `mplsoccer`.

* **Examples Content:**
  * [Making a simple Radar Chart](#making-a-simple-radar-chart)
  * [Label And Range Fontsize](#label-and-range-fontsize)
  * [Adding Title](#adding-title)
  * [Adding title on both sides](#adding-title-on-both-sides)
  * [Adding Endnote](#adding-endnote)
  * [Changing the size of endnote](#changing-the-size-of-endnote)
  * [Changing color of endnote](#changing-color-of-endnote)
  * [Saving radar chart](#saving-radar-chart)
  * [Changing dpi](#changing-dpi)
  * [Changing Font](#changing-font)
  * [Adding Image](#adding-image)
  * [Making comparison radar chart](#making-comparison-radar-chart)
  * [Changing alpha values for comparison radar](#changing-alpha-values-for-comparison-radar)
  * [Passing fig, ax](#passing-fig-ax)
  * [Making clean radar charts](#making-clean-radar-charts)
  * [Multiple Radar Charts in One Figure](#multiple-radar-charts-in-one-figure)

### Making a simple Radar Chart

* Here we will make a very simple radar chart using `mplsoccer` module `radar_chart`. 

* We will be making use of `ranges`, `params`, `values` and `radar_color` parameter.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## instantiate object
radar = Radar()

## plot radar
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                                 radar_color=['#B6282F', '#FFFFFF'])
```

* *Output:*

![1_Making_Simple](https://user-images.githubusercontent.com/33928040/92324984-7e9f8200-f064-11ea-9958-adef7ba4ae75.jpg)


### Label And Range Fontsize

* Here we will see how we can use `label_fontsize` and `range_fontsize` parameter. We will here increase the values of these two parameters and you will see that the ranges and labels now are larger than the previous output.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## instantiate object -- changing fontsize
radar = Radar(label_fontsize=12, range_fontsize=7.5)    ## change in parameter value

## plot radar
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'])
```

* *Output:*

![2_Label_Range_Fontsize](https://user-images.githubusercontent.com/33928040/92325010-c0302d00-f064-11ea-93a2-e97c2ef2c91e.jpg)


### Adding Title

* Here we will create a dictionary to specify title values and will pass it to `plot_radar` method.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## instantiate object
radar = Radar()

## plot radar -- title
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title)
```

* *Output:*

![3_Adding_title](https://user-images.githubusercontent.com/33928040/92325077-62e8ab80-f065-11ea-88aa-9d166049e0b4.jpg)


### Adding title on both sides

* Here we will see how to add title on both top-left and top-right sides of the plot using `title`.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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
    title_name='Sergiño Dest',     ## title on left side
    subtitle_name='AFC Ajax',      ## subtitle on left side
    subtitle_color='#B6282F',
    title_name_2='Radar Chart',    ## title on right side
    subtitle_name_2='Fullback',    ## subtitle on right side
    subtitle_color_2='#B6282F',
    title_fontsize=18,             ## same fontsize for both title
    subtitle_fontsize=15,          ## same fontsize for both subtitle
)

## instantiate object
radar = Radar()

## plot radar -- title
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title)
```

* *Output:*

![4_example_02](https://user-images.githubusercontent.com/33928040/92325186-384b2280-f066-11ea-8fa9-cb14157fa423.jpg)


* The user can also change the fontsize for top-right title and subtitle. The below code shows how to do it.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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
    title_fontsize=18,                ## fontsize for left-title
    subtitle_fontsize=15,             ## fontsize for left-subtitle
    title_fontsize_2=14,              ## fontsize for right-title
    subtitle_fontsize_2=14            ## fontsize for right-subtitle
)

## instantiate object
radar = Radar()

## plot radar -- title
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title)
```

* *Output:*

![a](https://user-images.githubusercontent.com/33928040/92325240-9f68d700-f066-11ea-9c2a-ed4e14c5786a.jpg)


### Adding Endnote

* Let's now see how one can add some endnote to the radar chart.

* **Note:** The *Inspired By* endnote will always be there, in order to thank those who developed and popularized it.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "viz made by: Anmol Durgapal(@slothfulwave612)\ncreated using mplsoccer"

## instantiate object
radar = Radar()

## plot radar -- endnote
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                          endnote=endnote)
```

* *Output:*

![x](https://user-images.githubusercontent.com/33928040/100632816-4b168000-3353-11eb-97e0-dcff41811105.jpg)


## Changing the size of endnote

* Here we can pass `end_size` parameter to `plot_radar` method to change the fontsize of endnote.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object
radar = Radar()

## plot radar -- end_size
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                          endnote=endnote, end_size=11.3)   
```

* *Output:*

![6_endnote_size](https://user-images.githubusercontent.com/33928040/92325388-e0152000-f067-11ea-8db8-adbb59ed20bd.jpg)


### Changing color of endnote

* We can pass `end_color` argument in order to change the color of endnote.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object
radar = Radar()

## plot radar -- end_color
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                          endnote=endnote, end_size=10, end_color="#121212")
```

* *Output:*

![6_fendnote_color](https://user-images.githubusercontent.com/33928040/92325408-16529f80-f068-11ea-85ae-8b3f60e69d83.jpg)


### Saving radar chart

* One can pass `filename` argument in `plot_radar` method to save the radar chart.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object
radar = Radar()

## plot radar -- filename
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                           endnote=endnote, 
                           filename="my_radar.jpg")
```

* *Output:*

![7_my_radar](https://user-images.githubusercontent.com/33928040/92325442-7cd7bd80-f068-11ea-8f1c-f77e7d341102.jpg)


## Changing dpi

* *dpi* or *Dots per Inch*.

* We can increase or decrease the resolution of our plot by passing in the `dpi` parameter to `plot_radar` method. More the dpi better the plot looks(high-resolution).

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object
radar = Radar()

## plot radar -- filename and dpi
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                           endnote=endnote,  
                           filename="my_radar.jpg", dpi=500)
```

* *Output:*

![8_my_radar_dpi](https://user-images.githubusercontent.com/33928040/92325487-e5269f00-f068-11ea-9516-7a5942f5f1f9.jpg)

### Changing Font

* Pass `fontfamily` argument to `Radar` to change the font.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object -- fontfamily
radar = Radar(fontfamily="Gayathri")

## plot radar
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title, endnote=endnote)
```

* *Output:*

![10_fontfamily](https://user-images.githubusercontent.com/33928040/92325600-a9400980-f069-11ea-96cf-04c53b652fe6.jpg)


### Adding Image

* We can also add image to our radar chart. Let's see two ways of doing it.

* We can use `soccerplots.utils.add_image` method for adding an image.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar
from mplsoccer.utils import add_image

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object
radar = Radar()

## plot radar 
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                           endnote=endnote)

## add image -- http://bit.do/ajax_img
fig = add_image(image="ajax.png", fig=fig, left=0.464, bottom=0.81, width=0.1, height=0.075)
```

* *Output:*

![10_image](https://user-images.githubusercontent.com/33928040/92325664-0c31a080-f06a-11ea-9944-5ac93c2ed0d0.jpg)


* An alternative way is to pass `image` and `img_coord` argument to `plot_radar` method.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object 
radar = Radar()

## plot radar -- image link: http://bit.do/ajax_img
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#FFFFFF'], title=title,
                           image='ajax.png', image_coord=[0.464, 0.81, 0.1, 0.075],
                           endnote=endnote)
```

* *Output:*

![10_image_2](https://user-images.githubusercontent.com/33928040/92325706-56b31d00-f06a-11ea-9134-0bff594ca105.jpg)


### Making comparison radar chart

* We can use `mplsoccer` to make comparison chart as well.

* Here is how one can do it.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object
radar = Radar()

## plot radar -- compare
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#B6282F', '#344D94'], 
                           title=title, endnote=endnote,
                           compare=True)
```

* *Output:*

![11_compare](https://user-images.githubusercontent.com/33928040/92325747-9ed23f80-f06a-11ea-9818-411d15ec7c98.jpg)


### Changing alpha values for comparison radar

* We can also change the alpha value to shade dark/light the polygon covering the area in the radar-chart.

* One can pass `alphas` which is a list of alpha values to obtain required changes.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object 
radar = Radar()

## plot radar -- alphas
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                                 radar_color=['#B6282F', '#344D94'], 
                                 alphas=[0.8, 0.6], title=title, endnote=endnote,
                                 compare=True)
```

* *Output:*

![12_compare_alpha](https://user-images.githubusercontent.com/33928040/92325798-f670ab00-f06a-11ea-8f45-bdc53c312a4f.jpg)


### Passing fig, ax

* If the user has it's own defined `figure` and `axis` object, can pass it to `figax` argument in `plot_radar` method to plot radar in defined `figure` and `axis` object.

* *Code Snippet:*

```python
import matplotlib.pyplot as plt
from mplsoccer.radar_chart import Radar

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

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## make a subplot
fig, ax = plt.subplots(figsize=(20, 10))

## instantiate object 
radar = Radar()

## plot radar -- figax
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                           values=values, radar_color=['#B6282F', '#FFFFFF'],
                           title=title, endnote=endnote, figax=(fig,ax))
```

* *Output:*

![12_figax](https://user-images.githubusercontent.com/33928040/92325841-59fad880-f06b-11ea-98b8-157401c7e745.jpg)

### Making Clean Radar Charts

* A clean radar chart is one where the final plot does not include the range and param values only showing the shape of the polygon.

* To make a clean radar chart, one can pass one of the following combinations to the `plot_radar` method:
  
  1. Pass `params=None`, this will not plot param names in the radar-chart.
  
      * *Code Snippet:*
        ```python
        from mplsoccer.radar_chart import Radar
        
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

        ## endnote 
        endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

        ## instantiate object
        radar = Radar()

        ## plot radar
        fig, ax = radar.plot_radar(ranges=ranges, params=None, values=values,
                                   radar_color=['#B6282F', '#FFFFFF'], title=title, endnote=endnote
        )
        ```
      * *Output:*
      ![clean_with_range](https://user-images.githubusercontent.com/33928040/100618949-7d6bb180-3342-11eb-9226-e9cfd7d6d654.jpg)
  
  2. Pass `plot_range=False`, this will not plot the range values in the radar-chart.
      
      * *Code Snippet:*
        ```python
        from mplsoccer.radar_chart import Radar
        
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

        ## endnote 
        endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

        ## instantiate object
        radar = Radar()

        ## plot radar
        fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, plot_range=False,
                                   radar_color=['#B6282F', '#FFFFFF'], title=title, endnote=endnote
        )
        ```
      
      * *Output:*
      ![clean_wo_range](https://user-images.githubusercontent.com/33928040/100619683-84df8a80-3343-11eb-8a6d-62d1788221ce.jpg)
      
  3. Pass `params=None` and `plot_range=False` to produce super-clean-radar
     
     * *Code Snippet:*
       ```python
        from mplsoccer.radar_chart import Radar
        
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

        ## endnote 
        endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

        ## instantiate object
        radar = Radar()

        ## plot radar
        fig, ax = radar.plot_radar(ranges=ranges, params=None, values=values, plot_range=False,
                                   radar_color=['#B6282F', '#FFFFFF'], title=title, endnote=endnote
        )
       ```
     
     * *Output:*
     ![super_clean](https://user-images.githubusercontent.com/33928040/100620406-675ef080-3344-11eb-87ca-399b344fde57.jpg)
     
  4. Make clean-comparison-charts
      
      * *Code Snippet:*
        ```python
        from mplsoccer.radar_chart import Radar
        
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

        ## endnote 
        endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

        ## instantiate object
        radar = Radar()

        ## plot radar -- compare
        fig, ax = radar.plot_radar(
            ranges=ranges, params=None, values=values, plot_range=False,
            radar_color=['#B6282F', '#344D94'], 
            title=title, endnote=endnote, compare=True
        )
        ```
      * *Output:*
      ![clean_compare](https://user-images.githubusercontent.com/33928040/100620912-fc61e980-3344-11eb-962c-13c56eacdd72.jpg)
      
### Multiple Radar Charts in One Figure

* Here is a code snippet one can use to plot multiple radar charts in one single figure. (there can be multiple ways of doing this)

* *Code Snippet:*
```python
import matplotlib.pyplot as plt
from mplsoccer.radar_chart import Radar
from mplsoccer.utils import set_size

## parameter names
params = [
    "Param 01", "Param 02", "Param 03", "Param 04", "Param 05", "Param 06"
]

## range values
ranges = [
    (0.25, 0.65), (0.55, 1.0), (0.09, 0.2), (0.2, 2.5), (4.1, 10.5), (0.3, 3.5)
]

## parameter value
values = [
    [0.90, 1.11, 0.175, 1.92, 8.37, 3.26],      ## for player 01
    [0.64, 1.10, 0.23, 1.69, 5.76, 2.12],       ## for player 02
    [0.28, 0.9, 0.15, 1.23, 6.26, 3.0],         ## for player 03
    [0.71, 0.86, 0.03, 1.56, 5.67, 2.2],        ## for player 04
    [0.55, 0.5, 0.11, 2, 7.7, 2.12],            ## for player 05
    [0.33, 0.7, 0.18, 1.4, 4.0, 2.12]           ## for player 06
]

## create subplot
fig, ax = plt.subplots(
    nrows=3, ncols=2
)

## init object of Radar class
radar = Radar()

## traverse through the axis
for counter, axes in zip(range(0, len(values)), fig.get_axes()):
    ## plot radar
    fig, axes = radar.plot_radar(
        ranges=ranges, params=params, values=values[counter],
        radar_color=['#B6282F', '#FFFFFF'], end_color="#FFFFFF", figax=(fig, axes)
    )
    
    ## plot axes title
    axes.text(
        0, 22,
        f"Player {counter+1}", fontsize=20, color="#121212", fontfamily="Liberation Serif", fontweight="bold",
        ha="center", va="center"
    )
    
    ## set size for axes
    set_size(20,20,axes)

## plot figure title
plt.figtext(
    0.5, 1,
    f"Multiple Radar Charts in One Figure", fontsize=25, color="#121212", fontfamily="Liberation Serif", fontweight="bold",
    ha="center", va="center"
)
  
## tight layout    
plt.tight_layout(pad=3)
```

* *Output:*
![final_fig](https://user-images.githubusercontent.com/33928040/100630735-eeb26100-3350-11eb-9382-510f7d5f4215.jpg)


## Dark Theme Template

* Using `mplsoccer` package one can plot radar chart with his/her own defined theme, i.e. can now change the background, label and range colors as well.

* Here are some examples on how to make *dark mode radar charts* using `mplsoccer`.

* **Contents:**
  * [Dark Theme](#dark-theme)
  * [Adding Image in Dark Mode](#adding-image-in-dark-mode)
  * [Alpha value to image](#alpha-value-to-image)
  * [Making Comparison Radar Chart](#making-comparison-radar-chart)

### Dark Theme

* The user can update the colors by passing `background_color`, `patch_color`, `label_color` and `range_color` argument to the `Radar`.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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
    title_name="Sergiño Dest",
    title_color="#E3DDED",
    subtitle_name="AFC Ajax",
    subtitle_color="#C72C41",
    title_name_2="Radar Chart",
    title_color_2="#E3DDED",
    subtitle_name_2='Fullback',
    subtitle_color_2='#C72C41',
    title_fontsize=18,
    subtitle_fontsize=15
)
    
## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#FFFFFF",
              range_color="#FFFFFF")
              
## plot radar
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                           values=values, radar_color=['#1c547f', '#CF6679'], 
                           title=title, endnote=endnote)
```

* *Output:*

![13_dark_1](https://user-images.githubusercontent.com/33928040/92325931-f1f8c200-f06b-11ea-97ef-0454aaae323f.jpg)


### Adding Image in Dark Mode

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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
    title_name="Sergiño Dest",
    title_color="#E3DDED",
    subtitle_name="AFC Ajax",
    subtitle_color="#C72C41",
    title_name_2="Radar Chart",
    title_color_2="#E3DDED",
    subtitle_name_2='Fullback',
    subtitle_color_2='#C72C41',
    title_fontsize=18,
    subtitle_fontsize=15
)

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#FFFFFF",
              range_color="#FFFFFF")
              
## plot radar -- image link: http://bit.do/ajax_dark           
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                           values=values, radar_color=['#1c547f', '#CF6679'], 
                           title=title, endnote=endnote,
                           image='ajax_dark.png', image_coord=[0.495, 0.805, 0.04, 0.1])
```

* *Output:*

![14_dark_img](https://user-images.githubusercontent.com/33928040/92325980-603d8480-f06c-11ea-9e41-0f14e0e37b50.jpg)


### Alpha value to image

* One can pass the `alpha` value to `plot_radar` method to adjust the transparency of the image.

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

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
    title_name="Sergiño Dest",
    title_color="#E3DDED",
    subtitle_name="AFC Ajax",
    subtitle_color="#C72C41",
    title_name_2="Radar Chart",
    title_color_2="#E3DDED",
    subtitle_name_2='Fullback',
    subtitle_color_2='#C72C41',
    title_fontsize=18,
    subtitle_fontsize=15
)

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#FFFFFF",
              range_color="#FFFFFF")
              
## plot radar              
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                           values=values, radar_color=['#1c547f', '#CF6679'], 
                           title=title, endnote=endnote,
                           image='ajax_dark.png', image_coord=[0.495, 0.805, 0.04, 0.1],
                           alpha=0.7)
```

* *Output:*

![15_dark_img_alpha](https://user-images.githubusercontent.com/33928040/92326033-c4f8df00-f06c-11ea-970c-cd3cc13ace7b.jpg)


### Making Comparison Radar Chart

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

## parameter names
params = ['xAssists', 'Key Passes', 'Crosses Into Box', 'Cross Competion', 'Deep Completions', 
          'Progressive Passes', 'Prog. Passes Accuracy%', 'Dribbles', 'Progressive Runs', 
          'PADJ Interceptions', 'Succ. Def Actions', 'Def Duel Win%']

## range values
ranges = [(0.0, 0.15), (0.0, 0.67), (0.06, 0.63), (19.51, 50.0), (0.35, 1.61), (6.45, 11.94), (62.94, 79.46), (0.43, 4.08), 
(0.6, 2.33), (5.01, 7.2), (9.02, 12.48), (52.44, 66.67)]

## parameter value
values = [
    [0.11, 0.53, 0.70, 27.66, 1.05, 6.84, 84.62, 4.56, 2.22, 5.93, 8.88, 64.29],   ## for Sergino Dest
    [0.07, 0.36, 0.16, 32.14, 1.04, 7.37, 74.46, 3.68, 2.40, 6.87, 8.97, 61.14]    ## for Nelson Semedo
]

## title
title = dict(
    title_name='Sergiño Dest',
    title_color='#9B3647',
    subtitle_name='AFC Ajax',
    subtitle_color='#ABCDEF',
    title_name_2='Nelson Semedo',
    title_color_2='#3282b8',
    subtitle_name_2='Barcelona',
    subtitle_color_2='#ABCDEF',
    title_fontsize=18,
    subtitle_fontsize=15,
)

## endnote 
endnote = "Visualization made by: Anmol Durgapal(@slothfulwave612)\nAll units are in per90"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0",
              range_color="#F0FFF0")
              
## plot radar              
fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                           radar_color=['#9B3647', '#3282b8'], 
                           title=title, endnote=endnote,
                           alphas=[0.55, 0.5], compare=True)
```

* *Output:*

![15_dark_compare](https://user-images.githubusercontent.com/33928040/92326083-1a34f080-f06d-11ea-9cd7-40f5176a1dfe.jpg)


## Some More Templates

* Thanks to [Gareth Cooper](#https://twitter.com/ThatGarateyjc).

* **Contents:**
  * [Robert Lewandowski](#robert-lewandowski)
  * [Erling Braut Håland](#erling-braut-håland)
  * [Rodri](#rodri)

### Robert Lewandowski 

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

## parameter names
params = ["xG90", "Goals", "xG/Shot", "Shots On Target", "Touches In Box",
          "Shot Creating Actions", "Assists", "Pressures", "Successful Pressures",
          "Aerial Wins", "Successful Dribbles", "Fouls Won"]

## range values
ranges = [(0.25, 0.65), (0.55, 1.0), (0.09, 0.2), (0.2, 2.5), (4.1, 10.5),
          (0.3, 3.5), (0.09, 0.25), (8.0, 20.0), (0.5, 4.2), 
          (0.2, 2.2), (1.5, 8.5), (0.09, 2.9)]

## parameter value
values = [0.90, 1.11, 0.175, 1.92, 8.37, 3.26, 0.13, 12.6, 4.01, 2.02, 1.95, 1.40]

## title values
title = dict(
    title_name="Robert Lewandowski",
    title_color="#F0FFF0",
    subtitle_name="Bayern Munich",
    subtitle_color="#C72C41",
    title_name_2="Bundesliga 2019/20",
    title_color_2="#F0FFF0",
    subtitle_name_2="Time Played: 30.7 90s",
    subtitle_color_2='#F0FFF0',
    title_fontsize=18,
    subtitle_fontsize=15
)

## endnote 
endnote = "Credits: @ThatGarateyjc\nVisualization made by: Anmol Durgapal(@slothfulwave612)"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0",
              range_color="#F0FFF0")
              
## plot radar              
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                           values=values, radar_color=['#1c547f', '#CF6679'], 
                           title=title, endnote=endnote)
```

* *Output:*

![16_cf_st_temp](https://user-images.githubusercontent.com/33928040/92326168-bd860580-f06d-11ea-9b7d-b897b4390bc1.jpg)


### Erling Braut Håland

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

## parameter names
params = ["xG90", "Goals", "xG/Shot", "Shots On Target", "Touches In Box",
          "Shot Creating Actions", "Assists", "Pressures", "Successful Pressures",
          "Aerial Wins", "Successful Dribbles", "Fouls Won"]

## range values
ranges = [(0.25, 0.65), (0.55, 1.0), (0.09, 0.2), (0.2, 2.5), (4.1, 10.5),
          (0.3, 3.5), (0.09, 0.25), (8.0, 20.0), (0.5, 4.2), 
          (0.2, 2.2), (1.5, 8.5), (0.09, 2.9)]

## parameter value
values = [0.69, 1.10, 0.23, 1.69, 5.76, 2.12, 0.17, 11.9, 3.39, 1.78, 1.02, 0.59]

## title values
title = dict(
    title_name="Erling Braut Håland",
    title_color="#F0FFF0",
    subtitle_name="Borussia Dortmund",
    subtitle_color="#F2A365",
    title_name_2="Bundesliga 2019/20",
    title_color_2="#F0FFF0",
    subtitle_name_2="Time Played: 11.8 90s",
    subtitle_color_2='#F0FFF0',
    title_fontsize=18,
    subtitle_fontsize=15
)

## endnote 
endnote = "Credits: @ThatGarateyjc\nVisualization made by: Anmol Durgapal(@slothfulwave612)"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#F0FFF0",
              range_color="#F0FFF0")
              
## plot radar              
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                           values=values, radar_color=['#30475e', '#F2A365'], 
                           title=title, endnote=endnote)
```

* *Output:*
![16_cf_st_temp_2](https://user-images.githubusercontent.com/33928040/92326200-09d14580-f06e-11ea-8696-9a9297aa7f2d.jpg)


### Rodri

* *Code Snippet:*

```python
from mplsoccer.radar_chart import Radar

## parameter names
params = ["Pass %", "Prog Passes", "KP", "GCA", "Succ Drib", "Fouls Won",
          "Tack Won", "Tack + Int", "Pressures", "Press Succ", "Assists", "xA"]

## range values
ranges = [(72.0, 91.0), (3.1, 11.5), (0.2, 2.2), (0.4, 2.0), (0.7, 2.7),
          (0.09, 4.3), (0.5, 3.1), (1.2, 5.2), (11.0, 25.0), (2.3, 6.7),
          (0.05, 0.15), (0.04, 0.12)]

## parameter value
values = [93.1, 6.09, 1.16, 0.11, 0.07, 1.16, 1.59, 3.33, 16.7, 4.96, 0.07, 0.06]

## title values
title = dict(
    title_name="Rodri",
    title_color="#F0FFF0",
    subtitle_name="Manchester City",
    subtitle_color="#73f9ff",
    title_name_2="Premier League 2019/20",
    title_color_2="#F0FFF0",
    subtitle_name_2="Time Played: 27.6 90s",
    subtitle_color_2='#F0FFF0',
    title_fontsize=18,
    subtitle_fontsize=15
)

## endnote 
endnote = "Credits: @ThatGarateyjc\nVisualization made by: Anmol Durgapal(@slothfulwave612)"

## instantiate object 
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#BFE9BF",
              range_color="#BFE9BF")

## plot radar
fig, ax = radar.plot_radar(ranges=ranges, params=params, 
                               values=values, radar_color=['#0f4c75', '#e94560'], 
                           title=title, endnote=endnote)
```

* *Output:*

![17_cm_temp](https://user-images.githubusercontent.com/33928040/92326219-31281280-f06e-11ea-9ba2-f1354137f66f.jpg)

---
