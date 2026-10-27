"""`mplsoccer.animation` is a Python module for animating
data on a pitch.

It contains a `animate` function that takes a long-form
dataframe and layer classes saying what to draw in each frame."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import transforms
from matplotlib.animation import FuncAnimation, PillowWriter, writers
from matplotlib.path import Path

from .quiver import arrows
from .scatterutils import arrowhead_marker


__all__ = ['animate', 'AnimationScatter', 'AnimationText',
           'AnimationLines', 'AnimationArrows', 'AnimationSurface',
           'AnimationTrail', 'AnimationHull', 'AnimationPolygon',
           'AnimationScoreboard', 'AnimationFollow', 'GifWriter',
           'halfcircle_marker']


def _label_text(value):
    """The label text for one entity: '' for missing values, and
    whole-number floats without the '.0' (a jersey column with NaN for
    the ball is float dtype, so 7 would otherwise read '7.0')."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return ''
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return str(int(value))
    return str(value)


def _frame_keys(data, frame):
    """Each row's frame: the sorted source keys and the row's position in
    them. A list of columns is a composite key whose keys are tuples."""
    if isinstance(frame, (list, tuple)) and len(frame) == 1:
        frame = frame[0]                  # one column: keys stay scalars
    if isinstance(frame, (list, tuple)):
        keys = pd.MultiIndex.from_frame(data[list(frame)])
    else:
        keys = pd.Index(data[frame])
    codes, uniques = keys.factorize(sort=True)
    if (codes < 0).any():
        raise ValueError(f'frame column(s) {frame!r} have missing values.')
    f_index = uniques.to_numpy()
    if isinstance(uniques, pd.MultiIndex):
        f_index = np.empty(len(uniques), dtype=object)
        f_index[:] = list(uniques)        # keep each key a tuple
    return f_index, codes


def _entities_by_row_order(f_index, f_codes):
    """ids=None: an entity is a row's position within its frame, so every
    frame needs the same number of rows and the frames must be sorted."""
    counts = np.bincount(f_codes)
    if counts.min() != counts.max():
        raise ValueError(
            f'frame {f_index[counts.argmin()]} has {counts.min()} rows, '
            f'expected {counts.max()}. Pass ids= to reshape by identity.')
    if np.any(np.diff(f_codes) < 0):
        raise ValueError(
            'with ids=None rows are matched by row order, so the dataframe '
            'must be sorted by frame (each frame\'s rows together, frames '
            'ascending): sort_values(frame) first, or pass ids= to match '
            'rows by identity.')
    n_per_frame = counts.max()
    return np.arange(n_per_frame), np.arange(f_codes.size) % n_per_frame


def _entities_by_id(ids, f_codes):
    """ids=column: the sorted entity ids and each row's position in them;
    a (frame, entity) pair may appear only once."""
    e_codes, e_index = pd.Index(ids).factorize(sort=True)
    pairs = f_codes.astype(np.int64) * e_index.size + e_codes
    n_dup = pairs.size - np.unique(pairs).size
    if n_dup:
        raise ValueError(
            f'{n_dup} rows share a (frame, ids) pair with another row. If '
            'frame numbering restarts (per period or per match) pass frame= '
            "a list of columns, e.g. frame=['period', 'frame'].")
    return e_index.to_numpy(), e_codes


def _scatter(column, codes, n_frames, n_entities):
    """A column as an (n_frames, n_entities) grid, NaN where an entity
    has no row in a frame."""
    grid = np.full((n_frames, n_entities), np.nan)
    grid[codes] = np.asarray(column, dtype=float)
    return grid


def _entity_attrs(data, attrs, e_index, e_codes):
    """Per-entity text from a column (first row wins) or a mapping keyed
    by entity id."""
    out = {}
    first = np.unique(e_codes, return_index=True)[1]
    for name, col in (attrs or {}).items():
        if col is None:
            continue
        if isinstance(col, str):
            values = np.asarray(data[col])[first]
        else:
            if hasattr(col, 'to_dict'):      # pandas Series
                if col.index.has_duplicates:
                    raise ValueError(
                        f'{name}= mapping has duplicate entity ids in its index.')
                mapping = col.to_dict()
            else:
                mapping = dict(col)
            values = [mapping.get(e) for e in e_index]
            if not any(v is not None for v in values):
                ent, key = e_index[0], next(iter(mapping), None)
                raise ValueError(
                    f'{name}= mapping matched 0 of {len(e_index)} entities; '
                    f'entity ids look like {ent!r} ({type(ent).__name__}) but '
                    f'mapping keys look like {key!r} ({type(key).__name__}).')
        out[name] = np.array([_label_text(v) for v in values], dtype=object)
    return out


class Frames:
    """The ingested clip handed to every layer, and to user callables
    ``(frames, i)`` where ``i`` is the 0-based frame position.

    Attributes
    ----------
    xy : ndarray, shape (n_frames, n_entities, 2)
        Positions in the drawn axes' coordinates: on a vertical pitch x
        and y are already swapped (see ``swapped``). NaN where an entity
        has no row in a frame.
    frame_index : ndarray, shape (n_frames,)
        The source frame key of each frame position, in play order
        (sorted; tuples for a composite ``frame=`` key).
    entity_index : ndarray, shape (n_entities,)
        The entity id of each entity position, sorted.
    swapped : bool
        Whether the pitch is vertical, i.e. ``xy`` is (provider y,
        provider x). Geometry a callable returns to a layer is always in
        provider coordinates: the layer swaps it itself.
    """

    def __init__(self, xy, attrs, entity_index, frame_index, source=None,
                 codes=None, swapped=False):
        self.xy = xy
        self.attrs = attrs                # name -> (n_entities,) array
        self.entity_index = entity_index
        self.frame_index = frame_index
        self.swapped = swapped
        self.channels = {}                # name -> (n_frames, n_entities)
        # the source dataframe and each row's (frame, entity) position, so
        # channel columns can be read lazily: a layer names the column and
        # the block scatters it on first access, so the column name appears
        # exactly once, on the layer that consumes it
        self._source = source
        self._codes = codes

    @classmethod
    def from_columns(cls, data, frame, x, y, ids=None, attrs=None):
        if len(data) == 0:
            raise ValueError('data has no rows.')
        f_index, f_codes = _frame_keys(data, frame)
        if ids is None:
            e_index, e_codes = _entities_by_row_order(f_index, f_codes)
        else:
            e_index, e_codes = _entities_by_id(data[ids], f_codes)
        codes = (f_codes, e_codes)
        xy = np.stack([_scatter(data[x], codes, f_index.size, e_index.size),
                       _scatter(data[y], codes, f_index.size, e_index.size)],
                      axis=-1)
        out_attrs = _entity_attrs(data, attrs, e_index, e_codes)
        return cls(xy, out_attrs, e_index, f_index, source=data, codes=codes)

    def select(self, ids):
        """Boolean mask over the entity axis for a layer's ids= subset."""
        if ids is None:
            return np.ones(self.entity_index.size, dtype=bool)
        sel = np.isin(self.entity_index, ids)
        if not sel.any():
            ids = np.atleast_1d(ids)
            raise ValueError(
                f'ids= matched 0 of {self.entity_index.size} entities; '
                f'entity ids look like {self.entity_index[0]!r} '
                f'({type(self.entity_index[0]).__name__}) but the layer\'s '
                f'ids look like {ids[0]!r} ({type(ids[0]).__name__}).')
        return sel

    def attr(self, name, sel):
        """Attr values for a subset, or None if the column wasn't passed."""
        if name in self.attrs:
            return self.attrs[name][sel]
        return None

    def channel(self, name, sel):
        """A channel's full (n_frames, n_selected) time series,
        scattered lazily from the source column on first access."""
        if name not in self.channels:
            if self._source is None or name not in self._source:
                available = (list(self._source.columns)
                             if self._source is not None else [])
                raise KeyError(
                    f'channel {name!r} not found in the data; '
                    f'available columns: {available}')
            self.channels[name] = _scatter(self._source[name], self._codes,
                                           self.n_frames, self.entity_index.size)
        return self.channels[name][:, sel]

    @property
    def n_frames(self):
        return self.xy.shape[0]


