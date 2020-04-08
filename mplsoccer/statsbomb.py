""" `mplsoccer` is a python library for plotting soccer / football pitches in Matplotlib. """

# Authors: Andrew Rowlinson, https://twitter.com/numberstorm
# License: MIT

import pandas as pd
import os

def split_location_cols(df, col, new_cols):
    ''' Location is stored as a list. split into columns'''
    if col in df.columns:
        df[new_cols] = df[col].apply(pd.Series)
        df.drop(col,axis=1,inplace=True)
        
def list_dictionary_to_df(df, col, value_name, var_name):
    '''Some columns are a list of dictionaries. This turns them into a new dataframe of rows'''
    df = df.loc[df[col].notnull(),['id',col]]
    df.set_index('id',inplace=True)
    df = df[col].apply(pd.Series).copy()
    df.reset_index(inplace=True)
    df = df.melt(id_vars='id',value_name=value_name,var_name=var_name)
    df[var_name] = df[var_name] + 1
    df = df[df[value_name].notnull()].copy()
    df.reset_index(inplace=True,drop=True)
    return df

def split_dict_col(df,col):
    '''function to split a dictionary column to seperate columns'''
    # handle missings by filling with an empty dictionary
    df[col] = df[col].apply(lambda x: {} if pd.isna(x) else x)
    # split the non missings and change column names
    df_temp_cols = pd.io.json.json_normalize(df[col]).set_index(df.index)
    col_names = df_temp_cols.columns
    # note add column description to column name if doesn't already contain it
    col_names = [(c).replace('.','_') if c[:len(col)]==col else (col+'_'+c).replace('.','_') for c in col_names]
    df[col_names] = df_temp_cols
    # drop old column
    df.drop(col,axis=1,inplace=True)
    return df

def read_event(PATH):
    ''' Extracts individual event jsons and loads as four dataframes: events, related events,
    shot freeze frames, and tactics lineups.'''
    # timestamp defaults to today's date so store as a string - feather can't store time objects
    df = pd.read_json(PATH,encoding='utf-8')
    #df['timestamp'] = df['timestamp'].dt.time.astype(str)
    
    # get match id
    match_id = int(os.path.basename(PATH)[:-5])
    
    # loop through the columns that are still dictionary columns and add them as seperate cols to the dataframe
    # these are nested dataframes in the docs - although dribbled_past/ pressure isn't needed here?
    # also some others are needed: type, possession_team, play_pattern, team, tactics, player, position
    dictionary_columns = ['50_50','bad_behaviour','ball_receipt','ball_recovery','block','carry',
                          'clearance','dribble','duel','foul_committed','foul_won','goalkeeper',
                          'half_end','half_start','injury_stoppage','interception',
                          'miscontrol','pass','play_pattern','player','player_off','position',
                          'possession_team','shot','substitution','tactics','team','type',] 
    for col in dictionary_columns:
        if col in df.columns:
            df = split_dict_col(df,col)
    
    # sort by time and reset index
    df.sort_values(['minute','second','timestamp','possession'],inplace=True)
    df.reset_index(inplace=True,drop=True)
    
    # split location info to x, y and (z for shot) columns and drop old columns
    split_location_cols(df,'location',['x','y'])
    split_location_cols(df,'pass_end_location',['pass_end_x','pass_end_y'])
    split_location_cols(df,'carry_end_location',['carry_end_x','carry_end_y'])
    split_location_cols(df,'shot_end_location',['shot_end_x','shot_end_y','shot_end_z'])
    split_location_cols(df,'goalkeeper_end_location',['goalkeeper_end_x','goalkeeper_end_y'])
    
    # replace weird * character in the type_name for ball receipt
    df['type_name'] = df['type_name'].replace({'Ball Receipt*':'Ball Receipt'})
    
    # create an overall outcome name column from the outcome_name columns
    outcome_name_col = df.columns[df.columns.str.contains('outcome_name')]
    df['outcome_name'] = df.lookup(df.index,df[outcome_name_col].notnull().idxmax(axis=1))
    df.drop(outcome_name_col,axis=1,inplace=True)
    
    # create an overall outcome_id column from the outcome_id columns
    outcome_id_col = df.columns[df.columns.str.contains('outcome_id')]
    df['outcome_id'] = df.lookup(df.index,df[outcome_id_col].notnull().idxmax(axis=1))
    df.drop(outcome_id_col,axis=1,inplace=True)
    
    # create an overall body_part_id column from the body_part_id columns
    body_part_id_col = df.columns[df.columns.str.contains('body_part_id')]
    df['body_part_id'] = df.lookup(df.index,df[body_part_id_col].notnull().idxmax(axis=1))
    df.drop(body_part_id_col,axis=1,inplace=True)
    
    # create an overall body_part_name column from the body_part_name columns
    body_part_name_col = df.columns[df.columns.str.contains('body_part_name')]
    df['body_part_name'] = df.lookup(df.index,df[body_part_name_col].notnull().idxmax(axis=1))
    df.drop(body_part_name_col,axis=1,inplace=True)
    
    # create a related events dataframe
    df_related_events = list_dictionary_to_df(df,col='related_events',
                                              value_name='related_event',var_name='event_related_id')
    # some carries don't have the corresponding events. This makes sure all events are linked both ways
    df_related_events.drop('event_related_id',axis=1,inplace=True)
    df_related_events_reverse = df_related_events.rename({'related_event':'id','id':'related_event'},axis=1)
    df_related_events = pd.concat([df_related_events,df_related_events_reverse],sort=False)
    df_related_events.drop_duplicates(inplace=True)
    # and add on the type_names, index for easier lookups of how the events are related
    df_event_type = df[['id','type_name','index']].copy()
    df_related_events = df_related_events.merge(df_event_type,on='id',how='left',validate='m:1')
    df_event_type.rename({'id':'related_event'},axis=1,inplace=True)
    df_related_events = df_related_events.merge(df_event_type,on='related_event',
                                                 how='left',validate='m:1',suffixes=['','_related'])
    df_related_events.rename({'related_event':'id_related'},axis=1,inplace=True)
    
    # create a shot freeze frame dataframe - also splits dictionary of player details into columns
    df_shot_freeze = list_dictionary_to_df(df,col='shot_freeze_frame',
                                           value_name='player',var_name='event_freeze_id')
    df_shot_freeze = split_dict_col(df_shot_freeze,'player')
    split_location_cols(df_shot_freeze,'player_location',['x','y'])

    # create a tactics lineup frame dataframe - also splits dictionary of player details into columns
    df_tactics_lineup = list_dictionary_to_df(df,col='tactics_lineup',
                                           value_name='player',var_name='event_tactics_id')
    df_tactics_lineup = split_dict_col(df_tactics_lineup,'player')
    
    # drop columns stored as a seperate table 
    df.drop(['related_events','shot_freeze_frame','tactics_lineup'],axis=1,inplace=True)
    
    # add match id to dataframes
    df['match_id'] = match_id
    df_related_events['match_id'] = match_id
    df_shot_freeze['match_id'] = match_id    
    df_tactics_lineup['match_id'] = match_id
    
    return df, df_related_events, df_shot_freeze, df_tactics_lineup
