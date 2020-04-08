""" `mplsoccer` is a python library for plotting soccer / football pitches in Matplotlib. """

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import pandas as pd
import os


def _split_location_cols(df, col, new_cols):
    """ Location is stored as a list. split into columns. """
    if col in df.columns:
        df[new_cols] = df[col].apply(pd.Series)
        df.drop(col, axis=1, inplace=True)


def _list_dictionary_to_df(df, col, value_name, var_name):
    """ Some columns are a list of dictionaries. This turns them into a new dataframe of rows."""
    df = df.loc[df[col].notnull(), ['id', col]]
    df.set_index('id', inplace=True)
    df = df[col].apply(pd.Series).copy()
    df.reset_index(inplace=True)
    df = df.melt(id_vars='id', value_name=value_name, var_name=var_name)
    df[var_name] = df[var_name] + 1
    df = df[df[value_name].notnull()].copy()
    df.reset_index(inplace=True, drop=True)
    return df


def _split_dict_col(df, col):
    """ Function to split a dictionary column to separate columns."""
    # handle missing data by filling with an empty dictionary
    df[col] = df[col].apply(lambda x: {} if pd.isna(x) else x)
    # split the non-missing data and change the column names
    df_temp_cols = pd.json_normalize(df[col]).set_index(df.index)
    col_names = df_temp_cols.columns
    # note add column description to column name if doesn't already contain it
    col_names = [c.replace('.', '_') if c[:len(col)] == col else (col+'_'+c).replace('.', '_') for c in col_names]
    df[col_names] = df_temp_cols
    # drop old column
    df.drop(col, axis=1, inplace=True)
    return df


def _simplify_cols_and_drop(df, col):
    """ Function to merge similar columns together and drop original columns. """
    cols = df.columns[df.columns.str.contains(col)]
    df[col] = df.lookup(df.index, df[cols].notnull().idxmax(axis=1))
    df.drop(cols, axis=1, inplace=True)
    return df


