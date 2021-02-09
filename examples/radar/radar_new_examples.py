""" Example using refactored Radar."""

from mplsoccer import Radar, FontManager
import matplotlib.pyplot as plt

# fonts for the charts
URL1 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/master/'
        'fonts/SourceSerifPro-Regular.ttf?raw=true')
URL2 = ('https://github.com/googlefonts/SourceSerifProGFVersion/blob/master/'
        'fonts/SourceSerifPro-ExtraLight.ttf?raw=true')
font_params = FontManager(URL1)
font_range = FontManager(URL2)

# inputs
params = ["npxG", "Non-Penalty\n Goals", "xA", "Key\n Passes", "Through\n Balls",
          "Progressive\n Passes",
          "Shot-Creating\n Actions", "Goal-Creating\n Actions", "Dribbles\n Completed",
          "Pressure\n Regains", "Touches\nIn Box"]
values = [0.25, 0.42, 0.42, 3.47, 1.04,  8.06, 5.62, 0.97, 0.56, 5.14, 3.54]
values_compare = [0.32, 0.00, 0.43, 3.50, 0.98,  7.72, 6.18, 0.98, 1.71, 4.88, 4.96]
low = [0.08, 0.00, 0.10, 1.00, 0.60,  4.00, 3.00, 0.30, 0.30, 2.00, 2.00]
high = [0.37, 0.60, 0.60, 4.00, 1.20, 10.00, 8.00, 1.30, 1.50, 5.50, 5.00]

# radar comparison
radar = Radar(params, low, high)
fig, ax = radar.setup_axis()
rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#ffffb2', hatch='//',
                                 linewidths=[1, 3, 5])
radar_output = radar.draw_radar_compare(values, values_compare=values_compare, ax=ax,
                                        kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
                                        kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
radar_poly1, radar_poly2, vertices1, vertices2 = radar_output
range_labels = radar.draw_range_labels(ax=ax, fontproperties=font_range.prop, fontsize=10)
param_labels = radar.draw_param_labels(ax=ax, fontproperties=font_params.prop, fontsize=12)
sc1 = ax.scatter(vertices1[:, 0], vertices1[:, 1], c='#00f2c1', s=80,
                 zorder=3, edgecolors='#01493b')
sc2 = ax.scatter(vertices2[:, 0], vertices2[:, 1], c='#d80499', s=80,
                 zorder=3, edgecolors='#440130')

# just one radar
radar2 = Radar(params, low, high, num_circles=6)
fig_2, ax_2 = radar2.setup_axis()
rings_inner_2 = radar2.draw_circles(ax=ax_2, facecolor='#ffb2b2', edgecolor='#ffffb2',
                                    hatch='//', linewidths=[0, 1, 3, 5])
radar_output = radar2.draw_radar(values, ax=ax_2,
                                 kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
                                 kwargs_rings={'facecolor': '#d80499', 'alpha': 0.6})
radar_poly_2, rings_outer_2, vertices_2 = radar_output
range_labels_2 = radar2.draw_range_labels(ax=ax_2, fontproperties=font_range.prop, fontsize=10)
param_labels_2 = radar2.draw_param_labels(ax=ax_2, fontproperties=font_params.prop, fontsize=12)
sc1_2 = ax_2.scatter(vertices_2[:, 0], vertices_2[:, 1], c='#00f2c1', s=80,
                     edgecolors='#d80499', lw=2, zorder=3)

# show the plots
plt.show()
