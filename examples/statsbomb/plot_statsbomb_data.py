"""
=========
StatsBomb
=========

mplsoccer contains functions to return StatsBomb data in a flat, tidy dataframe.
However, if you want to flatten the json into a dictionary you can also set ``dataframe=False``.

You can read more about the Statsbomb open-data on their
`resource centre <https://www.statsbomb.com/resource-centre>`_ page.

It can be used with the StatBomb `open-data <https://github.com/statsbomb/open-data>`_
or the StatsBomb API if you are lucky enough to have access:

StatsBomb API:

.. code-block:: python

    # this only works if you have access
    # to the StatsBomb API and assumes
    # you have set the environmental
    # variables SB_USERNAME
    # and SB_PASSWORD
    # otherwise pass the arguments:
    # parser = Sbapi(username='changeme',
    # password='changeme')
    from mplsoccer import Sbapi
    parser = Sbapi(dataframe=True)
    (events, related,
    freeze, tactics) = parser.event(3788741)

StatsBomb local data:

.. code-block:: python

    from mplsoccer import Sblocal
    parser = Sblocal(dataframe=True)
    (events, related,
    freeze, tactics) = parser.event(3788741)

Here are some alternatives to mplsoccer's statsbomb module:

- `statsbombapi <https://github.com/Torvaney/statsbombapi>`_
- `statsbombpy <https://github.com/statsbomb/statsbombpy>`_
- `statsbomb-parser <https://github.com/imrankhan17/statsbomb-parser>`_
"""

from mplsoccer import Sbopen

# instantiate a parser object
parser = Sbopen()

##############################################################################
# Competition data
# ----------------
# Get the competition data as a dataframe

df_competition = parser.competition()
df_competition.info()

##############################################################################
#  Match data
# -----------
# Get the match data as a dataframe.
# Note there is a mismatch between the length of this file
# and the number of event files because some event files don't have match data in the open-data.
df_match = parser.match(competition_id=11, season_id=1)
df_match.info()

##############################################################################
# Lineup data
# -----------
df_lineup = parser.lineup(7478)
df_lineup.info()

##############################################################################
# Event data
# ----------
df_event, df_related, df_freeze, df_tactics = parser.event(7478)

# exploring the data
df_event.info()
df_related.info()
df_freeze.info()
df_tactics.info()

##############################################################################
# 360 data
# --------
df_frame, df_visible = parser.frame(3788741)

# exploring the data
df_frame.info()
df_visible.info()
