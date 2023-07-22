"""`mplsoccer.statsbomb` is a python module for loading StatsBomb open, local and API data."""

import json
import os

import pandas as pd
import requests

__all__ = ['Sbopen', 'Sbapi', 'Sblocal']


class Sbopen:
    """ Class for loading data from the StatsBomb open-data.
    The data is available at: https://github.com/statsbomb/open-data under
    a non-commercial license.

    Parameters
    ----------
    dataframe : bool, default True
        Whether to return dataframes (True) or flattened list of dictionaries (False)
        from the class methods.
    """

    def __init__(self, dataframe=True):
        self.dataframe = dataframe
        self.url = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/'

    @staticmethod
    def _get_data(url):
        """ Get the StatsBomb data as a list of dictionaries.

        Parameters
        ----------
        url : str

        Returns
        -------
        json-encoded content of a request's response
            For the StatsBomb data this is typically a list of dictionaries.
        """
        resp = requests.get(url=url)
        resp.raise_for_status()
        return resp.json()

    def event(self, match_id):
        """ StatsBomb event open-data.

        Parameters
        ----------
        match_id : int

        Returns
        -------
        events, related, freeze, tactics
            Either dataframes or flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbopen
        >>> parser = Sbopen(dataframe=True)
        >>> events, related, freeze, tactics = parser.event(3788741)
        """
        url = f'{self.url}events/{match_id}.json'
        data = self._get_data(url)
        return flatten_event(data, match_id, self.dataframe)

    def lineup(self, match_id):
        """ StatsBomb lineup open-data.

        Parameters
        ----------
        match_id : int

        Returns
        -------
        lineups
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbopen
        >>> parser = Sbopen(dataframe=True)
        >>> lineups = parser.lineup(3788741)
        """
        url = f'{self.url}lineups/{match_id}.json'
        data = self._get_data(url)
        return flatten_lineup(data, match_id, self.dataframe)

    def match(self, competition_id, season_id):
        """ StatsBomb match open-data.

        Parameters
        ----------
        competition_id : int
        season_id : int

        Returns
        -------
        matches
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbopen
        >>> parser = Sbopen(dataframe=True)
        >>> matches = parser.match(11, 1)
        """
        url = f'{self.url}matches/{competition_id}/{season_id}.json'
        data = self._get_data(url)
        return flatten_match(data, self.dataframe)

    def competition(self):
        """ StatsBomb competition open-data.

        Returns
        -------
        competition
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbopen
        >>> parser = Sbopen(dataframe=True)
        >>> competition = parser.competition()
        """
        url = f'{self.url}competitions.json'
        data = self._get_data(url)
        return pd.DataFrame(data) if self.dataframe else data

    def frame(self, match_id):
        """ StatsBomb 360 open-data.

        Parameters
        ----------
        match_id : int

        Returns
        -------
        frames, visible
            Either dataframes or flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbopen
        >>> parser = Sbopen(dataframe=True)
        >>> frames, visible = parser.frame(3788741)
        """
        url = f'{self.url}three-sixty/{match_id}.json'
        data = self._get_data(url)
        return flatten_360(data, match_id, self.dataframe)


