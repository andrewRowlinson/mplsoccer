# Bumpy Charts

## Content

* [Overview](#overview)
* [Documentation](#soccerplotsbumpy_chartbumpy)
* [Examples](#examples)

## Overview

* *Bumpy Chart* or *Bump Chart* is used to compare two dimensions against each other using one of the Measure value.

* They are very useful for exploring the changes in Rank of a value over a time dimension or place dimension or some other dimension relevant to the analysis.

* Using `soccerplots` package one can easily build a bumpy chart, here we will look into the documentation and some examples that will help user to create bumpy charts.
  
## soccerplots.bumpy_chart.Bumpy

```python
soccerplots.bumpy_chart.Bumpy(
    background_color="#1B1B1B", scatter_color="#4F535C", scatter_points='o', scatter_size=100,
    ticklabel_size=13, fontfamily="Liberation Serif", curviness=0.85,
    rotate_xticks=0, rotate_yticks=0, show_right=False, label_size=20, labelpad=20, horizontalalignment_x='left',
    horizontalalignment_y='right', alignment_xvalue=0.035, alignment_yvalue=0.16, label_color='#FFFFFF', 
    plot_labels=True
)
```

|  No.  |  Parameter  |  About Parameter  |
|-------|-------------|-------------------|
|1.| background_color| (str, optional) background color for the plot. Defaults to "#1B1B1B".|
|2.| scatter_color| (str, optional) color value for our scater points. Defaults to "#4F535C".|
|3.| scatter_points| (str, optional) type of scatter point user wants to plot. Defaults to 'o'.|
|4.| scatter_size| (float, optional) size of the scatter_points. Defaults to 100.|
|5.| ticklabel_size| (float, optional) fontsize of the ticklabel. Defaults to 13.|
|6.| fontfamily| (str, optional) fontfamily available in matplotlib. Defaults to "Liberation Serif".|
|7.| curviness| (float, optional) value of the curved line. Defaults to 0.85.|
|8.| rotate_xticks| (int, optional) rotation of xticklabels in degrees. Defaults to 0.|
|9.| rotate_yticks| (int, optional) rotation of yticklabels. Defaults to 0.|
|10.| show_right| (bool, optional) yticklabels to be shown at the right y-axis or not. Defaults to False.|
|11.| label_size| (int, optional) fontsize of the x and y labels. Defaults to 20.|
|12.| labelpad| (int, optional) padding between labels and ticklables. Defaults to 20.|
|11.| horizontalalignment_x| (str, optional) alignment for the x-label. Defaults to 'left'.|
|12.| horizontalalignment_y| (str, optional) alignment for the y-label. Defaults to 'right'.|
|13.| alignment_xvalue| (float, optional) value for alignment of x-label. Defaults to 0.035.|
|14.| alignment_yvalue| (float, optional) value for alignment of y-label. Defaults to 0.16.|
|15.| label_color| (str, optional) color value for labels. Defaults to '#FFFFFF'.|
|16.| plot_labels| (bool, optional): to plot the labels. Defaults to True.|

      
## soccerplots.bumpy_chart.Bumpy.plot      
      
```python
soccerplots.bumpy_chart.Bumpy.plot(
     x_list, y_list, values, highlight_dict, filename=None, dpi=300, figsize=(12,8), lw=2, show=True, 
     x_label=None, y_label=None, title=None, title_dict=None, xy=None, title_color="#FFFFFF", title_size=25, 
     endnote=None, xy_end=None, end_color="#808080", end_size=15, image=None, image_coord=None, alpha=1, 
     interpolation="none", xlim=None, ylim=None, figax=None, **kwargs
)
```

|  No.  |  Parameter  |  About Parameter  |
|-------|-------------|-------------------|
|1.|x_list| (list) xticklabel values(serial-wise order from left to right).|
|2.|y_list| (list) yticklabel values(serial-wise order from top to bottom).|
|3.|values| (dict) containing key as team-name and value as list of rank for that team.|
|4.|highlight_dict| (dict) containing key as the team-name to be highlighted with their corresponding color.|
|5.|filename| (str, optional) the name of the file per which plot will be saved. Defaults to None.|
|6.|dpi| (int, optional) dots per inch value. Defaults to 300.|
|7.|figsize| (tuple, optional) size of the plot. Defaults to (12,8).|
|8.|lw| (int, optional) line-width for the lines in the plot. Defaults to 2.|
|9.|show| (bool, optional) whether to display the plot or not. Defaults to True.|
|10.|x_label| (str, optional) x-label-name. Defaults to None.|
|11.|y_label| (str, optional) y-label-name. Defaults to None.|
|12.|title| (str, optional) the title of the plot. Defaults to None.|
|13.|title_dict| (dict, optional) extra information about title. Defaults to None.|
|14.|xy| (tuple, optional) x and y coordinate for the title. Defaults to None.|
|15.|title_color| (str, optional) color value for title. Defaults to "#FFFFFF".|
|16.|title_size| (float, optional) size of the title. Defaults to 25.|
|17.|endnote| (str, optional) the endnote of the plot. Defaults to None.|
|18.|xy_end| (tuple, optional) x and y coordinate for endnote. Defaults to None.|
|19.|end_color| (str, optional) color value for the endnote. Defaults to "#808080".|
|20.|end_size| (float, optional) size of endnote. Defaults to 15.|
|21.|image| (str, optional) path of the image to be added. Defaults to None.|
|22.|image_coord| (list, optional) containing left, bottom, width, height for image. Defaults to None.|
|23.|alpha| (float, optional) the alpha value for the image. Defaults to 1.|
|24.|interpolation| (str, optional) interpolation for the image. Defaults to "none".|
|25.|xlim| (tuple, optional) limit for x axis value. Defaults to None.|
|26.|ylim| (tuple, optional) limit for y axis value. Defaults to None.|
|27.|figax| (tuple, optional) figure and axis object. Defaults to None.

|  No.  |  Returns  |  About  |
|-------|-----------|---------|
|  1.   |  fig      | (matplotlib.Figure.figure) figure object |
|  2.   |  ax       | (axes.Axes) axis object |
 

## Examples

* Here we will look into some of the examples that can help in making bump-charts using `soccerplots`.

* **Examples Content:**
  * [Making a simple Bump Chart](#making-a-simple-bump-chart)
  * [Changing ticklables and labels size](#changing-ticklables-and-labels-size)
  * [Adding title](#adding-title)
  * [Title color](#title-color)
  * [Adding Image](#adding-image)
  * [Adjust alpha for image](#adjust-alpha-for-image)
  * [Change scatter points](#change-scatter-points)
  * [Show labels on right side](#show-labels-on-right-side)
  * [Aligning Labels](#aligning-labels)
  * [Changing Theme](#changing-theme)
  * [Labelpad](#labelpad)
  * [Changing Font](#changing-font)
  * [Adding Endnote](#adding-endnote)
  * [Saving The Plot](#saving-the-plot)
  * [Some More Examples](#some-more-examples)

### Making a simple Bump Chart

* Here we will make a simple bump-chart, comparing the weekwise standing of Premier League teams in 2019/20 season.

* And will highlight out `Man City` with *skyblue* color, `Liverpool` with *crimson* color and `Man Utd` with *gold* color.

* Data [here](http://bit.do/data_epl) (scrapped from transfermarkt).

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## instantiate object
bumpy = Bumpy(rotate_xticks=90)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position'
)
```

* *Output:*

![1_simple_bumpy](https://user-images.githubusercontent.com/33928040/92328350-dc8c9380-f07d-11ea-87d0-7d8abb6a02e6.jpg)


### Changing ticklables and labels size

* One can pass `ticklabel_size` and `label_size` to change the fontsize for ticklables and labels.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## instantiate object
bumpy = Bumpy(rotate_xticks=90, ticklabel_size=17, label_size=30)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position'
)
```

* *Output:*

![2_labelsize](https://user-images.githubusercontent.com/33928040/92328420-44db7500-f07e-11ea-9a28-3329fbfebc0e.jpg)


### Adding title

* `Bumpy.plot` method uses `soccerplots.utils.plot_text` method to plot title.

* So the user have to pass `text`(i.e. title) and `text_dict`(i.e. dict specifying which word to modify).

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(rotate_xticks=90, ticklabel_size=17, label_size=30)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5]
)
```

* *Output:*

![3_title](https://user-images.githubusercontent.com/33928040/92328482-c0d5bd00-f07e-11ea-9885-92bdc21a1537.jpg)


### Title color

* `title_color` argument is the default color for the title if `title_dict` is not passed it will use that color. It is also the same color for the rest of the words that are not specified in the `title_dict`.

* **Note:** If the title wont show in the plot try adjusting `ylim` in `plot` method as shown below.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(rotate_xticks=90, ticklabel_size=17, label_size=30)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    title_color="grey"
)
```

* *Output:*

![3_title_rest](https://user-images.githubusercontent.com/33928040/92328535-2629ae00-f07f-11ea-9e73-76b0f43df57d.jpg)


### Adding Image

* The user can pass `image` and `image_coord` to the `plot` method to plot an image.

* **Note:** If the image wont show in the plot try adjusting `ylim` in `plot` method as shown below.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(rotate_xticks=90, ticklabel_size=17, label_size=30)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(16.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="epl.png", image_coord=[0.135, 0.8, 0.1, 0.1]
)
```

* *Output:*

![4_image](https://user-images.githubusercontent.com/33928040/92328620-a3552300-f07f-11ea-89e8-1925cc794154.jpg)


### Adjust alpha for image

* To control the transparency of the image pass `alpha` argument to `plot` method.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(rotate_xticks=90, ticklabel_size=17, label_size=30)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(16.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="epl.png", image_coord=[0.135, 0.8, 0.1, 0.1], alpha=0.7
)
```

* *Output:*

![4_image_alpha](https://user-images.githubusercontent.com/33928040/92328646-db5c6600-f07f-11ea-8726-98bfe139088d.jpg)


### Change scatter points

* The user can also change the scatter points style. Default is a circle.

* Visit [here](https://matplotlib.org/3.3.1/api/markers_api.html) to see all available styles.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, label_size=30)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(16.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="epl.png", image_coord=[0.135, 0.8, 0.1, 0.1]
)
```

* *Output:*

![5_scatter_points](https://user-images.githubusercontent.com/33928040/92329357-9129b380-f084-11ea-95f9-b552b1ffab5f.jpg)


### Show labels on right side

* To show the y-ticklables on right-side, the user can pass `show_right=True`.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, label_size=30,
            show_right=True)
            
## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(16.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="epl.png", image_coord=[0.135, 0.8, 0.1, 0.1]
)
```

* *Output:*

![6_show_right](https://user-images.githubusercontent.com/33928040/92329374-aa326480-f084-11ea-8566-2690fb84f17e.jpg)


### Aligning Labels

* To change the position of the x-lables and y-labels the user can use `alignment_xvalue` and `alignment_yvalue` parameters.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man City": "skyblue", "Liverpool": "crimson", "Man Utd": "gold"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Liverpool, Man_City and Man_Utd"""

## title info
title_dict = {
    "Liverpool,": dict(color="crimson", ignore_last=True),
    "Man_City": dict(color="skyblue", ignore=True),
    "Man_Utd": dict(color="gold", ignore=True)
}

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, label_size=30,
            show_right=True, alignment_xvalue=0.44, alignment_yvalue=0.44)
            
## plot bumpy chart            
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(16.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="epl.png", image_coord=[0.135, 0.8, 0.1, 0.1]
)
```

* *Output:*

![7_align_labels](https://user-images.githubusercontent.com/33928040/92329409-ea91e280-f084-11ea-93ac-474c1e6a2461.jpg)


### Changing Theme

* The default theme is a dark one, but the user have the access to change it. 

* One can pass `background_color`, `scatter_color`, `label_color` arguments.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man Utd": "crimson", "Chelsea": "blue"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Man_Utd and Chelsea"""

## title info
title_dict = {
    "Man_Utd": dict(color="crimson", ignore=True),
    "Chelsea": dict(color="blue")
}

## instantiate object
bumpy = Bumpy(background_color="#FFFFFF", scatter_color="grey", label_color="#000000",
              scatter_points="D", rotate_xticks=90, ticklabel_size=17, 
              label_size=30,show_right=True)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    title_color="#121212"
)
```

* *Output:*

![9_color_diff](https://user-images.githubusercontent.com/33928040/92329503-655afd80-f085-11ea-99aa-0669d4caf443.jpg)


### Labelpad

* To increase or decrease the distance between labels and ticklabels one can use `labelpad` argument.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man Utd": "crimson", "Chelsea": "skyblue"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Man_Utd and Chelsea"""

## title info
title_dict = {
    "Man_Utd": dict(color="crimson", ignore=True),
    "Chelsea": dict(color="skyblue")
}

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, 
              label_size=30,show_right=True, labelpad=45)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5]
)
```

* *Output:*

![10_labelpad](https://user-images.githubusercontent.com/33928040/92329544-a6531200-f085-11ea-9666-cbacb28b2fa3.jpg)


### Changing Font

* To change the font pass `fontfamily` argument to `Bumpy`.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man Utd": "crimson", "Chelsea": "skyblue"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Man_Utd and Chelsea"""

## title info
title_dict = {
    "Man_Utd": dict(color="crimson", ignore=True),
    "Chelsea": dict(color="skyblue")
}

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, 
              label_size=30,show_right=True, fontfamily="Ubuntu")

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5]
)
```

* *Output:*

![11_fontfamily](https://user-images.githubusercontent.com/33928040/92329578-e2867280-f085-11ea-91ee-9803cba17e68.jpg)


### Adding Endnote

* To add endnote pass `endnote` argument to `plot` method.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man Utd": "crimson", "Chelsea": "skyblue"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Man_Utd and Chelsea"""

## title info
title_dict = {
    "Man_Utd": dict(color="crimson", ignore=True),
    "Chelsea": dict(color="skyblue")
}

## endnote
endnote = """Created using soccerplots
Visualization by: Anmol Durgapal(@slothfulwave612)"""

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, 
              label_size=30,show_right=True)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    endnote=endnote
)
```

* *Output:*

![12_endnote](https://user-images.githubusercontent.com/33928040/92329628-4872fa00-f086-11ea-8523-1e5114c5af03.jpg)


* **Note:** One can also make use of `end_color` and `end_size` in `plot` method to change color and size of the endnote respectively.


### Saving The Plot

* Use `filename` and `dpi` arguments to save the file.

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"Man Utd": "crimson", "Chelsea": "skyblue"}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Man_Utd and Chelsea"""

## title info
title_dict = {
    "Man_Utd": dict(color="crimson", ignore=True),
    "Chelsea": dict(color="skyblue")
}

## endnote
endnote = """Created using soccerplots
Visualization by: Anmol Durgapal(@slothfulwave612)"""

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, 
              label_size=30,show_right=True)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(12.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    filename="my_bumpy.jpg", dpi=500
)
```

* *Output:*

![13_save](https://user-images.githubusercontent.com/33928040/92329680-a9023700-f086-11ea-8e78-8dc2337726fd.jpg)


### Some More Examples

* **Content:**
  * [Example 01](#example-01)
  * [Example 02](#example-02)
  * [Example 03](#example-03)
  * [Example 04](#example-04)
  * [Example 05](#example-05)
  * [Example 06](#example-06)

#### Example 01

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("la_liga.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {"FC Barcelona": "skyblue", "Real Madrid": "#D4AF37"}

## title 
title = """La Liga 2019/20 week-wise standings:
A comparison between FC_Barcelona and Real_Madrid"""

## title info
title_dict = {
    "FC_Barcelona": dict(color="skyblue", ignore=True),
    "Real_Madrid": dict(color="#D4AF37", ignore=True)
}

## endnote
endnote = "visualization made by Anmol Durgapal(@slothfulwave612)"

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, label_size=30,
            show_right=True)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(15, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="laliga.png", image_coord=[0.135, 0.805, 0.1, 0.1], endnote=endnote
)
```

* *Output:*

![a](https://user-images.githubusercontent.com/33928040/92329984-275fd880-f089-11ea-8a9d-68e92a67c4f2.jpg)


#### Example 02

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("la_liga.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {
    "Atlético Madrid": "crimson", "Sevilla FC": "gold", "Real Sociedad": "skyblue"
}

## title 
title = """La Liga 2019/20 week-wise standings:
A comparison between Atlético_Madrid, Sevilla_FC and Real_Sociedad"""

## title info
title_dict = {
    "Atlético_Madrid,": dict(color="crimson", ignore=True, ignore_last=True),
    "Sevilla_FC": dict(color="gold", ignore=True),
    "Real_Sociedad": dict(color="skyblue", ignore=True)
}

## endnote
endnote = "visualization made by Anmol Durgapal(@slothfulwave612)"

## instantiate object
bumpy = Bumpy(scatter_points="o", rotate_xticks=90, ticklabel_size=17, label_size=30,
            show_right=True)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(17.5, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="laliga.png", image_coord=[0.135, 0.805, 0.1, 0.1], endnote=endnote
)
```

* *Output:*

![a](https://user-images.githubusercontent.com/33928040/92330122-1d8aa500-f08a-11ea-8f58-30193e502325.jpg)


#### Example 03

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data: http://bit.do/data_epl
season_dict = json.load(open("epl.json"))

## match-week and highlight dict
match_day = ["Week " + str(num) for num in range(1, 39)]
team_dict = {
    "Man Utd": "#907E46", "Chelsea": "skyblue"
}

## title 
title = """Premier League 2019/20 week-wise standings:
A comparison between Man_Utd and Chelsea"""

## title info
title_dict = {
    "Man_Utd": dict(color="#907E46", ignore=True),
    "Chelsea": dict(color="skyblue"),
}

## endnote
endnote = "visualization made by Anmol Durgapal(@slothfulwave612)"

## instantiate object
bumpy = Bumpy(scatter_points="D", rotate_xticks=90, ticklabel_size=17, label_size=30,
            show_right=True)

## plot bumpy chart
fig, ax = bumpy.plot(
    x_list=match_day, y_list=list(range(1, 21)), values=season_dict, 
    highlight_dict=team_dict, figsize=(20,16), x_label='Week', y_label='Position',
    title=title, title_dict=title_dict, xy=(17, 21.5), ylim=(-0.1, 23), title_size=[30,22.5],
    image="epl.png", image_coord=[0.135, 0.805, 0.1, 0.1], endnote=endnote
)
```

* *Output:*

![a](https://user-images.githubusercontent.com/33928040/92330276-42334c80-f08b-11ea-912a-e409313b622a.jpg)


#### Example 04

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data:  http://bit.do/data_ucl
season_dict = json.load(open("ucl.json"))

## season names
season = [
    '03/04',
    '04/05',
    '05/06',
    '06/07',
    '07/08',
    '08/09',
    '09/10',
    '10/11',
    '11/12',
    '12/13',
    '13/14',
    '14/15',
    '15/16',
    '16/17',
    '17/18',
    '18/19',
    '19/20'
]

## position names
position = [
    'Winner',
    'Runner-Up',
    'Semi-Final',
    'Quarter-Final',
    'RO16',
    'Group-Stage',
    'Not-Eligible'
]

## title
text = """At which stage did the teams finished their UCL Campaign(2003-2020)
A comparison between Real_Madrid and Barcelona"""

## endnote
endnote = "visualization made by Anmol Durgapal(@slothfulwave612)"

## title dict
text_dict = {
    "Real_Madrid": dict(color="#D4AF37", ignore=True),
    "Barcelona": dict(color="skyblue")
}

## highlight dict
hdict = {
    "Real Madrid": "#D4AF37", "Barcelona": "skyblue"
}

## instantiate object
rank = Bumpy(scatter_color='#38393B', rotate_xticks=90, ticklabel_size=17, 
             label_size=30, show_right=True)

## plot bumpy chart
fig, ax = rank.plot(
    season, position, season_dict, 
    highlight_dict=hdict, figsize=(16,12),
    x_label='Season', y_label='Position', image='ucl.png', image_coord=[0.13, 0.715, 0.1, 0.2],
    title=text, xy=(10.4, 7.8), title_dict=text_dict, title_size = [24, 22],
    endnote=endnote, xy_end=(len(season)+1.6, -1.5), end_size=17, ylim=(0, 9)
)
```

* *Output:*

![ucl](https://user-images.githubusercontent.com/33928040/92330516-f97c9300-f08c-11ea-860d-c4351f47c889.jpg)


#### Example 05

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data:  http://bit.do/data_ucl
season_dict = json.load(open("ucl.json"))

## season names
season = [
    '03/04',
    '04/05',
    '05/06',
    '06/07',
    '07/08',
    '08/09',
    '09/10',
    '10/11',
    '11/12',
    '12/13',
    '13/14',
    '14/15',
    '15/16',
    '16/17',
    '17/18',
    '18/19',
    '19/20'
]

## position names
position = [
    'Winner',
    'Runner-Up',
    'Semi-Final',
    'Quarter-Final',
    'RO16',
    'Group-Stage',
    'Not-Eligible'
]

## title
text = """At which stage did the teams finished their UCL Campaign(2003-2020)
A comparison between Chelsea and Man_Utd"""

## endnote
endnote = "visualization made by Anmol Durgapal(@slothfulwave612)"

## title dict
text_dict = {
    "Man_Utd": dict(color="crimson", ignore=True),
    "Chelsea": dict(color="skyblue")
}

## highlight dict
hdict = {
    "Man Utd": "crimson", "Chelsea": "skyblue"
}

## instantiate object
rank = Bumpy(scatter_color='#38393B', rotate_xticks=90, ticklabel_size=17, 
             label_size=30, show_right=True)

## plot bumpy chart
fig, ax = rank.plot(
    season, position, season_dict, 
    highlight_dict=hdict, figsize=(16,12),
    x_label='Season', y_label='Position', image='ucl.png', image_coord=[0.13, 0.715, 0.1, 0.2],
    title=text, xy=(10.4, 7.8), title_dict=text_dict, title_size = [24, 22],
    endnote=endnote, xy_end=(len(season)+1.6, -1.5), end_size=17, ylim=(0, 9)
)
```

* *Output:*

![ucl_2](https://user-images.githubusercontent.com/33928040/92330553-5d06c080-f08d-11ea-9aa0-56bf7c175474.jpg)


#### Example 06

* *Code Snippet:*

```python
import json
from soccerplots.bumpy_chart import Bumpy

## load the data:  http://bit.do/data_ucl
season_dict = json.load(open("ucl.json"))

## season names
season = [
    '03/04',
    '04/05',
    '05/06',
    '06/07',
    '07/08',
    '08/09',
    '09/10',
    '10/11',
    '11/12',
    '12/13',
    '13/14',
    '14/15',
    '15/16',
    '16/17',
    '17/18',
    '18/19',
    '19/20'
]

## position names
position = [
    'Winner',
    'Runner-Up',
    'Semi-Final',
    'Quarter-Final',
    'RO16',
    'Group-Stage',
    'Not-Eligible'
]

## title
text = """At which stage did the teams finished their UCL Campaign(2003-2020)
A comparison between Liverpool and Man_Utd"""

## endnote
endnote = "visualization made by Anmol Durgapal(@slothfulwave612)"

## title dict
text_dict = {
    "Man_Utd": dict(color="#907E46", ignore=True),
    "Liverpool": dict(color="crimson")
}

## highlight dict
hdict = {
    "Man Utd": "#907E46", "Liverpool": "crimson"
}

## instantiate object
rank = Bumpy(scatter_points='D', scatter_color='#38393B', rotate_xticks=90, ticklabel_size=17, 
             label_size=30, show_right=True)

## plot bumpy chart
fig, ax = rank.plot(
    season, position, season_dict, 
    highlight_dict=hdict, figsize=(16,12),
    x_label='Season', y_label='Position', image='ucl.png', image_coord=[0.13, 0.715, 0.1, 0.2],
    title=text, xy=(10.4, 7.8), title_dict=text_dict, title_size = [24, 22],
    endnote=endnote, xy_end=(len(season)+1.6, -1.5), end_size=17, ylim=(0, 9)
)
```

* *Output:*

![ucl_3](https://user-images.githubusercontent.com/33928040/92330647-16fe2c80-f08e-11ea-93f8-851b5a881c60.jpg)

---