# ---------------------------------------------------------------- layers

_EMPTY_PATH = Path(np.empty((0, 2)))


def _ink_centred_glyphs(labels, prop=None):
    """TextPath outlines at size 100, each with its measured ink box
    centred on the origin (the TextPatch idea, points-sized downstream
    via the collection ``sizes`` machinery)."""
    from matplotlib.textpath import TextPath
    paths = []
    for lab in labels:
        if not str(lab).strip():               # no label: draw nothing
            paths.append(_EMPTY_PATH)
            continue
        tp = TextPath((0, 0), str(lab), size=100, prop=prop)
        ink = tp.get_extents()
        centre = transforms.Affine2D().translate(
            -(ink.x0 + ink.x1) / 2, -(ink.y0 + ink.y1) / 2)
        paths.append(centre.transform_path(tp))
    return paths


def _font_kwargs(kwargs):
    """Split the text styling out of ``kwargs``, REMOVING those keys so
    the remainder can be forwarded to a collection untouched. Returns
    the FontProperties and the font size in points (named sizes such as
    'large' resolve through FontProperties, so rcParams apply)."""
    from matplotlib.font_manager import FontProperties
    prop = kwargs.pop('fontproperties', kwargs.pop('font_properties', None))
    prop = FontProperties() if prop is None else prop.copy()
    for setter, keys in ((prop.set_family, ('fontfamily', 'family')),
                         (prop.set_weight, ('fontweight', 'weight')),
                         (prop.set_style, ('fontstyle', 'style')),
                         (prop.set_size, ('fontsize', 'size'))):
        value = kwargs.pop(keys[0], kwargs.pop(keys[1], None))
        if value is not None:
            setter(value)
    return prop, prop.get_size_in_points()


def _pop_cmap_kwargs(kwargs):
    """Remove the colormap kwargs so the rest can be forwarded untouched."""
    return {k: kwargs.pop(k, None) for k in ('cmap', 'norm', 'vmin', 'vmax')}


def _per_entity(values, n, name):
    """``values`` as one row per entity: a single value broadcasts, a
    sequence must have one entry per entity (as ``ax.scatter`` does)."""
    values = np.asarray(values)
    if len(values) == 1:
        return np.repeat(values, n, axis=0)
    if len(values) != n:
        raise ValueError(f'{name}= needs one value or one per entity '
                         f'({n}), got {len(values)}.')
    return values


def _facing(degrees_clockwise, swapped):
    """The screen angle (radians anticlockwise from +x) of a marker
    facing ``degrees_clockwise`` from the direction of play: the rule
    of the static ``scatter_rotation`` (0 is to the right on a
    horizontal pitch and up on a vertical one)."""
    angle = -np.radians(degrees_clockwise)
    return angle + np.pi / 2 if swapped else angle


class _Mapped:
    """A channel mapped through a colormap — the animated analogue of
    ``ax.scatter(c=values, cmap=..., norm=...)``. The norm is fixed over
    ALL frames up front, so a colour means the same thing throughout
    the clip (per-frame autoscaling would recolour every frame)."""

    def __init__(self, values, cmap=None, norm=None, vmin=None, vmax=None):
        from matplotlib import colormaps
        from matplotlib.colors import Normalize
        self.values = values
        self.cmap = colormaps.get_cmap(cmap)
        if norm is None:
            if vmin is None:
                vmin = np.nanmin(values)
            if vmax is None:
                vmax = np.nanmax(values)
            norm = Normalize(vmin=vmin, vmax=vmax)
        elif vmin is not None or vmax is not None:
            raise ValueError('pass norm= or vmin=/vmax=, not both.')
        self.norm = norm

    def rgba(self, values):
        return self.cmap(self.norm(np.ma.masked_invalid(values)))


