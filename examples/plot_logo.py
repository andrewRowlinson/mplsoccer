"""
=========================
Plot a logo for mplsoccer
=========================
"""

from mplsoccer.pitch import Pitch
import matplotlib.patheffects as path_effects

pitch = Pitch(pitch_color='grass', figsize=(16, 9), pad_bottom=-15,
              stripe=True, view='half', orientation='vertical', goal_type='box', linewidth=5, line_color='white')
fig, ax = pitch.draw()
pitch.lines(100, 56, 120, 40, lw=50, comet=True, cmap='jet', transparent=True, ax=ax)
pitch.scatter(97, 56, s=40000, marker='football', edgecolors='black', c='white', lw=3, ax=ax)
text = pitch.annotate('mpl', xy=(95, 27), fontsize=250, c='#eac672', ha='center', va='center', ax=ax)
text.set_path_effects([path_effects.Stroke(linewidth=10, foreground='black'), path_effects.Normal()])
