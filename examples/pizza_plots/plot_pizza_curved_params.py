"""
========================
Pizza Plot Curved Labels
========================

This example shows how to draw curved parameter labels on a colorful pizza plot
with multi-color slices.
"""

import matplotlib.pyplot as plt

from mplsoccer import PyPizza

##############################################################################
# Data
# ----

params = [
    "Non-Penalty Goals",
    "npxG",
    "xA",
    "Shot Creating Actions",
    "Penalty Area Entries",
    "Touches per Turnover",
    "Progressive Passes",
    "Progressive Carries",
    "Final 1/3 Passes",
    "Final 1/3 Carries",
    "Pressure Regains",
    "Tackles Made",
]

values = [70, 77, 74, 68, 60, 96, 89, 97, 92, 94, 16, 19]

slice_colors = ["#1A78CF"] * 4 + ["#FF9300"] * 4 + ["#D70232"] * 4
text_colors = ["#000000"] * 8 + ["#F2F2F2"] * 4

##############################################################################
# Plot
# ----

baker = PyPizza(
    params=params,
    background_color="#EBEBE9",
    straight_line_color="#EBEBE9",
    straight_line_lw=1,
    last_circle_lw=0,
    other_circle_lw=0,
    inner_circle_size=20,
)

fig, ax = baker.make_pizza(
    values,
    figsize=(8, 8.5),
    curved_params=True,
    wrap=10,
    color_blank_space="same",
    slice_colors=slice_colors,
    value_colors=text_colors,
    value_bck_colors=slice_colors,
    blank_alpha=0.4,
    kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
    kwargs_params=dict(color="#000000", fontsize=10, va="center"),
    kwargs_values=dict(
        fontsize=10,
        zorder=3,
        bbox=dict(
            edgecolor="#000000",
            facecolor="cornflowerblue",
            boxstyle="round,pad=0.2",
            lw=1,
        ),
    ),
)

fig.text(0.5, 0.98, "Curved parameter labels", ha="center", va="top", fontsize=14)

plt.show()