class AnimationScatter:
    """Animated markers for a group of entities (players / ball /
    referee).

    One layer per visual group (home, away, ball) — marker and zorder
    are per layer, so split groups on those; everything else is plain
    ``ax.scatter`` styling forwarded untouched. Per-frame styling names
    a COLUMN: ``hue='speed'`` colours each marker by that column through
    ``cmap``/``norm`` (seaborn's ``hue``; ``c``/``color`` stay literal
    colours), and ``s='size'`` sizes it in points squared.

    Parameters
    ----------
    ids : list, optional
        Entity ids (values from animate's ``ids=`` column) this layer
        draws. None draws every entity. Ids matching no entity raise.
    label : bool, default False
        Also draw each entity's label (the animate ``label=`` column)
        upright inside its marker. Labels are interleaved into the same
        collection directly after their marker, so a player in front
        occludes the player behind INCLUDING their number — separate
        marker and text layers cannot do that (their z-order is
        layer-level, so an occluded player's number floats up onto the
        circle covering them).
    labelcolor : color, optional
        Label colour, default ``rcParams['text.color']``; pick for
        contrast with the marker face.
    rotation : str, optional
        Name of a per-frame column with each entity's orientation in
        DEGREES CLOCKWISE, 0 = the direction of play (to the right on a
        horizontal pitch, up on a vertical one) — the same convention
        as ``pitch.scatter(rotation_degrees=)``, and what
        ``pitch.calculate_angle_and_distance(..., degrees=True)``
        returns, e.g. from positions and velocities
        ``pitch.calculate_angle_and_distance(x, y, x + vx, y + vy,
        degrees=True)[0]``. NFL Big Data Bowl's ``o``/``dir`` (degrees
        clockwise from +y) convert with ``dir - 90``. The default
        marker becomes mplsoccer's arrowhead (orientation needs a glyph
        with a nose — symmetric markers are 180-degree ambiguous);
        labels stay upright. NaN rotation hides the marker for that
        frame, like NaN positions do.
    hue : str, optional
        A per-frame column to colour each marker by, through ``cmap``/
        ``norm`` (or ``vmin``/``vmax``, fixed over the whole clip) —
        seaborn's ``hue``, so ``c``/``color`` stay literal colours.
        Overrides them.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to the scatter/collection: ``s``, ``color``/``c``,
        ``ec``/``edgecolor``, ``lw``/``linewidth``, ``marker``,
        ``alpha``, ``zorder``; one value, or one per entity as in
        ``ax.scatter``. With label=True also ``fontsize`` and
        ``fontfamily``/``fontweight``/``fontstyle``/``fontproperties``.
        ``s`` may instead name a per-frame column of sizes in points
        squared. Unset styling falls back to rcParams as ``ax.scatter``
        does.

    Examples
    --------
    >>> AnimationScatter(ids=home, s=280, color='#c8102e', ec='black', lw=1,
    ...             label=True, labelcolor='white', fontsize=12, zorder=2)
    >>> AnimationScatter(ids=['ball'], s=40, color='white', ec='black',
    ...             zorder=3)
    >>> AnimationScatter(ids=home, rotation='o', s=200, color='#c8102e',
    ...             label=True, labelcolor='white', zorder=2)
    """

    def __init__(self, ids=None, label=False, labelcolor=None,
                 rotation=None, hue=None, ax=None, **kwargs):
        self.ids = ids
        self.label = label
        self.labelcolor = labelcolor
        self.rotation = rotation
        self.hue = hue
        self.ax = ax
        self.kwargs = kwargs

    def precompute(self, frames):
        self.sel = frames.select(self.ids)
        kwargs = dict(self.kwargs)             # the layer's own stay intact
        self._hue = self._s = self._angles = None
        if self.hue is not None:
            self._hue = _Mapped(frames.channel(self.hue, self.sel),
                                **_pop_cmap_kwargs(kwargs))
            for key in ('c', 'color', 'fc', 'facecolor', 'facecolors'):
                kwargs.pop(key, None)          # hue overrides literal colours
        if isinstance(kwargs.get('s'), str):
            self._s = frames.channel(kwargs.pop('s'), self.sel)
        if self.rotation is not None:
            self._angles = frames.channel(self.rotation, self.sel)
        self._kwargs = kwargs

    def setup(self, ax, frames):
        xy = frames.xy[0, self.sel]
        if self.rotation is None and not self.label:
            return self._setup_scatter(ax, xy)
        return self._setup_paths(ax, frames, xy)

    def _setup_scatter(self, ax, xy):
        kwargs = dict(self._kwargs)
        if self._hue is not None:              # the usual mappable scatter
            kwargs.update(c=self._hue.values[0], cmap=self._hue.cmap,
                          norm=self._hue.norm)
        if self._s is not None:
            kwargs['s'] = np.nan_to_num(self._s[0])
        self.collection = ax.scatter(xy[:, 0], xy[:, 1], **kwargs)
        self._mappable = True
        # a single-path collection hits Agg's marker-stamping fast path,
        # which rounds every marker to whole pixels — gliding markers hop
        # while text glides, so numbers wobble inside their circles.
        # Per-point path copies force the subpixel path renderer; for a
        # single point, pad with an empty path (draws nothing) instead.
        paths = list(self.collection.get_paths())
        if len(xy) > 1:
            self.collection.set_paths(paths * len(xy))
        elif len(xy) == 1:
            self.collection.set_paths(paths + [_EMPTY_PATH])
        return [self.collection]

    def _setup_paths(self, ax, frames, xy):
        """One PathCollection with a path per entity (rotated per frame
        when rotation= is set), each followed by its label glyph when
        label=True."""
        from matplotlib.cbook import normalize_kwargs
        from matplotlib.collections import Collection, PathCollection
        from matplotlib.colors import to_rgba, to_rgba_array
        from matplotlib.markers import MarkerStyle
        n = len(xy)
        # one spelling per property (ec/edgecolors -> edgecolor, ...);
        # conflicting spellings raise, as they do in matplotlib
        kwargs = normalize_kwargs(self._kwargs, Collection)
        prop, fontsize = _font_kwargs(kwargs)
        marker = kwargs.pop('marker', None)
        if marker is None:
            marker = (arrowhead_marker if self.rotation is not None
                      else plt.rcParams['scatter.marker'])
        style = MarkerStyle(marker)
        self._marker = style.get_path().transformed(style.get_transform())
        size = kwargs.pop('s', plt.rcParams['lines.markersize'] ** 2)
        face = kwargs.pop('c', kwargs.pop('color', kwargs.pop('facecolor', None)))
        if face is None:                       # the colour cycle, as scatter
            face = ax._get_patches_for_fill.get_next_color()
        faces = _per_entity(to_rgba_array(face), n, 'color')
        edge = kwargs.pop('edgecolor', plt.rcParams['scatter.edgecolors'])
        edges = (faces if isinstance(edge, str) and edge == 'face'
                 else _per_entity(to_rgba_array(edge), n, 'edgecolor'))
        # scatter leaves filled markers' linewidth to the collection default
        lw = kwargs.pop('linewidth', plt.rcParams['patch.linewidth'])
        self._face = list(faces)
        self._size = list(_per_entity(np.ravel(size).astype(float), n, 's'))
        self._glyphs = self._glyph_size = self._labelcolor = None
        if self.label:
            labels = frames.attr('label', self.sel)
            if labels is None:
                raise ValueError('label=True needs label= passed to animate().')
            self._glyphs = _ink_centred_glyphs(labels, prop)
            self._glyph_size = (fontsize / 100) ** 2
            self._labelcolor = to_rgba(self.labelcolor
                                       if self.labelcolor is not None
                                       else plt.rcParams['text.color'])
        if self._angles is not None:
            self._screen = _facing(self._angles, frames.swapped)
        self.collection = PathCollection(
            self._paths(0), sizes=self._sizes(0), facecolors=self._faces(0),
            edgecolors=self._interleave(edges, 'none'),
            linewidths=self._interleave(
                _per_entity(np.ravel(lw).astype(float), n, 'linewidth'), 0),
            offsets=self._offsets(xy),
            offset_transform=ax.transData,
            transform=transforms.IdentityTransform(),
            **kwargs)                          # alpha, zorder, ... untouched
        self._mappable = False
        ax.add_collection(self.collection, autolim=False)
        return [self.collection]

    def _interleave(self, values, glyph_value):
        """Per-item values: each entity's, then its glyph's if label=True."""
        values = list(values)
        if self._glyphs is None:
            return values
        return [v for value in values for v in (value, glyph_value)]

    def _offsets(self, xy):
        return np.repeat(xy, 2, axis=0) if self._glyphs is not None else xy

    def _paths(self, i):
        n = len(self._face)
        if self._angles is None:
            markers = [self._marker] * n
            shown = np.ones(n, dtype=bool)
        else:
            # markers are authored pointing +y, so rotate by angle - 90
            # degrees; NaN rotation = no orientation info: hide marker
            # (and glyph)
            shown = np.isfinite(self._screen[i])
            markers = [transforms.Affine2D().rotate(a - np.pi / 2)
                       .transform_path(self._marker) if ok else _EMPTY_PATH
                       for a, ok in zip(self._screen[i], shown)]
        if self._glyphs is None:
            return markers
        return [p for k, (m, ok) in enumerate(zip(markers, shown))
                for p in (m, self._glyphs[k] if ok else _EMPTY_PATH)]

    def _sizes(self, i):
        sizes = (list(np.nan_to_num(self._s[i])) if self._s is not None
                 else self._size)
        return self._interleave(sizes, self._glyph_size)

    def _faces(self, i):
        faces = (list(self._hue.rgba(self._hue.values[i]))
                 if self._hue is not None else self._face)
        return self._interleave(faces, self._labelcolor)

    def update(self, i, frames):
        xy = frames.xy[i, self.sel]
        if self._mappable:
            self.collection.set_offsets(xy)
            if self._hue is not None:
                self.collection.set_array(self._hue.values[i])
            if self._s is not None:
                self.collection.set_sizes(np.nan_to_num(self._s[i]))
            return [self.collection]
        if self._angles is not None:
            self.collection.set_paths(self._paths(i))
        self.collection.set_offsets(self._offsets(xy))
        if self._hue is not None or self._s is not None:
            self.collection.set_sizes(self._sizes(i))
            self.collection.set_facecolor(self._faces(i))
        return [self.collection]


def _per_frame(spec, frames, i, default):
    """Resolve a per-frame spec: a callable ``(frames, i)``, a dict
    keyed by source frame id (``default`` for missing frames), or a
    constant used for every frame."""
    if callable(spec):
        return spec(frames, i)
    if isinstance(spec, dict):
        return spec.get(frames.frame_index[i], default)
    return spec


def _vertex_lists(verts, what):
    """Check a layer was given a LIST of (n, 2) arrays, not one array."""
    if isinstance(verts, np.ndarray) and verts.ndim == 2:
        raise ValueError(f'{what} takes a list of (n, 2) arrays per '
                         'frame; wrap a single array in a list.')
    return [np.asarray(v, dtype=float) for v in verts]


