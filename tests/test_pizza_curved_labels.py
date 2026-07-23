"""Tests for curved text on polar axes and curved pizza parameter labels."""

import math

import matplotlib.pyplot as plt
import numpy as np
import pytest

from mplsoccer import CurvedText, PyPizza


def pizza_style_axes(figsize=(4, 4)):
    """A polar axes configured like PyPizza sets it up."""
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rorigin(-20)
    ax.set_rmin(0)
    ax.set_rmax(100)
    return fig, ax


def glyph_geometry(text, ax, center_px):
    """(pixel offset from the arc center, rotation) for each visible glyph."""
    out = []
    for line in text._lines:
        for artist in line.artists:
            if artist is None:
                continue
            px = ax.transData.transform(artist._mplsoccer_position)
            out.append((px - center_px, artist._mplsoccer_rotation))
    return out


def test_pizza_curved_param_labels_smoke():
    params = ['Top', 'Right', 'Bottom', 'Left']
    baker = PyPizza(params=params)
    fig, ax = baker.make_pizza([10, 20, 30, 40], figsize=(4, 4),
                               curved_params=True)
    fig.canvas.draw()

    labels = baker.get_param_texts()
    assert len(labels) == len(params)
    assert all(isinstance(label, CurvedText) for label in labels)
    glyphs = labels[0].get_children()
    assert glyphs
    assert all(hasattr(g, '_mplsoccer_position') for g in glyphs)
    assert all(hasattr(g, '_mplsoccer_rotation') for g in glyphs)

    # the value texts keep using straight Text (they support bbox boxes)
    assert all(not isinstance(t, CurvedText) for t in baker.get_value_texts())
    plt.close(fig)


def test_curved_text_polar_glyphs_on_circle():
    # every glyph must sit at the same pixel distance from the disc center,
    # including when the center is moved by a non-zero origin radius
    fig, ax = pizza_style_axes()
    text = CurvedText(ax, 0.0, 104.0, 'A Long Curving Label', fontsize=12)
    ax.add_artist(text)
    fig.canvas.draw()

    center_px = ax.transData.transform((0.0, ax.get_rorigin()))
    glyphs = glyph_geometry(text, ax, center_px)
    radii = [float(np.hypot(*offset)) for offset, _ in glyphs]
    assert radii
    assert np.ptp(radii) < 1e-6
    plt.close(fig)


def test_curved_text_polar_matches_cartesian():
    # the polar layout must reproduce the Cartesian layout exactly when the
    # arc lands on the same pixels: the pizza-style axes maps radii
    # [rorigin, rmax] = [-20, 100] across the disc, so a circle at r=104
    # equals a Cartesian circle of radius 124 with limits of +-120
    s = 'The quick brown fox jumps over the lazy dog'
    fig_polar, ax_polar = pizza_style_axes()
    text_polar = CurvedText(ax_polar, 0.0, 104.0, s, fontsize=11)
    ax_polar.add_artist(text_polar)
    fig_polar.canvas.draw()
    center_polar = ax_polar.transData.transform((0.0, ax_polar.get_rorigin()))
    glyphs_polar = glyph_geometry(text_polar, ax_polar, center_polar)

    fig_cart, ax_cart = plt.subplots(figsize=(4, 4))
    ax_cart.set_xlim(-120, 120)
    ax_cart.set_ylim(-120, 120)
    ax_cart.set_aspect('equal')
    text_cart = CurvedText(ax_cart, 0.0, 124.0, s, fontsize=11)
    ax_cart.add_artist(text_cart)
    fig_cart.canvas.draw()
    center_cart = ax_cart.transData.transform((0.0, 0.0))
    glyphs_cart = glyph_geometry(text_cart, ax_cart, center_cart)

    assert len(glyphs_polar) == len(glyphs_cart)
    for (offset_p, rot_p), (offset_c, rot_c) in zip(glyphs_polar, glyphs_cart):
        assert np.allclose(offset_p, offset_c, atol=1e-6)
        assert rot_p == pytest.approx(rot_c, abs=1e-9)
    plt.close(fig_polar)
    plt.close(fig_cart)


