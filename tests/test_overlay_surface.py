""" Test the overlay_surface utility and Pitch.overlay_surface method."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import QuadMesh

from mplsoccer import Pitch, VerticalPitch


def test_overlay_surface_returns_quadmesh():
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    surface = np.random.uniform(size=(8, 12))
    mesh = pitch.overlay_surface(surface, ax=ax)
    assert isinstance(mesh, QuadMesh)
    assert mesh.get_array().size == surface.size
    plt.close(fig)


def test_overlay_surface_defaults_to_pitch_extent():
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    mesh = pitch.overlay_surface(np.zeros((4, 6)), ax=ax)
    coords = mesh._coordinates
    xmin, xmax, ymin, ymax = pitch.dim.pitch_extent
    assert np.isclose(coords[..., 0].min(), xmin)
    assert np.isclose(coords[..., 0].max(), xmax)
    assert np.isclose(coords[..., 1].min(), ymin)
    assert np.isclose(coords[..., 1].max(), ymax)
    plt.close(fig)


def test_overlay_surface_vertical_swaps_axes():
    surface = np.random.uniform(size=(4, 6))
    pitch = Pitch(pitch_type='statsbomb')
    fig_h, ax_h = pitch.draw()
    mesh_h = pitch.overlay_surface(surface, ax=ax_h)
    vertical = VerticalPitch(pitch_type='statsbomb')
    fig_v, ax_v = vertical.draw()
    mesh_v = vertical.overlay_surface(surface, ax=ax_v)
    # the x range of the horizontal mesh becomes the y range of the vertical mesh
    assert np.isclose(mesh_h._coordinates[..., 0].max(), mesh_v._coordinates[..., 1].max())
    assert np.isclose(mesh_h._coordinates[..., 1].max(), mesh_v._coordinates[..., 0].max())
    plt.close(fig_h)
    plt.close(fig_v)


def test_overlay_surface_explicit_extent():
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    mesh = pitch.overlay_surface(np.zeros((2, 2)), extent=(60, 120, 0, 40), ax=ax)
    coords = mesh._coordinates
    assert np.isclose(coords[..., 0].min(), 60)
    assert np.isclose(coords[..., 0].max(), 120)
    assert np.isclose(coords[..., 1].max(), 40)
    plt.close(fig)


def test_overlay_surface_rejects_non_2d():
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw()
    with pytest.raises(ValueError):
        pitch.overlay_surface(np.zeros(12), ax=ax)
    plt.close(fig)