class AnimationLines:
    """Animated lines: polylines through entities and/or supplied segments.

    One matplotlib LineCollection; segment and vertex counts may change
    freely per frame. NaN entities break their segment rather than
    drawing to a stale position.

    Parameters
    ----------
    groups : list, dict or callable, optional
        Polylines through ENTITIES, connected in the order given. A
        static list of id-lists (e.g. the banks of a 4-4-2:
        ``[['2', '3', '4', '5'], ['6', '7', '8', '9'], ['10', '11']]``);
        or, for membership that changes mid-clip, a dict
        ``{source frame id: list of id-lists}`` or a callable
        ``(frames, i) -> list of id-lists`` (resolved once up front).
    segments : list, dict or callable, optional
        SUPPLIED geometry — lists of (n, 2) vertex arrays in the same
        three input forms (NFL scrimmage / first-down lines, anything
        not anchored to entities). A separate argument because entity
        ids are often numeric, so ``[11, 12]`` cannot disambiguate "two
        players" from "a point". Coordinates are in the data's own
        system (never read them back from ``frames.xy``, which is
        already swapped on a vertical pitch); the layer swaps them.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to LineCollection: ``colors``, ``linewidths``/``lw``,
        ``alpha``, ``linestyle``, ``zorder``.

    Examples
    --------
    >>> AnimationLines(groups=[['2', '3', '4', '5']], colors='red',
    ...                lw=2, alpha=0.6, zorder=1)
    >>> AnimationLines(segments=[np.array([[35., -1e4], [35., 1e4]])],
    ...                colors='gold', lw=2)
    """

    def __init__(self, groups=None, segments=None, ax=None, **kwargs):
        if groups is None and segments is None:
            raise ValueError('AnimationLines needs groups= and/or segments=.')
        self.groups = groups
        self.segments = segments
        self.ax = ax
        self.kwargs = kwargs
        self._cache = None

    def precompute(self, frames):
        self._pos = {e: k for k, e in enumerate(frames.entity_index)}
        # per-frame groups make this a frame-derived layer (membership
        # depends on every entity in the frame), so the per-frame work
        # runs once here and update() only indexes
        if any(callable(s) or isinstance(s, dict)
               for s in (self.groups, self.segments)):
            self._cache = [self._resolve(frames, i)
                           for i in range(frames.n_frames)]

    def setup(self, ax, frames):
        from matplotlib.collections import LineCollection
        self.collection = LineCollection(self._segments(frames, 0),
                                         **self.kwargs)
        ax.add_collection(self.collection, autolim=False)
        return [self.collection]

    def _rows(self, group):
        try:
            return [self._pos[e] for e in group]
        except KeyError as err:
            ids = list(self._pos)
            raise ValueError(
                f'groups= id {err.args[0]!r} is not an entity id; entity '
                f'ids look like {ids[0]!r} ({type(ids[0]).__name__}).') from None

    def _resolve(self, frames, i):
        segs = []
        if self.groups is not None:
            groups = _per_frame(self.groups, frames, i, [])
            segs += [frames.xy[i, self._rows(grp)] for grp in groups]
        if self.segments is not None:
            supplied = _vertex_lists(
                _per_frame(self.segments, frames, i, []), 'segments=')
            if frames.swapped:
                supplied = [v[:, ::-1] for v in supplied]
            segs += supplied
        return segs

    def _segments(self, frames, i):
        if self._cache is not None:
            return self._cache[i]
        return self._resolve(frames, i)

    def update(self, i, frames):
        self.collection.set_segments(self._segments(frames, i))
        return [self.collection]


class AnimationSurface:
    """An animated surface over the pitch (pitch control and friends).

    One matplotlib AxesImage updated with set_array. The layer draws
    surfaces; it does not implement a model — compute values with your
    own model (or a published one) and pass the result.

    Parameters
    ----------
    values : array or callable
        A precomputed (n_frames, ny, nx) stack, or a callable
        ``(frames, i) -> (ny, nx) array`` resolved once up front. Row 0
        is the row at ``ymin`` of the extent (``np.meshgrid`` order,
        drawn with ``origin='lower'``).
    extent : tuple
        (xmin, xmax, ymin, ymax) of the grid in the data's own
        coordinates; on a vertical pitch the layer transposes the stack
        and swaps the extent itself.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to imshow: ``cmap``, ``norm``, ``alpha``, ``zorder``,
        ``interpolation``. The axes aspect the pitch set is kept unless
        you pass ``aspect``. For contourf-style bands keep the values
        smooth and pass ``norm=BoundaryNorm(levels, 256)`` with
        ``interpolation='bilinear', interpolation_stage='data'`` —
        banding the data itself leaves a blocky compute-grid staircase.

    Examples
    --------
    >>> AnimationSurface(values=control, extent=(-52.5, 52.5, -34, 34),
    ...                  cmap='RdBu', alpha=0.5, zorder=0.7)
    """

    def __init__(self, values, extent, ax=None, **kwargs):
        self.values = values
        self.extent = extent
        self.ax = ax
        self.kwargs = kwargs

    def precompute(self, frames):
        if callable(self.values):
            self._vals = np.stack([self.values(frames, i)
                                   for i in range(frames.n_frames)])
        else:
            self._vals = np.asarray(self.values)
        if self._vals.ndim != 3 or len(self._vals) != frames.n_frames:
            raise ValueError(
                f'values must have shape (n_frames, ny, nx) with n_frames='
                f'{frames.n_frames}; got {self._vals.shape}.')
        # values/extent arrive in provider data space; on a vertical
        # pitch the block is flipped, so the image flips with it
        self._extent = self.extent
        if frames.swapped:
            self._vals = self._vals.transpose(0, 2, 1)
            e = self.extent
            self._extent = (e[2], e[3], e[0], e[1])

    def setup(self, ax, frames):
        # imshow would otherwise reset the aspect the pitch set
        kwargs = {'aspect': ax.get_aspect(), **self.kwargs}
        self.im = ax.imshow(self._vals[0], extent=self._extent,
                            origin='lower', **kwargs)
        return [self.im]

    def update(self, i, frames):
        self.im.set_array(self._vals[i])
        return [self.im]


class AnimationArrows:
    """Animated arrows from supplied vector channels (e.g. velocity).

    One matplotlib Quiver drawn through mplsoccer's ``arrows``, so the
    styling matches ``pitch.arrows``. A pure renderer: deriving velocity
    from positions, smoothing and unit conversion are your job — one
    ``groupby().diff()`` in pandas. NaN components hide that arrow for
    the frame.

    Parameters
    ----------
    u, v : str
        Dataframe columns with the vector components per entity per
        frame (the data's own coordinates; swapped as a pair on
        vertical pitches). Read lazily — no declaration on animate
        needed.
    ids : list, optional
        Entity ids this layer draws. None draws every entity.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to ``pitch.arrows``/quiver: ``color``, ``width`` (shaft
        width in points, default 4), ``headwidth``, ``headlength``,
        ``zorder``. Arrows are in data units (``scale=1``), so the tip
        sits where the entity would be one second ahead.

    Examples
    --------
    >>> AnimationArrows(u='u', v='v', ids=players, color='black',
    ...                 width=2, zorder=1.5)
    """

    def __init__(self, u, v, ids=None, ax=None, **kwargs):
        self.u = u
        self.v = v
        self.ids = ids
        self.ax = ax
        self.kwargs = kwargs

    def precompute(self, frames):
        self.sel = frames.select(self.ids)
        U = frames.channel(self.u, self.sel)
        V = frames.channel(self.v, self.sel)
        if frames.swapped:                   # reflection across y = x
            U, V = V, U
        self._uv = np.stack([U, V], axis=-1)

    def setup(self, ax, frames):
        xy = frames.xy[0, self.sel]
        u, v = self._uv[0, :, 0], self._uv[0, :, 1]
        self.quiver = arrows(xy[:, 0], xy[:, 1], xy[:, 0] + u, xy[:, 1] + v,
                             ax=ax, **self.kwargs)
        return [self.quiver]

    def update(self, i, frames):
        xy = frames.xy[i, self.sel]
        self.quiver.set_offsets(xy)
        # Quiver computes angles from the positions it was created with
        # (XY), which set_offsets does not touch: refresh them so an
        # entity missing at frame 0 still gets its arrow later
        self.quiver.XY = np.asarray(xy)
        self.quiver.set_UVC(self._uv[i, :, 0], self._uv[i, :, 1])
        return [self.quiver]


