"""
================
Standardize data
================

This example converts data from one data provider to another,
based on the excellent `ggsoccer <https://github.com/Torvaney/ggsoccer>`_ (R language).

The conversion maintains the relevant position to the pitch markings,
so if a shot is half-way between the penalty spot and the penalty-area box,
it stays that way after conversion.

We convert data like this because most providers (Opta, Wyscout, StatsBomb) fix the coordinates
inside the penalty area regardless of the pitch size, while the rest of the pitch stretches to
the side-lines. For example, Liverpool’s ground, Anfield, is 68 meters wide and Fulham’s ground,
Craven Cottage, is 65 meters wide. With the fixed pitch coordinates,
the extra three meters of space squeezes between the penalty area and the pitch side-lines.

During conversion, coordinates outside the pitch side-lines are clipped to the pitch shape,
while missing values are maintained.

The following pitch markings are used in the conversion: the pitch side-lines, six-yard-box,
goal-posts, penalty spot, penalty area and the centre-line.
"""

import os
import json

import pandas as pd
import requests
from kloppy import WyscoutSerializer, to_pandas
from adjustText import adjust_text

from mplsoccer import VerticalPitch, Standardizer, FontManager
from mplsoccer.statsbomb import read_event, EVENT_SLUG

##############################################################################
# Here we will get the event data from both a Wyscout and StatsBomb
# game and standardize to the same coordinates to compare.

# I have prepared a table of match ids that are the same between the StatsBomb and Wyscout
# open data. Here we get the 50th of the 100 overlapping games (from La Liga / World Cup.)
df_overlap = pd.read_csv(('https://raw.githubusercontent.com/andrewRowlinson/mplsoccer/master/'
                          'wyscout_statsbomb_overlap.csv'))
IDX = 50

# Get the Wyscout data. Here we use @mr_le_fox's (https://twitter.com/mr_le_fox)
# version of the Wyscout open-data available at
# https://github.com/koenvo/wyscout-soccer-match-event-dataset
wyscout_id = df_overlap.iloc[IDX].wyscout_json
WYSCOUT_URL = (f'https://raw.githubusercontent.com/koenvo/wyscout-soccer-match-event-dataset/'
               f'main/processed/files/{wyscout_id}')

# Here we get the url of the cooresponding statsbomb match
statsbomb_id = df_overlap.iloc[IDX].statsbomb_json
STATSBOMB_URL = f'{EVENT_SLUG}/{statsbomb_id}'

##############################################################################
# Get the StatsBomb data as a dataframe
# -------------------------------------

df_statsbomb = read_event(STATSBOMB_URL, related_event_df=False, shot_freeze_frame_df=False,
                          tactics_lineup_df=False)['event']

##############################################################################
# Get the Wyscout data as a dataframe using Kloppy
# ------------------------------------------------
# We first save the file locally and then load it in Kloppy as a dataframe

# create the data/wyscout directories to store the file if they don't exist
WYSCOUT_PATH = os.path.join('data', 'wyscout')
if os.path.exists(WYSCOUT_PATH) is False:
    os.makedirs(WYSCOUT_PATH)

# Save the Wyscout json in the data/wyscout directory
WYSCOUT_JSON_PATH = os.path.join(WYSCOUT_PATH, wyscout_id)
if os.path.exists(WYSCOUT_JSON_PATH) is False:  # only download it if it doesn't exist
    with open(WYSCOUT_JSON_PATH, 'w') as f:
        response = requests.get(url=WYSCOUT_URL)
        response.encoding = 'unicode-escape'  # to make sure the encoding for é etc. is correct
        json.dump(response.json(), f)

# load the wyscout events as a dataframe using Kloppy
serializer = WyscoutSerializer()

with open(WYSCOUT_JSON_PATH) as event_data:
    wyscout_dataset = serializer.deserialize(inputs={'event_data': event_data})

df_wyscout = to_pandas(wyscout_dataset,
                       additional_columns={'player_name': lambda event: str(event.player),
                                           'team_name': lambda event: str(event.player.team)})

##############################################################################
# Standardize the Wyscout data to StatsBomb coordinates
# -----------------------------------------------------
# You can use any of the supported pitches in the pitch_from/ pitch_to here.
# They are currently: 'statsbomb', 'tracab', 'opta', 'wyscout', 'uefa',
# 'metricasports', 'custom', 'skillcorner', and 'secondspectrum'.
#
# If the pitch size varies ('tracab', 'metricasports', 'custom', 'skillcorner', 'secondspectrum')
# then you also need to supply the relevant
# length_from/ length_to or width_from/ width_to in meters.

# setup the Standardizer
standard = Standardizer(pitch_from='wyscout', pitch_to='statsbomb')
# transform the coordinates and save to the dataframe
x_std, y_std = standard.transform(df_wyscout.coordinates_x, df_wyscout.coordinates_y)
df_wyscout['coordinates_x'] = x_std
df_wyscout['coordinates_y'] = y_std

