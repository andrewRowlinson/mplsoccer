"""Tests for mplsoccer.animation: ingestion, the layers' per-frame
updates, channel-mapped styling and animating onto an existing axes."""
import io

import numpy as np
import pandas as pd
import pytest
from matplotlib.animation import writers
import matplotlib.pyplot as plt

from mplsoccer import (Pitch, VerticalPitch, animate, AnimationScatter,
                       AnimationTrail, AnimationArrows, AnimationSurface,
                       AnimationText, AnimationFollow, AnimationScoreboard,
                       GifWriter, halfcircle_marker)
from mplsoccer.animation import Frames

N_FRAMES, N_ENT = 12, 4
IDS = [f'p{e}' for e in range(N_ENT)]


@pytest.fixture
def df():
    rows = [{'frame': f, 'player': f'p{e}', 'jersey': e + 1,
             'x': 20. + f * 3 + e * 5, 'y': 10. + e * 10 + f,
             'speed': float(e + f), 'size': 50. + 20 * e,
             'o': f / 10 + e, 'width': 0.5 + e, 'u': 1.0, 'v': 0.5}
            for f in range(N_FRAMES) for e in range(N_ENT)]
    data = pd.DataFrame(rows)
    # p3 disappears halfway (a substitution / tracking gap)
    data.loc[(data.frame >= 6) & (data.player == 'p3'), ['x', 'y']] = np.nan
    return data


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close('all')


def run(pitch, df, layers, frames=(0, 5, 11), **kwargs):
    kwargs.setdefault('label', 'jersey')
    fig, anim = animate(pitch, df, frame='frame', x='x', y='y',
                        ids='player', layers=layers, **kwargs)
    for i in frames:
        anim._draw_frame(i)
    # blitting marks the layer artists animated, which a plain canvas
    # draw skips; saving renders them, so draw-time errors surface
    fig.savefig(io.BytesIO())
    return layers


@pytest.mark.parametrize('pitch', [Pitch(), VerticalPitch()])
def test_scatter_channels_plain(pitch, df):
    layer, = run(pitch, df, [AnimationScatter(ids=IDS, s='size', hue='speed',
                                              cmap='viridis')])
    coll = layer.collection
    # frame 11 was drawn last: colours and sizes follow the channels
    assert np.allclose(np.ma.filled(coll.get_array(), np.nan),
                       df.loc[df.frame == 11, 'speed'].to_numpy())
    assert np.allclose(coll.get_sizes(), [50, 70, 90, 110])
    # the norm spans every frame, not just the first
    assert coll.norm.vmin == 0 and coll.norm.vmax == N_ENT - 1 + N_FRAMES - 1


def test_scatter_c_stays_a_literal_colour(df):
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, c='red')])
    assert layer.collection.get_array() is None
    assert np.allclose(layer.collection.get_facecolor()[0], (1, 0, 0, 1))


def test_scatter_hue_overrides_color(df):
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, color='red',
                                                hue='speed')])
    assert layer.collection.get_array() is not None


@pytest.mark.parametrize('rotation', [None, 'o'])
def test_scatter_channels_labelled(rotation, df):
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, label=True,
                                                rotation=rotation, s='size',
                                                hue='speed', vmin=0, vmax=20,
                                                labelcolor='white')])
    coll = layer.collection
    faces = coll.get_facecolor()
    assert len(faces) == 2 * N_ENT             # marker then glyph per entity
    assert np.allclose(faces[1::2], (1, 1, 1, 1))  # glyphs keep labelcolor
    expected = layer._hue.cmap(layer._hue.norm(
        df.loc[df.frame == 11, 'speed'].to_numpy()))
    assert np.allclose(faces[0::2], expected)
    assert np.allclose(coll.get_sizes()[0::2], [50, 70, 90, 110])


@pytest.mark.parametrize('kwargs', [{}, {'label': True}, {'rotation': 'o'}])
def test_scatter_paths_share_scatter_defaults_and_aliases(kwargs, df):
    # the same styling means the same thing whichever path draws it
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, color='red',
                                                edgecolors='black',
                                                linewidths=3, **kwargs)])
    coll = layer.collection
    assert np.allclose(np.asarray(coll.get_edgecolor())[0], (0, 0, 0, 1))
    assert np.asarray(coll.get_linewidth())[0] == 3
    with pytest.raises(TypeError, match='aliases'):
        run(Pitch(), df, [AnimationScatter(ids=IDS, ec='k', edgecolor='r',
                                           **kwargs)])


def test_scatter_per_entity_colours_with_label(df):
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, label=True,
                                                color=['r', 'g', 'b', 'k'],
                                                labelcolor='white')])
    faces = layer.collection.get_facecolor()
    assert np.allclose(faces[0], (1, 0, 0, 1)) and np.allclose(faces[2], (0, 0.5, 0, 1))
    assert np.allclose(faces[1::2], (1, 1, 1, 1))