def read_event(path_or_buf):
    """ Extracts individual event jsons and loads as four dataframes: df_event, df_related event,
    df_shot_freeze, and df_tactic_lineup.
    
    Parameters
        ----------
        path_or_buf : a valid JSON str, path object or file-like object
            Any valid string path is acceptable. The string could be a URL. Valid
            URL schemes include http, ftp, s3, and file. For file URLs, a host is
            expected. A local file could be:
            ``file://localhost/path/to/table.json``.
            If you want to pass in a path object, pandas accepts any
            ``os.PathLike``.
            By file-like object, we refer to objects with a ``read()`` method,
            such as a file handler (e.g. via builtin ``open`` function)
            or ``StringIO``.


        Returns
        -------
        4 DataFrames: df_event, df_related_events, df_shot_freeze, df_tactics_lineup.
        In that order.


        Examples
        --------
        # read from path - note change path to navigate to open-data folder
        from mplsoccer.statsbomb import read_event
        import os
        PATH_TO_EDIT = os.path.join('open-data','data','events','7430.json')
        df_event, df_related_event, df_shot_freeze, df_tactics_lineup = read_event(PATH_TO_EDIT)

        # read from url
        from mplsoccer.statsbomb import read_event, EVENT_SLUG
        import os
        URL = os.path.join(EVENT_SLUG,'7430.json')
        df_event, df_related_event, df_shot_freeze, df_tactic_lineup = read_event(URL)
    
    """
    
    # timestamp defaults to today's date so store as a string - feather can't store time objects
    df = pd.read_json(path_or_buf, encoding='utf-8')
    
    # get match id and add to the event dataframe
    match_id = int(os.path.basename(path_or_buf)[:-5])
    df['match_id'] = match_id
    
    # loop through the columns that are still dictionary columns and add them as separate cols to the dataframe
    # these are nested dataframes in the docs - although dribbled_past/ pressure isn't needed here?
    # also some others are needed: type, possession_team, play_pattern, team, tactics, player, position
    dictionary_columns = ['pass', '50_50', 'bad_behaviour', 'ball_receipt', 'ball_recovery', 'block', 'carry',
                          'clearance', 'dribble', 'duel', 'foul_committed', 'foul_won', 'goalkeeper',
                          'half_end', 'half_start', 'injury_stoppage', 'interception',
                          'miscontrol', 'play_pattern', 'player', 'player_off', 'position',
                          'possession_team', 'shot', 'substitution', 'tactics', 'team', 'type']
    for col in dictionary_columns:
        if col in df.columns:
            df = _split_dict_col(df, col)
    
    # sort by time and reset index
    df.sort_values(['minute', 'second', 'timestamp', 'possession'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    
    # split location info to x, y and (z for shot) columns and drop old columns
    _split_location_cols(df, 'location', ['x', 'y'])
    _split_location_cols(df, 'pass_end_location', ['pass_end_x', 'pass_end_y'])
    _split_location_cols(df, 'carry_end_location', ['carry_end_x', 'carry_end_y'])
    _split_location_cols(df, 'shot_end_location', ['shot_end_x', 'shot_end_y', 'shot_end_z'])
    _split_location_cols(df, 'goalkeeper_end_location', ['goalkeeper_end_x', 'goalkeeper_end_y'])
    
    # replace weird * character in the type_name for ball receipt
    df['type_name'] = df['type_name'].replace({'Ball Receipt*': 'Ball Receipt'})
    
    # because some columns were contained in dictionaries they have been split into separate columns
    # with different prefixes, e.g. clearance_aerial_won, pass_aerial_won, shot_aerial_won
    # this combines them into one column and drops the original columns
    df = _simplify_cols_and_drop(df, 'outcome_id')
    df = _simplify_cols_and_drop(df, 'outcome_name')
    df = _simplify_cols_and_drop(df, 'body_part_id')
    df = _simplify_cols_and_drop(df, 'body_part_name')
    df = _simplify_cols_and_drop(df, 'aerial_won')
    
    # create a related events dataframe
    df_related_event = _list_dictionary_to_df(df, col='related_events',
                                              value_name='related_event', var_name='event_related_id')
    # some carries don't have the corresponding events. This makes sure all events are linked both ways
    df_related_event.drop('event_related_id', axis=1, inplace=True)
    df_related_event_reverse = df_related_event.rename({'related_event': 'id', 'id': 'related_event'}, axis=1)
    df_related_event = pd.concat([df_related_event, df_related_event_reverse], sort=False)
    df_related_event.drop_duplicates(inplace=True)
    # and add on the type_names, index for easier lookups of how the events are related
    df_event_type = df[['id', 'type_name', 'index']].copy()
    df_related_event = df_related_event.merge(df_event_type, on='id', how='left', validate='m:1')
    df_event_type.rename({'id': 'related_event'}, axis=1, inplace=True)
    df_related_event = df_related_event.merge(df_event_type, on='related_event',
                                              how='left', validate='m:1', suffixes=['', '_related'])
    df_related_event.rename({'related_event': 'id_related'}, axis=1, inplace=True)
    
    # create a shot freeze frame dataframe - also splits dictionary of player details into columns
    df_shot_freeze = _list_dictionary_to_df(df, col='shot_freeze_frame',
                                            value_name='player', var_name='event_freeze_id')
    df_shot_freeze = _split_dict_col(df_shot_freeze, 'player')
    _split_location_cols(df_shot_freeze, 'player_location', ['x', 'y'])

    # create a tactics lineup frame dataframe - also splits dictionary of player details into columns
    df_tactic_lineup = _list_dictionary_to_df(df, col='tactics_lineup',
                                              value_name='player', var_name='event_tactics_id')
    df_tactic_lineup = _split_dict_col(df_tactic_lineup, 'player')
    
    # drop columns stored as a separate table
    df.drop(['related_events', 'shot_freeze_frame', 'tactics_lineup'], axis=1, inplace=True)
        
    # add match id to dataframes
    df_related_event['match_id'] = match_id
    df_shot_freeze['match_id'] = match_id    
    df_tactic_lineup['match_id'] = match_id
    
    # reorder columns so some of the most used ones are first
    cols = ['match_id', 'id', 'index', 'period', 'timestamp', 'minute',
            'second', 'type_id', 'type_name', 'outcome_id', 'outcome_name',  'play_pattern_id', 'play_pattern_name',
            'possession_team_id', 'possession',  'possession_team_name', 'team_id', 'team_name',
            'player_id', 'player_name', 'position_id',
            'position_name', 'duration', 'x', 'y', 'pass_end_x', 'pass_end_y', 'carry_end_x',
            'carry_end_y', 'shot_end_x', 'shot_end_y', 'shot_end_z',
            'goalkeeper_end_x', 'goalkeeper_end_y', 'body_part_id', 'body_part_name']
    other_cols = df.columns[~df.columns.isin(cols)]
    cols.extend(other_cols)
    df_event = df[cols].copy()
    
    return df_event, df_related_event, df_shot_freeze, df_tactic_lineup


def _get_links(url):
    # imports here as don't expect these functions to be used all the time
    from bs4 import BeautifulSoup
    import urllib.request
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'html.parser', from_encoding=response.info().get_param('charset'))
    links = soup.find_all('a', href=True)
    return links


def get_match_links():
    """ Returns a list of links to the StatsBomb open-data match jsons."""
    match_url = 'https://github.com/statsbomb/open-data/tree/master/data/matches'
    match_raw_slug = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches'
    match_folders = _get_links(match_url)
    match_folders = [(f'https://github.com/{link["href"]}',
                      link['title']) for link in match_folders if '/tree/master/data/matches' in link['href']]
    match_files = []
    for link, folder in match_folders:
        json_links = _get_links(link)
        json_links = [f'{match_raw_slug}/{folder}/{link["title"]}' for link in json_links
                      if link['href'][-4:] == 'json']
        match_files.extend(json_links)
    return match_files


def get_event_links():
    """ Returns a list of links to the StatsBomb open-data event jsons."""
    url = 'https://github.com/statsbomb/open-data/tree/master/data/events'
    raw_slug = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/events'
    links = _get_links(url)
    links = [f'{raw_slug}/{link["title"]}' for link in links if link['href'][-4:] == 'json']
    return links


def get_lineup_links():
    """ Returns a list of links to the StatsBomb open-data lineup jsons."""
    url = 'https://github.com/statsbomb/open-data/tree/master/data/lineups'
    raw_slug = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/lineups'
    links = _get_links(url)
    event_files = [f'{raw_slug}/{link["title"]}' for link in links if link['href'][-4:] == 'json']
    return event_files