def _halfcircle_path():
    """Half-disk orientation marker: flat chord = front (facing),
    round side = back. Front-back asymmetric, so unambiguous — and one
    closed path, so no overlapping outlines. Authored pointing +y,
    centred on the player position."""
    arc = Path.arc(180, 360)
    verts = np.concatenate([arc.vertices, [arc.vertices[0]]])
    codes = np.concatenate([arc.codes, [Path.CLOSEPOLY]])
    return Path(verts, codes).transformed(
        transforms.Affine2D().translate(0, 0.5))


halfcircle_marker = _halfcircle_path()


class AnimationTrail:
    """Fading comet tails: each entity's path over the recent past.

    One matplotlib LineCollection with a fixed segment count; the alpha
    ramp (faint old -> ``alpha`` new) is built once, so updates only
    move segments. Trails grow in from nothing at the clip start, and
    an absent entity's tail ages away naturally instead of leaving a
    stub.

    Parameters
    ----------
    ids : list, optional
        Entity ids this layer draws. None draws every entity.
    length : int, default 25
        Tail length in frames (e.g. 2 seconds of 25 fps data = 50).
    color : color, optional
        Tail colour, default ``rcParams['lines.color']``; one trail
        layer per visual group, like scatter.
    alpha : float or array, default 0.8
        Opacity at the newest end of the tail, ramping linearly down to
        ``alpha / (length - 1)`` at the old end. Or the whole ramp:
        ``length - 1`` values, oldest segment first — e.g. a
        canvas-style exponential fade
        ``0.5 * 0.85 ** np.arange(length - 1)[::-1]`` keeps a bright
        head and a long faint tail.
    hue : str, optional
        A per-frame column to colour each tail SEGMENT by, through
        ``cmap``/``norm`` (or ``vmin``/``vmax``, fixed over the whole
        clip) — a speed channel paints a trail by how fast the entity
        was moving at that point. Overrides ``color``; the alpha ramp
        still applies.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to LineCollection: ``linewidths``/``lw``, ``zorder``.
        ``lw`` may instead name a per-frame column of widths in points.

    Examples
    --------
    >>> AnimationTrail(ids=home, length=30, color='red', lw=2, zorder=1)
    >>> AnimationTrail(ids=home, length=30, hue='speed', cmap='plasma',
    ...                vmin=0, vmax=8, lw='width', zorder=1)
    """

    def __init__(self, ids=None, length=25, color=None, alpha=0.8, hue=None,
                 ax=None, **kwargs):
        self.ids = ids
        self.length = length
        self.color = color
        self.alpha = alpha
        self.hue = hue
        self.ax = ax
        self.kwargs = kwargs

    def precompute(self, frames):
        self.sel = frames.select(self.ids)
        kwargs = dict(self.kwargs)
        self._hue = self._lw = None
        if self.hue is not None:
            self._hue = _Mapped(frames.channel(self.hue, self.sel),
                                **_pop_cmap_kwargs(kwargs))
        for key in ('lw', 'linewidth', 'linewidths'):
            if isinstance(kwargs.get(key), str):
                self._lw = frames.channel(kwargs.pop(key), self.sel)
        self._kwargs = kwargs

    def _window(self, values, i):
        """The last ``length`` frames of a (n_frames, ...) array, NaN
        padded at the old end so trails grow in at the clip start."""
        n = self.length
        w = values[max(0, i - n + 1):i + 1]
        if len(w) < n:
            pad = np.full((n - len(w),) + w.shape[1:], np.nan)
            w = np.concatenate([pad, w], axis=0)
        return w

    def _segments(self, frames, i):
        # window first: selecting first would copy the whole clip each frame
        w = self._window(frames.xy, i)[:, self.sel]
        segs = np.stack([w[:-1], w[1:]], axis=2)     # (n-1, ents, 2, 2)
        return segs.transpose(1, 0, 2, 3).reshape(-1, 2, 2)

    def _per_segment(self, channel, i):
        """A channel at each segment's newer end, in segment order."""
        return self._window(channel, i)[1:].T.ravel()

    def _colors(self, i):
        rgba = self._hue.rgba(self._per_segment(self._hue.values, i))
        rgba[:, 3] *= np.tile(self._ramp, self._n_ent)
        return rgba

    def setup(self, ax, frames):
        from matplotlib.collections import LineCollection
        from matplotlib.colors import to_rgba
        self._n_ent = int(self.sel.sum())
        if np.ndim(self.alpha) == 0:
            self._ramp = np.linspace(0.0, self.alpha, self.length)[1:]
        else:
            self._ramp = np.asarray(self.alpha, dtype=float)
            if self._ramp.shape != (self.length - 1,):
                raise ValueError(
                    f'alpha= ramp needs length - 1 = {self.length - 1} '
                    f'values (oldest first), got {self._ramp.shape}.')
        kwargs = dict(self._kwargs)
        color = kwargs.pop('colors', self.color)
        if self._hue is not None:
            colors = self._colors(0)
        else:                                # the ramp is built once
            base = to_rgba(plt.rcParams['lines.color'] if color is None
                           else color)
            colors = np.tile(np.column_stack(
                [np.tile(base[:3], (self.length - 1, 1)), self._ramp]),
                (self._n_ent, 1))
        if self._lw is not None:
            kwargs['linewidths'] = np.nan_to_num(self._per_segment(self._lw, 0))
        self.collection = LineCollection(self._segments(frames, 0),
                                         colors=colors, **kwargs)
        ax.add_collection(self.collection, autolim=False)
        return [self.collection]

    def update(self, i, frames):
        self.collection.set_segments(self._segments(frames, i))
        if self._hue is not None:
            self.collection.set_color(self._colors(i))
        if self._lw is not None:
            self.collection.set_linewidths(
                np.nan_to_num(self._per_segment(self._lw, i)))
        return [self.collection]