class Sbapi:
    """ Class for loading data from the StatsBomb API. You can either set the SB_USERNAME and
    SB_PASSWORD environmental variables or use the username and password arguments.

    Parameters
    ----------
    username : str, default None
        Username for accessing StatsBomb API.
        If None then uses the SB_USERNAME environmental variable.
    password : str, default None
        Password for accessing the StatsBomb API.
        If None then uses the SB_PASSWORD environmental variable.
    dataframe : bool, default True
        Whether to return dataframes (True) or flattened list of dictionaries (False)
        from the class methods.
    """

    def __init__(self, username=None, password=None, dataframe=True):
        if username is None:
            username = os.environ.get("SB_USERNAME")
        if password is None:
            password = os.environ.get("SB_PASSWORD")
        self.auth = requests.auth.HTTPBasicAuth(username, password)
        self.dataframe = dataframe
        self.url = 'https://data.statsbombservices.com/api/v'

    def _get_data(self, url):
        """ Get the StatsBomb data as a list of dictionaries.

        Parameters
        ----------
        url : str

        Returns
        -------
        json-encoded content of a request's response
            For the StatsBomb data this is typically a list of dictionaries.
        """
        resp = requests.get(url=url, auth=self.auth)
        resp.raise_for_status()
        return resp.json()

    def event(self, match_id, version=6):
        """ StatsBomb event data from the API.

        Parameters
        ----------
        match_id : int
        version : int, default 6

        Returns
        -------
        events, related, freeze, tactics
            Either dataframes or flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbapi
        >>> parser = Sbapi(dataframe=True)
        >>> events, related, freeze, tactics = parser.event(3788741)
        """
        url = f'{self.url}{version}/events/{match_id}'
        data = self._get_data(url)
        return flatten_event(data, match_id, self.dataframe)

    def lineup(self, match_id, version=2):
        """ StatsBomb lineup data from the API.

        Parameters
        ----------
        match_id : int
        version : int, default 2

        Returns
        -------
        lineups
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbapi
        >>> parser = Sbapi(dataframe=True)
        >>> lineups = parser.lineup(3788741)
        """
        url = f'{self.url}{version}/lineups/{match_id}'
        data = self._get_data(url)
        return flatten_lineup(data, match_id, self.dataframe)

    def match(self, competition_id, season_id, version=5):
        """ StatsBomb match data from the API.

        Parameters
        ----------
        competition_id : int
        season_id : int
        version : int

        Returns
        -------
        matches
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbapi
        >>> parser = Sbapi(dataframe=True)
        >>> matches = parser.match(11, 1)
        """
        url = f'{self.url}{version}/competitions/{competition_id}/seasons/{season_id}/matches'
        data = self._get_data(url)
        return flatten_match(data, self.dataframe)

    def competition(self, version=4):
        """ StatsBomb competition from the API.

        Parameters
        ----------
        version : int, default 4

        Returns
        -------
        competition
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbapi
        >>> parser = Sbapi(dataframe=True)
        >>> competition = parser.competition()
        """
        url = f'{self.url}{version}/competitions'
        data = self._get_data(url)
        return pd.DataFrame(data) if self.dataframe else data

    def frame(self, match_id, version=1):
        """ StatsBomb 360 data from the API.

        Parameters
        ----------
        match_id : int
        version : int, default 1

        Returns
        -------
        frames, visible
            Either dataframes or flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sbapi
        >>> parser = Sbapi(dataframe=True)
        >>> frames, visible = parser.frame(3788741)
        """
        url = f'{self.url}{version}/360-frames/{match_id}'
        data = self._get_data(url)
        return flatten_360(data, match_id, self.dataframe)


class Sblocal:
    """ Class for loading local StatsBomb data.

    Parameters
    ----------
    dataframe : bool, default True
        Whether to return dataframes (True) or flattened list of dictionaries (False)
        from the class methods.
    """

    def __init__(self, dataframe=True):
        self.dataframe = dataframe

    @staticmethod
    def _get_data(path):
        """ Read the StatsBomb data.

        Parameters
        ----------
        path : path to file

        Returns
        -------
        For the StatsBomb data this typically returns a list of dictionaries.
        """
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
        return data

    def event(self, path):
        """ Read the event data from a local file.

        Parameters
        ----------
        path : path to file

        Returns
        -------
        events, related, freeze, tactics
            Either dataframes or flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sblocal
        >>> parser = Sblocal(dataframe=True)
        >>> events, related, freeze, tactics = parser.event(path)
        """
        data = self._get_data(path)
        match_id = int(os.path.basename(path)[:-5])
        return flatten_event(data, match_id, self.dataframe)

    def lineup(self, path):
        """ Read the lineup data from a local file.

        Parameters
        ----------
        path : path to file

        Returns
        -------
        lineups
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sblocal
        >>> parser = Sblocal(dataframe=True)
        >>> lineups = parser.lineup(path)
        """
        data = self._get_data(path)
        match_id = int(os.path.basename(path)[:-5])
        return flatten_lineup(data, match_id, self.dataframe)

    def match(self, path):
        """ Read the match data from a local file.

        Parameters
        ----------
        path : path to file

        Returns
        -------
        matches
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sblocal
        >>> parser = Sblocal(dataframe=True)
        >>> matches = parser.match(path)
        """
        data = self._get_data(path)
        return flatten_match(data, self.dataframe)

    def competition(self, path):
        """ Read the competition data from a local file.

        Parameters
        ----------
        path : path to file

        Returns
        -------
        competition
            A dataframe or a flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sblocal
        >>> parser = Sblocal(dataframe=True)
        >>> competition = parser.competition(path)
        """
        data = self._get_data(path)
        return pd.DataFrame(data) if self.dataframe else data

    def frame(self, path):
        """ Read the 360 data from a local file.


        Parameters
        ----------
        path : path to file

        Returns
        -------
        frames, visible
            Either dataframes or flattened list of dictionaries.

        Examples
        --------
        >>> from mplsoccer import Sblocal
        >>> parser = Sblocal(dataframe=True)
        >>> frames, visible = parser.frame(path)
        """
        data = self._get_data(path)
        match_id = int(os.path.basename(path)[:-5])
        return flatten_360(data, match_id, self.dataframe)


