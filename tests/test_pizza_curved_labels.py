"""Tests for curved parameter labels in mplsoccer pizza plots."""

import numpy as np
import matplotlib.pyplot as plt

from mplsoccer import PyPizza
from mplsoccer.curved_text import PolarCurvedText


def test_pizza_curved_param_labels_smoke():
    params = ["Top", "Right", "Bottom", "Left"]
    baker = PyPizza(params)
    fig, ax = baker.make_pizza(
        values=[50, 50, 50, 50],
        curved_params=True,
        kwargs_params={"fontsize": 12},
    )

    fig.canvas.draw()

    labels = baker.get_param_texts()
    assert len(labels) == len(params)
    assert all(isinstance(label, PolarCurvedText) for label in labels)
    plt.close(fig)


def test_pizza_curved_param_labels_bottom_reads_left_to_right():
    params = ["Top", "Right", "BottomLabel", "Left"]
    baker = PyPizza(params)
    fig, ax = baker.make_pizza(
        values=[50, 50, 50, 50],
        curved_params=True,
        wrap=None,
        kwargs_params={"fontsize": 12},
    )

    fig.canvas.draw()

    bottom = baker.get_param_texts()[2]
    children = bottom.get_children()
    assert children

    xs = [ax.transData.transform(child.get_position())[0] for child in children]
    assert xs[0] < xs[-1]  # reading direction is left-to-right

    rotations = [child.get_rotation() for child in children]
    rotations = [((rot + 180) % 360) - 180 for rot in rotations]  # normalize to [-180, 180)
    assert all(-90 <= rot <= 90 for rot in rotations)  # not upside-down
    plt.close(fig)


def test_pizza_curved_param_labels_multiline_uses_multiple_radii():
    params = ["AAA\nBBB", "Right", "Bottom", "Left"]
    baker = PyPizza(params)
    fig, ax = baker.make_pizza(
        values=[50, 50, 50, 50],
        curved_params=True,
        wrap=None,
        kwargs_params={"fontsize": 12},
    )

    fig.canvas.draw()

    label0 = baker.get_param_texts()[0]
    children = label0.get_children()
    radii_a = [child.get_position()[1] for child in children if child.get_text() == "A"]
    radii_b = [child.get_position()[1] for child in children if child.get_text() == "B"]
    assert radii_a
    assert radii_b
    # The first line ("AAA") should be outermost, i.e. on a larger radius.
    assert np.mean(radii_a) > np.mean(radii_b)
    plt.close(fig)


def test_pizza_curved_param_labels_multiline_order_bottom_half():
    params = ["Top", "Right", "AAA\nBBB", "Left"]
    baker = PyPizza(params)
    fig, ax = baker.make_pizza(
        values=[50, 50, 50, 50],
        curved_params=True,
        wrap=None,
        kwargs_params={"fontsize": 12},
    )

    fig.canvas.draw()

    bottom = baker.get_param_texts()[2]
    children = bottom.get_children()
    radii_a = [child.get_position()[1] for child in children if child.get_text() == "A"]
    radii_b = [child.get_position()[1] for child in children if child.get_text() == "B"]
    assert radii_a
    assert radii_b
    # At the bottom half, the first line ("AAA") should be innermost (closer to the plot).
    assert np.mean(radii_a) < np.mean(radii_b)
    plt.close(fig)


def test_pizza_curved_param_labels_wrap_inserts_newlines():
    params = ["AA BB CC", "Right", "Bottom", "Left"]
    baker = PyPizza(params)
    fig, ax = baker.make_pizza(
        values=[50, 50, 50, 50],
        curved_params=True,
        wrap=2,
        kwargs_params={"fontsize": 12},
    )

    fig.canvas.draw()

    label0 = baker.get_param_texts()[0]
    assert label0.get_text().splitlines() == ["AA", "BB", "CC"]
    plt.close(fig)


def test_pizza_curved_param_labels_left_no_rotation_flips():
    params = ["Top", "Right", "Bottom", "Final 1/3 Carries"]
    baker = PyPizza(params)
    fig, ax = baker.make_pizza(
        values=[50, 50, 50, 50],
        curved_params=True,
        wrap=None,
        kwargs_params={"fontsize": 12},
    )

    fig.canvas.draw()

    left = baker.get_param_texts()[3]
    children = left.get_children()
    assert children

    rotations = [((child.get_rotation() + 180) % 360) - 180 for child in children]
    diffs = [
        abs(((rotations[i + 1] - rotations[i] + 180) % 360) - 180)
        for i in range(len(rotations) - 1)
    ]
    assert max(diffs) < 90
    plt.close(fig)