class AnimationFollow:
    """A moving view window that follows the action (broadcast camera).

    A VIEW layer: it draws nothing — each frame it slides the axes
    limits along the pitch length so the window is centred on your
    target. The camera path is data you supply: smooth it for inertia
    and clamp it to the pitch, e.g.
    ``np.clip(gaussian_filter1d(ball_x, 20), -52.5 + w/2, 52.5 - w/2)``.
    Size the figure for the window (``width`` by the pitch width plus
    padding), not the whole pitch, or the figure is letterboxed.

    Parameters
    ----------
    target : array, dict or callable
        Window centre in the data's own x per frame: an array aligned
        with the frames, a dict ``{source frame id: x}``, or a callable
        ``(frames, i)``. NaN (or None) freezes the camera in place.
    width : float
        Window size along the pitch length, in pitch units. Keep it
        constant or the figure aspect breathes.
    ax : matplotlib.axes.Axes, optional
        Follow on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).

    Examples
    --------
    >>> AnimationFollow(target=camera_path, width=44)
    """

    # moving the limits invalidates the background that blitting caches,
    # so animate() turns blitting off when this layer is present
    blit_safe = False

    def __init__(self, target, width, ax=None):
        self.target = target
        self.width = width
        self.ax = ax

    def precompute(self, frames):
        if not callable(self.target) and not isinstance(self.target, dict):
            self._target = np.asarray(self.target, dtype=float)
            if len(self._target) != frames.n_frames:
                raise ValueError(
                    f'target has {len(self._target)} values, the clip has '
                    f'{frames.n_frames} frames.')

    def setup(self, ax, frames):
        self._ax = ax
        self._vertical = frames.swapped
        lims = ax.get_ylim() if self._vertical else ax.get_xlim()
        self._sign = 1 if lims[1] > lims[0] else -1
        self.update(0, frames)
        return []

    def _centre(self, frames, i):
        if callable(self.target) or isinstance(self.target, dict):
            return _per_frame(self.target, frames, i, np.nan)
        return self._target[i]

    def update(self, i, frames):
        cx = self._centre(frames, i)
        if cx is not None and np.isfinite(cx):
            half = self._sign * self.width / 2
            if self._vertical:
                self._ax.set_ylim(cx - half, cx + half)
            else:
                self._ax.set_xlim(cx - half, cx + half)
        return []


class AnimationScoreboard:
    """Per-frame text at a fixed screen position: clock, score,
    down-and-distance — and despite the name, any text that changes per
    frame (status lines, narration).

    One matplotlib Text anchored in axes coordinates, so it sits in the
    same screen position on horizontal and vertical pitches.

    Parameters
    ----------
    texts : str, array, dict or callable
        The string per frame: a constant string, an array aligned with
        the frames, a dict ``{source frame id: str}`` (missing frames
        show nothing), or a callable ``(frames, i) -> str``.
    xy : tuple, default (0.02, 0.98)
        Position in axes fractions ((0, 0) = bottom left of the pitch
        axes), top left by default. Keep it inside the axes: live
        playback redraws only the axes area, so text outside it would
        not update (``pad_top`` on the pitch makes room inside).
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to the Text: ``fontsize``, ``color``, ``ha``/``va``
        (default 'left'/'top'), ``fontweight``.

    Examples
    --------
    >>> clock = dict(zip(df['frame_id'], df['timestamp'].astype(str)))
    >>> AnimationScoreboard(texts=clock, fontsize=12, fontweight='bold')
    """

    def __init__(self, texts, xy=(0.02, 0.98), ax=None, **kwargs):
        self.texts = texts
        self.xy = xy
        self.ax = ax
        self.kwargs = kwargs

    def precompute(self, frames):
        if (not callable(self.texts) and not isinstance(self.texts, (dict, str))
                and len(self.texts) != frames.n_frames):
            raise ValueError(f'texts has {len(self.texts)} entries, the clip '
                             f'has {frames.n_frames} frames.')

    def _resolve(self, frames, i):
        if callable(self.texts) or isinstance(self.texts, (dict, str)):
            return _per_frame(self.texts, frames, i, '')
        return str(np.asarray(self.texts)[i])

    def setup(self, ax, frames):
        kwargs = {'transform': ax.transAxes, 'ha': 'left', 'va': 'top',
                  **self.kwargs}
        self.text = ax.text(*self.xy, self._resolve(frames, 0), **kwargs)
        return [self.text]

    def update(self, i, frames):
        self.text.set_text(self._resolve(frames, i))
        return [self.text]


class AnimationHull:
    """Animated convex hull around a group of entities — how much pitch
    a team occupies (the animated plot_convex_hull).

    One matplotlib PolyCollection recomputed per frame. NaN entities
    drop out (a red card visibly shrinks the area); fewer than three
    finite points draws nothing. Exclude the keeper or the hull
    stretches to the goal line.

    Parameters
    ----------
    ids : list, optional
        Entity ids forming the hull. None uses every entity.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to PolyCollection: ``facecolor``, ``edgecolor``,
        ``alpha``, ``linewidths``/``lw``, ``zorder``.

    Examples
    --------
    >>> AnimationHull(ids=outfield, facecolor='red', edgecolor='red',
    ...               alpha=0.2, zorder=1)
    """

    def __init__(self, ids=None, ax=None, **kwargs):
        self.ids = ids
        self.ax = ax
        self.kwargs = kwargs

    def setup(self, ax, frames):
        from matplotlib.collections import PolyCollection
        self.sel = frames.select(self.ids)
        self.collection = PolyCollection([self._verts(frames, 0)],
                                         **self.kwargs)
        ax.add_collection(self.collection, autolim=False)
        return [self.collection]

    def _verts(self, frames, i):
        from scipy.spatial import ConvexHull, QhullError
        xy = frames.xy[i, self.sel]
        xy = xy[np.isfinite(xy).all(axis=1)]
        if len(xy) < 3:
            return np.empty((0, 2))
        try:
            return xy[ConvexHull(xy).vertices]
        except QhullError:                     # e.g. collinear players
            return np.empty((0, 2))

    def update(self, i, frames):
        self.collection.set_verts([self._verts(frames, i)])
        return [self.collection]


class AnimationPolygon:
    """Animated polygons with supplied geometry — e.g. the broadcast
    camera's visible-pitch footprint that some providers ship
    (SkillCorner's ``image_corners_projection``).

    One matplotlib PolyCollection. Frames with no entry draw nothing
    (replays and close-ups have no projection). Geometry is in the
    data's own coordinates (never read it back from ``frames.xy``,
    which is already swapped on a vertical pitch); the layer swaps it.

    Parameters
    ----------
    polys : list, dict or callable
        Lists of (n, 2) vertex arrays: a static list, a dict
        ``{source frame id: list of arrays}``, or a callable
        ``(frames, i)`` (resolved once up front).
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Forwarded to PolyCollection: ``facecolor``, ``edgecolor``,
        ``alpha``, ``zorder``.

    Examples
    --------
    >>> AnimationPolygon(polys=camera_footprints, facecolor='0.7',
    ...                  alpha=0.3, zorder=0.5)
    """

    def __init__(self, polys, ax=None, **kwargs):
        self.polys = polys
        self.ax = ax
        self.kwargs = kwargs
        self._cache = None

    def precompute(self, frames):
        if callable(self.polys) or isinstance(self.polys, dict):
            self._cache = [self._resolve(frames, i)
                           for i in range(frames.n_frames)]

    def _resolve(self, frames, i):
        verts = _vertex_lists(_per_frame(self.polys, frames, i, []), 'polys=')
        if frames.swapped:
            verts = [v[:, ::-1] for v in verts]
        return verts

    def _verts(self, frames, i):
        return self._cache[i] if self._cache is not None \
            else self._resolve(frames, i)

    def setup(self, ax, frames):
        from matplotlib.collections import PolyCollection
        self.collection = PolyCollection(self._verts(frames, 0),
                                         **self.kwargs)
        ax.add_collection(self.collection, autolim=False)
        return [self.collection]

    def update(self, i, frames):
        self.collection.set_verts(self._verts(frames, i))
        return [self.collection]


