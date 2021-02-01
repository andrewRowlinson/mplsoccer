<p align="center">
<img src="docs/source/logo-green.png" alt="mplsoccer logo"/>
</p>

**mplsoccer is a Python library for plotting soccer/football charts in Matplotlib 
and loading StatsBomb open-data.**

---

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mplsoccer.

```bash
pip install mplsoccer
```

---

## Docs

Read more in the [docs](https://mplsoccer.readthedocs.io/) and see some 
examples in our [gallery](https://mplsoccer.readthedocs.io/en/latest/gallery/index.html).

---

## Quick start

Plot a StatsBomb pitch

```python
from mplsoccer import Pitch
pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
fig, ax = pitch.draw()
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/quick_start.png?raw=true 
"statsbomb quick start pitch example")

---

## What is mplsoccer?
In mplsoccer, you can
- plot football/soccer pitches on nine different pitch types
- plot arrows, heatmaps, hexbins, scatter, and (comet) lines
- plot radar charts
- load StatsBomb data as a tidy dataframe
- standardize pitch coordinates into a single format

I hope mplsoccer helps you make insightful graphics faster, so you don't have to build from scratch.

---

## Want to help?
I would love the community to get involved in mplsoccer.
Take a look at our [open-issues](https://github.com/andrewRowlinson/mplsoccer/issues) 
for inspiration.
Please get in touch at rowlinsonandy@gmail.com or 
[@numberstorm](https://twitter.com/numberstorm) on Twitter to find out more.

---

## Recent changes

View the [changelog](https://github.com/andrewRowlinson/mplsoccer/blob/master/CHANGELOG.md) 
for a full list of the recent changes to mplsoccer.

---

## Inspiration

mplsoccer was inspired by:
- [Peter McKeever](http://petermckeever.com/2019/01/plotting-pitches-in-python/) inspired 
the API design
- [ggsoccer](https://github.com/Torvaney/ggsoccer) - a library for plotting pitches in R
- [lastrow](https://twitter.com/lastrowview) - often tweets animations from matches and the 
accompanying code
- [fcrstats](http://fcrstats.com/) - tutorials for using football data
- [fcpython](https://fcpython.com/) - Python tutorials for using football data
- [Karun Singh](https://twitter.com/karun1710) - tweets some interesting football analytics 
and visuals
- [StatsBomb](https://statsbomb.com/) - great visual design and free open-data
- John Burn-Murdoch's [tweet](https://twitter.com/jburnmurdoch/status/1057907312030085120) got me 
interested in football analytics

---

## License

[MIT](https://choosealicense.com/licenses/mit)