def test_scatter_facecolor_keeps_label_colour(df):
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, label=True,
                                                facecolor='red',
                                                labelcolor='white')])
    assert np.allclose(layer.collection.get_facecolor()[1], (1, 1, 1, 1))


def test_scatter_path_markers_are_normalised_like_string_markers(df):
    # a Path marker goes through MarkerStyle, so s= means the same size
    layer, = run(Pitch(), df, [AnimationScatter(ids=IDS, rotation='o',
                                                marker=halfcircle_marker)])
    assert layer._marker.get_extents().width == pytest.approx(1.0)


def test_scatter_norm_and_vmin_conflict(df):
    from matplotlib.colors import Normalize
    with pytest.raises(ValueError, match='norm='):
        run(Pitch(), df, [AnimationScatter(ids=IDS, hue='speed', vmin=0,
                                           norm=Normalize(0, 1))])


def test_missing_channel_lists_columns(df):
    with pytest.raises(KeyError, match='available columns'):
        run(Pitch(), df, [AnimationScatter(ids=IDS, s='nope')])


def _screen_direction(ax, pitch, x0, y0, x1, y1):
    xy0 = ax.transData.transform(pitch._reverse_if_vertical(np.array([x0]),
                                                            np.array([y0])))
    xy1 = ax.transData.transform(pitch._reverse_if_vertical(np.array([x1]),
                                                            np.array([y1])))
    return np.degrees(np.arctan2(*(xy1 - xy0)[0][::-1]))


def _nose_direction(collection):
    nose = collection.get_paths()[0].vertices[0]      # authored at +y
    return np.degrees(np.arctan2(nose[1], nose[0]))


def _angle_difference(a, b):
    return (a - b + 180) % 360 - 180


@pytest.mark.parametrize('pitch_kwargs', [
    {'pitch_type': 'skillcorner', 'pitch_length': 105, 'pitch_width': 68},
    {'pitch_type': 'statsbomb'}])
@pytest.mark.parametrize('cls', [Pitch, VerticalPitch])
@pytest.mark.parametrize('theta', [0., np.pi / 2, 2.3])
def test_rotation_faces_the_direction_of_motion(cls, pitch_kwargs, theta):
    # the rotation column holds what the pitch's own angle helper returns
    # (degrees clockwise from the direction of play), so inverted y
    # (statsbomb) and vertical pitches leave the marker facing its motion
    pitch = cls(**pitch_kwargs)
    x0, y0 = 50., 40.
    x1, y1 = x0 + 5 * np.cos(theta), y0 + 5 * np.sin(theta)
    degrees, _ = pitch.calculate_angle_and_distance(x0, y0, x1, y1,
                                                    degrees=True)
    data = pd.DataFrame({'frame': [0, 1], 'player': ['a', 'a'],
                         'x': [x0, x1], 'y': [y0, y1], 'o': degrees[0]})
    fig, anim = animate(pitch, data, frame='frame', ids='player',
                        layers=[AnimationScatter(rotation='o')])
    ax = fig.axes[0]
    fig.savefig(io.BytesIO())
    motion = _screen_direction(ax, pitch, x0, y0, x1, y1)
    assert _angle_difference(_nose_direction(ax.collections[-1]),
                             motion) == pytest.approx(0, abs=0.5)


@pytest.mark.parametrize('pitch_type', ['statsbomb', 'opta'])
@pytest.mark.parametrize('cls', [Pitch, VerticalPitch])
@pytest.mark.parametrize('degrees', [0., 90., 215.])
def test_rotation_matches_static_rotation_degrees(cls, pitch_type, degrees):
    # the same number faces the same way in pitch.scatter and animate
    from mplsoccer import arrowhead_marker
    pitch = cls(pitch_type=pitch_type)
    fig, ax = pitch.draw()
    static = pitch.scatter([50.], [40.], rotation_degrees=degrees,
                           marker=arrowhead_marker, ax=ax)
    fig.canvas.draw()
    data = pd.DataFrame({'frame': [0], 'player': ['a'], 'x': [50.],
                         'y': [40.], 'o': [degrees]})
    fig, anim = animate(pitch, data, frame='frame', ids='player',
                        layers=[AnimationScatter(rotation='o')])
    fig.savefig(io.BytesIO())
    animated = fig.axes[0].collections[-1]
    assert _angle_difference(_nose_direction(animated),
                             _nose_direction(static)) == pytest.approx(0, abs=1e-6)