class AnimationText:
    """Animated per-entity text at the entity positions — labels beside
    markers. For numbers INSIDE markers use
    ``AnimationScatter(label=True)`` instead (it occludes correctly);
    for per-frame text use ``AnimationScoreboard``.

    Strings come from animate's ``label=`` and are constant per entity
    (one label per entity per animation, shared with
    ``AnimationScatter(label=True)``).

    Parameters
    ----------
    ids : list, optional
        Entity ids this layer draws. None draws every entity.
    dx, dy : float, default 0
        Nudge in points, display space — for placing labels beside
        markers (composes correctly with vertical pitches).
    vectorized : bool, default False
        Draw glyph outlines in one collection instead of Text artists:
        subpixel motion in lockstep with markers, at the cost of font
        hinting at small sizes. Glyphs are ink-centred on the (nudged)
        position, so ``ha``/``va`` do not apply.
    ax : matplotlib.axes.Axes, optional
        Draw on this axes instead of the one animate draws on — for
        several pitches in one figure (see ``animate(ax=)``).
    **kwargs
        Text styling: ``fontsize``, ``color``, ``ha``/``va``,
        ``fontweight``, ``alpha``; unset values fall back to rcParams.

    Examples
    --------
    >>> AnimationText(ids=home, dy=-10, color='black', fontsize=8)
    """

    def __init__(self, ids=None, dx=0, dy=0, vectorized=False, ax=None,
                 **kwargs):
        self.ids = ids
        self.dx = dx
        self.dy = dy
        self.vectorized = vectorized
        self.ax = ax
        self.kwargs = kwargs

    def _offset_transform(self, ax):
        if self.dx or self.dy:
            return transforms.offset_copy(ax.transData, fig=ax.figure,
                                          x=self.dx, y=self.dy, units='points')
        return ax.transData

    def setup(self, ax, frames):
        self.sel = frames.select(self.ids)
        labels = frames.attr('label', self.sel)
        if labels is None:
            raise ValueError('AnimationText needs label= passed to animate().')
        if self.vectorized:
            return self._setup_paths(ax, frames, labels)
        # clip_on so off-pitch labels vanish like clipped scatter markers do,
        # instead of drawing on the figure margin. va='center_baseline', not
        # 'center': 'center' centres the font layout box, whose descender
        # space digits never use, so numbers sit ~0.12em high in the circle;
        # 'center_baseline' ink-centres digit strings exactly (measured 0px)
        kwargs = {'ha': 'center', 'va': 'center_baseline', 'clip_on': True,
                  **self.kwargs}
        if self.dx or self.dy:
            kwargs['transform'] = self._offset_transform(ax)
        self.texts = [ax.text(x, y, str(lab), **kwargs)
                      for (x, y), lab in zip(frames.xy[0, self.sel], labels)]
        return self.texts

    def _setup_paths(self, ax, frames, labels):
        from matplotlib.collections import PathCollection
        kwargs = dict(self.kwargs)
        # glyphs built at size 100 for outline precision, scaled to points
        # via sizes= (sqrt(sizes) * dpi/72 at draw time, like markers)
        prop, fontsize = _font_kwargs(kwargs)
        color = kwargs.pop('color', kwargs.pop('c', plt.rcParams['text.color']))
        for key in ('ha', 'horizontalalignment', 'va', 'verticalalignment'):
            kwargs.pop(key, None)              # ink-centred: no alignment
        paths = _ink_centred_glyphs(labels, prop)
        self.collection = PathCollection(
            paths, sizes=np.full(len(paths), (fontsize / 100) ** 2),
            facecolors=color, edgecolors='none',
            offsets=frames.xy[0, self.sel],
            offset_transform=self._offset_transform(ax),
            transform=transforms.IdentityTransform(),
            **{'zorder': 3, **kwargs})        # Text's own zorder
        ax.add_collection(self.collection, autolim=False)
        return [self.collection]

    def update(self, i, frames):
        if self.vectorized:
            self.collection.set_offsets(frames.xy[i, self.sel])
            return [self.collection]
        for text, (x, y) in zip(self.texts, frames.xy[i, self.sel]):
            if np.isfinite(x) and np.isfinite(y):
                text.set_position((x, y))
                text.set_visible(True)
            else:
                text.set_visible(False)
        return self.texts


