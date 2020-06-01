# mplsoccer

mplsoccer is a Python library for drawing soccer/football pitches in Matplotlib and loading StatsBomb open-data.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mplsoccer.

```bash
pip install mplsoccer
```

## Docs

Here are the [docs](https://mplsoccer.readthedocs.io/) for mplsoccer.

## Quick start

Plot a StatsBomb pitch

```python
from mplsoccer.pitch import Pitch
pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
fig, ax = pitch.draw()
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/quick_start.png?raw=true "statsbomb pitch")

## Why mplsoccer exists

mplsoccer shares some of the tools I built for the OptaPro Analytics Forum.
At the time there weren’t any open-sourced python tools. Now alternatives exist, such as [matplotsoccer](https://pypi.org/project/matplotsoccer/).

By using mplsoccer, I hope that you can spend more time building insightful graphics rather than having to learn to draw pitches from scratch.


## Advantages of mplsoccer

mplsoccer:

1. draws 7 different pitch types by changing a single argument, which is useful as there isn’t a standardised data format
2. extends matplotlib to plot heatmaps, (comet) lines, footballs and rotated markers
3. flips the data coordinates when in a vertical orientation so you don’t need to remember to flip them
4. creates tidy dataframes for StatsBomb data, which is useful as most of the alternatives produce nested dataframes

## License

[MIT](https://choosealicense.com/licenses/mit)

## Contributions
Contributions are welcome. It would be great to add the following functionality to mplsoccer:
- pass maps
- pass sonars

Examples to help others are also welcome for a gallery.

Please get in touch at rowlinsonandy@gmail.com or [@numberstorm](https://twitter.com/numberstorm) on Twitter.

## Inspiration

mplsoccer was inspired by other people's work:
- [Peter McKeever](http://petermckeever.com/2019/01/plotting-pitches-in-python/) inspired the API design
- [ggsoccer](https://github.com/Torvaney/ggsoccer) - a library for plotting pitches in R
- [lastrow](https://twitter.com/lastrowview) - often tweets animations from matches and the accompanying code
- [fcrstats](http://fcrstats.com/) - tutorials for using football data
- [fcpython](https://fcpython.com/) - Python tutorials for using football data
- [Karun Singh](https://twitter.com/karun1710) - tweets some interesting football analytics and visuals
- [StatsBomb](https://statsbomb.com/) - great visual design and free open-data
- John Burn-Murdoch's [tweet](https://twitter.com/jburnmurdoch/status/1057907312030085120) got me interested in football analytics

## Recent changes

mplsoccer's recent changes fixed several issues with the heatmap functionality
- Pitch.label_heatmap(), now filters out labels outside of the pitch.
- Pitch.bin_statistic(), now works for a statistic argument other than 'count'.
- Pitch.heatmap(), now returns a mesh in horizontal orientation.
- Pitch.voronoi() calculates Voronoi vertices.
- Pitch.goal_angle(), plots the angle to the goal.
- Pitch.polygon(), plots polygons on the pitch (e.g. goal angle and Voronoi)
- add_image adds images as a new axis to matplotlib figures.
- fixed the statsbomb module so works when the json file is empty.

The statsbomb module also now cleans the data faster.
