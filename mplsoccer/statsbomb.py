""" `mplsoccer.statsbomb` is a python module for loading StatsBomb data. """

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import pandas as pd
import os
import numpy as np
import warnings

EVENT_SLUG = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/events'
MATCH_SLUG = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches'
LINEUP_SLUG = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/lineups'
COMPETITION_URL = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json'

statsbomb_warning = ('Please be responsible with Statsbomb data.'
                     'Register your details on https://www.statsbomb.com/resource-centre'
                     'and read the User Agreement carefully (on the same page).')


def _split_location_cols(df, col, new_cols):
    """ Location is stored as a list. split into columns. """
    for new_col in new_cols:
        df[new_col] = np.nan
    if col in df.columns:
        mask_not_null = df[col].notnull()
        df_not_null = df.loc[mask_not_null, col]
        df_new = pd.DataFrame(df_not_null.tolist(), index=df_not_null.index, columns=new_cols)
        df.loc[mask_not_null, new_cols] = df_new
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


def read_event(path_or_buf, related_event_df=True, shot_freeze_frame_df=True, tactics_lineup_df=True, warn=True):
    """ Extracts individual event json and loads as a dictionary of up to
    four pandas.DataFrame: 'event', 'related event', 'shot_freeze_frame', and 'tactics_lineup'.
    
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
            
        related_event_df : bool, default True
            Whether to return a 'related_event' Dataframe in the returned dictionary.   
        
        shot_freeze_frame_df : bool, default True
            Whether to return a 'shot_freeze_frame' in the returned dictionary.   
        
        tactics_lineup_df : bool, default True
            Whether to return a 'tactics_lineup' Dataframe in the returned dictionary.

        warn : bool, default True
            Whether to warn about Statsbomb's data license agreement.
            
        Returns
        -------
        Dict of up to 4 pandas.DataFrame.
            Dict keys: 'event', 'related_event', 'shot_freeze_frame', 'tactics_lineup'.


        Examples
        --------
        # read from path - note change path to navigate to open-data folder
        from mplsoccer.statsbomb import read_event
        import os
        PATH_TO_EDIT = os.path.join('open-data','data','events','7430.json')
        dict_dfs = read_event(PATH_TO_EDIT)

        # read from url
        from mplsoccer.statsbomb import read_event, EVENT_SLUG
        import os
        URL = os.path.join(EVENT_SLUG,'7430.json')
        dict_dfs = read_event(URL)
    """
    if warn:
        warnings.warn(statsbomb_warning)
        
    df_dict = {}
    
    # read as dataframe
    df = pd.read_json(path_or_buf, encoding='utf-8')
    if df.empty:
        print(f'Skipping {path_or_buf}: empty json')
        return
    
    # timestamp defaults to today's date so store as integers in seperate columns
    df['timestamp_minute'] = df.timestamp.dt.minute
    df['timestamp_second'] = df.timestamp.dt.second
    df['timestamp_millisecond'] = (df.timestamp.dt.microsecond/1000).astype(np.int64)
    df.drop('timestamp', axis=1, inplace=True)
    
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
    df.sort_values(['minute', 'second', 'timestamp_minute',
                    'timestamp_second', 'timestamp_millisecond', 'possession'], inplace=True)
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
    if related_event_df:
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
        # add on match_id and add to dictionary
        df_related_event['match_id'] = match_id
        df_dict['related_event'] = df_related_event
    
    # create a shot freeze frame dataframe - also splits dictionary of player details into columns
    if shot_freeze_frame_df:
        df_shot_freeze = _list_dictionary_to_df(df, col='shot_freeze_frame',
                                                value_name='player', var_name='event_freeze_id')
        df_shot_freeze = _split_dict_col(df_shot_freeze, 'player')
        _split_location_cols(df_shot_freeze, 'player_location', ['x', 'y'])
        # add on match_id and add to dictionary
        df_shot_freeze['match_id'] = match_id
        df_dict['shot_freeze_frame'] = df_shot_freeze

    # create a tactics lineup frame dataframe - also splits dictionary of player details into columns
    if tactics_lineup_df:
        df_tactic_lineup = _list_dictionary_to_df(df, col='tactics_lineup',
                                                  value_name='player', var_name='event_tactics_id')
        df_tactic_lineup = _split_dict_col(df_tactic_lineup, 'player')
        # add on match_id and add to dictionary
        df_tactic_lineup['match_id'] = match_id
        df_dict['tactics_lineup'] = df_tactic_lineup
    
    # drop columns stored as a separate table
    df.drop(['related_events', 'shot_freeze_frame', 'tactics_lineup'], axis=1, inplace=True)
           
    # reorder columns so some of the most used ones are first
    cols = ['match_id', 'id', 'index', 'period', 'timestamp_minute', 'timestamp_second', 
            'timestamp_millisecond', 'minute', 'second', 'type_id', 'type_name',
            'outcome_id', 'outcome_name',  'play_pattern_id', 'play_pattern_name',
            'possession_team_id', 'possession',  'possession_team_name', 'team_id', 'team_name',
            'player_id', 'player_name', 'position_id',
            'position_name', 'duration', 'x', 'y', 'pass_end_x', 'pass_end_y', 'carry_end_x',
            'carry_end_y', 'shot_end_x', 'shot_end_y', 'shot_end_z',
            'goalkeeper_end_x', 'goalkeeper_end_y', 'body_part_id', 'body_part_name']
    other_cols = df.columns[~df.columns.isin(cols)]
    cols.extend(other_cols)
    df = df[cols].copy()
    
    # add to dictionary
    df_dict['event'] = df
    
    return df_dict


