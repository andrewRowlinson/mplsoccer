"""mplsoccer's text artists.

The module contains ``CurvedText``, which draws text along a circular arc
and is used by the radar charts to render curved parameter labels.

CurvedText author: PGupta-Git (https://github.com/PGupta-Git)
"""

from dataclasses import dataclass
from typing import Literal
import warnings

import numpy as np
from matplotlib import cbook
from matplotlib.artist import Artist
from matplotlib.patches import PathPatch
from matplotlib.text import Text
from matplotlib.textpath import TextPath, text_to_path
from matplotlib.transforms import Affine2D, Bbox

from .utils import validate_ax

__all__ = ['CurvedText']


_Align = Literal["center", "start", "end"]
_Direction = Literal["auto", "clockwise", "counterclockwise"]
_RadialAnchor = Literal["inner", "center"]


@dataclass
class _LineGlyphs:
    text: str
    chars: list[str]
    artists: list[PathPatch | None]  # None for whitespace characters
    advances_pt: list[float]  # character advance widths in points


class CurvedText(Artist):
    """Draw text along a circular arc for mplsoccer radar charts.

    Parameters
    ----------
    ax : matplotlib axis
        The axis to plot on.
    x, y : float
        The position to place the text in data coordinates. The text curves
        along the circle through ``(x, y)`` around ``center``, with the line
        of text vertically centered on the circle. Must differ from ``center``.
    s : str
        The text to draw. Newlines split the text into multiple arcs
        stacked radially (see ``radial_anchor``).
    center : tuple of float, default (0, 0)
        The point the text curves around, in data coordinates.
    align : {'center', 'start', 'end'}, default 'center'
        How to align the text relative to ``(x, y)``. ``'start'`` and ``'end'``
        refer to the text's reading direction along the arc rather than
        left/right, because ``direction='auto'`` can flip the direction
        the text flows.
    direction : {'auto', 'clockwise', 'counterclockwise'}, default 'auto'
        Direction to lay out characters along the arc. ``'auto'`` flips
        direction in the lower half of the circle so the text stays readable.
    radial_anchor : {'inner', 'center'}, default 'inner'
        How multiline text stacks relative to the circle through ``(x, y)``:
        ``'inner'`` centers the innermost line on the circle with further
        lines stacking outward, while ``'center'`` centers the whole block
        of lines on the circle. Single-line text is centered on the
        circle either way.
    letter_spacing : float, default 0
        Additional spacing between characters in points, added on top of the
        font's natural character widths. The default of 0 uses the font's
        normal spacing; negative values tighten it.
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.text.
        Arguments that do not translate to per-glyph curved layout
        (e.g. ``rotation`` and the alignment arguments) are ignored
        with a warning.

    Notes
    -----
    - Mathtext/TeX rendering is disabled for curved text (it is non-trivial to
      support when placing per-character glyphs along an arc).
    - The layout mixes three unit systems, named by variable suffix:
      ``_data`` (data coordinates, where the arc is defined), ``_px``
      (display pixels, where text sizes are known) and ``_pt`` (points,
      1/72 inch, where font metrics are known). Each character's angular
      step along the arc is its pixel width divided by the pixel radius
      (an angle is an arc length over a radius).
    - An 'advance' is a font's per-character pen movement: the width a
      character occupies, including the small side bearings around its
      ink. Glyphs are spaced by their advances, like normal text.
    - The data-to-pixel scale is measured from the axes transform on every
      draw rather than assumed, so unequal aspect ratios, inverted axes
      and figure resizes are handled.
    """

    def __init__(
        self,
        ax,
        x: float,
        y: float,
        s: str,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        align: _Align = "center",
        direction: _Direction = "auto",
        radial_anchor: _RadialAnchor = "inner",
        letter_spacing: float = 0.0,
        **kwargs,
    ):
        validate_ax(ax)
        super().__init__()

        # Text kwargs that do not translate to per-glyph curved layout are
        # accepted but ignored, with a warning (like the 'colors' argument
        # of the lines method).
        unsupported = ("rotation", "rotation_mode", "ha", "horizontalalignment",
                       "va", "verticalalignment", "transform", "bbox",
                       "backgroundcolor", "parse_math", "usetex")
        ignored = [key for key in unsupported if key in kwargs]
        if ignored:
            warnings.warn(
                f"curved text ignores the argument(s): {ignored}",
                UserWarning,
                stacklevel=2,
            )

        self.axes = ax
        self.set_figure(ax.figure)

        self._center = (float(center[0]), float(center[1]))
        delta_x = float(x) - self._center[0]
        delta_y = float(y) - self._center[1]
        self._radius = float(np.hypot(delta_x, delta_y))
        if self._radius == 0:
            raise ValueError(
                f"The text position ({x}, {y}) must differ from the center "
                f"{center} so it defines the circle the text curves along."
            )
        # The angle convention matches mplsoccer's radar charts: theta=0 at
        # the top, increasing clockwise, so x = r * sin(theta), y = r * cos(theta).
        self._theta = float(np.arctan2(delta_x, delta_y))
        self._align: _Align = align
        self._direction: _Direction = direction
        self._radial_anchor: _RadialAnchor = radial_anchor
        self._letter_spacing_points = float(letter_spacing)

        self._text = "" if s is None else str(s)
        self._validate_no_mathtext()

        self._text_kwargs = {key: value for key, value in kwargs.items()
                             if key not in unsupported}

        # Match Matplotlib Text default zorder (3) so curved labels layer similarly.
        zorder = self._text_kwargs.pop("zorder", 3)
        self.set_zorder(zorder)

        # prevents clipping labels outside the axes with savefig(bbox_inches='tight')
        if not self._text_kwargs.get("clip_on"):
            self.set_clip_on(False)

        # A hidden, never-drawn Text that resolves the kwargs (rcParams
        # defaults, named fontsizes, validation); the glyphs copy its styling.
        self._template = Text(0, 0, "", **self._text_kwargs)
        self._template.set_parse_math(False)
        self._template.set_usetex(False)
        self._template.set_figure(ax.figure)
        self._template.axes = ax

        self._lines: list[_LineGlyphs] = []
        self._glyphs_stale = False
        self._rebuild()

    def _validate_no_mathtext(self) -> None:
        """
        Curved text is laid out one glyph at a time along the arc, which
        cannot represent mathtext's two-dimensional layout (superscripts,
        fractions), so fail loudly rather than draw the markup literally.
        """
        for line in self._text.splitlines():
            if cbook.is_math_text(line):
                raise NotImplementedError(
                    f"mathtext is not implemented for curved text: {line!r}. "
                    "Use plain text, or escape dollar signs as \\$ "
                    "for a literal '$'."
                )

    def set_text(self, text: str) -> None:
        """Set the text string."""
        self._text = "" if text is None else str(text)
        self._validate_no_mathtext()
        self._glyphs_stale = True
        self.stale = True

    def get_text(self) -> str:
        """Return the text string."""
        return self._text

    # Common Text setters, so labels returned by draw_param_labels can be
    # restyled the same way whether or not they are curved. Each routes
    # through the template Text and marks the glyph patches for rebuild,
    # as their styling is otherwise fixed at construction.
    def set_color(self, color) -> None:
        """Set the text color."""
        self._template.set_color(color)
        self._glyphs_stale = True
        self.stale = True

    def get_color(self):
        """Return the text color."""
        return self._template.get_color()

    def set_fontsize(self, fontsize) -> None:
        """Set the font size in points."""
        self._template.set_fontsize(fontsize)
        self._glyphs_stale = True
        self.stale = True

    def get_fontsize(self):
        """Return the font size in points."""
        return self._template.get_fontsize()

    def set_alpha(self, alpha) -> None:
        """Set the transparency, from 0 (invisible) to 1 (opaque)."""
        super().set_alpha(alpha)
        self._template.set_alpha(alpha)
        self._glyphs_stale = True

    def get_alpha(self):
        """Return the transparency."""
        return self._template.get_alpha()

    def get_children(self):
        """Return the glyph patches, rebuilding them first if stale."""
        if self._glyphs_stale:
            self._rebuild()
        children: list[Artist] = []
        for line in self._lines:
            for artist in line.artists:
                if artist is not None:
                    children.append(artist)
        return children

    def _rebuild(self) -> None:
        """Recreate the glyph patches (one PathPatch per visible character).

        Decides what to draw, not where: each glyph outline is created at
        the origin with no transform, alongside the advance widths needed
        to place it; ``_layout`` positions the glyphs each time the
        artist is rendered. Each patch's styling is fixed when it is
        created, which is why restyling schedules a rebuild
        (``_glyphs_stale``) instead of updating the patches in place.
        """
        self._glyphs_stale = False
        self._lines.clear()
        fontsize_points = float(self._template.get_fontsize())
        prop = self._template.get_fontproperties()
        # unescape \$ like matplotlib's non-math text path does, so the
        # escape recommended by the mathtext error renders as a plain '$'
        text = self._text.replace(r"\$", "$")
        lines = text.splitlines() or [""]
        for line in lines:
            chars = list(line)
            artists: list[PathPatch | None] = []
            advances_pt = []
            for ch in chars:
                # Measure each character's advance width individually
                # rather than from cumulative text widths. Cumulative
                # widths include kerning adjustments that don't apply when
                # each character is rendered individually, causing spacing
                # mismatches.
                width, _, _ = text_to_path.get_text_width_height_descent(
                    ch, prop, ismath=False
                )
                advances_pt.append(float(width))
                if ch.isspace():
                    artists.append(None)
                    continue

                glyph_path = TextPath(
                    (0, 0), ch, size=fontsize_points, prop=prop, usetex=False
                )

                # Copy the template's styling and the common Artist
                # properties that users may set via text kwargs. Only this
                # closed list reaches the patches; text-only kwargs (e.g.
                # fontstyle) stay on the template.
                patch = PathPatch(
                    glyph_path,
                    facecolor=self._template.get_color(),
                    edgecolor="none",
                    linewidth=0,
                    antialiased=self._template.get_antialiased(),
                    alpha=self._template.get_alpha(),
                    path_effects=self._template.get_path_effects(),
                    zorder=self.get_zorder(),
                    clip_on=self._template.get_clip_on(),
                    clip_box=self._template.get_clip_box(),
                    clip_path=self._template.get_clip_path(),
                    url=self._template.get_url(),
                )
                patch.set_figure(self.figure)
                patch.axes = self.axes
                artists.append(patch)
            self._lines.append(_LineGlyphs(text=line, chars=chars, artists=artists,
                                           advances_pt=advances_pt))

    def _direction_sign(self) -> int:
        """The sign of the angular step per character: 1 for clockwise, -1
        for counterclockwise ('auto' flips in the lower half for readability)."""
        if self._direction == "clockwise":
            return 1
        if self._direction == "counterclockwise":
            return -1
        # the tolerance keeps text exactly at the left/right of the circle
        # (cos(theta) == 0) on the unflipped branch rather than letting
        # floating-point rounding decide
        return -1 if np.cos(self._theta) < -1e-9 else 1

    def _hide_glyphs(self, lines) -> None:
        """Hide glyphs whose positions cannot be computed.

        The layout skips a line (or the whole text) when the pixel radius
        or radial scale is not positive and finite (e.g. a NaN position,
        or a zero-size figure). ``draw`` renders every glyph with whatever
        transform it has, so skipped glyphs must be switched off or they
        would render at a stale or identity transform as stray marks at
        the figure origin. The next successful layout makes them visible
        again.
        """
        for line in lines:
            for artist in line.artists:
                if artist is not None:
                    artist.set_visible(False)

    def _layout_line(
        self,
        line: _LineGlyphs,
        radius_data: float,
        anchor_theta: float,
        direction_sign: int,
    ) -> None:
        """Decide where to draw: position one line's glyphs along the arc
        of ``radius_data`` (the baseline radius) from ``anchor_theta`` in
        the ``direction_sign`` direction, by setting each glyph's display
        transform."""
        if not line.chars:
            return

        # The arc radius in pixels: the distance between the transformed
        # center and a transformed point on the arc. Pixel widths divided
        # by this radius give the angular steps along the arc.
        center_x, center_y = self._center
        assert self.axes is not None
        center_px = self.axes.transData.transform((center_x, center_y))
        anchor_xy = (
            center_x + radius_data * float(np.sin(anchor_theta)),
            center_y + radius_data * float(np.cos(anchor_theta)),
        )
        anchor_px = self.axes.transData.transform(anchor_xy)
        radius_px = float(np.hypot(*(anchor_px - center_px)))
        if not np.isfinite(radius_px) or radius_px <= 0:
            self._hide_glyphs([line])
            return

        pt_to_px = self.figure.dpi / 72.0
        advances_px = [width * pt_to_px for width in line.advances_pt]
        letter_spacing_px = self._letter_spacing_points * pt_to_px
        total_width_px = (sum(advances_px)
                          + letter_spacing_px * max(0, len(advances_px) - 1))

        # Where the text begins reading: slide back from the anchor angle
        # so the text is centered on it ('center') or ends at it ('end').
        start_theta = anchor_theta
        if self._align == "center":
            start_theta -= direction_sign * total_width_px / (2 * radius_px)
        elif self._align == "end":
            start_theta -= direction_sign * total_width_px / radius_px

        # March along the arc, placing each glyph at the center of its
        # advance width, like a pen advancing after each character.
        arc_offset_px = 0.0
        for idx, (advance_pt, advance_px, artist) in enumerate(
            zip(line.advances_pt, advances_px, line.artists)
        ):
            glyph_center_px = arc_offset_px + (advance_px / 2)
            glyph_theta = start_theta + direction_sign * (glyph_center_px / radius_px)
            glyph_x = center_x + radius_data * float(np.sin(glyph_theta))
            glyph_y = center_y + radius_data * float(np.cos(glyph_theta))

            if artist is not None:
                rotation = -np.rad2deg(glyph_theta)
                if direction_sign == -1:
                    rotation += 180

                glyph_px = self.axes.transData.transform((glyph_x, glyph_y))

                # Anchor each glyph by the centre of its advance box -- the
                # same quantity used to place it along the arc. Anchoring by
                # the ink bounding-box centre instead shifts every glyph by
                # its side-bearing asymmetry (up to ~5% of the em for e.g.
                # 'r'), which makes the letter spacing visibly wobble.
                transform = (
                    Affine2D()
                    # half the advance leftward, staying on the baseline
                    .translate(-advance_pt / 2.0, 0.0)
                    .scale(pt_to_px)
                    .rotate_deg(rotation)
                    .translate(glyph_px[0], glyph_px[1])
                )
                artist.set_transform(transform)
                artist.set_visible(True)

                # Stash the data-space anchor and rotation for tests/debugging.
                artist._mplsoccer_position = (glyph_x, glyph_y)
                artist._mplsoccer_rotation = float(rotation)

            arc_offset_px += advance_px
            if idx < (len(advances_px) - 1):
                arc_offset_px += letter_spacing_px

    def _radial_pixel_scale(self) -> tuple[float, bool]:
        """Measure how data units map to pixels at the text's position.

        Takes the anchor point and a second point a tiny step further
        from the center, transforms both to pixels and compares them:
        the pixel distance divided by the step gives
        ``px_per_data_radial`` (how many pixels one data unit spans,
        moving away from the center), and ``flip_line_order`` is True
        when the second point lands lower on the screen, meaning wrapped
        lines must be stacked in reverse to read top-to-bottom (the
        lower half of the circle, or an inverted axis). Measuring
        instead of assuming handles unequal aspect ratios, inverted
        axes and nonlinear scales.
        """
        center_x, center_y = self._center
        nudge = max(1e-6, abs(self._radius) * 1e-3)
        # the x/y change per unit travelled away from the center
        step_x = float(np.sin(self._theta))
        step_y = float(np.cos(self._theta))
        anchor = (center_x + self._radius * step_x,
                  center_y + self._radius * step_y)
        nudged = (center_x + (self._radius + nudge) * step_x,
                  center_y + (self._radius + nudge) * step_y)
        anchor_px = self.axes.transData.transform(anchor)
        nudged_px = self.axes.transData.transform(nudged)
        flip_line_order = bool(nudged_px[1] < anchor_px[1])
        px_per_data_radial = float(np.hypot(*(nudged_px - anchor_px))) / nudge
        return px_per_data_radial, flip_line_order

    def _line_stack_offset(self, line_idx: int, num_lines: int,
                           flip_line_order: bool) -> float:
        """Which multiple of the line spacing this line sits at radially.

        Chosen so wrapped lines read top-to-bottom on the screen like
        normal multiline text: with ``radial_anchor='inner'`` the block
        grows away from the given radius, with ``'center'`` it is
        centered on it. ``flip_line_order`` reverses the stacking where
        farther from the center means lower on the screen.
        """
        if self._radial_anchor == "center":
            half = (num_lines - 1) / 2
            return (line_idx - half) if flip_line_order else (half - line_idx)
        if flip_line_order:
            return float(line_idx)  # the first line lands on the circle
        return float((num_lines - 1) - line_idx)  # the last line lands on the circle

    def _center_to_baseline_data(self, line: _LineGlyphs,
                                 px_per_data_radial: float) -> float:
        """Radial offset (in data units) from a line's center to its baseline.

        Glyph paths are anchored on the text baseline, but the caller's
        radius is treated as the line's visual centerline. The offset is
        half the line height minus the descent, measured against an 'lp'
        reference (full ascender plus descender) so lines without tall or
        deep characters get the same height as lines with them.
        """
        prop = self._template.get_fontproperties()
        _, ref_height, ref_descent = text_to_path.get_text_width_height_descent(
            "lp", prop, ismath=False
        )
        _, height, descent = text_to_path.get_text_width_height_descent(
            line.text if line.text else "lp", prop, ismath=False
        )
        height = float(max(height, ref_height))
        descent = float(max(descent, ref_descent))
        center_to_baseline_pt = (height / 2.0) - descent
        center_to_baseline_px = center_to_baseline_pt * self.figure.dpi / 72.0
        return center_to_baseline_px / px_per_data_radial

    def _layout(self) -> None:
        """Set display-space transforms on every glyph patch (no drawing)."""
        direction_sign = self._direction_sign()

        px_per_data_radial, flip_line_order = self._radial_pixel_scale()
        if not np.isfinite(px_per_data_radial) or px_per_data_radial <= 0:
            self._hide_glyphs(self._lines)
            return

        fontsize_points = float(self._template.get_fontsize())
        linespacing = self._template.get_linespacing()
        if linespacing == "normal":
            # approximate the font-derived 'normal' of newer matplotlib
            # with its classic default: 1.2 multiples of the fontsize
            linespacing = 1.2
        line_spacing_px = fontsize_points * float(linespacing) * self.figure.dpi / 72.0
        line_spacing_data = line_spacing_px / px_per_data_radial

        num_lines = len(self._lines)
        for line_idx, line in enumerate(self._lines):
            stack_offset = self._line_stack_offset(line_idx, num_lines,
                                                   flip_line_order)
            center_radius = self._radius + stack_offset * line_spacing_data
            baseline_radius = center_radius - direction_sign * (
                self._center_to_baseline_data(line, px_per_data_radial)
            )
            self._layout_line(
                line=line,
                radius_data=baseline_radius,
                anchor_theta=self._theta,
                direction_sign=direction_sign,
            )

    def draw(self, renderer) -> None:
        """Position the glyphs for the current axes transform, then
        draw them."""
        if not self.get_visible():
            return
        if self.axes is None or self.figure is None:
            return
        self._layout()
        for artist in self.get_children():
            artist.draw(renderer)

    def get_window_extent(self, renderer=None):
        """Return the bounding box of the laid-out glyphs in display space.

        Implementing this lets curved labels participate in tight bounding
        box calculations (``savefig(bbox_inches='tight')``, ``tight_layout``,
        ``constrained_layout``) instead of reporting a zero-size box, which
        would crop the labels out of saved figures.
        """
        if self.axes is None or self.figure is None:
            return Bbox.null()
        self._layout()
        extents = [artist.get_window_extent(renderer)
                   for artist in self.get_children()]
        if not extents:
            return Bbox.null()
        return Bbox.union(extents)

    def contains(self, mouseevent):
        """Return whether a mouse click or hover is over any of the glyphs,
        so curved labels respond to interactive events like regular text."""
        if (self.axes is None or self.figure is None
                or mouseevent.canvas is not self.figure.canvas):
            return False, {}
        self._layout()
        inside = any(artist.contains(mouseevent)[0]
                     for artist in self.get_children())
        return inside, {}
