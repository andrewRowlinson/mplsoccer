# fbplot
mplsoccer is a Python plotting library for drawing soccer / football pitches quickly in Matplotlib.

mplsoccer currently supports several data formats:
- Opta
- Tracab (ChyronHego) tracking data
- Statsbomb
- STATS (formely Prozone)
- Wyscout (pitch dimensions from ggsoccer: https://github.com/Torvaney/ggsoccer)

The following example draws an Opta pitch(the default) using mplsoccer in xkcd comic mode.
``` python
from pitch import Pitch
import matplotlib.pyplot as plt
plt.xkcd()
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
```

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/doc/figures/README_example_pitch.png "pitch xkcd style")