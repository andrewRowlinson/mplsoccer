"""Tests for curved parameter labels in mplsoccer radar charts."""

import numpy as np
import matplotlib.pyplot as plt

from mplsoccer import Radar
from mplsoccer.curved_text import CurvedText


def test_radar_curved_param_labels_smoke():
    params = ["Top", "Right", "Bottom", "Left"]
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True, fontsize=12)
    fig.canvas.draw()

    assert len(labels) == len(params)
    assert all(isinstance(label, CurvedText) for label in labels)
    plt.close(fig)


def test_radar_curved_param_labels_bottom_reads_left_to_right():
    params = ["Top", "Right", "BottomLabel", "Left"]
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True, wrap=None, fontsize=12)
    fig.canvas.draw()

    bottom = labels[2]
    children = bottom.get_children()
    assert children  # should draw at least one glyph

    xs = [child.get_position()[0] for child in children]
    assert xs[0] < xs[-1]  # reading direction is left-to-right

    rotations = [child.get_rotation() for child in children]
    rotations = [((rot + 180) % 360) - 180 for rot in rotations]  # normalize to [-180, 180)
    assert all(-90 <= rot <= 90 for rot in rotations)  # not upside-down
    plt.close(fig)


def test_radar_curved_param_labels_multiline_uses_multiple_radii():
    params = ["AAA\nBBB", "Right", "Bottom", "Left"]
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True, wrap=None, fontsize=12)
    fig.canvas.draw()

    label0 = labels[0]
    children = label0.get_children()
    radii_a = [
        float(np.hypot(*child.get_position()))
        for child in children
        if child.get_text() == "A"
    ]
    radii_b = [
        float(np.hypot(*child.get_position()))
        for child in children
        if child.get_text() == "B"
    ]
    assert radii_a
    assert radii_b
    # The first line ("AAA") should be outermost, i.e. on a larger radius.
    assert np.mean(radii_a) > np.mean(radii_b)
    plt.close(fig)


def test_radar_curved_param_labels_multiline_order_bottom_half():
    params = ["Top", "Right", "AAA\nBBB", "Left"]
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True, wrap=None, fontsize=12)
    fig.canvas.draw()

    bottom_label = labels[2]
    children = bottom_label.get_children()
    radii_a = [
        float(np.hypot(*child.get_position()))
        for child in children
        if child.get_text() == "A"
    ]
    radii_b = [
        float(np.hypot(*child.get_position()))
        for child in children
        if child.get_text() == "B"
    ]
    assert radii_a
    assert radii_b
    # At the bottom half, the first line ("AAA") should be innermost (closer to the plot).
    assert np.mean(radii_a) < np.mean(radii_b)
    plt.close(fig)
