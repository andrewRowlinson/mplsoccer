# mplsoccer

mplsoccer is a Python plotting library for drawing soccer / football pitches in Matplotlib and loading StatsBomb open-data.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mplsoccer.

```bash
pip install mplsoccer
```

## Pitch plotting basics

The main aim of mplsoccer is to quickly plot pitches. Here is a lightweight example, which plots the default StatsBomb pitch:

``` python
from mplsoccer.pitch import Pitch
import os
pitch = Pitch(orientation='horizontal',figsize=(5,3),stripe=True)
fig, ax = pitch.draw()
fig.savefig(os.path.join('figures','README_example_statsbomb_pitch.png'),pad_inches=0,bbox_inches='tight')
```

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_statsbomb_pitch.png?raw=true "statsbomb pitch")

As a matplotlib figure and axis is returned you are free to use any of matplotlib's functions instead of those included in mplsoccer. 

You can also draw pitches on an existing axis by specifying an axis when drawing the pitch.

``` python
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
import os
pitch = Pitch(orientation='vertical', view='half', pitch_color='grass')
fig, ax = plt.subplots(figsize=(6,4))
pitch.draw(ax=ax)
fig.savefig(os.path.join('figures','README_example_existing_axis.png'),pad_inches=0,bbox_inches='tight')
```

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_example_existing_axis.png?raw=true "plot on existing axis")

#### Pitch plotting methods

> The Pitch class also includes methods to quickly make plots. This is for two reasons:
>
> a) a common mistake is not flipping the x-axis and y-axis when changing from horizontal to vertical orientation. mplsoccer
> handles this automatically so plots look the same when rotated.
>
> b) additional functionality such as plotting footballs, creating heatmaps, rotating markers and setting some defaults.

#### Pitch types
There is support for seven pitch types, currently StatsBomb is the default pitch (`pitch_type`='statsbomb'). More details about which pitches are supported is [here](https://github.com/andrewRowlinson/mplsoccer/blob/master/README.md#pitch-types-1).

## StatsBomb open-data

TO DO


## Plotting

TO DO

#### 1. Plot

TO DO

####  2. Scatter

TO DO

####  3. Lines

TO DO

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

If you don't know much about Seaborn's kernel density plots, I recommend [fcpython's tutorial](https://fcpython.com/visualisation/football-heatmaps-seaborn) for a football related example.

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

mplsoccer uses [matplotlib.axes.Axes.hexbin](https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.hexbin.html) to plot hexbin plots. I don't particularly like them for football data, but I have seen them used a couple of times so have included them.

Hexbins currently do not look the same in vertical and horizontal orientations. This is because matplotlib bins the data according to the number of bins in the x-direction. Unfortunately the x-direction changes when using different orientations.

Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_hexbin_example.png?raw=true "hexbin plot")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/07-Plotting-hexbin.ipynb):
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
pitch = Pitch(pitch_type = 'statsbomb', figsize = (16, 9), layout = (1, 2), pitch_color = '#22312b',
              stripe = False, line_zorder = 2)
fig, ax = pitch.draw()
pitch.hexbin(df_before_false9.x, df_before_false9.y, gridsize=10, ax = ax[0], cmap = 'Blues')
pitch.hexbin(df_false9.x, df_false9.y, gridsize=10, ax = ax[1], cmap = 'Blues')
ax[0].set_title('Messi in the game directly before \n playing in the false 9 role', fontsize = 25, pad = 20);
ax[1].set_title('The first Game Messi \nplayed in the false 9 role', fontsize = 25, pad = 20);
fig.savefig(os.path.join('figures', 'README_hexbin_example.png'), bbox_inches = 'tight')
```

#### 8. Heatmap

There are three steps to creating heatmaps in mplsoccer:
1) create the statistics and bins, which uses [scipy.stats.binned_statistic_2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binned_statistic_2d.html).
2) plot a heatmap, which uses [matplotlib.axes.Axes.pcolormesh](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html)
3) plot the labels (optional), which uses [matplotlib.axes.Axes.annotate](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html)

I deliberately did not combine these methods so that you can post-process the values, e.g. rounding, formating, subtracting or differencing from the league average.

mplsoccer contains two ways to bin the data:
a) bins. Specified by the number of x coordinate bins and the number of y coordinate bins
b) positional. This bins the data according to the [Juego de Posición](https://spielverlagerung.com/2014/11/26/juego-de-posicion-a-short-explanation/) concept

###### Bins Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

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
    bin_statistic = pitch.bin_statistic(df.x, df.y, statistic='count', bins = bin)
    # draw
    pitch.heatmap(bin_statistic, ax=ax[i], cmap='coolwarm', edgecolors = '#22312b')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=ax[i])
    
    # replace raw counts with percentages and add percentage sign (note immutable named tuple so used _replace)
    bin_statistic = bin_statistic._replace(statistic = 
                                           (bin_statistic.statistic / len(df) * 100)
                                           .round(1).astype(str) + np.char.array(['%']))
    pitch.label_heatmap(bin_statistic, color='white', fontsize=18, ax=ax[i], ha = 'center', va = 'bottom')
fig.suptitle('Location of pressure events - 3 home games for Chelsea FC Women', x=0.5, y=0.98, fontsize=30,);
fig.savefig(os.path.join('figures','README_heatmap_bins.png'), bbox_inches = 'tight')
```

