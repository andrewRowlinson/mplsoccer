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
import os
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig(os.path.join('figures','README_pitch_type.png'),pad_inches=0,bbox_inches='tight')
```
![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_statsbomb_pitch.png?raw=true "statsbomb pitch")

For fun you can also plot the same pitch in xkcd mode.
``` python
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
plt.xkcd()
pitch = Pitch(orientation='horizontal',figsize=(10,10),stripe=True)
fig, ax = pitch.draw()
fig.savefig(os.path.join('figures','README_example_xkcd_pitch.png'),pad_inches=0,bbox_inches='tight')
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

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_arrow_example.png?raw=true "arrow plot")

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
pitch = Pitch(pitch_type = 'statsbomb', orientation = 'horizontal', tight_layout = True,
              pitch_color = '#22312b', line_color = '#c7d5cc', figsize = (16, 9))
fig, ax = pitch.draw()
pitch.quiver(df_pass[mask_complete].x, df_pass[mask_complete].y,
             df_pass[mask_complete].pass_end_x, df_pass[mask_complete].pass_end_y, width = 1,
             headwidth = 10, headlength = 10, color = '#ad993c', ax = ax, label = 'completed passes')
pitch.quiver(df_pass[~mask_complete].x, df_pass[~mask_complete].y,
             df_pass[~mask_complete].pass_end_x, df_pass[~mask_complete].pass_end_y, width = 1, 
             headwidth = 10, headlength = 10, color = '#ba4f45', ax = ax, label = 'other passes')
ax.legend(facecolor = '#22312b', edgecolor = 'None', fontsize = 'large')
team1, team2 = df.team_name.unique()
ax.set_title(f'{team1} vs {team2}', fontsize = 30);
fig.set_facecolor('#22312b')
fig.set_constrained_layout(False)
fig.savefig(os.path.join('figures','README_arrow_example.png'), facecolor = '#22312b', bbox_inches = 'tight')
```

####  5. Kernel density plots

mplsoccer uses [seaborn.kdeplot](https://seaborn.pydata.org/generated/seaborn.kdeplot.html) to plot kernel density plots. Behind the scenes, the Pitch.kdeplot() method also clips the plot to the edges of the pitch.

Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_kdeplot_example.png?raw=true "kernel density plot")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/05-Plotting-kdeplot.ipynb):
``` python
from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import os

# load first game that Messi played as a false-9 and the match before
kwargs = {'related_event_df': False,'shot_freeze_frame_df': False, 'tactics_lineup_df': False}
df_false9 = read_event(os.path.join(EVENT_SLUG,'69249.json'), **kwargs)['event']
df_before_false9 = read_event(os.path.join(EVENT_SLUG,'69251.json'), **kwargs)['event']
# filter messi's actions (starting positions)
df_false9 = df_false9.loc[df_false9.player_id == 5503,['x', 'y']]
df_before_false9 = df_before_false9.loc[df_before_false9.player_id == 5503,['x', 'y']]
# plotting
pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 9), layout = (1, 2), pitch_color = 'grass', stripe = True)
fig, ax = pitch.draw()
ax[0].set_title('Messi in the game directly before \n playing in the false 9 role', fontsize = 25, pad = 20)
pitch.kdeplot(df_before_false9.x, df_before_false9.y, ax = ax[0], cmap = 'plasma', linewidths = 3)
pitch.annotate('6-2 thrashing \nof Real Madrid', (25,10), color = 'white',
               fontsize = 25, ha = 'center', va = 'center', ax = ax[1])
ax[1].set_title('The first Game Messi \nplayed in the false 9 role', fontsize = 25, pad = 20)
pitch.kdeplot(df_false9.x, df_false9.y, ax = ax[1], cmap = 'plasma', linewidths = 3)
pitch.annotate('2-2 draw \nagainst Valencia', (25,10), color = 'white',
               fontsize = 25, ha = 'center', va = 'center', ax = ax[0])
pitch.annotate('more events', (90,68), (30,68), ax=ax[0], color='white', ha = 'center', va = 'center',
               fontsize = 20, arrowprops=dict(facecolor='white', edgecolor = 'None'))
pitch.annotate('fewer events', (80,17), (80,5), ax=ax[0], color='white', ha = 'center', va = 'center',
               fontsize = 20, arrowprops=dict(facecolor='white', edgecolor = 'None'))
fig.savefig(os.path.join('figures', 'README_kdeplot_example.png'), bbox_inches = 'tight')
```

####  6. Jointplot

mplsoccer uses [seaborn.jointplot](https://seaborn.pydata.org/generated/seaborn.jointplot.html) to plot joint plots. This method is the only Pitch plotting method that does not take a Matplotlib axis (ax) as an argument. Instead, first we plot a Seaborn jointplot and then we draw on a pitch after. Seaborn.jointplot's are square and take a height arguement to set up the figure size, the Pitch figsize is therefore ignored.

Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_jointplot_example.png?raw=true "joint plot")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/06-Plotting-jointplot.ipynb):
``` python
from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import os

# load first game that Messi played as a false-9
kwargs = {'related_event_df': False,'shot_freeze_frame_df': False, 'tactics_lineup_df': False}
df_false9 = read_event(os.path.join(EVENT_SLUG,'69249.json'), **kwargs)['event']
# filter messi's actions (starting positions)
df_false9 = df_false9.loc[df_false9.player_id == 5503,['x', 'y']]

