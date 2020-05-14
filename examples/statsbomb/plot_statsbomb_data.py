"""
=========
Statsbomb
=========

In the words of @Torvaney "I did The Bad Thing and started writing another API wrapper for Statsbomb data" (https://twitter.com/Torvaney/status/1251435801407184896).

Why?

Well, in my opinion, all of the existing ones don't return a flat, tidy dataframe useful for analysis.

Here are some alternatives

- https://github.com/Torvaney/statsbombapi
- https://github.com/statsbomb/statsbombpy
- https://github.com/imrankhan17/statsbomb-parser

I hope to inspire others to make a better one, so this one can become obsolete.

Please be responsible with Statsbomb data. Register your details on https://www.statsbomb.com/resource-centreand read the User Agreement carefully (on the same page).
"""

import mplsoccer.statsbomb as sbapi
import pandas as pd
import os
import glob
pd.set_option("display.max_columns", 6)

##############################################################################
# Scraping StatsBomb links
# ------------------------
# I have deliberately made functions to scrape links for the open-data, so it is easy. 
# However, it is better to clone the StatsBomb data to store the data locally.
# This will manage all the data updates for you.
# First download git (if you are using Windows: https://gitforwindows.org/).
# Then navigate in the git terminal to a directory where you want to store the data.
# Use cd [directory name], for example, cd ~/documents/data.
# Then run: git clone https://github.com/statsbomb/open-data.git
#
# From time-to-time, the open-data gets updated, to get the latest files run the command: git pull 
# from the directory where the data is stored, e.g. cd ~/documents/data/open-data
# and it will download all the latest files
#
# Here's how to get the links to the data without using git:

# scrape the links for all the open-data files, which returns a list of links to the files
event_links = sbapi.get_event_links()
lineup_links = sbapi.get_lineup_links()
match_links = sbapi.get_match_links()
competition_path = sbapi.COMPETITION_URL

print('Number of event files:',len(event_links))
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
STATSBOMB_DATA = os.path.join('..', '..', '..', 'open-data','data')  
event_links = glob.glob(os.path.join(STATSBOMB_DATA, 'events', '**', '*.json'),recursive=True)
lineup_links = glob.glob(os.path.join(STATSBOMB_DATA, 'lineups', '**', '*.json'),recursive=True)
match_links = glob.glob(os.path.join(STATSBOMB_DATA, 'matches', '**', '*.json'),recursive=True)
competition_path = os.path.join(STATSBOMB_DATA, 'competitions.json')

print('Number of event files:',len(event_links))
print('Number of lineup files:', len(lineup_links))
print('Number of match files:', len(match_links))

##############################################################################
# Setup some destination folders
# ------------------------------

##############################################################################
# Competition data
# ----------------
# Get the competition data as a dataframe

df_competition = sbapi.read_competition(competition_path)
##############################################################################
df_competition.head()
##############################################################################
df_competition.info()

##############################################################################
#  Match data
# -----------
# Get the match data as a dataframe.
# Note there is a mismatch between the length of this file
# and the number of event files since some event files don't have match data.

match_dfs = [sbapi.read_match(file) for file in match_links]
df_match = pd.concat(match_dfs)
##############################################################################
df_match.head()
##############################################################################
df_match.info()

##############################################################################
# Lineup data
# -----------
# There are hundreds of event files.
# For this demo, we will loop through the first five files and save them to the local disc.
# I have saved the dataframes as parquet files as they are small and load rapidly 
# (see here for more info https://ursalabs.org/blog/2019-10-columnar-perf/).

# Amend this path to where you want to store the data
LINEUP_FOLDER = os.path.join('..','..','data','lineup')
# get the first five files - comment out this if you want all of them
lineup_links = lineup_links[:5]
# loop through the links and store as parquet files - small and fast files
for file in lineup_links:
    df_lineup = sbapi.read_lineup(file)
    df_lineup.to_parquet(os.path.join(LINEUP_FOLDER,f'{os.path.basename(file)[:-4]}parquet'))

##############################################################################
# Get the lineup files as a single dataframe
lineup_files = glob.glob(os.path.join(LINEUP_FOLDER,'*.parquet'))
df_lineup = pd.concat([pd.read_parquet(file) for file in lineup_files])

##############################################################################
df_lineup.head()
##############################################################################
df_lineup.info()

##############################################################################
# Event data
# ----------
# This is also possible for event files.
# However, the read_event function returns a dictionary of four dataframes: 'event', 'related_event',
# 'shot_freeze_frame' and 'tactics_lineup'. You can alter this to return fewer dataframes (see the API docs).

# Amend this path to where you want to store the data
DATA_FOLDER = os.path.join('..','..','data')
# get the first five files - comment out this if you want all of them
event_links = event_links[:5]
# loop through the links and store as parquet files - small and fast files
for file in event_links:
    dict_event = sbapi.read_event(file)
    save_path = f'{os.path.basename(file)[:-4]}parquet'
    # save to parquet files
    # using the dictionary key to access the dataframes from the dictionary
    dict_event['event'].to_parquet(os.path.join(DATA_FOLDER, 'event', save_path))
    dict_event['related_event'].to_parquet(os.path.join(DATA_FOLDER, 'related_event', save_path))
    dict_event['shot_freeze_frame'].to_parquet(os.path.join(DATA_FOLDER, 'freeze_frame', save_path))
    dict_event['tactics_lineup'].to_parquet(os.path.join(DATA_FOLDER, 'tactic', save_path))

##############################################################################
# Get event files as a single dataframe
event_files = glob.glob(os.path.join(DATA_FOLDER,'event','*.parquet'))
df_event = pd.concat([pd.read_parquet(file) for file in event_files])

##############################################################################
# Show the first five rows
df_event.head()

##############################################################################
# Show the info
df_event.info(verbose=True, null_counts=True)

##############################################################################
# Get shot freeze frames as a single dataframe
freeze_files = glob.glob(os.path.join(DATA_FOLDER,'freeze_frame','*.parquet'))
df_freeze = pd.concat([pd.read_parquet(file) for file in freeze_files])

##############################################################################
# Show the first five rows
df_freeze.head()

##############################################################################
# Show the info
df_freeze.info()

##############################################################################
# Get tactic files as a single dataframe
tactic_files = glob.glob(os.path.join(DATA_FOLDER,'tactic','*.parquet'))
df_tactic = pd.concat([pd.read_parquet(file) for file in tactic_files])

##############################################################################
# Show the first five rows
df_tactic.head()

##############################################################################
# Show the info
df_tactic.info()

##############################################################################
# Get related events as a single dataframe
related_files = glob.glob(os.path.join(DATA_FOLDER,'related_event','*.parquet'))
df_related = pd.concat([pd.read_parquet(file) for file in related_files])

##############################################################################
# Show the first five rows
df_related.head()

##############################################################################
# Show the info
df_related.info()
