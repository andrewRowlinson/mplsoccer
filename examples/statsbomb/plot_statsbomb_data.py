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
# Scraping StatsBomb links
# ------------------------
# I have deliberately made functions to scrape links for the open-data, so it is easy.
# However, it is better to clone the StatsBomb data, which stores the data locally.
# This will manage all the data updates for you.
#
#
# First download git (if you are using Windows: https://gitforwindows.org/).
# Then navigate in the git terminal to a directory where you want to store the data.
# Use cd [directory name], for example: cd ~/documents/data.
# Then run the command: git clone https://github.com/statsbomb/open-data.git
#
# From time-to-time, the open-data gets updated, to get the latest files run the command: git pull
# from the directory where the data is stored, e.g. cd ~/documents/data/open-data then git pull
# and it will download all the latest files
#
# Here's how to get the links to the data without using git (if you are using git comment this out):

# scrape the links for all the open-data files, which returns a list of links to the files
event_links = sbapi.get_event_links()
lineup_links = sbapi.get_lineup_links()
match_links = sbapi.get_match_links()
COMPETITION_PATH = sbapi.COMPETITION_URL

print('Number of event files:', len(event_links))
print('Number of lineup files:', len(lineup_links))
print('Number of match files:', len(match_links))
print('For example, a link for the 1st json of each type:')
print(event_links[0])
print(lineup_links[0])
print(match_links[0])

##############################################################################
# Using the cloned open-data
# --------------------------
# Assuming you have cloned the open-data using git you can also get a list of files with glob.
# If you are not using git, comment this out

# change the path of STATSBOMB_DATA to the location of you open-data
# STATSBOMB_DATA = os.path.join('..', '..', '..', 'open-data','data')
# event_links = glob.glob(os.path.join(STATSBOMB_DATA, 'events', '**', '*.json'),recursive=True)
# lineup_links = glob.glob(os.path.join(STATSBOMB_DATA, 'lineups', '**', '*.json'),recursive=True)
# match_links = glob.glob(os.path.join(STATSBOMB_DATA, 'matches', '**', '*.json'),recursive=True)
# COMPETITION_PATH = os.path.join(STATSBOMB_DATA, 'competitions.json')

# print('Number of event files:',len(event_links))
# print('Number of lineup files:', len(lineup_links))
# print('Number of match files:', len(match_links))

##############################################################################
# Setup some destination folders
# ------------------------------
# Now we need to setup some folders to store the dataframes.
# We are going to setup the following directory structure
#
# | data <- top level directory to store the combined dataframes
# | ├── event_raw <- Folder for event data
# | ├── related_raw <- Folder for info on how events are connected
# | ├── freeze_raw <- Folder for the individual shot freeze frames
# | ├── tactic_raw <-Folder for the lineup tactics
# | ├── lineup_raw <- Folder for the lineup info
#
# I am saving the dataframes as parquet files as they are small and load rapidly
# (see here for more info https://ursalabs.org/blog/2019-10-columnar-perf/).

# Amend this path to where you want to store the data
DATA_FOLDER = os.path.join('')

# make the directory structure
for folder in ['event_raw', 'related_raw', 'freeze_raw', 'tactic_raw', 'lineup_raw']:
    path = os.path.join(DATA_FOLDER, folder)
    if not os.path.exists(path):
        os.mkdir(path)

##############################################################################
# Competition data
# ----------------
# Get the competition data as a dataframe as save as parquet file

df_competition = sbapi.read_competition(COMPETITION_PATH, warn=False)
# note there is a slight loss of data quality with timestamps,
# but these aren't relevant for analysis
# pandas has nanoseconds, which aren't supported in parquet (supports milliseconds)
df_competition.to_parquet(os.path.join(DATA_FOLDER, 'competition.parquet'),
                          allow_truncated_timestamps=True)
df_competition.info()

##############################################################################
#  Keep a copy of the old match data
# ----------------------------------
# We are going to use this to compare to the new match file and check for updates.

match_path = os.path.join(DATA_FOLDER, 'match.parquet')
if os.path.exists(match_path):
    df_match_copy = pd.read_parquet(match_path).copy()
    UPDATE_FILES= True
else:
    UPDATE_FILES = False