@writers.register('mplsoccer_gif')
class GifWriter(PillowWriter):
    """The recommended GIF writer: matplotlib's PillowWriter with one
    256-colour palette for the whole clip and no dithering. Flat
    regions (pitches, heatmap bands) stay flat instead of grainy, and
    because every frame shares the palette the file stores only the
    pixels that change between frames — 3-4x smaller than a palette
    per frame. The palette is built from a sample of frames across the
    clip, so a colour that appears only briefly may land on its nearest
    neighbour. Registered as ``'mplsoccer_gif'``, so
    ``anim.save('clip.gif', writer='mplsoccer_gif')`` takes the frame
    rate from the animation. GIF holds every frame in memory until the
    end; for long clips or the smallest files save an mp4 instead,
    e.g. ``anim.save('clip.mp4', writer=FFMpegWriter(fps=25))`` from
    ``matplotlib.animation`` (needs ffmpeg installed), which is about
    20x smaller again.

    Parameters
    ----------
    fps : int, default 5
        Frames per second of the file. When passing an instance, give
        the clip's rate yourself (the same ``fps`` as ``animate``);
        passing the name ``'mplsoccer_gif'`` to ``anim.save`` instead
        uses the animation's rate.
    metadata : dict, optional
        Written to the file, e.g. ``{'title': 'Clip'}``. ``codec`` and
        ``bitrate`` are accepted for matplotlib compatibility but GIF
        does not use them.

    Examples
    --------
    >>> anim.save('clip.gif', writer='mplsoccer_gif', dpi=80)
    >>> anim.save('clip.gif', writer=GifWriter(fps=25), dpi=80)
    """

    palette_samples = 12

    def _supports_transparency(self):
        # tell Animation.save to composite translucent figure colours
        # onto the background: the quantised GIF has no alpha channel
        return False

    def finish(self):
        from PIL import Image
        step = max(1, len(self._frames) // self.palette_samples)
        sample = [frame.convert('RGB') for frame in self._frames[::step]]
        width, height = sample[0].size
        sheet = Image.new('RGB', (width, height * len(sample)))
        for k, frame in enumerate(sample):
            sheet.paste(frame, (0, k * height))
        palette = sheet.quantize(colors=256, dither=Image.Dither.NONE)
        self._frames = [frame.convert('RGB').quantize(palette=palette,
                                                      dither=Image.Dither.NONE)
                        for frame in self._frames]
        self._frames[0].save(
            self.outfile, save_all=True, append_images=self._frames[1:],
            duration=int(1000 / self.fps), loop=0, optimize=True)


# ---------------------------------------------------------------- driver

def _build(pitch, data, frame, layers, x, y, ids, label, draw_kws, ax):
    """Shared setup for animate: ingest, flip, draw, set up the layers."""
    block = Frames.from_columns(data, frame=frame, x=x, y=y, ids=ids,
                                attrs={'label': label})
    if pitch.vertical:                       # the ONLY pitch-aware step
        block.xy = np.ascontiguousarray(block.xy[..., ::-1])
        block.swapped = True

    if ax is None:
        draw_kws = dict(draw_kws or {})
        if draw_kws.get('nrows', 1) != 1 or draw_kws.get('ncols', 1) != 1:
            raise ValueError('for several pitches draw them first with '
                             'pitch.draw(nrows=, ncols=) and pass ax= '
                             '(see animate(ax=)).')
        fig, ax = pitch.draw(**draw_kws)
    elif draw_kws:
        raise ValueError('draw_kws= are for pitch.draw; with ax= the pitch '
                         'is already drawn.')
    else:
        fig = ax.figure
    for layer in layers:                     # expensive, once, before setup
        pre = getattr(layer, 'precompute', None)
        if pre is not None:
            pre(block)
    # a layer's own ax= wins over the figure-level one (several pitches)
    artists = [a for layer in layers
               for a in layer.setup(getattr(layer, 'ax', None) or ax, block)]
    # the layout engine re-runs each time the figure is rendered (saving
    # renders every frame) and would move the axes as artists move, so
    # the animated artists must not take part in the layout
    for artist in artists:
        artist.set_in_layout(False)
    return fig, block, artists


def animate(pitch, data, frame, layers, x='x', y='y', ids=None,
            label=None, fps=25, draw_kws=None, ax=None, blit=None):
    """Animate tracking data on a pitch.

    Takes LONG-FORM tracking data — one row per entity (player / ball /
    referee) per frame — and a
    list of layers saying what to draw. Pass exactly the rows you want
    animated: slice a clip with pandas first, e.g.
    ``df[df['frame'].between(a, b)]``.

    Parameters
    ----------
    pitch : mplsoccer.Pitch or mplsoccer.VerticalPitch
        Draws the pitch and owns the coordinate space; use the
        pitch_type that matches your data provider.
    data : pandas.DataFrame
        Long-form tracking data. Extra per-frame columns (orientation,
        velocity components, is_detected, ...) need no declaring here —
        a layer names the column directly, e.g.
        ``AnimationScatter(rotation='o')``, and it is read lazily.
    frame : str or list of str
        WHEN each row happens: rows sharing a value belong to the same
        animation frame. Frames play in sorted order of the values
        (numbers numerically, strings alphabetically — so prefer
        numeric or datetime keys). Use a single column when it uniquely
        numbers moments across the whole dataframe (soccer providers
        number frames once per match). Use a list when numbering
        RESTARTS, so no single column is unique: ``['period', 'frame']``
        if a provider restarts each half, ``['match_id', 'frame']`` for
        several matches concatenated, or NFL Big Data Bowl's
        ``['gameId', 'playId', 'frameId']`` — where a *play* is one
        snap-to-whistle passage (not a player!) and ``frameId``
        restarts at 1 in every one. Rows that share a frame key and an
        entity raise, pointing at the list form.
    layers : list
        What to draw: AnimationScatter, AnimationTrail, AnimationLines, AnimationSurface,
        AnimationArrows, AnimationHull, AnimationPolygon, AnimationScoreboard,
        AnimationFollow, AnimationText. Stack order comes from each layer's
        ``zorder``.
    x, y : str, default 'x' and 'y'
        Coordinate columns, in the pitch's coordinate system.
    ids : str, optional
        WHICH entity (player / ball / referee) each row belongs to; with
        ``frame`` it locates every row, like
        ``data.pivot(index=frame, columns=ids)``. A missing
        (frame, ids) pair is simply not drawn — substitutions, red
        cards, tracking gaps. If omitted, rows are matched by ROW ORDER:
        the dataframe must be sorted by frame, and every frame must
        have the same rows in the same order (entity ids are then the
        row positions 0, 1, 2, ...). Differing counts or unsorted
        frames raise, telling you to sort or to pass ids=.
    label : str or mapping, optional
        One constant string per ENTITY (jersey number, name) — it
        attaches to ``ids``, not to frames. A column name reads each
        entity's first row (Big Data Bowl-style data, constants
        inline). When labels live in a separate players table
        (fast-forward, SkillCorner, StatsBomb), pass a mapping keyed by
        entity id instead — a dict or pandas Series, e.g.
        ``dict(zip(players['player_id'], players['jersey_number']))``.
        Entities missing from a mapping get no label (the ball,
        naturally absent from lineups); a mapping matching NO entities
        raises, pointing out id/key dtype mismatches. Used by
        ``AnimationScatter(label=True)`` and ``AnimationText``; for text that
        changes per frame use ``AnimationScoreboard``.
    fps : int, default 25
        Playback rate; use the data's native frame rate. Saving with
        ``writer='mplsoccer_gif'`` reuses it.
    draw_kws : dict, optional
        Passed to ``pitch.draw``, e.g. ``{'figsize': (8, 5.5)}``.
    ax : matplotlib.axes.Axes, optional
        An axes the pitch is ALREADY drawn on (``pitch.draw(ax=ax)``,
        ``pitch.grid``, your own layout). The layers animate onto it;
        their artists are excluded from the figure's layout engine
        (tight or constrained layout re-runs on every render and would
        otherwise move the axes as they move), and the figure is
        otherwise left alone — add titles, legends and static artists
        before or after calling. For several pitches in one figure,
        draw them all first (``pitch.draw(ncols=2)``), pass one here
        and point the other layers at theirs with the layer's own
        ``ax=``; one animation then drives every pitch, so saving and
        the notebook player just work.
    blit : bool, optional
        Whether live playback redraws only the animated artists over a
        cached background (fast) rather than the whole figure. Default:
        on, unless a layer moves the view (``AnimationFollow``), whose
        cached background would go stale. Saving and the notebook
        player always render whole frames.

    Returns
    -------
    fig, anim : matplotlib Figure and FuncAnimation
        Save with ``anim.save('clip.gif', writer='mplsoccer_gif',
        dpi=80)``; for one frame, ``anim._draw_frame`` is private, so
        draw it yourself: ``layer.update(i, frames)`` is random-access
        (see the Notes).

    Notes
    -----
    In Jupyter the bare return displays only a static first frame. To
    get an interactive player, set once per notebook::

        plt.rcParams['animation.html'] = 'jshtml'

    then UNPACK the return and end the cell with the animation object
    alone — ``fig, anim = animate(...)`` then ``anim`` as the last
    line. (Ending the cell with the un-unpacked ``animate(...)`` call
    shows a tuple, which never renders as a player.) The first display
    renders every frame, so long clips take a while to appear. Keep a reference to ``anim`` (an
    unreferenced animation is garbage-collected), and note embedded
    players are capped by ``rcParams['animation.embed_limit']``
    (20 MB) — save long clips to a file instead; GIF writers hold every
    frame in memory, so very long clips are better saved as mp4 with
    ``matplotlib.animation.FFMpegWriter``.

    User callables ``(frames, i)`` (lines, polygons, surfaces, the
    camera target, scoreboard text) receive the 0-based frame position
    ``i`` and the ingested clip: ``frames.xy`` (n_frames, n_entities, 2)
    positions in the drawn axes' coordinates (already swapped on a
    vertical pitch), ``frames.frame_index`` the source frame keys in
    play order and ``frames.entity_index`` the entity ids. Geometry a
    callable returns is in the data's own coordinates; the layer swaps
    it, so do not build it from ``frames.xy`` on a vertical pitch.

    Examples
    --------
    >>> import pandas as pd
    >>> from mplsoccer import Pitch, animate, AnimationScatter
    >>> df = pd.DataFrame({'frame': [0, 0, 1, 1],
    ...                    'player': ['a', 'b', 'a', 'b'],
    ...                    'jersey': [7, 9, 7, 9],
    ...                    'x': [30., 60., 32., 61.],
    ...                    'y': [20., 40., 22., 40.]})
    >>> pitch = Pitch(pitch_type='statsbomb')
    >>> fig, anim = animate(pitch, df, frame='frame', x='x', y='y',
    ...                     ids='player', label='jersey',
    ...                     layers=[AnimationScatter(ids=['a', 'b'], s=280,
    ...                                              color='red', ec='black',
    ...                                              label=True,
    ...                                              labelcolor='white')])
    >>> # anim.save('clip.gif', writer='mplsoccer_gif', dpi=80)
    """
    fig, block, artists = _build(pitch, data, frame, layers,
                                 x, y, ids, label, draw_kws, ax)
    if blit is None:
        blit = all(getattr(layer, 'blit_safe', True) for layer in layers)

    def _update(i):
        return [a for layer in layers for a in layer.update(i, block)]

    anim = FuncAnimation(fig, _update, frames=block.n_frames,
                         init_func=lambda: artists,
                         interval=1000 / fps, blit=blit)
    return fig, anim