def read_match(path_or_buf, warn=True):
    """ Extracts individual match json and loads as a pandas.DataFrame.
    
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

        warn : bool, default True
            Whether to warn about Statsbomb's data license agreement.

        Returns
        -------
        pandas.DataFrame

        Examples
        --------
        # read from path - note change path to navigate to open-data folder
        from mplsoccer.statsbomb import read_match
        import os
        PATH_TO_EDIT = os.path.join('open-data','data','matches','11','1.json')
        df_match = read_match(PATH_TO_EDIT)

        # read from url
        from mplsoccer.statsbomb import read_match, MATCH_SLUG
        import os
        URL = os.path.join(MATCH_SLUG,'11','1.json')
        df_match = read_match(URL)
    """
    if warn:
        warnings.warn(statsbomb_warning)
        
    df_match = pd.read_json(path_or_buf, convert_dates=['match_date', 'last_updated'])
    if df_match.empty:
        print(f'Skipping {path_or_buf}: empty json')
        return
    
    # loop through the columns that are still dictionary columns and add them as seperate cols to the datafram
    dictionary_columns = ['competition', 'season', 'home_team', 'away_team', 'metadata', 'competition_stage',
                          'stadium', 'referee']
    for col in dictionary_columns:
        if col in df_match.columns:
            df_match = _split_dict_col(df_match, col)
        
    # convert kickoff to datetime - date + kickoff time
    df_match['kick_off'] = pd.to_datetime(df_match.match_date.astype(str) + ' ' + df_match.kick_off)
    # drop one gender column as always equal to the other
    # drop match status as always available
    df_match.drop(['away_team_gender', 'match_status'], axis=1, inplace=True)
    df_match.rename({'home_team_gender': 'competition_gender'}, axis=1, inplace=True)
    # manager is a list (len=1) containing a dictionary so lets split into columns
    if 'home_team_managers' in df_match.columns:
        df_match['home_team_managers'] = df_match.home_team_managers.str[0]
        df_match = _split_dict_col(df_match, 'home_team_managers')
        df_match['home_team_managers_dob'] = pd.to_datetime(df_match['home_team_managers_dob'])
    if 'away_team_managers' in df_match.columns:
        df_match['away_team_managers'] = df_match.away_team_managers.str[0]
        df_match = _split_dict_col(df_match, 'away_team_managers')
        df_match['away_team_managers_dob'] = pd.to_datetime(df_match['away_team_managers_dob'])
    # ids to integers
    for col in ['competition_id', 'season_id', 'home_team_id', 'competition_stage_id']:
        df_match[col] = df_match[col].astype(np.int64)
    # sort and reset index: ready for exporting to feather
    df_match.sort_values('kick_off', inplace=True)
    df_match.reset_index(inplace=True, drop=True)
    return df_match