def test_rotation_nan_hides_marker_and_label(df):
    data = df.copy()
    data.loc[(data.player == 'p1') & (data.frame == 11), 'o'] = np.nan
    layer, = run(Pitch(), df if False else data,
                 [AnimationScatter(ids=IDS, rotation='o', label=True)])
    paths = layer.collection.get_paths()
    assert len(paths[2].vertices) == 0 and len(paths[3].vertices) == 0
    assert len(paths[0].vertices) > 0


def test_empty_label_draws_nothing(df):
    # entities missing from a label mapping (the ball) get no label
    layers = run(Pitch(), df, [AnimationScatter(ids=IDS, label=True),
                               AnimationText(ids=IDS, vectorized=True)],
                 label={'p0': 7})
    glyphs = layers[0].collection.get_paths()[1::2]
    assert len(glyphs[0].vertices) > 0
    assert all(len(g.vertices) == 0 for g in glyphs[1:])


def test_label_column_with_nan_formats_whole_numbers(df):
    data = df.assign(jersey=df.jersey.where(df.player != 'p0'))
    layer, = run(Pitch(), data, [AnimationText(ids=IDS)])
    assert [t.get_text() for t in layer.texts] == ['', '2', '3', '4']


def test_layers_are_reusable(df):
    layer = AnimationScatter(ids=IDS, rotation='o', marker=halfcircle_marker,
                             s='size', hue='speed', cmap='plasma', vmin=0,
                             vmax=20, color='red', ec='white', lw=3)
    kwargs = dict(layer.kwargs)
    run(Pitch(), df, [layer])
    run(VerticalPitch(), df, [layer])
    assert layer.kwargs == kwargs
    assert layer._hue.cmap.name == 'plasma' and layer._hue.norm.vmax == 20
    assert layer._s is not None


@pytest.mark.parametrize('pitch', [Pitch(), VerticalPitch()])
def test_trail_channels(pitch, df):
    length = 5
    layer, = run(pitch, df, [AnimationTrail(ids=IDS, length=length, hue='speed',
                                            cmap='plasma', lw='width',
                                            alpha=0.5)])
    coll = layer.collection
    n_seg = N_ENT * (length - 1)
    assert len(coll.get_segments()) == n_seg
    colors = coll.get_colors()
    assert colors.shape == (n_seg, 4)
    # alpha ramps up to 0.5 at the newest segment within each tail
    assert np.allclose(colors[:length - 1, 3],
                       np.linspace(0, 0.5, length)[1:])
    # widths come from the column at each segment's newer end
    assert np.allclose(coll.get_linewidths()[:length - 1], 0.5)
    assert np.allclose(coll.get_linewidths()[-(length - 1):], 3.5)
    # the vanished entity's segments are NaN (not drawn), not stale
    assert np.isnan(coll.get_segments()[-1]).all()


def test_trail_alpha_ramp_array(df):
    ramp = 0.5 * 0.8 ** np.arange(3)[::-1]
    layer, = run(Pitch(), df, [AnimationTrail(ids=IDS, length=4, alpha=ramp,
                                              color='blue')])
    assert np.allclose(layer.collection.get_colors()[:3, 3], ramp)
    with pytest.raises(ValueError, match='oldest first'):
        run(Pitch(), df, [AnimationTrail(ids=IDS, length=4, alpha=[0.1, 0.2])])


def test_trail_constant_colour_unchanged(df):
    layer, = run(Pitch(), df, [AnimationTrail(ids=IDS, length=4, color='blue',
                                              lw=2)])
    colors = layer.collection.get_colors()
    assert np.allclose(colors[:, :3], (0, 0, 1))
    assert np.allclose(layer.collection.get_linewidths(), 2)


def test_arrows_match_pitch_arrows_and_survive_a_missing_first_frame(df):
    data = df.copy()
    data.loc[(data.player == 'p1') & (data.frame < 2), ['x', 'y']] = np.nan
    layer, = run(Pitch(), data, [AnimationArrows(u='u', v='v', ids=IDS,
                                                 width=4)])
    quiver = layer.quiver
    assert quiver.units == 'inches' and quiver.width == pytest.approx(4 / 72)
    # the entity absent at frame 0 (p1) has an arrow once it appears
    assert np.isfinite(quiver.XY[1]).all()


@pytest.mark.parametrize('cls', [Pitch, VerticalPitch])
def test_surface_keeps_the_pitch_aspect(cls, df):
    pitch = cls(pitch_type='opta')
    values = np.zeros((N_FRAMES, 8, 12))
    layer, = run(pitch, df, [AnimationSurface(values, extent=(0, 100, 0, 100))])
    assert layer.im.axes.get_aspect() == pytest.approx(pitch.aspect)
    with pytest.raises(ValueError, match='n_frames'):
        run(pitch, df, [AnimationSurface(values[:3], extent=(0, 100, 0, 100))])