def _flatten_location(row, value, keyword=''):
    """ Flatten a list of locations into dictionary keys (x, y, z)."""
    if len(value) == 2:
        row[f'{keyword}x'], row[f'{keyword}y'] = value
    elif len(value) == 3:
        row[f'{keyword}x'], row[f'{keyword}y'], row[f'{keyword}z'] = value
    else:
        msg = 'location length not equal to 2 (x, y) or 3 (x, y, z)'
        raise AssertionError(msg)


def _flatten_freeze(data, match_id, event_id):
    """ Flatten the freeze-frame events."""
    for row in data:
        row['match_id'] = match_id
        row['id'] = event_id
        for key in list(row):
            value = row[key]
            if key == 'location':
                _flatten_location(row, value)
                del row['location']
            elif key in ['player', 'position']:
                for nested_key in value:
                    row[f'{key}_{nested_key}'] = value[nested_key]
                del row[key]
    return data


def _flatten_tactic(data, match_id, event_id):
    """ Flatten the tactics events."""
    for row in data:
        row['match_id'] = match_id
        row['id'] = event_id
        for key in list(row):
            if key in ['player', 'position']:
                value = row[key]
                for nested_key in value:
                    row[f'{key}_{nested_key}'] = value[nested_key]
                del row[key]
    return data


def _flatten_list_of_lists(list_of_lists, key):
    """ Flatten a list of lists into a list"""
    flat_list = []
    for sublist in list_of_lists:
        for idx, item in enumerate(sublist):
            item[key] = idx + 1
            flat_list.append(item)
    return flat_list