def read_competition(path_or_buf, warn=True):
    """ Extracts competition json and loads as a pandas.DataFrame.
    
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

        warn : bool, default True
            Whether to warn about Statsbomb's data license agreement.

        Returns
        -------
        pandas.DataFrame

        Examples
        --------
        # read from path - note change path to navigate to open-data folder
        from mplsoccer.statsbomb import read_competition
        import os
        PATH_TO_EDIT = os.path.join('open-data','data','competitions.json')
        df_competition = read_competition(PATH_TO_EDIT)

        # read from url
        from mplsoccer.statsbomb import read_competition, COMPETITION_URL
        df_competition = read_competition(COMPETITION_URL)
    """
    if warn:
        warnings.warn(statsbomb_warning)
        
    df_competition = pd.read_json(path_or_buf, convert_dates=['match_updated', 'match_available'])
    if df_competition.empty:
        print(f'Skipping {path_or_buf}: empty json')
        return
    df_competition.sort_values(['competition_id', 'season_id'], inplace=True)
    df_competition.reset_index(drop=True, inplace=True)
    return df_competition


def read_lineup(path_or_buf, warn=True):
    """ Extracts individual lineup jsons and loads as a pandas.DataFrame.
    
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

        warn : bool, default True
            Whether to warn about Statsbomb's data license agreement.
            
        Returns
        -------
        pandas.DataFrame

        Examples
        --------
        # read from path - note change path to navigate to open-data folder
        from mplsoccer.statsbomb import read_lineup
        import os
        PATH_TO_EDIT = os.path.join('open-data','data','lineups','7430.json')
        df_lineup = read_lineup(PATH_TO_EDIT)

        # read from url
        from mplsoccer.statsbomb import read_lineup, LINEUP_SLUG
        import os
        URL = os.path.join(LINEUP_SLUG,'7430.json')
        df_lineup = read_lineup(URL)
    """
    if warn:
        warnings.warn(statsbomb_warning)
        
    df_lineup = pd.read_json(path_or_buf)
    if df_lineup.empty:
        print(f'Skipping {path_or_buf}: empty json')
        return
    df_lineup['match_id'] = os.path.basename(path_or_buf[:-5])
    # each line has a column named player that contains a list of dictionaries
    # we split into seperate columns and then create a new row for each player using melt
    df_lineup_players = df_lineup.lineup.apply(pd.Series)
    df_lineup = df_lineup.merge(df_lineup_players, left_index=True, right_index=True)
    df_lineup.drop('lineup', axis=1, inplace=True)
    df_lineup = df_lineup.melt(id_vars=['team_id', 'team_name', 'match_id'], value_name='player')
    df_lineup.drop('variable', axis=1, inplace=True)
    df_lineup = df_lineup[df_lineup.player.notnull()].copy()
    df_lineup = _split_dict_col(df_lineup, 'player')
    # turn ids to integers if no missings
    df_lineup['match_id'] = df_lineup.match_id.astype(np.int64)
    df_lineup['player_id'] = df_lineup.player_id.astype(np.int64)
    # sort and reset index: ready for exporting to feather
    df_lineup.sort_values('player_id', inplace=True)
    df_lineup.reset_index(inplace=True, drop=True)
    return df_lineup


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
    match_folders = _get_links(match_url)
    match_folders = [(f'https://github.com/{link["href"]}',
                      link['title']) for link in match_folders if '/tree/master/data/matches' in link['href']]
    match_files = []
    for link, folder in match_folders:
        json_links = _get_links(link)
        json_links = [f'{MATCH_SLUG}/{folder}/{link["title"]}' for link in json_links
                      if link['href'][-4:] == 'json']
        match_files.extend(json_links)
    return match_files


def get_event_links():
    """ Returns a list of links to the StatsBomb open-data event jsons."""
    url = 'https://github.com/statsbomb/open-data/tree/master/data/events'
    links = _get_links(url)
    links = [f'{EVENT_SLUG}/{link["title"]}' for link in links if link['href'][-4:] == 'json']
    return links


def get_lineup_links():
    """ Returns a list of links to the StatsBomb open-data lineup jsons."""
    url = 'https://github.com/statsbomb/open-data/tree/master/data/lineups'
    links = _get_links(url)
    event_files = [f'{LINEUP_SLUG}/{link["title"]}' for link in links if link['href'][-4:] == 'json']
    return event_files