def test_follow_turns_blitting_off(df):
    fig, anim = animate(Pitch(), df, frame='frame', ids='player',
                        layers=[AnimationScatter(ids=IDS)])
    assert anim._blit
    fig, anim = animate(Pitch(), df, frame='frame', ids='player',
                        layers=[AnimationScatter(ids=IDS),
                                AnimationFollow(target=np.full(N_FRAMES, 50.),
                                                width=40)])
    assert not anim._blit


def test_scoreboard_default_sits_inside_the_axes(df):
    layer, = run(Pitch(), df, [AnimationScoreboard(texts='clock')])
    ax = layer.text.axes
    assert ax.bbox.contains(*layer.text.get_window_extent().p0)
    assert ax.bbox.contains(*layer.text.get_window_extent().p1)


def test_gif_writer_is_registered_and_composites_alpha():
    assert writers['mplsoccer_gif'] is GifWriter
    assert not GifWriter()._supports_transparency()


def test_gif_writer_is_smaller_and_takes_the_animation_fps(df, tmp_path):
    from matplotlib.animation import PillowWriter
    from PIL import Image
    pitch = Pitch(pitch_color='grass', stripe=True)
    layers = [AnimationScatter(ids=IDS, color='red')]
    fig, anim = animate(pitch, df, frame='frame', ids='player', fps=20,
                        layers=layers)
    anim.save(tmp_path / 'ours.gif', writer='mplsoccer_gif', dpi=40)
    fig, anim = animate(pitch, df, frame='frame', ids='player', fps=20,
                        layers=layers)
    anim.save(tmp_path / 'pillow.gif', writer=PillowWriter(fps=20), dpi=40)
    # one shared palette lets Pillow store only the changed pixels
    assert (tmp_path / 'ours.gif').stat().st_size < \
        0.5 * (tmp_path / 'pillow.gif').stat().st_size
    with Image.open(tmp_path / 'ours.gif') as im:
        assert im.n_frames == N_FRAMES
        assert im.info['duration'] == 50          # 1000 / fps


def test_row_order_mode_requires_frame_sorted_rows(df):
    sorted_by_frame = df.sort_values(['frame', 'player'])
    block = Frames.from_columns(sorted_by_frame, 'frame', 'x', 'y')
    expected = Frames.from_columns(df, 'frame', 'x', 'y', ids='player')
    assert np.allclose(block.xy, expected.xy, equal_nan=True)
    with pytest.raises(ValueError, match='sorted by frame'):
        Frames.from_columns(df.sort_values(['player', 'frame']), 'frame',
                            'x', 'y')


def test_duplicate_frame_entity_rows_raise(df):
    with pytest.raises(ValueError, match=r"frame=\['period', 'frame'\]"):
        Frames.from_columns(pd.concat([df, df]), 'frame', 'x', 'y',
                            ids='player')


def test_composite_frame_key_and_single_column_list(df):
    halves = pd.concat([df.assign(period=1), df.assign(period=2)])
    block = Frames.from_columns(halves, ['period', 'frame'], 'x', 'y',
                                ids='player')
    assert block.n_frames == 2 * N_FRAMES
    assert block.frame_index[0] == (1, 0) and block.frame_index[-1] == (2, 11)
    block = Frames.from_columns(df, ['frame'], 'x', 'y', ids='player')
    assert block.frame_index[0] == 0          # scalar keys, not 1-tuples


def test_ids_matching_no_entity_raise(df):
    with pytest.raises(ValueError, match='matched 0 of'):
        run(Pitch(), df, [AnimationScatter(ids=[0, 1])])


def test_animate_onto_existing_axes_per_layer(df):
    pitch = Pitch()
    fig, axs = pitch.draw(ncols=2)
    fig_, anim = animate(pitch, df, frame='frame', ids='player', ax=axs[0],
                         layers=[AnimationTrail(ids=IDS[:2], hue='speed'),
                                 AnimationScatter(ids=IDS[2:], hue='speed',
                                                  ax=axs[1])])
    assert fig_ is fig
    trail, scatter = anim._func(3)          # one animation drives both
    assert trail.axes is axs[0] and scatter.axes is axs[1]
    # the figure keeps its layout engine; the animated artists stay out
    assert type(fig.get_layout_engine()).__name__ != 'PlaceHolderLayoutEngine'
    assert not trail.get_in_layout() and not scatter.get_in_layout()


def test_ax_rejects_draw_kws_and_multi_pitch_draw_kws(df):
    pitch = Pitch()
    fig, ax = pitch.draw()
    with pytest.raises(ValueError, match='draw_kws'):
        animate(pitch, df, frame='frame', ids='player', ax=ax,
                layers=[], draw_kws={'figsize': (3, 3)})
    with pytest.raises(ValueError, match='pass ax='):
        animate(pitch, df, frame='frame', ids='player', layers=[],
                draw_kws={'ncols': 2})