def _event_dataframe(data):
    """ Transform the event dictionary into a dataframe."""
    df = pd.DataFrame(data)
    if df.empty:
        return None
    mask = df['tactics_formation'].notnull()
    # tactics_formation from float to string
    df.loc[mask, 'tactics_formation'] = df.loc[mask, 'tactics_formation'].astype(int).astype(str)
    df.loc[~mask, 'tactics_formation'] = None
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.time
    df.sort_values(['period', 'timestamp', 'index'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    for col in ['counterpress', 'under_pressure', 'off_camera', 'out']:
        if col in df.columns:
            df[col] = df[col].astype(float)
    return df


def _related_dataframe(data, df_events):
    """ Transform the related-events dictionary into a dataframe. For carries, we also
    ensure that both the carry and the related event are related both ways.
    Sometimes another event is not related to the carry event (but it is the other way round)"""
    df = pd.DataFrame(data)
    if df.empty:
        return None
    cols = ['id', 'index', 'type_name']
    df = df.merge(df_events[cols].rename({'id': 'id_related'}, axis='columns'),
                  how='left', on='id_related', validate='m:1',
                  suffixes=('', '_related'))
    df_carry = df[df['type_name'] == 'Carry'].copy()
    df_carry.rename({'id': 'id_related',
                     'index': 'index_related',
                     'type_name': 'type_name_related',
                     'id_related': 'id',
                     'index_related': 'index',
                     'type_name_related': 'type_name'},
                    axis='columns', inplace=True)
    df = pd.concat([df, df_carry]).drop_duplicates()
    return df


def _competition_dataframe(data):
    """ Format the competition data as a dataframe."""
    df = pd.DataFrame(data)
    date_cols = ['match_updated', 'match_updated_360', 'match_available_360', 'match_available']
    for date in date_cols:
        if date in df.columns:
            df[date] = pd.to_datetime(df[date])
    return df


def _match_dataframe(data):
    """ Format the match data as a dataframe."""
    df = pd.DataFrame(data)
    if df.empty:
        return None
    df['kick_off'] = pd.to_datetime(df['match_date'] + ' ' + df['kick_off'])
    date_cols = ['match_date', 'last_updated', 'last_updated_360',
                 'home_team_managers_dob', 'away_team_managers_dob']
    for date in date_cols:
        if date in df.columns:
            if pd.__version__ < '2':
                df[date] = pd.to_datetime(df[date])
            else:
                df[date] = pd.to_datetime(df[date], format='ISO8601')
    return df


def flatten_event(events, match_id, dataframe=True):
    """ Flatten the events (list) so each row (dictionary) contains no nested events.

    Parameters
    ----------
    events : list of dicts
        The events to flatten.
    match_id : int
        The StatsBomb match identifier.
    dataframe : bool, default True
        Whether to return the results as a dataframe (True)
        or as flattened lists of dictionaries (False)

    Returns
    -------
    events, related, freeze, tactics
        If dataframe=True then returns dataframes else if dataframe=False
        each of the returned values is a list of dictionaries.
    """
    related = []
    freeze = []
    tactics = []
    cols_to_drop = ['pass_through_ball', 'pass_outswinging', 'pass_inswinging', 'clearance_head',
                    'clearance_left_foot', 'clearance_right_foot', 'pass_straight',
                    'clearance_other', 'goalkeeper_punched_out',
                    'goalkeeper_shot_saved_off_target', 'shot_saved_off_target',
                    'goalkeeper_shot_saved_to_post', 'shot_saved_to_post', 'goalkeeper_lost_out',
                    'goalkeeper_lost_in_play', 'goalkeeper_success_out',
                    'goalkeeper_success_in_play', 'goalkeeper_saved_to_post',
                    'shot_kick_off', 'goalkeeper_penalty_saved_to_post']

    for row in events:
        row['match_id'] = match_id
        for key in list(row):
            if isinstance(row[key], dict):
                for nested_key in list(row[key]):
                    nested_value = row[key][nested_key]
                    if nested_key == 'end_location':
                        _flatten_location(row, nested_value, keyword='end_')
                    elif nested_key == 'aerial_won':
                        row[f'{nested_key}'] = nested_value
                    elif nested_key in ['outcome', 'body_part', 'technique', 'aerial_won']:
                        for k in nested_value:
                            row[f'{nested_key}_{k}'] = nested_value[k]
                    elif nested_key == 'freeze_frame':
                        freeze.append(_flatten_freeze(nested_value, match_id, row['id']))
                    elif nested_key == 'lineup':
                        tactics.append(_flatten_tactic(nested_value, match_id, row['id']))
                    elif nested_key == 'type':
                        for k in nested_value:
                            row[f'sub_{nested_key}_{k}'] = nested_value[k]
                    elif isinstance(nested_value, dict):
                        for k in nested_value:
                            row[f'{key}_{nested_key}_{k}'] = nested_value[k]
                    else:
                        row[f'{key}_{nested_key}'] = nested_value
                del row[key]
        if 'location' in row:
            _flatten_location(row, row['location'])
            del row['location']
        row['type_name'] = row['type_name'].replace('Ball Receipt*', 'Ball Receipt')
        # pass through ball is deprecated now, but it was not always added to technique name
        if 'pass_through_ball' in row:
            row['technique_name'] = 'Through Ball'
        for col in cols_to_drop:
            row.pop(col, None)
        if 'related_events' in row:
            related.extend({'match_id': match_id, 'id': row['id'], 'index': row['index'],
                            'type_name': row['type_name'], 'id_related': related_event}
                           for related_event in row['related_events'])

            del row['related_events']
    tactics = _flatten_list_of_lists(tactics, key='event_tactics_id')
    freeze = _flatten_list_of_lists(freeze, key='event_freeze_id')
    if dataframe:
        events = _event_dataframe(events)
        related = _related_dataframe(related, events)
        freeze = pd.DataFrame(freeze)
        tactics = pd.DataFrame(tactics)
    return events, related, freeze, tactics


def flatten_lineup(data, match_id, dataframe=True):
    """ Flatten the lineup (list) so each row (dictionary) contains no nested events.

    Parameters
    ----------
    data : list of dicts
        The lineup to flatten.
    match_id : int
        The StatsBomb match identifier.
    dataframe : bool, default True
        Whether to return the results as a dataframe (True)
        or as flattened lists of dictionaries (False)

    Returns
    -------
    lineups
        If dataframe=True then returns a dataframe else if dataframe=False
        returns a list of dictionaries.
    """
    lineup = []
    for row in data:
        for player in row['lineup']:
            player['match_id'] = match_id
            player['team_id'] = row['team_id']
            player['team_name'] = row['team_name']
            if 'country' in player:
                player['country_id'] = player['country']['id']
                player['country_name'] = player['country']['name']
                del player['country']
            if 'player_nickname' in player and player['player_nickname'] is None:
                player['player_nickname'] = player['player_name']
            player.pop('positions', None)  # if flattened would be multiple lines
            player.pop('cards', None)  # if flattened would be multiple lines
            lineup.append(player)
    if dataframe:
        lineup = pd.DataFrame(lineup)
    return lineup


def flatten_match(match, dataframe=True):
    """ Flatten the match (list) so each row (dictionary) contains no nested events.

    Parameters
    ----------
    match : list of dicts
        The match to flatten.
    dataframe : bool, default True
        Whether to return the results as a dataframe (True)
        or as flattened lists of dictionaries (False)

    Returns
    -------
    matches
        If dataframe=True then returns a dataframe else if dataframe=False
        returns a list of dictionaries.
    """
    for row in match:
        for key in list(row):
            value = row[key]
            if isinstance(value, dict):
                for nested_key in list(value):
                    nested_value = value[nested_key]
                    if isinstance(nested_value, list):
                        nested_value = nested_value[0]
                    if isinstance(nested_value, dict):
                        for k in list(nested_value):
                            if k == 'nickname' and not nested_value[k]:
                                row[f'{key}_{nested_key}_{k}'] = nested_value['name']
                            elif isinstance(nested_value[k], dict):
                                for sub_k in nested_value[k]:
                                    nested_sub_value = nested_value[k][sub_k]
                                    row[f'{key}_{nested_key}_{k}_{sub_k}'] = nested_sub_value
                            else:
                                row[f'{key}_{nested_key}_{k}'] = nested_value[k]
                    elif key in ['competition_stage', 'stadium', 'referee', 'metadata']:
                        row[f'{key}_{nested_key}'] = nested_value
                    else:
                        row[nested_key] = nested_value
                del row[key]
    if dataframe:
        match = _match_dataframe(match)
    return match


def flatten_360(data, match_id, dataframe=True):
    """ Flatten the 360 data (list) so each row (dictionary) contains no nested events.

    Parameters
    ----------
    data : list of dicts
        The 360 data to flatten.
    match_id : int
        The StatsBomb match identifier.
    dataframe : bool, default True
        Whether to return the results as a dataframe (True)
        or as flattened lists of dictionaries (False)

    Returns
    -------
    frames, visible
        If dataframe=True then returns dataframes else if dataframe=False
        each of the returned values is a list of dictionaries.
    """
    frames = []
    visible = []
    for row in data:
        for frame in row['freeze_frame']:
            frame['match_id'] = match_id
            frame['id'] = row['event_uuid']
            _flatten_location(frame, frame['location'])
            del frame['location']
            frames.append(frame)
        frame_visible = {'match_id': match_id,
                         'id': row['event_uuid'],
                         'visible_area': row['visible_area'],
                         }
        visible.append(frame_visible)
    if dataframe:
        frames = pd.DataFrame(frames)
        visible = pd.DataFrame(visible)
    return frames, visible
