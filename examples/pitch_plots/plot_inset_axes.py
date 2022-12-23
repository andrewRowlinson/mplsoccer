"""
=======================
Insetting Axes in the Pitch
=======================

The Pitch classes have two functions which allow you to inset embedded axes, with their own coordinate system, into the pitch.

`pitch.inset_axes` allows you to inset an axes centered at a specified x,y coordinate, while
`pitch.inset_formation_axes` will bulk insert axes for each position in a specified formation.


In an example below, we use this to create a Team of the Week graphic.
"""

from mplsoccer import VerticalPitch
from urllib.request import urlopen
from PIL import Image
from mplsoccer.utils import inset_axes

##############################################################################
# First, generate some data for the Team of the Week.  We will use the 4-3-3 formation
# and specify position names provided by the ``FormationHelper`` class. (see: :ref:`Plotting position locations on the pitch with FormationHelper`)
# 

import pandas as pd

badge_urls = {
    'Manchester United':'https://www.thesportsdb.com/images/media/team/badge/xzqdr11517660252.png',
    'Chelsea':'https://www.thesportsdb.com/images/media/team/badge/yvwvtu1448813215.png',
    'Manchester City':'https://www.thesportsdb.com/images/media/team/badge/vwpvry1467462651.png',
    'Reading':'https://www.thesportsdb.com/images/media/team/badge/tprvtu1448811527.png',
    'Arsenal':"https://www.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png"

}

totw_player_data = pd.DataFrame(
    {
        'position':['LW','ST','RW','LCM','CDM','RCM','LB','LCB','RCB','RB','GK'],
        'player':['Reiten','Kerr','Fleming','Charles','Miedema','Kirby','Blundell','Greenwood','Bryson','Battle','Earps'],
        'score':[9.7, 8.6, 8.7, 9.1, 8.7, 9.5, 7.6, 8.0, 8.0, 9.1, 8.3],
        'team':['Chelsea','Chelsea','Chelsea','Chelsea','Arsenal','Chelsea','Manchester United','Manchester City','Reading','Manchester United', 'Manchester United']
    }
)
totw_player_data

##############################################################################
# Next, create the pitch figure using `pitch.grid` to create a header space for the title.
# We use 'inset_formation_axes' to create axes for each position in the formation, and then 
# use `inset_axes` from the `utils` module to inset the team badge into each position axes.
# We also use `inset_axes` to inset the league badge into the title axes.




pitch = VerticalPitch(pitch_type='opta', pitch_color='#333333', line_color='white', line_alpha=0.2, line_zorder=3)

fig, axes = pitch.grid(endnote_height=0, figheight=13, title_height=0.1, title_space=0, space=0)
fig.set_facecolor('#333333')
fig.set_tight_layout(True)
axes['title'].axis('off')
axes['title'].text(0.5, 0.6, 'WSL Team of the Week', ha='center', va='center', color='white', fontsize=20)
axes['title'].text(0.5, 0.3, 'Round 9', ha='center', va='center', color='white', fontsize=14)

# width and length are in axis coordinates. Note that in VerticalPitch, the x coordinate is the y coordinate of the pitch
title_inset_ax = pitch.inset_axes(y=.9, x=0.5, width=0.2, length=1, ax=axes['title'])
title_inset_ax.axis('off')
title_inset_ax.imshow(Image.open(urlopen('https://www.thesportsdb.com/images/media/league/badge/kxo7zf1656519439.png')))


position_axes = pitch.inset_formation_axes('433', length=12, width=12/pitch.ax_aspect, ax=axes['pitch'])
for position, ax in position_axes.items():
    ax.axis('off')
    data = totw_player_data[totw_player_data['position']==position]
    ax.text(0.5, 0.2, data['player'].iloc[0], ha='center', va='center', color='white', fontsize=11)
    ax.text(0.5, 0.38, data['score'].iloc[0], ha='center', va='center', color='white', fontsize=11, bbox=dict(facecolor='green', boxstyle='round,pad=0.2', linewidth=0))

    # width and length are in axis coordinates. Note that in VerticalPitch, the x coordinate is the y coordinate of the pitch
    inner_ax = pitch.inset_axes(y=.5, x=0.75, length=0.5, width=0.5, ax=ax, zorder=4)
    inner_ax.axis('off')
    inner_ax.imshow(Image.open(urlopen(badge_urls[data['team'].iloc[0]])))