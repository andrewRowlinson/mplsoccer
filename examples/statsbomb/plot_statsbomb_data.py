"""
=========
Statsbomb
=========

In the words of @Torvaney "I did The Bad Thing and started writing another API wrapper for Statsbomb data" (https://twitter.com/Torvaney/status/1251435801407184896).

Why?

Well in my opinion all of the existing ones suck for analysis because they don't return a flat, tidy dataframe.

Here's some alternatives

- https://github.com/Torvaney/statsbombapi
- https://github.com/statsbomb/statsbombpy
- https://github.com/imrankhan17/statsbomb-parser

I hope to inspire others to make a better one, so this one can become obselete.

Please be responsible with Statsbomb data.Register your details on https://www.statsbomb.com/resource-centreand read the User Agreement carefully (on the same page). warnings.warn(statsbomb_warning)
"""

import mplsoccer.statsbomb as sbapi
import pandas as pd
import os
import glob
pd.set_option("display.max_columns", 10)

##############################################################################
# Scraping StatsBomb links
# ------------------------
# I have deliberately made functions to scrape links for the open-data so it's easier for beginners.
# However, it's much better to just clone all of the data from the repository: https://github.com/statsbomb/open-data.git
# so you have the files stored locally
# See : https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository

# scrape the links for all the open-data files, returning a list of links to the files
event_links = sbapi.get_event_links()
lineup_links = sbapi.get_lineup_links()
match_links = sbapi.get_match_links()

print('Number of event files:',len(event_links))
print('Number of lineup files:', len(lineup_links))
print('Number of match files:', len(match_links))

##############################################################################
# Competition data
# ----------------
# Get the competition data as a dataframe

df_competition = sbapi.read_competition(sbapi.COMPETITION_URL)
##############################################################################
df_competition.head()
##############################################################################
df_competition.info()

##############################################################################
#  Match data
# -----------
# Get the match data as a dataframe.
# Note the mismatch as some event files don't match data!

match_dfs = [sbapi.read_match(file) for file in match_links]
df_match = pd.concat(match_dfs)
##############################################################################
df_match.head()
##############################################################################
df_match.info()

##############################################################################
# Lineup data
# -----------
# I don't recommend looping through all of the lineup links in one go as there are hundreds,
# and one might fail! For demo purposes, we will loop through the first five files and save them to the local disc.
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
    
lineup_files = glob.glob(os.path.join(LINEUP_FOLDER,'*.parquet'))
##############################################################################
df_lineup.head()
##############################################################################
df_lineup.info()

##############################################################################
# Event data
# ----------
# Let's do the same for the event files (the first five only again).
# Note that the read_event function returns a dictionary of four dataframes: 'event', 'related_event',
# 'shot_freeze_frame' and 'tactics_lineup'. This can be altered to return fewer dataframes (see the API docs)

# Amend this path to where you want to store the data
DATA_FOLDER = os.path.join('..','..','data')
# get the first five files - comment out this if you want all of them
event_links = event_links[:5]
# loop through the links and store as parquet files - small and fast files
for file in event_links:
    dict_event = sbapi.read_event(file)
    save_path = f'{os.path.basename(file)[:-4]}parquet'
    # save to parquet files
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