##############################################################################
#  Match data
# -----------
# Get the match data as a dataframe and save as parquet.
# Note there is a mismatch between the length of this file
# and the number of event files because some event files don't have match data.

match_dfs = [sbapi.read_match(file, warn=False) for file in match_links]
df_match = pd.concat(match_dfs)
# again there is a slight loss of quality when saving timestamps, but only relevant for last_updated
df_match.to_parquet(os.path.join(DATA_FOLDER, 'match.parquet'),
                    allow_truncated_timestamps=True)
df_match.info()

##############################################################################
#  Get a list of games which have been updated
# --------------------------------------------

if UPDATE_FILES:
    df_match_copy = (df_match[['match_id', 'last_updated']]
                     .merge(df_match_copy[['match_id', 'last_updated']],
                            how='left', suffixes=['', '_old'], on='match_id'))
    df_match_copy = df_match_copy[(df_match_copy.last_updated.dt.floor('ms') !=
                                   df_match_copy.last_updated_old.dt.floor('ms'))].copy()
    to_update = df_match_copy.match_id.unique()

    # get array of event links to update - based on whether they have been updated in the match json
    event_link_ids = [int(os.path.splitext(os.path.basename(link))[0]) for link in event_links]
    event_to_update = [link in to_update for link in event_link_ids]
    event_links = np.array(event_links)[event_to_update]

    # get array of lineup links to update -
    # based on whether they have been updated in the match jsons
    lineup_link_ids = [int(os.path.splitext(os.path.basename(link))[0]) for link in lineup_links]
    lineup_to_update = [link in to_update for link in lineup_link_ids]
    lineup_links = np.array(lineup_links)[lineup_to_update]

##############################################################################
#  Subset a few files for demo purposes
# -------------------------------------
# For the purposes of the demo, we will take the first five event and lineup files
# Comment this out if you want the whole of the open-data
lineup_links = lineup_links[:5]
event_links = event_links[:5]

##############################################################################
# Lineup data
# -----------

# Amend this path to where you want to store the data
LINEUP_FOLDER = os.path.join(DATA_FOLDER, 'lineup_raw')
# loop through all the changed links and store as parquet files - small and fast files
for file in lineup_links:
    save_path = f'{os.path.basename(file)[:-4]}parquet'
    try:
        df_lineup = sbapi.read_lineup(file, warn=False)
        df_lineup.to_parquet(os.path.join(LINEUP_FOLDER, save_path))
    except ValueError:
        print('Skipping file:', file)

##############################################################################
# Get the lineup files as a single dataframe

if len(lineup_links) == 0:
    print('No update')
else:
    lineup_files = glob.glob(os.path.join(LINEUP_FOLDER, '*.parquet'))
    df_lineup = pd.concat([pd.read_parquet(file) for file in lineup_files])
    df_lineup.to_parquet(os.path.join(DATA_FOLDER, 'lineup.parquet'))
    df_lineup.info()

##############################################################################
# Event data
# ----------
# We will also loop through the first five event files.
# However, the ``read_event`` function returns a dictionary of four dataframes:
# 'event', 'related_event', 'shot_freeze_frame' and 'tactics_lineup'.
# It's possible to alter ``read_event`` to return fewer dataframes (see the API docs).

# loop through all the changed links and store as parquet files - small and fast files
for file in event_links:
    save_path = f'{os.path.basename(file)[:-4]}parquet'
    try:
        dict_event = sbapi.read_event(file, warn=False)
        # save to parquet files
        # using the dictionary key to access the dataframes from the dictionary
        dict_event['event'].to_parquet(os.path.join(DATA_FOLDER, 'event_raw', save_path))
        dict_event['related_event'].to_parquet(os.path.join(DATA_FOLDER, 'related_raw', save_path))
        dict_event['shot_freeze_frame'].to_parquet(os.path.join(DATA_FOLDER, 'freeze_raw',
                                                                save_path))
        dict_event['tactics_lineup'].to_parquet(os.path.join(DATA_FOLDER, 'tactic_raw', save_path))
    except ValueError:
        print('Skipping:', file)

##############################################################################
#  Get a list of match_ids to update
# ----------------------------------

