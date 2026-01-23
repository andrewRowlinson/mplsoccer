"""
==================
Speedometer Charts
==================

* ``mplsoccer``, ``speedometer`` module helps plot speedometer/gauge charts.

* The speedometer chart is inspired by `znstrider's speedo library
  <https://github.com/znstrider/speedo>`_.

* Speedometer charts are useful for displaying player speed metrics,
  performance scores, or any single value within a defined range.

Here we will show some examples of how to use ``mplsoccer`` to plot speedometer charts.
"""

from mplsoccer import Speedometer
import matplotlib.pyplot as plt

##############################################################################
# Basic Speedometer
# -----------------
# The simplest speedometer just needs a start value, end value, and the current value.

speedo = Speedometer(start_value=0, end_value=12)
fig, ax = speedo.draw(value=8.5)
plt.show()

##############################################################################
# Player Sprint Speed
# -------------------
# A more realistic example showing a player's sprint speed with title and units.

speedo = Speedometer(
    start_value=0,
    end_value=12,
    title="Sprint Speed",
    unit=" m/s",
    title_fontsize=14,
    annotation_fontsize=14,
)
fig, ax = speedo.draw(value=9.2, figsize=(6, 4))
plt.show()

##############################################################################
# Custom Colors
# -------------
# You can customize the color gradient of the speedometer.

speedo = Speedometer(
    start_value=0,
    end_value=100,
    colors=["#2ecc71", "#f1c40f", "#e74c3c"],  # Green -> Yellow -> Red
    segments_per_color=8,
    title="Performance Score",
    unit="%",
)
fig, ax = speedo.draw(value=72)
plt.show()

##############################################################################
# Different Angle Range
# ---------------------
# Change the start and end angles to create different arc shapes.

speedo = Speedometer(
    start_value=0,
    end_value=10,
    start_angle=0,
    end_angle=180,
    title="Half-Circle Gauge",
)
fig, ax = speedo.draw(value=7)
plt.show()

##############################################################################
# Multiple Speedometers
# ---------------------
# Create multiple speedometers in a grid layout.

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

players = [
    ("Mbappé", 9.8),
    ("Haaland", 9.2),
    ("Salah", 8.9),
]

for ax, (name, speed) in zip(axes, players):
    speedo = Speedometer(
        start_value=7,
        end_value=11,
        title=name,
        unit=" m/s",
        title_fontsize=12,
        annotation_fontsize=12,
        label_fontsize=6,
    )
    speedo.draw(value=speed, ax=ax)

fig.suptitle("Top Sprint Speeds", fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

##############################################################################
# Dark Theme
# ----------
# Speedometer on a dark background.

fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1a1a2e')
ax.set_facecolor('#1a1a2e')

speedo = Speedometer(
    start_value=0,
    end_value=100,
    colors=["#e94560", "#f39c12", "#16a085"],
    title="Match Rating",
    title_fontcolor='white',
    label_fontcolor='white',
    annotation_fontcolor='white',
    arc_edgecolor='#1a1a2e',
)
speedo.draw(value=78, ax=ax)
plt.show()
