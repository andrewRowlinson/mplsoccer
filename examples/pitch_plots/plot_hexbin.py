"""
===========
Hexbin plot
===========

This example shows how to plot the location of events occurring in a match
using hexbins.
"""
from urllib.request import urlopen

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from PIL import Image
from highlight_text import ax_text

from mplsoccer import VerticalPitch, add_image, FontManager
from mplsoccer.statsbomb import read_event, EVENT_SLUG

##############################################################################
# load first game that Messi played as a false-9 and the match before
kwargs = {'related_event_df': False, 'shot_freeze_frame_df': False,
          'tactics_lineup_df': False, 'warn': False}
df_false9 = read_event(f'{EVENT_SLUG}/69249.json', **kwargs)['event']
df_before_false9 = read_event(f'{EVENT_SLUG}/69251.json', **kwargs)['event']
# filter messi's actions (starting positions)
df_false9 = df_false9.loc[df_false9.player_id == 5503, ['x', 'y']]
df_before_false9 = df_before_false9.loc[df_before_false9.player_id == 5503, ['x', 'y']]

##############################################################################
# Create a custom colormap
# Note see the Custom colormaps example for more ideas
flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 10 colors",
                                                  ['#e3aca7', '#c03a1d'], N=10)

##############################################################################
# Plot Messi's game before becoming a false-9
pitch = VerticalPitch(line_color='#000009', line_zorder=2, pitch_color='white')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
hexmap = pitch.hexbin(df_before_false9.x, df_before_false9.y, ax=ax, edgecolors='#f4f4f4',
                      gridsize=(8, 8), cmap=flamingo_cmap)

##############################################################################
# Plot Messi's first game as a false-9
pitch = VerticalPitch(line_color='#000009', line_zorder=2, pitch_color='white')
fig, ax = pitch.draw(figsize=(4.4, 6.4))
hexmap = pitch.hexbin(df_false9.x, df_false9.y, ax=ax, edgecolors='#f4f4f4',
                      gridsize=(8, 8), cmap=flamingo_cmap)

# Load the StatsBomb logo and Messi picture
MESSI_URL = 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Messi_vs_Nigeria_2018.jpg'
messi_image = Image.open(urlopen(MESSI_URL))
SB_LOGO_URL = 'https://raw.githubusercontent.com/statsbomb/open-data/master/img/statsbomb-logo.jpg'
sb_logo = Image.open(urlopen(SB_LOGO_URL))

##############################################################################
# Plot Messi's game before and after becoming a false-9
# We will use mplsoccer's grid function, which is a convenient way to plot a grid
# of pitches with a title and endnote axes.

fig, pitch_axs, title_ax, endnote_ax = pitch.grid(ncols=2)
hexmap_before = pitch.hexbin(df_before_false9.x, df_before_false9.y, ax=pitch_axs[0],
                             edgecolors='#f4f4f4',
                             gridsize=(8, 8), cmap='Reds')
hexmap2_after = pitch.hexbin(df_false9.x, df_false9.y, ax=pitch_axs[1], edgecolors='#f4f4f4',
                             gridsize=(8, 8), cmap='Blues')
ax_sb_logo = add_image(sb_logo, fig,
                       # set the left, bottom and height to align with the endnote
                       left=endnote_ax.get_position().x0,
                       bottom=endnote_ax.get_position().y0,
                       height=endnote_ax.get_position().height)
ax_messi = add_image(messi_image, fig, interpolation='hanning',
                     # set the left, bottom and height to align with the title
                     left=title_ax.get_position().x0,
                     bottom=title_ax.get_position().y0,
                     height=title_ax.get_position().height)

# titles using highlight_text and a google font (Robotto)
URL = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
robotto_regular = FontManager(URL)
TITLE_STR1 = 'The Evolution of Lionel Messi'
TITLE_STR2 = 'Actions in the match <before> and\n<after> becoming a False-9'
title1_text = title_ax.text(0.5, 0.7, TITLE_STR1, fontsize=28, color='#000009',
                            fontproperties=robotto_regular.prop,
                            ha='center', va='center')
ax_text(0.5, 0.3, TITLE_STR2, ha='center', va='center', fontsize=18, color='#000009',
        fontproperties=robotto_regular.prop,
        highlight_colors=['#800610', '#08306b'], ax=title_ax)

# turn off title and endnote axes
endnote_ax.axis('off')
title_ax.axis('off')

# Messi Photo from: https://en.wikipedia.org/wiki/Lionel_Messi#/media/File:Messi_vs_Nigeria_2018.jpg
# License: https://creativecommons.org/licenses/by-sa/3.0/;
# Creator: Кирилл Венедиктов

plt.show()  # If you are using a Jupyter notebook you do not need this line