##############################################################################
# Add the last name to the dataframes

df_statsbomb['last_name'] = df_statsbomb.player_name.str.split(' ').str[-1]
df_wyscout['last_name'] = df_wyscout.player_name.str.split(' ').str[-1]

##############################################################################
# Plot the standardized data
# --------------------------

pitch = VerticalPitch(pitch_type='statsbomb', half=True, pad_left=-10,
                      pad_right=-10, pad_bottom=-20)
fig, ax = pitch.draw(figsize=(16, 9))
fm = FontManager()  # a mplsoccer fontmanager with the default Robotto font

# subset portugals shots for both data providers
mask_portugal_sb = df_statsbomb.team_name == 'Portugal'
mask_shot_sb = df_statsbomb.type_name == 'Shot'
mask_portugal_wyscout = df_wyscout.team_name == 'Portugal'
mask_shot_wyscout = df_wyscout.event_type == 'SHOT'
df_wyscout_portugal = df_wyscout[mask_shot_wyscout & mask_portugal_wyscout].copy()
df_statsbomb_portugal = df_statsbomb[mask_shot_sb & mask_portugal_sb].copy()

# plotting the shots as a scatter plot with a legend
pitch.scatter(df_wyscout_portugal.coordinates_x, df_wyscout_portugal.coordinates_y,
              ax=ax, color='#56ae6c', label='wyscout', s=250)
pitch.scatter(df_statsbomb_portugal.x, df_statsbomb_portugal.y,
              ax=ax, color='#7f63b8', label='statsbomb', s=250)

# plotting the text and using adjust text so it doesn't overlap
texts = []
for i in range(len(df_wyscout_portugal)):
    text = ax.text(df_wyscout_portugal['coordinates_y'].iloc[i],
                   df_wyscout_portugal['coordinates_x'].iloc[i],
                   df_wyscout_portugal['last_name'].iloc[i],
                   color='#56ae6c', fontsize=20, fontproperties=fm.prop)
    texts.append(text)

for i in range(len(df_statsbomb_portugal)):
    text = ax.text(df_statsbomb_portugal['y'].iloc[i],
                   df_statsbomb_portugal['x'].iloc[i],
                   df_statsbomb_portugal['last_name'].iloc[i],
                   color='#7f63b8', fontsize=20, fontproperties=fm.prop)
    texts.append(text)
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='black'))

# adding a legend
legend = ax.legend(prop=fm.prop)
for text in legend.get_texts():
    text.set_fontsize(30)

##############################################################################
# Reverse the standardization
# ---------------------------
# You can reverse the standardization with the reverse keyword

x_std, y_std = standard.transform(df_wyscout.coordinates_x, df_wyscout.coordinates_y, reverse=True)

##############################################################################
# Standardize to an abritary shaped pitch
# ---------------------------------------
# According to Wikipedia the Campo de fútbol de Vallecas stadium is 100 meters x 65 meters
# Let's load StatsBomb data from a Rayo Vallecano home game versus Barcelona and convert to meters.

df_rayo_vallecano = read_event(f'{EVENT_SLUG}/266653.json')['event']

custom_standard = Standardizer(pitch_from='statsbomb',
                               pitch_to='custom', length_to=100, width_to=65)

rayo_x_std, rayo_y_std = custom_standard.transform(df_rayo_vallecano.x, df_rayo_vallecano.y)
xend_std, yend_std = custom_standard.transform(df_rayo_vallecano.end_x, df_rayo_vallecano.end_y)

df_rayo_vallecano['x'] = rayo_x_std
df_rayo_vallecano['y'] = rayo_y_std
df_rayo_vallecano['end_x'] = xend_std
df_rayo_vallecano['end_y'] = yend_std

##############################################################################
# Now let's calculate the distance in meters for the passes in the game
# And compare to pass distance given in the StatsBomb dataframe
# The calculated distances are shorter as the pitch is smaller than the standard
# pitch dimensions (105 meters X 68 meters)

# filter passes
df_rayo_vallecano_pass = df_rayo_vallecano[df_rayo_vallecano.type_name == 'Pass'].copy()
# calculate the average pass length
custom_pitch = VerticalPitch(pitch_type='custom', pitch_length=100, pitch_width=65)
angle, distance = custom_pitch.calculate_angle_and_distance(df_rayo_vallecano_pass.x,
                                                            df_rayo_vallecano_pass.y,
                                                            df_rayo_vallecano_pass.end_x,
                                                            df_rayo_vallecano_pass.end_y)
print('Calculated distance in meters')
print(pd.Series(distance).describe())
print('\nDistances in the StatsBomb data')
print((df_rayo_vallecano.pass_length * 0.9144).describe())  # note converted from yards to meters
