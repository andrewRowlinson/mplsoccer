"""Tests for curved parameter labels in mplsoccer radar charts."""

import numpy as np
import matplotlib.pyplot as plt
import pytest

from mplsoccer import Radar
from mplsoccer import CurvedText


def test_radar_curved_param_labels_smoke():
    params = ["Top", "Right", "Bottom", "Left"]
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True, fontsize=12)
    fig.canvas.draw()

    assert len(labels) == len(params)
    assert all(isinstance(label, CurvedText) for label in labels)

    # Regression: vector glyph artists expose stable positions/rotations.
    glyphs = labels[0].get_children()
    assert glyphs
    assert all(hasattr(g, "_mplsoccer_char") for g in glyphs)
    assert all(hasattr(g, "_mplsoccer_position") for g in glyphs)
    assert all(hasattr(g, "_mplsoccer_rotation") for g in glyphs)
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

    xs = [child._mplsoccer_position[0] for child in children]
    assert xs[0] < xs[-1]  # reading direction is left-to-right

    rotations = [child._mplsoccer_rotation for child in children]
    rotations = [
        ((rot + 180) % 360) - 180 for rot in rotations
    ]  # normalize to [-180, 180)
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
        float(np.hypot(*child._mplsoccer_position))
        for child in children
        if child._mplsoccer_char == "A"
    ]
    radii_b = [
        float(np.hypot(*child._mplsoccer_position))
        for child in children
        if child._mplsoccer_char == "B"
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
        float(np.hypot(*child._mplsoccer_position))
        for child in children
        if child._mplsoccer_char == "A"
    ]
    radii_b = [
        float(np.hypot(*child._mplsoccer_position))
        for child in children
        if child._mplsoccer_char == "B"
    ]
    assert radii_a
    assert radii_b
    # At the bottom half, the first line ("AAA") should be innermost (closer to the plot).
    assert np.mean(radii_a) < np.mean(radii_b)
    plt.close(fig)


def test_radar_curved_param_labels_mathtext_raises():
    params = [r'$\alpha$ Rating', 'Right', 'Bottom', 'Left']
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    with pytest.raises(NotImplementedError, match='mathtext'):
        radar.draw_param_labels(ax=ax, curved=True)
    plt.close(fig)


def test_radar_curved_param_labels_escaped_dollar_allowed():
    params = [r'Cost \$M', 'Right', 'Bottom', 'Left']
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True)
    fig.canvas.draw()
    assert len(labels) == len(params)
    # the escape renders as a plain '$', not a literal backslash
    chars = [child._mplsoccer_char for child in labels[0].get_children()]
    assert '$' in chars
    assert '\\' not in chars
    plt.close(fig)


def test_radar_curved_param_labels_warns_on_ignored_kwargs():
    params = ['Top', 'Right', 'Bottom', 'Left']
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    with pytest.warns(UserWarning, match='ignores'):
        radar.draw_param_labels(ax=ax, curved=True, rotation=45)
    plt.close(fig)

    # the warning is per-call, not once-per-process: a second chart
    # with a different ignored argument warns again
    fig, ax = radar.setup_axis(figsize=(4, 4))
    with pytest.warns(UserWarning, match='ignores'):
        radar.draw_param_labels(ax=ax, curved=True,
                                bbox={'facecolor': 'yellow'})
    plt.close(fig)


def test_radar_curved_param_labels_horizontal_spokes_deterministic():
    # horizontal spokes (left/right) sit exactly on the flip boundary;
    # the direction must not depend on how the angle was computed
    fig, ax = plt.subplots()
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    thetas_horizontal = [np.pi / 2, 3 * np.pi / 2,          # exact
                         (2 * np.pi / 4) * 3,               # 4 params, left
                         (2 * np.pi / 12) * 3,              # 12 params, right
                         (2 * np.pi / 12) * 9]              # 12 params, left
    for theta in thetas_horizontal:
        label = CurvedText(ax, np.sin(theta), np.cos(theta), 'Label')
        assert label._direction_sign() == 1, theta
    # just below horizontal (bottom half) still flips
    theta = np.pi / 2 + 0.01
    label = CurvedText(ax, np.sin(theta), np.cos(theta), 'Label')
    assert label._direction_sign() == -1
    plt.close(fig)


def test_radar_curved_param_labels_support_text_setters():
    # labels can be restyled after creation like straight Text labels
    params = ['Top', 'Right', 'Bottom', 'Left']
    radar = Radar(params, min_range=[0, 0, 0, 0], max_range=[1, 1, 1, 1])
    fig, ax = radar.setup_axis(figsize=(4, 4))

    labels = radar.draw_param_labels(ax=ax, curved=True, fontsize=12)
    for label in labels:
        label.set_fontsize(20)
        label.set_color('red')
        label.set_alpha(0.5)
    fig.canvas.draw()

    assert labels[0].get_fontsize() == 20
    assert labels[0].get_color() == 'red'
    glyph = labels[0].get_children()[0]
    assert glyph.get_facecolor()[:3] == (1.0, 0.0, 0.0)  # red reached the glyphs
    assert glyph.get_alpha() == 0.5
    plt.close(fig)
