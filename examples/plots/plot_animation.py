"""
=========
Animation
=========

This example shows how to animate tracking data from metricasports (https://github.com/metrica-sports/sample-data).
Unfortunately, sphinx-gallery doesn't currently render gifs or videos, but I think the next version will.
"""

from mplsoccer.pitch import Pitch
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

##############################################################################
# Load the data

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

##############################################################################
# Reset the column names

# column names aren't great so this sets the player ones with _x and _y suffixes
def set_col_names(df):
    cols = list(np.repeat(df.columns[3::2],2))
    cols = [col+'_x' if i%2==0 else col+'_y' for i, col in enumerate(cols)]
    cols = np.concatenate([df.columns[:3],cols])
    df.columns = cols
    
set_col_names(df_away)
set_col_names(df_home)

##############################################################################
# Subset 2 seconds of data

# get a subset of the data (10 seconds)
df_away = df_away[(df_away['Time [s]'] >= 815) & ((df_away['Time [s]'] < 817))].copy()
df_home = df_home[(df_home['Time [s]'] >= 815) & ((df_home['Time [s]'] < 817))].copy()

##############################################################################
# Split off the ball data, and drop the ball columns from the df_away/ df_home dataframes

# split off a df_ball dataframe and drop the ball columns from the player dataframes
df_ball = df_away[['Period','Frame','Time [s]', 'Ball_x', 'Ball_y']].copy()
df_home.drop(['Ball_x','Ball_y'],axis=1,inplace=True)
df_away.drop(['Ball_x','Ball_y'],axis=1,inplace=True)
df_ball.rename({'Ball_x':'x','Ball_y':'y'},axis=1,inplace=True)

##############################################################################
# Convert to long form. So each row is a single player's coordinates for a single frame

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

##############################################################################
# Show the away data
df_away.head()

##############################################################################
# Show the home data
df_home.head()

##############################################################################
# Show the ball data
df_ball.head()

##############################################################################
# Plot the animation

# First set up the figure, the axis
pitch = Pitch(pitch_type='metricasports', figsize=(16,10.4), pitch_color='grass',
              pitch_width=68, pitch_length=105, goal_type='line', stripe = True)
fig, ax = pitch.draw()

# then setup the pitch plot markers we want to animate
marker_kwargs = {'marker':'o', 'markeredgecolor': 'black', 'linestyle': 'None'}
ball, = ax.plot([], [], ms=6, markerfacecolor='w', zorder=3, **marker_kwargs)
away, = ax.plot([], [], ms=10, markerfacecolor='#b94b75', **marker_kwargs) #red/maroon
home, = ax.plot([], [], ms=10, markerfacecolor='#7f63b8', **marker_kwargs) #purple

# initialization function: plot on the background for each frame
def init():
    ball.set_data([], [])
    away.set_data([], [])
    home.set_data([], [])
    return ball,away,home

# animation function
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

# call the animator, animate so 25 frames per second
# note that its hard to get the ffmpeg requirements right.
# I installed from conda-forge: see the environment.yml file in the docs folder
anim = animation.FuncAnimation(fig, animate, frames=len(df_ball), init_func=init, interval=50,
                               blit=True, repeat=False)

# how to save animation - commented out for example
# anim.save('example.mp4', dpi=300, fps=25,
#          extra_args=['-vcodec', 'libx264'],
#          savefig_kwargs={'pad_inches':0, 'facecolor':'#457E29'})