######  Positional Example using [StatsBomb open-data](https://github.com/statsbomb/open-data):

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
    bin_statistic = pitch.bin_statistic_positional(df.x, df.y,statistic='count',positional=pos)
    pitch.heatmap_positional(bin_statistic, ax=ax[i], cmap='coolwarm', edgecolors='#22312b')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=ax[i])
    # replace raw counts with percentages and add percentage sign (note immutable named tuple so used _replace)
    bin_statistic = [b._replace(statistic=
                                 (b.statistic/len(df)*100).round(1).astype(str) + np.char.array(['%']))
                      for b in bin_statistic]
    pitch.label_heatmap(bin_statistic, color = 'white', fontsize = 18, ax = ax[i], ha = 'center', va = 'bottom')
fig.suptitle('Location of pressure events - 3 home games for Chelsea FC Women', x=0.5, y=0.98, fontsize=30,);
fig.savefig(os.path.join('figures','README_heatmap_positional.png'), bbox_inches = 'tight')
```

#### 09. Animation

Sometimes is useful to use animation. There is a short demo below using [metrica sports](https://github.com/metrica-sports/sample-data) sample tracking data.

![alt text](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/figures/README_animation_example.gif?raw=true "tracking data animation")

Code available in [this notebook](https://github.com/andrewRowlinson/mplsoccer/blob/master/docs/09-Plotting-animation.ipynb):
``` python
from mplsoccer.pitch import Pitch
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import os

# load away data
link1 = ('https://raw.githubusercontent.com/metrica-sports/sample-data/master/'
         'data/Sample_Game_1/Sample_Game_1_RawTrackingData_Away_Team.csv')
df_away = pd.read_csv(link1,skiprows=2)
df_away.sort_values('Time [s]', inplace=True)

# load home data
link2 = ('https://raw.githubusercontent.com/metrica-sports/sample-data/master/'
         'data/Sample_Game_1/Sample_Game_1_RawTrackingData_Home_Team.csv')
df_home = pd.read_csv(link2,skiprows=2)
df_home.sort_values('Time [s]', inplace=True)

# column names aren't great so this sets the player ones with _x and _y suffixes
def set_col_names(df):
    cols = list(np.repeat(df.columns[3::2],2))
    cols = [col+'_x' if i%2==0 else col+'_y' for i, col in enumerate(cols)]
    cols = np.concatenate([df.columns[:3],cols])
    df.columns = cols
set_col_names(df_away)
set_col_names(df_home)

# get a subset of the data (10 seconds)
df_away = df_away[(df_away['Time [s]'] > 815) & ((df_away['Time [s]'] <= 825))].copy()
df_home = df_home[(df_home['Time [s]'] > 815) & ((df_home['Time [s]'] <= 825))].copy()

# split off a df_ball dataframe and drop the ball columns from the player dataframes
df_ball = df_away[['Period','Frame','Time [s]', 'Ball_x', 'Ball_y']].copy()
df_home.drop(['Ball_x','Ball_y'],axis=1,inplace=True)
df_away.drop(['Ball_x','Ball_y'],axis=1,inplace=True)

