# mplsoccer
mplsoccer is a Python plotting library for drawing soccer / football pitches quickly in Matplotlib.

mplsoccer currently supports several data formats:
- Opta
- Tracab (ChyronHego) tracking data
- Statsbomb
- STATS (formerly Prozone)
- Wyscout (the pitch dimensions are taken from ggsoccer: https://github.com/Torvaney/ggsoccer)

The following example draws an Opta pitch (the default) with stripes.
``` python
from mplsoccer import Pitch
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig('opta.png',pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_opta_pitch.png "pitch xkcd style")

For fun you can also plot the same pitch in xkcd mode.
``` python
from mplsoccer import Pitch
import matplotlib.pyplot as plt
plt.xkcd()
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig('opta_xkcd.png',pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_xkcd_pitch.png "pitch xkcd style")

# This library is under development
The following developments are planned
- add docstrings
- add warnings/ error messages:
- raise error warning if no pitch width or length when tracab
- raise error warning if view not full/ half
- raise error warning if not horizontal/ vertical
- raise error for goal type
- rotation of scatter plot markers
- create pass map methods
- add examples (team line-up / pass maps/ pressure maps/ subplots)
- add method for plotting Voronoi diagrams
- create documentation using Sphinx