event_files = glob.glob(os.path.join(DATA_FOLDER, 'event_raw', '*.parquet'))
if UPDATE_FILES:
    ids_to_update = [int(os.path.splitext(os.path.basename(link))[0]) for link in event_links]


# Function to load the old dataframe (if exists) and combine with the updated parquet files
def update(directory, file_type, update_ids):
    """ Update an old DataFrame with files that have changed/ been added.

    Parameters
    ----------
    directory : path to directory containing the files
    file_type : str
        One of 'event', 'freeze', 'tatic', or related'
    update_ids : list of integers
        A list of the match ids to update

    Returns
    -------
    df : pandas.DataFrame
        An updated DataFrame with the new/changed matches.
    """
    # get a list of parquet files to add to the old dataframe
    files = glob.glob(os.path.join(directory, f'{file_type}_raw', '*.parquet'))
    files_id = [int(os.path.splitext(os.path.basename(file))[0]) for file in files]
    mask_update = [match_id in update_ids for match_id in files_id]
    files = np.array(files)[mask_update]
    # load the old dataframe, filter out changed matches and add the new parquet files
    df_old = pd.read_parquet(os.path.join(directory, f'{file_type}.parquet'))
    df_old = df_old[~df_old.match_id.isin(update_ids)]
    df_new = pd.concat([pd.read_parquet(file) for file in files])
    df_old = pd.concat([df_old, df_new])
    return df_old


##############################################################################
# Get event files as a single dataframe and save to parquet.
if len(event_links) == 0:
    print('No update')
else:
    if UPDATE_FILES:
        df_event = update(DATA_FOLDER, 'event', ids_to_update)
        df_event.to_parquet(os.path.join(DATA_FOLDER, 'event.parquet'))
        df_event.info(verbose=True, null_counts=True)
    else:
        df_event = pd.concat([pd.read_parquet(file) for file in event_files])
        df_event.to_parquet(os.path.join(DATA_FOLDER, 'event.parquet'))
        df_event.info(verbose=True, null_counts=True)

##############################################################################
# Get shot freeze frames files as a single dataframe and save to parquet.

if len(event_links) == 0:
    print('No update')
else:
    if UPDATE_FILES:
        df_freeze = update(DATA_FOLDER, 'freeze', ids_to_update)
        df_freeze.to_parquet(os.path.join(DATA_FOLDER, 'freeze.parquet'))
        df_freeze.info(verbose=True, null_counts=True)
    else:
        freeze_files = glob.glob(os.path.join(DATA_FOLDER, 'freeze_raw', '*.parquet'))
        df_freeze = pd.concat([pd.read_parquet(file) for file in freeze_files])
        df_freeze.to_parquet(os.path.join(DATA_FOLDER, 'freeze.parquet'))
        df_freeze.info()


##############################################################################
# Get tactics files as a single dataframe and save to parquet.

if len(event_links) == 0:
    print('No update')
else:
    if UPDATE_FILES:
        df_tactic = update(DATA_FOLDER, 'tactic', ids_to_update)
        df_tactic.to_parquet(os.path.join(DATA_FOLDER, 'tactic.parquet'))
        df_tactic.info(verbose=True, null_counts=True)
    else:
        tactic_files = glob.glob(os.path.join(DATA_FOLDER, 'tactic_raw', '*.parquet'))
        df_tactic = pd.concat([pd.read_parquet(file) for file in tactic_files])
        df_tactic.to_parquet(os.path.join(DATA_FOLDER, 'tactic.parquet'))
        df_tactic.info()

##############################################################################
# Get related events files as a single dataframe and save to parquet.

if len(event_links) == 0:
    print('No update')
else:
    if UPDATE_FILES:
        df_related = update(DATA_FOLDER, 'related', ids_to_update)
        df_related.to_parquet(os.path.join(DATA_FOLDER, 'related.parquet'))
        df_related.info(verbose=True, null_counts=True)
    else:
        related_files = glob.glob(os.path.join(DATA_FOLDER, 'related_raw', '*.parquet'))
        df_related = pd.concat([pd.read_parquet(file) for file in related_files])
        df_related.to_parquet(os.path.join(DATA_FOLDER, 'related.parquet'))
        df_related.info(verbose=True, null_counts=True)