def test_curved_text_polar_default_orientation():
    # matplotlib's default polar orientation (zero at East, counterclockwise)
    # must also lay glyphs tangent to the circle through the position
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': 'polar'})
    ax.set_rmax(1)
    text = CurvedText(ax, np.pi / 4, 0.9, 'Label', fontsize=12)
    ax.add_artist(text)
    fig.canvas.draw()

    center_px = ax.transData.transform((0.0, ax.get_rorigin()))
    glyphs = glyph_geometry(text, ax, center_px)
    assert glyphs
    for offset, rotation in glyphs:
        # screen angle of the position vector, clockwise from the screen top
        screen_theta = np.degrees(np.arctan2(offset[0], offset[1]))
        # these glyphs sit clockwise of the top of the circle, so they
        # must tilt clockwise by their screen angle (screen_theta) to stay
        # tangent. matplotlib text rotations are counterclockwise-positive,
        # so a clockwise tilt is a negative rotation: rotation is negative
        # while screen_theta is positive, and they cancel. remainder()
        # guards the cancellation: arctan2 confines screen_theta to
        # (-180, 180] but rotation is not normalized, so a perfect glyph
        # can sum to a whole turn (+-360) instead of 0
        mismatch = math.remainder(rotation + screen_theta, 360)
        assert mismatch == pytest.approx(0, abs=1e-6)
    plt.close(fig)


def test_curved_text_polar_center_raises():
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    with pytest.raises(ValueError, match='polar'):
        CurvedText(ax, 0.0, 1.0, 'Label', center=(0, 0))
    plt.close(fig)


def test_pizza_curved_param_labels_bottom_reads_left_to_right():
    params = ['Top', 'Right', 'BottomLabel', 'Left']
    baker = PyPizza(params=params)
    fig, ax = baker.make_pizza([10, 20, 30, 40], figsize=(4, 4),
                               curved_params=True)
    fig.canvas.draw()

    bottom = baker.get_param_texts()[2]
    children = bottom.get_children()
    assert children

    pixel_xs = [ax.transData.transform(child._mplsoccer_position)[0]
                for child in children]
    assert pixel_xs[0] < pixel_xs[-1]  # reading direction is left-to-right

    rotations = [math.remainder(child._mplsoccer_rotation, 360)
                 for child in children]  # wrapped to [-180, 180]
    assert all(-90 <= rot <= 90 for rot in rotations)  # not upside-down
    plt.close(fig)


def test_pizza_curved_param_labels_multiline_uses_multiple_radii():
    params = ['AAA\nBBB', 'Right', 'Bottom', 'Left']
    baker = PyPizza(params=params)
    fig, ax = baker.make_pizza([10, 20, 30, 40], figsize=(4, 4),
                               curved_params=True)
    fig.canvas.draw()

    line_a, line_b = baker.get_param_texts()[0]._lines
    # on polar axes the stashed positions are (theta, radius) data coords
    radii_a = [artist._mplsoccer_position[1]
               for artist in line_a.artists if artist is not None]
    radii_b = [artist._mplsoccer_position[1]
               for artist in line_b.artists if artist is not None]
    assert radii_a
    assert radii_b
    # The first line ("AAA") should be outermost at the top of the chart.
    assert np.mean(radii_a) > np.mean(radii_b)
    plt.close(fig)


def test_pizza_curved_param_labels_mathtext_raises():
    params = [r'$\alpha$ Rating', 'Right', 'Bottom', 'Left']
    baker = PyPizza(params=params)
    with pytest.raises(NotImplementedError, match='mathtext'):
        baker.make_pizza([10, 20, 30, 40], figsize=(4, 4), curved_params=True)
    plt.close('all')


def test_pizza_curved_param_labels_warns_on_ignored_kwargs():
    params = ['Top', 'Right', 'Bottom', 'Left']
    baker = PyPizza(params=params)
    with pytest.warns(UserWarning, match='ignores'):
        baker.make_pizza([10, 20, 30, 40], figsize=(4, 4), curved_params=True,
                         kwargs_params={'va': 'center'})
    plt.close('all')
