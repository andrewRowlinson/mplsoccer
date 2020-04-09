mplsoccer
-----------

mplsoccer is a Python plotting library for drawing soccer / football pitches quickly in Matplotlib.

To install:
```
pip install mplsoccer
```

mplsoccer was invented to quickly iterate through ideas by making it easy to plot on soccer / football pitches. It also makes it easy to plot the same chart horizontally or vertically with minimal code changes.


Pitch basics
-----------

mplsoccer can either plot on existing axis or create new axis.

#### Pitch type
mplsoccer currently supports several data formats:
- Statsbomb
- Stats Perform
- Tracab (ChyronHego) tracking data
- Opta
- STATS (formerly Prozone)
- Wyscout (the pitch dimensions are taken from ggsoccer: https://github.com/Torvaney/ggsoccer)

The following example draws a Statsbomb pitch (the default) with stripes.
``` python
from mplsoccer.pitch import Pitch
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig('statsbomb.png',pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_statsbomb_pitch.png?raw=true "statsbomb pitch")

For fun you can also plot the same pitch in xkcd mode.
``` python
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
plt.xkcd()
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig('statsbomb_xkcd.png',pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_xkcd_pitch.png?raw=true "pitch xkcd style")

#### Views

#### Layout
- figsize
- layout

#### Appearance

#### Padding

#### Axis


StatsBomb open-data
-----------


Plot
-----------


Scatter
-----------


Lines
-----------


Arrows
-----------


Kdeplot
-----------


Jointplot
-----------


Hexbin
-----------


Heatmap
-----------


Annotation
-----------


Animation
-----------


Inspiration
-----------


Contributions
-----------
Contributions to mplsoccer are welcome. It would be great to add the following functionality:
- pass maps
- pass sonars
- voronoi diagrams

Please get in touch at rowlinsonandy@gmail.com or [@numberstorm](https://twitter.com/numberstorm) on Twitter.