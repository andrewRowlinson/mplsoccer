"""
=========
Statsbomb
=========

mplsoccer contains functions to return StatsBomb data in a flat, tidy dataframe.

Please be responsible with Statsbomb data.
`Register your details <https://www.statsbomb.com/resource-centre>`_ and
read the user agreement carefully (on the same page).

It can be used with the StatBomb `open-data <https://github.com/statsbomb/open-data>`_
or the StatsBomb API if you are lucky enough to have access:

.. code-block:: python

    # this only works if you have access to the StatsBomb API
    import requests
    from mplsoccer.statsbomb import EVENT_SLUG, read_event
    username = 'CHANGEME'
    password = 'CHANGEME'
    auth = requests.auth.HTTPBasicAuth(username, password)
    URL = 'CHANGEME'
    response = requests.get(URL, auth=auth)
    df_dict = read_event(response)


Here are some alternatives to mplsoccer's statsbomb module:

- `statsbombapi <https://github.com/Torvaney/statsbombapi>`_
- `statsbombpy <https://github.com/statsbomb/statsbombpy>`_
- `statsbomb-parser <https://github.com/imrankhan17/statsbomb-parser>`_
"""

import glob
import os

import numpy as np
import pandas as pd

import mplsoccer.statsbomb as sbapi

##############################################################################
# Competition data
# ----------------
# Get the competition data as a dataframe as save as parquet file

df_competition = sbapi.read_competition(sbapi.COMPETITION_URL, warn=False)
df_competition.info()

##############################################################################
#  Match data
# -----------
# Get the match data as a dataframe
# Note there is a mismatch between the length of this file
# and the number of event files because some event files don't have match data.
match_links = sbapi.get_match_links()
match_dfs = [sbapi.read_match(file, warn=False) for file in match_links]
df_match = pd.concat(match_dfs)
df_match.info()

##############################################################################
# Lineup data
# -----------
df_lineup = sbapi.read_lineup(f'{sbapi.LINEUP_SLUG}/7478.json', warn=False)
df_lineup.info()

##############################################################################
# Event data
# ----------
dict_event = sbapi.read_event(f'{sbapi.EVENT_SLUG}/7478.json', warn=False)
df_event = dict_event['event']
df_related_event = dict_event['related_event']
df_shot_freeze = dict_event['shot_freeze_frame']
df_tactics_lineup = dict_event['tactics_lineup']

# exploring the data
df_event.info()
df_related_event.info()
df_shot_freeze.info()
df_tactics_lineup.info()
