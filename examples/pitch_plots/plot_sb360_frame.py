"""
=============
StatsBomb 360
=============
This example shows how to plot the StatsBomb 360 data.
"""

import json
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
import requests


## load in Statsbomb360 data remotely 
data = requests.get("https://raw.githubusercontent.com/statsbomb/open-data/master/data/three-sixty/3788741.json").json()
## `print(data)` to check out the data returned and available fields

## get plotting data
frame_idx = 50

visible_area_xs = data[frame_idx]["visible_area"][::2]
visible_area_ys = data[frame_idx]["visible_area"][1::2]

player_position_data = data[frame_idx]["freeze_frame"]
teammate_locs = [ppd["location"] for ppd in player_position_data if ppd["teammate"]]
opponent_locs = [ppd["location"] for ppd in player_position_data if not ppd["teammate"]]


## set up pitch
p = Pitch(pitch_type='statsbomb')
fig, ax = p.draw(figsize=(12,8))

## plot
ax.fill(visible_area_xs, visible_area_ys, color=(1,0,0,0.3)) ##coloring the camera visible area
[ax.scatter(x, y, color='orange', s=80, ec='k') for (x,y) in teammate_locs] ## teammate locations scatter
[ax.scatter(x, y, color='dodgerblue', s=80, ec='k') for (x,y) in opponent_locs] ##opponents locations scatter

plt.show() ##to see the plot. You don't need this if you're using a jupyter notebook
