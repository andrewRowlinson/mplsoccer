"""
================
Pitch comparison
================
"""
from mplsoccer import Pitch
import matplotlib.pyplot as plt
plt.style.use('dark_background')

fig, axes = plt.subplots(4, 2, figsize=(12, 14))
axes = axes.ravel()
pitch_kwargs = {'line_color': '#94A7AE', 'axis': True, 'label': True, 'pad_left': 0,
                'pad_right': 0, 'pad_top': 0, 'pad_bottom': 0, 'linewidth': 1}
pitch_types = ['statsbomb', 'opta', 'tracab', 'skillcorner', 'wyscout',
               'metricasports', 'uefa', 'custom']
FONTCOLOR = '#b6b9ea'
arrowprops = {'arrowstyle': '->', 'lw': 4,
              'connectionstyle': 'angle3,angleA=0,angleB=-90', 'color': FONTCOLOR}
font_kwargs = {'fontsize': 14, 'ha': 'center', 'va': 'bottom', 'fontweight': 'bold',
               'fontstyle': 'italic', 'c': FONTCOLOR}

for idx, pt in enumerate(pitch_types):
    if pt in ['tracab', 'metricasports', 'custom', 'skillcorner']:
        pitch = Pitch(pitch_type=pt, pitch_length=105, pitch_width=68, **pitch_kwargs)
    else:
        pitch = Pitch(pitch_type=pt, **pitch_kwargs)
    pitch.draw(axes[idx])
    xmin, xmax, ymin, ymax = pitch.extent
    if pitch.dim.aspect != 1:
        TEXT = 'data coordinates \n are square (1:1) \n scale up to a real-pitch size'
        axes[idx].annotate(TEXT, xy=(xmin, ymin), xytext=(0 + (xmax - xmin)/2, ymin),
                           **font_kwargs)
    axes[idx].xaxis.set_ticks([xmin, xmax])
    axes[idx].yaxis.set_ticks([ymin, ymax])
    axes[idx].tick_params(labelsize=15)
    if pt == 'skillcorner':
        axes[idx].set_title('skillcorner / secondspectrum', fontsize=20, c='#9749b9', pad=15)
    else:
        axes[idx].set_title(pt, fontsize=20, c='#9749b9', pad=15)
    if pitch.dim.invert_y:
        TEXT = 'inverted y axis'
        xytext = (0 + (xmax - xmin)/2, ymin + (ymax - ymin)/2)
        axes[idx].annotate(TEXT, xy=(xmin, ymin), xytext=xytext,
                           arrowprops=arrowprops, **font_kwargs)
        axes[idx].annotate(TEXT, xy=(xmin, ymax), xytext=xytext,
                           alpha=0, arrowprops=arrowprops, **font_kwargs)
    if xmin < 0:
        TEXT = ('x and y axes are negative \n starts at -len/2 and -width/2'
                '\n ends at len/2 and width/2.')
        if pt == 'tracab':
            xytext = (0, -1000)
            TEXT = TEXT + '\n dimensions in centimeters'
        else:
            xytext = (0, -10)
            TEXT = TEXT + '\n dimensions in meters'
        axes[idx].annotate(TEXT, xy=(xmin, ymin), xytext=xytext,
                           arrowprops=arrowprops, **font_kwargs)
        axes[idx].annotate(TEXT, xy=(xmax, ymin), xytext=xytext,
                           alpha=0, arrowprops=arrowprops, **font_kwargs)
        axes[idx].annotate(TEXT, xy=(xmin, ymax), xytext=xytext,
                           alpha=0, arrowprops=arrowprops, **font_kwargs)
    if pt == 'custom':
        TEXT = 'decide the pitch dimensions\n via pitch_length and pitch_width'
        xytext = (0 + (xmax - xmin)/2, ymin + (ymax - ymin)/2)
        axes[idx].annotate(TEXT, xy=(xmin, ymax), xytext=xytext,
                           arrowprops=arrowprops, **font_kwargs)
        axes[idx].annotate(TEXT, xy=(xmax, ymin), xytext=xytext,
                           alpha=0, arrowprops=arrowprops, **font_kwargs)
fig.tight_layout()

plt.show()  # If you are using a Jupyter notebook you do not need this line
