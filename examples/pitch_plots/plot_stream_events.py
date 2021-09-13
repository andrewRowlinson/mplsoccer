"""
=======================
Plot event stream data
=======================
This example shows how to plot a stream of events occured in a match.
"""

from mplsoccer import Pitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
from matplotlib import rcParams
import pandas as pd
import matplotlib.pyplot as plt


# get event dataframe for game 8650 (Brazil vs Belgium | 2018 FIFA World Cup)
df_game = read_event(f'{EVENT_SLUG}/8650.json',
                     related_event_df=False,
                     shot_freeze_frame_df=False,
                     tactics_lineup_df=True)


##############################################################################
# Load events and players data

# get event data
df_events = df_game['event']

# get players data
players_df = df_game['tactics_lineup'][[
    'player_id', 'player_name', 'player_jersey_number'
]]

players_df = players_df.astype({"player_jersey_number": str})


##############################################################################
# Add jersey number to event data
df_events = df_events.merge(players_df, on='player_id', how='left')
df_events = df_events.merge(players_df,
                            left_on='pass_recipient_id',
                            right_on='player_id',
                            how='left',
                            suffixes=['', '_receipt'])

# fill missing numbers with empty string
df_events.loc[:, 'player_jersey_number'] = df_events.player_jersey_number.fillna('')
df_events.loc[:, 'player_jersey_number_receipt'] = df_events.player_jersey_number_receipt.fillna('')


##############################################################################
# Filter only relevant events (pass, carry and shot) from team1

# extract relevant events for display
events_relevant = ['Pass', 'Carry', 'Shot']


# filter only relevant events from team1
team1, team2 = df_events.team_name.unique()

mask_team1 = (df_events.type_name.isin(events_relevant)) & (df_events.team_name == team1)

df_relevant = df_events.loc[mask_team1, [
    'period', 'second', 'minute', 'player_id', 'x', 'y', 'end_x', 'end_y',
    'type_name', 'outcome_name', 'player_jersey_number',
    'player_jersey_number_receipt'
]].drop_duplicates().reset_index(drop=True)


##############################################################################
# Define function to plot event stream data

def event_stream():
    fig, ax = None, None
    df_shot, df_carry, df_pass = pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([])

    def plot_events():
        """
        Plot events (shots, passes and carries) on the Pitch
        """

        # shots
        pitch.arrows(df_shot.x, df_shot.y,
                     df_shot.end_x, df_shot.end_y,
                     linewidth=3, color=arrows_color, ax=ax,
                     label='shot', zorder=-3,
                     headwidth=5, headlength=5)

        # passes
        pitch.lines(df_pass.x, df_pass.y,
                    df_pass.end_x, df_pass.end_y,
                    linewidth=3, color=arrows_color, ax=ax,
                    label='passes', zorder=-3, comet=True)

        # carry
        for ind, row in df_carry.iterrows():
            ax.plot([row.x, row.end_x], [row.y, row.end_y],
                    color=lines_color, linestyle='--', linewidth=3,
                    label='carry', zorder=-3)


    def plot_players():
        """
        Plot players positions on the Pitch
        """

        # players: pass
        pitch.scatter(df_pass.x, df_pass.y, s=750,
                      c=players_color, ax=ax, label='players',
                      edgecolors=players_edge)
        pitch.scatter(df_pass[~df_pass.next_same_pos].end_x, df_pass[~df_pass.next_same_pos].end_y,
                      s=750, c=players_color, label='players',
                      ax=ax, edgecolors=players_edge)

        # players: carry
        pitch.scatter(df_carry.x, df_carry.y, s=750,
                      c=players_color, ax=ax, label='players',
                      edgecolors=players_edge, alpha=0.6)
        pitch.scatter(df_carry[~df_carry.next_same_pos].end_x, df_carry[~df_carry.next_same_pos].end_y,
                      s=750, c=players_color, label='players',
                      ax=ax, edgecolors=players_edge)
        
        # players: shot
        pitch.scatter(df_shot.x, df_shot.y, s=750,
                      c=players_color, ax=ax, label='players',
                      edgecolors=players_edge)

        
        # players numbers: pass
        for ind, row in df_pass.iterrows():
            ax.annotate(row['player_jersey_number'], (row.x, row.y),
                        weight='bold', ha='center', va='center',
                        fontsize=13)
            if not row.next_same_pos:
                ax.annotate(row['player_jersey_number_receipt'], (row.end_x, row.end_y),
                            weight='bold', ha='center', va='center',
                            fontsize=13)
        
        # players numbers: carry
        for ind, row in df_carry.iterrows():
            ax.annotate(row['player_jersey_number'], (row.x, row.y), weight='bold',
                        ha='center', va='center', fontsize=13,
                        alpha=0.7)
            if not row.next_same_pos:
                ax.annotate(row['player_jersey_number'], (row.end_x, row.end_y), weight='bold',
                            ha='center', va='center', fontsize=13)
        
        # players numbers: shot
        for ind, row in df_shot.iterrows():
            ax.annotate(row['player_jersey_number'], (row.x, row.y), weight='bold',
                        ha='center', va='center', fontsize=13)

            
    def plot_event_stream(df):
        """
        Plot a stream of events
        """
        
        nonlocal fig, ax, df_shot, df_carry, df_pass
        
        # plot empty pitch
        fig, ax = pitch.draw(figsize=(16, 11),
                             constrained_layout=True,
                             tight_layout=False)
        fig.set_facecolor(pitch_color)
        
        # compute extra info
        df.loc[:, 'next_same_pos'] = (df['end_x'] == df.shift(-1)['x']) & (df['end_y'] == df.shift(-1)['y'])
        df.loc[:, 'next_carry'] = list(df.type_name == 'Carry')[1:] + [False]
        df.loc[:, 'next_shot'] = list(df.type_name == 'Shot')[1:] + [False]

        df_pass = df[df.type_name == 'Pass']
        df_shot = df[df.type_name == 'Shot']
        df_carry = df[df.type_name == 'Carry']

        # plot events on the Pitch
        plot_events()
        
        # plot players on the Pitch
        plot_players()

        # remove duplicate legends
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(),
                  facecolor=pitch_color, edgecolor='None',
                  fontsize=17, loc='upper right')

        plt.show()


    # initialize Pitch and respective colors
    rcParams['text.color'] = '#FFFFFF'
    arrows_color = '#FFFF91'
    lines_color = '#FFFF91'
    players_color = '#376BD5'
    players_edge = '#0000FF'
    pitch_color = '#22312B'
    line_color = '#C7D5CC'

    pitch = Pitch(pitch_type='statsbomb',
                  pitch_color=pitch_color,
                  line_color=line_color)

    return plot_event_stream


##############################################################################
# Instantiate the Pitch where events can be plotted

stream = event_stream()


##############################################################################
# Plot a set of events on the Pitch

# example
stream(df_relevant[840:850].copy())
















