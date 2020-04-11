# mplsoccer

mplsoccer is a Python plotting library for drawing soccer / football pitches in Matplotlib and loading StatsBomb open-data.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mplsoccer.

```bash
pip install mplsoccer
```

## Pitch plotting basics

TO DO

mplsoccer can either plot on existing axis or create new axis.

#### a) Pitch type
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

####  b) Views

####  c) Layout
- figsize
- layout

####  d) Appearance

####  e) Padding

####  f) Axis


## StatsBomb open-data

TO DO


## Plotting

TO DO

#### 1. Plot

####  2. Scatter

####  3. Lines

####  4. Arrows

mplsoccer uses [matplotlib.axes.Axes.quiver](https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.quiver.html) to plot arrows. Behind the scenes, the Pitch.quiver() method modifies the start and end locations to a vector before plotting them. This avoids the need to use Matplotlib's annotate in a loop, which is another way of plotting arrows.

Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figure/README_arrows_example.png?raw=true "arrow plot")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/04-Plotting-Arrows.ipynb):
``` python
from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from matplotlib import rcParams
import os

rcParams['text.color'] = '#c7d5cc' # set the default text color

# get event dataframe for game 7478, create a dataframe of the passes, and a boolean mask for the outcome
df_dict = read_event(os.path.join(EVENT_SLUG,'7478.json'),
                     related_event_df = False, shot_freeze_frame_df = False, tactics_lineup_df = False)
df = df_dict['event'] # read_event returns a dictionary of dataframes
mask_pass_seattle = (df.type_name == 'Pass') & (df.team_name == 'Seattle Reign')
df_pass = df.loc[mask_pass_seattle, ['x','y','pass_end_x','pass_end_y','outcome_name']]
mask_complete = df_pass.outcome_name.isnull()

# Plot arrows
pitch = Pitch(pitch_type = 'statsbomb', orientation = 'horizontal',
              pitch_color = '#22312b', line_color = '#c7d5cc', figsize = (16, 9), pad_top = 10)
fig, ax = pitch.draw()
pitch.quiver(df_pass[mask_complete].x, df_pass[mask_complete].y,
             df_pass[mask_complete].pass_end_x, df_pass[mask_complete].pass_end_y, width = 1,
             headwidth = 10, headlength = 10, color = '#ad993c', ax=ax, label = 'complete passes')
pitch.quiver(df_pass[~mask_complete].x, df_pass[~mask_complete].y,
             df_pass[~mask_complete].pass_end_x, df_pass[~mask_complete].pass_end_y, width = 1, 
             headwidth = 10, headlength = 10, color = '#ba4f45', ax=ax, label = 'other passes')
ax.legend(facecolor = 'None', edgecolor = 'None', fontsize = 'large')
team1, team2 = df.team_name.unique()
ax.set_title(f'{team1} vs {team2}', pad=-40, fontsize = 30);
fig.savefig(os.path.join('figures','README_arrows_example.png'))
```

####  5. Kdeplot

####  6. Jointplot

####  7. Hexbin

#### 8. Heatmap

#### 9. Annotation

#### 10. Animation

#### 11. Advanced examples

## Inspiration

mplsoccer was inspired by other people's work:
- [Peter McKeever](http://petermckeever.com/2019/01/plotting-pitches-in-python/) inspired the API design
- [ggsoccer](https://github.com/Torvaney/ggsoccer) - a library for plotting pitches in R
- [lastrow](https://twitter.com/lastrowview) - often tweets animations from matches and the accompanying code
- [fcrstats](http://fcrstats.com/) - tutorials for using football data
- [Karun Singh](https://twitter.com/karun1710) - tweets some interesting football analytics and visuals
- [StatsBomb](https://statsbomb.com/) - great visual design and free open-data
- [John Burn-Murdoch](https://twitter.com/jburnmurdoch/status/1057907312030085120) - this tweet got me interested in football analytics.

## Pitch types

Unfortunately, the different data providers haven't yet standardised on a common coordinate system. Here's a diagram showing how they compare:
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_pitch_type.png?raw=true "pitch types")

## Contributions
Contributions are welcome. It would be great to add the following functionality to mplsoccer:
- pass maps
- pass sonars
- voronoi diagrams

Examples to help others are also welcome for a gallery.

Please get in touch at rowlinsonandy@gmail.com or [@numberstorm](https://twitter.com/numberstorm) on Twitter.

## License
[MIT](https://choosealicense.com/licenses/mit/)