# plotting
pitch = Pitch(pitch_type = 'statsbomb', pitch_color = 'grass', stripe = True, view = 'half', pad_left = 20)
joint_kws = {'shade': False, 'color': 'green', 'cmap': "plasma", 'linewidths': 3}
g = pitch.jointplot(df_false9.x, df_false9.y, height = 9, kind='kde',**joint_kws);
g.fig.suptitle("Messi's first game as a false 9", x = 0.5, y = 1.03, fontsize = 25, ha = 'center', va = 'center')
g.savefig(os.path.join('figures', 'README_jointplot_example.png'), bbox_inches = 'tight')
```

####  7. Hexbin

#### 8. Heatmap

There are three steps to creating heatmaps in mplsoccer:
1) create the statistics and bins, which uses [scipy.stats.binned_statistic_2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html).
2) plot a heatmap, which uses [matplotlib.axes.Axes.pcolormesh](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html)
3) plot the labels (optional), which uses [matplotlib.axes.Axes.annotate](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html)

I deliberately did not combine these methods so that you can post process the values, e.g. rounding, formating, subtracting or differencing from the league average.

mplsoccer contains two ways to bin the data:
a) bins. Specified by number of x coordinate bins and number of y coordinate bins
b) positional. This bins the data according to the [Juego de Posición](https://spielverlagerung.com/2014/11/26/juego-de-posicion-a-short-explanation/) concept

Bins Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_heatmap_bins.png?raw=true "heatmap bins")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/08-Plotting-heatmap.ipynb):
``` python
from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import os
import pandas as pd
import numpy as np

# get data
match_files = ['19789.json', '19794.json', '19805.json']
kwargs = {'related_event_df': False,'shot_freeze_frame_df': False, 'tactics_lineup_df': False}
df = pd.concat([read_event(os.path.join(EVENT_SLUG,file), **kwargs)['event'] for file in match_files])
# filter chelsea pressure events
mask_chelsea_pressure = (df.team_name == 'Chelsea FCW') & (df.type_name == 'Pressure')
df = df.loc[mask_chelsea_pressure,['x','y']]

# setup pitch
pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 9), layout = (1,3), line_zorder=2,
              pitch_color= '#22312b', line_color = 'white',orientation='vertical')
# draw
fig, ax = pitch.draw()
bins = [(6,5),(1,5),(6,1)]
for i, bin in enumerate(bins):
    (statistic, x_grid, y_grid, cx, cy) = pitch.binned_statistic_2d(df.x, df.y,
                                                                    statistic='count', bins = bin)
    # work out proportions
    all_pressure_count = statistic.sum()
    statistic = (statistic/all_pressure_count * 100).round(1)
    # draw
    pitch.heatmap(x_grid, y_grid, statistic, ax=ax[i], zorder=2, cmap='coolwarm', edgecolors = '#22312b')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=ax[i])
    statistic = statistic.astype(str) + np.char.array(['%'])
    pitch.label_heatmap(statistic, cx, cy, color='white', fontsize=18, ax=ax[i], ha = 'center', va = 'bottom')
fig.suptitle('Location of pressure events - 3 home games for Chelsea FC Women', x=0.5, y=0.98, fontsize=30,);
fig.savefig(os.path.join('figures','README_heatmap_bins.png'), bbox_inches = 'tight')
```

Positional Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_heatmap_positional.png?raw=true "positional heatmap")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/08-Plotting-heatmap.ipynb):
``` python
from mplsoccer.pitch import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import os
import pandas as pd
import numpy as np

# get data
match_files = ['19789.json', '19794.json', '19805.json']
kwargs = {'related_event_df': False,'shot_freeze_frame_df': False, 'tactics_lineup_df': False}
df = pd.concat([read_event(os.path.join(EVENT_SLUG,file), **kwargs)['event'] for file in match_files])
# filter chelsea pressure events
mask_chelsea_pressure = (df.team_name == 'Chelsea FCW') & (df.type_name == 'Pressure')
df = df.loc[mask_chelsea_pressure,['x','y']]

# setup pitch
pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 9), layout = (1,3), line_zorder=2,
              pitch_color= '#22312b', line_color = 'white',orientation='vertical')
# draw
fig, ax = pitch.draw()
positions = ['full','horizontal','vertical']
for i, pos in enumerate(positions):
    (statistic_grid, statistic, x_grid, y_grid, cx, cy) = pitch.binned_statistic_positional(df.x, df.y,
                                                                                            statistic='count',
                                                                                            positional=pos)
    # work out proportions
    all_pressure_count = statistic.sum()
    statistic_grid = [(array/all_pressure_count*100).round(1) for array in statistic_grid]
    statistic = (statistic/all_pressure_count * 100).round(1)
    pitch.heatmap_positional(x_grid, y_grid, statistic_grid, statistic, ax=ax[i], zorder=2,
                             cmap='coolwarm', edgecolors='#22312b')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=ax[i])
    statistic = [f'{stat}%' for stat in statistic]
    pitch.label_heatmap(statistic, cx, cy, color = 'white', fontsize = 18, ax = ax[i], ha = 'center', va = 'bottom')
fig.suptitle('Location of pressure events - 3 home games for Chelsea FC Women', x=0.5, y=0.98, fontsize=30,);
fig.savefig(os.path.join('figures','README_heatmap_positional.png'), bbox_inches = 'tight')
```

#### 09. Animation

#### 10. Advanced examples

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