# convert to long form from wide form
def to_long_form(df):
    df = pd.melt(df, id_vars=df.columns[:3], value_vars=df.columns[3:], var_name = 'player')
    df.loc[df.player.str.contains('_x'),'coordinate'] = 'x'
    df.loc[df.player.str.contains('_y'),'coordinate'] = 'y'
    df = df.dropna(axis=0, how='any')
    df['player'] = df.player.str[6:-2]
    df = (df.set_index(['Period','Frame','Time [s]','player','coordinate'])['value']
          .unstack()
          .reset_index()
          .rename_axis(None, axis=1))
    return df

df_away = to_long_form(df_away)
df_home = to_long_form(df_home)

# First set up the figure, the axis, and the plot elements we want to animate
pitch = Pitch(pitch_type='metricasports', figsize=(16,10.4), pitch_color='grass',
              pitch_width=68, pitch_length=105, goal_type='line', stripe = True)
fig, ax = pitch.draw()
marker_kwargs = {'marker':'o', 'markeredgecolor': 'black', 'linestyle': 'None'}
ball, = pitch.plot([], [], ms=6, markerfacecolor='w', zorder=3, ax=ax, **marker_kwargs)
away, = pitch.plot([], [], ms=10, markerfacecolor='#b94b75', ax=ax, **marker_kwargs) #red/maroon
home, = pitch.plot([], [], ms=10, markerfacecolor='#7f63b8', ax=ax, **marker_kwargs) #purple

# initialization function: plot the background of each frame
def init():
    ball.set_data([], [])
    away.set_data([], [])
    home.set_data([], [])
    return ball,away,home

# animation function of dataframes' list
def animate(i):
    # set the ball data with the x and y positions for the ith frame
    ball.set_data(df_ball.iloc[i,3], df_ball.iloc[i,4])
    # get the frame id for the ith frame
    frame = df_ball.iloc[i,1]
    # set the player data using the frame id
    away.set_data(df_away.loc[df_away.Frame==frame,'x'],
                  df_away.loc[df_away.Frame==frame,'y'])
    home.set_data(df_home.loc[df_home.Frame==frame,'x'],
                  df_home.loc[df_home.Frame==frame,'y']) 
    return ball, away, home

# call the animator, animate every 300 ms
# note that its hard to get the ffmpeg requirements right. I installed from conda-forge: see the conda.yml file
anim = animation.FuncAnimation(fig, animate, frames=len(df_ball), init_func=init, interval=50,
                               blit=True, repeat=False)
anim.save(os.path.join('figures','README_animation_example.mp4'), dpi=300, fps=25,
          extra_args=['-vcodec', 'libx264'],
          savefig_kwargs={'pad_inches':0, 'facecolor':'#457E29'})
```

#### 10. Pitch appearance

There are two pitch orientations (`orientation`='vertical' or 'horizontal') and two pitch views (`view`='full' or 'half').

You can amend the colors of the pitch and its lines and stripes with the arguments: `pitch_color`, `line_color`, and `stripe_color`. It's also possible to change the goals (`goal_type`='line' or 'box') and `linewidth` of the pitch markings.

You can add padding to the pitch (`pad_top`, `pad_bottom`, `pad_left`, `pad_right`). Negative padding reduces the amount of visible pitch and positive padding increases the amount of visible pitch. Currently the padding relates to the current orientation to make it easier to adjust, i.e. `pad_top`/ `pad_bottom` always changes the y-axis of the current view and `pad_left`, `pad_right` always changes the x-axis of the current view.

You can view the axis, labela and ticks. These are turned on with the boolean arguments: `axis`, `label`, and `tick`.

#### 11. Advanced examples

TO DO.

## Inspiration

mplsoccer was inspired by other people's work:
- [Peter McKeever](http://petermckeever.com/2019/01/plotting-pitches-in-python/) inspired the API design
- [ggsoccer](https://github.com/Torvaney/ggsoccer) - a library for plotting pitches in R
- [lastrow](https://twitter.com/lastrowview) - often tweets animations from matches and the accompanying code
- [fcrstats](http://fcrstats.com/) - tutorials for using football data
- [fcpython](https://fcpython.com/) - Python tutorials for using football data
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