# fbplot
mplsoccer is a Python plotting library for drawing soccer / football pitches quickly in Matplotlib.

mplsoccer currently supports several data formats:
- Opta
- Tracab (ChyronHego) tracking data
- Statsbomb
- STATS (formely Prozone)
- Wyscout (pitch dimensions from ggsoccer: https://github.com/Torvaney/ggsoccer)

The following example draws an Opta pitch (the default) with stripes.
``` python
from pitch import Pitch
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig('opta.png',pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/doc/figures/README_example_opta_pitch.png "pitch xkcd style")

For fun you can also plot the same pitch in xkcd mode.
``` python
from pitch import Pitch
import matplotlib.pyplot as plt
plt.xkcd()
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig('opta_xkcd.png',pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/doc/figures/README_example_xkcd_pitch.png "pitch xkcd style")

# This library is under developmen
The following developments are planned
- fix the lines plotting method so that the last point of a transparent line isn't lighter than the rest of the line
- add a heatmap method
- add a hexbins method
- add a kernel density method from seaborn
- add an arrow plot/ ability to plot rotated markers
- add docstrings
- create docs in Sphinx and upload to readthedocs.io
- add examples (team line-up / pass map/ plot player pressure/ subplots/ animation?)
- add dependencies
- upload to pip/ anaconda
- possible add method for voronoi plotting