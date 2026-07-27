""" Test that artists for hidden parts of the pitch (negative pads or half
pitches) are not drawn outside the axes. Inset axes are not clipped by their
parent axes, so out-of-view insets must not be created; text labels are
clipped to the axes."""

import numpy as np
import pytest

from mplsoccer import Pitch, VerticalPitch

PAD = {'pad_left': -25, 'pad_right': -25, 'pad_top': -15, 'pad_bottom': -15}


def sonar_data(num_points=4000):
    rng = np.random.default_rng(3)
    return (rng.uniform(0, 120, num_points), rng.uniform(0, 80, num_points),
            rng.uniform(0, 2 * np.pi, num_points))


def assert_insets_inside(axs, parent):
    """ Assert every created inset axes intersects the parent axes."""
    parent.figure.canvas.draw()  # inset positions are resolved at draw time
    parent_box = parent.get_position()
    for ax_inset in np.ravel(axs):
        if ax_inset is None:
            continue
        inset_box = ax_inset.get_position()
        assert not (inset_box.x1 < parent_box.x0 or inset_box.x0 > parent_box.x1 or
                    inset_box.y1 < parent_box.y0 or inset_box.y0 > parent_box.y1)


def test_negative_pad_sonar_grid():
    """ Test sonar_grid skips grid cells whose centre is outside the view."""
    x, y, angle = sonar_data()
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb', **PAD)
        fig, ax = pitch.draw()
        stats = pitch.bin_statistic_sonar(x, y, angle, bins=(6, 4, 5))
        axs = pitch.sonar_grid(stats, width=12, ax=ax)
        visible = pitch._inset_visible(np.ravel(stats['cx']), np.ravel(stats['cy']), ax)
        assert np.array_equal(np.array([a is not None for a in np.ravel(axs)]), visible)
        assert_insets_inside(axs, ax)
        # opting out restores the previous behaviour of drawing every inset
        fig, ax = pitch.draw()
        axs = pitch.sonar_grid(stats, width=12, exclude_outside=False, ax=ax)
        assert all(a is not None for a in np.ravel(axs))


def test_negative_pad_sonar_zones():
    """ Test sonar_zones skips zones whose centre is outside the view."""
    x, y, angle = sonar_data()
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb', **PAD)
        fig, ax = pitch.draw()
        regions, _ = pitch.positional_zones('full')
        stats = pitch.bin_statistic_sonar_zones(x, y, angle, regions, angle_bins=5)
        axs = pitch.sonar_zones(stats, width=12, ax=ax)
        visible = pitch._inset_visible(stats['cx'], stats['cy'], ax)
        assert np.array_equal(np.array([a is not None for a in axs]), visible)
        assert visible.sum() < len(regions)  # the negative pads hide some zones
        assert_insets_inside(axs, ax)


def test_negative_pad_label_heatmap():
    """ Test the heatmap labels are clipped to the axes."""
    x, y, _ = sonar_data()
    for pitch_class in [Pitch, VerticalPitch]:
        pitch = pitch_class(pitch_type='statsbomb', **PAD)
        fig, ax = pitch.draw()
        stats = pitch.bin_statistic(x, y, bins=(6, 4))
        labels = pitch.label_heatmap(stats, ax=ax, str_format='{:.0f}')
        assert all(annotation.get_clip_on() for annotation in labels)
        # an explicit clip_on=False is respected
        labels = pitch.label_heatmap(stats, ax=ax, str_format='{:.0f}', clip_on=False)
        assert not any(annotation.get_clip_on() for annotation in labels)


def test_half_pitch_formation_insets():
    """ Test formation insets for positions outside a half pitch are not created."""
    pitch = VerticalPitch(pitch_type='opta', half=True)
    fig, ax = pitch.draw()
    axes = pitch.formation('442', kind='axes', height=12, aspect=1, ax=ax)
    assert len(axes) == 11
    assert sum(ax_inset is None for ax_inset in axes.values()) > 0
    assert sum(ax_inset is not None for ax_inset in axes.values()) > 0
    assert_insets_inside(list(axes.values()), ax)
    # on a full pitch every position is drawn
    pitch = VerticalPitch(pitch_type='opta')
    fig, ax = pitch.draw()
    axes = pitch.formation('442', kind='axes', height=12, aspect=1, ax=ax)
    assert all(ax_inset is not None for ax_inset in axes.values())
