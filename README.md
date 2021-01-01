# branch to merge mplsoccer and soccerplots

# mplsoccer

mplsoccer is a Python library for drawing soccer/football pitches in Matplotlib and loading StatsBomb open-data.

#### Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mplsoccer.

```bash
pip install mplsoccer
```

#### Docs

Here are the [docs](https://mplsoccer.readthedocs.io/) for mplsoccer.

#### Quick start

Plot a StatsBomb pitch

```python
from mplsoccer.pitch import Pitch
pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
fig, ax = pitch.draw()
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/quick_start.png?raw=true "statsbomb pitch")

#### Why mplsoccer exists

mplsoccer shares some of the tools I built for the OptaPro Analytics Forum.
At the time there weren’t any open-sourced python tools. Now alternatives exist, such as [matplotsoccer](https://pypi.org/project/matplotsoccer/).

By using mplsoccer, I hope that you can spend more time building insightful graphics rather than having to learn to draw pitches from scratch.


#### Advantages of mplsoccer

mplsoccer:

1. draws 7 different pitch types by changing a single argument, which is useful as there isn’t a standardised data format
2. extends matplotlib to plot heatmaps, (comet) lines, footballs and rotated markers
3. flips the data coordinates when in a vertical orientation so you don’t need to remember to flip them
4. creates tidy dataframes for StatsBomb data, which is useful as most of the alternatives produce nested dataframes

#### License

[MIT](https://choosealicense.com/licenses/mit)

#### Contributions
Contributions are welcome. It would be great to add the following functionality to mplsoccer:
- pass maps
- pass sonars

Examples to help others are also welcome for a gallery.

Please get in touch at rowlinsonandy@gmail.com or [@numberstorm](https://twitter.com/numberstorm) on Twitter.

#### Inspiration

mplsoccer was inspired by other people's work:
- [Peter McKeever](http://petermckeever.com/2019/01/plotting-pitches-in-python/) inspired the API design
- [ggsoccer](https://github.com/Torvaney/ggsoccer) - a library for plotting pitches in R
- [lastrow](https://twitter.com/lastrowview) - often tweets animations from matches and the accompanying code
- [fcrstats](http://fcrstats.com/) - tutorials for using football data
- [fcpython](https://fcpython.com/) - Python tutorials for using football data
- [Karun Singh](https://twitter.com/karun1710) - tweets some interesting football analytics and visuals
- [StatsBomb](https://statsbomb.com/) - great visual design and free open-data
- John Burn-Murdoch's [tweet](https://twitter.com/jburnmurdoch/status/1057907312030085120) got me interested in football analytics

#### Recent changes

View the [changelog](https://github.com/andrewRowlinson/mplsoccer/blob/master/CHANGELOG.md) for a full list of the recent changes to mplsoccer.


# soccerplots

* **soccerplots** is a Python package that can be used for making visualizations for football analytics.

* The main aim of `soccerplots` is to save time for analysts so they can focus more on the analysis rather than coding the visualizations from scratch.

* If you have any problem or confusion regarding how to use it ping me [here](https://twitter.com/slothfulwave612).    

* **soccerplots v1.0.0:**
  
  * Now the users can make their own defined theme for plotting radar charts, see [this](https://github.com/Slothfulwave612/soccerplots/blob/master/docs/radar_chart.md).
  
  * Module for plotting bump charts has been added to the package, see [this](https://github.com/Slothfulwave612/soccerplots/blob/master/docs/bumpy_chart.md).
  
  * Added a method which can be used for adding and modifying text to matplotlib plots, see [this](https://github.com/Slothfulwave612/soccerplots/blob/master/docs/plot_text.md).

* **Version:**

  * Python: v3.7.7

  * Numpy: v1.19.1

  * Matplotlib: v3.3.0

  * Pillow(PIL): v7.2.0

* Previous version documentations and examples are available [here](https://github.com/Slothfulwave612/data/tree/master/soccerplots).