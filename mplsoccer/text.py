"""mplsoccer's text artists.

Text drawn from glyph outlines (``TextPath``) rather than ``ax.text``,
for geometric control that normal text rendering cannot give.
Currently contains ``CurvedText``, which draws text along a circular arc
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

__all__ = ['CurvedText']


_Align = Literal["center", "start", "end"]
_Direction = Literal["auto", "clockwise", "counterclockwise"]
_RadiiMode = Literal["outward", "center"]


@dataclass
class _LineGlyphs:
    text: str
    chars: list[str]
    artists: list[PathPatch | None]  # None for whitespace characters


class CurvedText(Artist):
    """Draw text along a circular arc for mplsoccer radar charts.

    Notes
    -----
    - The angle convention matches mplsoccer's radar charts:
      `theta=0` at the top, increasing clockwise, with coordinates:
      `x = r * sin(theta)`, `y = r * cos(theta)`.
    - Mathtext/TeX rendering is disabled for curved text (it is non-trivial to
      support when placing per-character glyphs along an arc).
    """

    def __init__(
        self,
        ax,
        text: str,
        radius: float,
        theta: float,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        align: _Align = "center",
        direction: _Direction = "auto",
        radii: _RadiiMode = "outward",
        line_spacing: float | None = None,
        letter_spacing: float = 0.0,
        **text_kwargs,
    ):
        super().__init__()

        # Text kwargs that do not translate to per-glyph curved layout are
        # accepted but ignored, with a warning (like the 'colors' argument
        # of the lines method).
        unsupported = ("rotation", "rotation_mode", "ha", "horizontalalignment",
                       "va", "verticalalignment", "transform", "bbox",
                       "backgroundcolor")
        ignored = [key for key in unsupported if key in text_kwargs]
        if ignored:
            warnings.warn(
                f"curved text ignores the argument(s): {ignored}",
                UserWarning,
                stacklevel=2,
            )

        self.axes = ax
        self.set_figure(ax.figure)

        self._center = (float(center[0]), float(center[1]))
        self._radius = float(radius)
        self._theta = float(theta)
        self._align: _Align = align
        self._direction: _Direction = direction
        self._radii: _RadiiMode = radii
        self._line_spacing_points = line_spacing
        self._letter_spacing_points = float(letter_spacing)

        self._text = "" if text is None else str(text)
        self._validate_no_mathtext()

        self._text_kwargs = dict(text_kwargs)
        for key in unsupported:
            self._text_kwargs.pop(key, None)
        self._text_kwargs.setdefault("parse_math", False)
        self._text_kwargs.setdefault("usetex", False)

        # Match Matplotlib Text default zorder (3) so curved labels layer similarly.
        zorder = self._text_kwargs.pop("zorder", 3)
        self.set_zorder(zorder)

        # Axes.add_artist assigns the axes patch as this artist's clip path.
        # Combined with the default clip_on=True that would clip the label
        # out of tight bounding boxes (savefig(bbox_inches='tight') would
        # crop labels outside the axes), which Axes.text-created labels do
        # not suffer. Default to unclipped like regular text unless the
        # caller explicitly asks for clipping.
        if not self._text_kwargs.get("clip_on"):
            self.set_clip_on(False)

        self._template = Text(0, 0, "", **self._text_kwargs)
        self._template.set_parse_math(False)
        self._template.set_usetex(False)
        self._template.set_figure(ax.figure)
        self._template.axes = ax

        self._lines: list[_LineGlyphs] = []
        self._rebuild()

    def _validate_no_mathtext(self) -> None:
        # curved text is laid out one glyph at a time along the arc, which
        # cannot represent mathtext's two-dimensional layout (superscripts,
        # fractions), so fail loudly rather than draw the markup literally
        for line in self._text.splitlines():
            if cbook.is_math_text(line):
                raise NotImplementedError(
                    f"mathtext is not implemented for curved text: {line!r}. "
                    "Use plain text, or escape dollar signs as \\$ "
                    "for a literal '$'."
                )

    def set_text(self, text: str) -> None:
        self._text = "" if text is None else str(text)
        self._validate_no_mathtext()
        self._rebuild()
        self.stale = True

    def get_text(self) -> str:
        return self._text

    # Common Text setters, so labels returned by draw_param_labels can be
    # restyled the same way whether or not they are curved. Each routes
    # through the template Text and rebuilds the glyph patches, which
    # otherwise bake in the properties at construction.
    def set_color(self, color) -> None:
        self._template.set_color(color)
        self._rebuild()
        self.stale = True

    def get_color(self):
        return self._template.get_color()

    def set_fontsize(self, fontsize) -> None:
        self._template.set_fontsize(fontsize)
        self._rebuild()
        self.stale = True

    def get_fontsize(self):
        return self._template.get_fontsize()

    def set_alpha(self, alpha) -> None:
        super().set_alpha(alpha)
        self._template.set_alpha(alpha)
        self._rebuild()

    def get_alpha(self):
        return self._template.get_alpha()

    def get_children(self):
        children: list[Artist] = []
        for line in self._lines:
            for artist in line.artists:
                if artist is not None:
                    children.append(artist)
        return children

    def _rebuild(self) -> None:
        self._lines.clear()
        # unescape \$ like matplotlib's non-math text path does, so the
        # escape recommended by the mathtext error renders as a plain '$'
        text = self._text.replace(r"\$", "$")
        lines = text.splitlines() or [""]
        for line in lines:
            chars = list(line)
            artists: list[PathPatch | None] = []
            for ch in chars:
                if ch.isspace():
                    artists.append(None)
                    continue

                fontsize_points = float(self._template.get_fontsize())
                prop = self._template.get_fontproperties()
                glyph_path = TextPath(
                    (0, 0), ch, size=fontsize_points, prop=prop, usetex=False
                )

                patch = PathPatch(
                    glyph_path,
                    facecolor=self._template.get_color(),
                    edgecolor="none",
                    linewidth=0,
                    antialiased=self._template.get_antialiased(),
                )
                patch.set_alpha(self._template.get_alpha())
                patch.set_path_effects(self._template.get_path_effects())
                patch.set_zorder(self.get_zorder())
                patch.set_figure(self.figure)
                patch.axes = self.axes

                # Preserve common Artist properties that users may set via text kwargs.
                patch.set_clip_on(self._template.get_clip_on())
                patch.set_clip_box(self._template.get_clip_box())
                patch.set_clip_path(self._template.get_clip_path())
                patch.set_url(self._template.get_url())

                # Stash the glyph for tests/debugging.
                patch._mplsoccer_char = ch  # type: ignore[attr-defined]

                artists.append(patch)
            self._lines.append(_LineGlyphs(text=line, chars=chars, artists=artists))

    def _direction_sign(self) -> int:
        if self._direction == "clockwise":
            return 1
        if self._direction == "counterclockwise":
            return -1
        # flip in the lower half of the chart so labels stay readable.
        # cos(theta) < 0 is the lower half; the tolerance makes exactly
        # horizontal spokes (cos(theta) == 0, i.e. the left/right spokes)
        # always take the unflipped branch rather than letting
        # floating-point rounding of (2 * pi / num_params) * k decide.
        return -1 if np.cos(self._theta) < -1e-9 else 1

    def _layout_line(
        self,
        line: _LineGlyphs,
        radius_data: float,
        start_theta: float,
        direction_sign: int,
    ) -> None:
        if not line.chars:
            return

        theta_ref = float(start_theta)

        center_x, center_y = self._center
        assert self.axes is not None
        center_px = self.axes.transData.transform((center_x, center_y))
        edge_xy = (
            center_x + radius_data * float(np.sin(theta_ref)),
            center_y + radius_data * float(np.cos(theta_ref)),
        )
        edge_px = self.axes.transData.transform(edge_xy)
        radius_px = float(np.hypot(*(edge_px - center_px)))
        if not np.isfinite(radius_px) or radius_px <= 0:
            return

        prop = self._template.get_fontproperties()

        # Use individual character widths instead of cumulative text widths.
        # Cumulative widths include kerning adjustments that don't apply when
        # each character is rendered individually, causing spacing mismatches.
        advances_pt = []
        for ch in line.text:
            w, _, _ = text_to_path.get_text_width_height_descent(ch, prop, ismath=False)
            advances_pt.append(float(w))

        pt_to_px = self.figure.dpi / 72.0
        advances_px = [w * pt_to_px for w in advances_pt]

        letter_spacing_px = self._letter_spacing_points * self.figure.dpi / 72.0
        total_width_px = float(sum(advances_px))
        if len(advances_px) > 1:
            total_width_px += letter_spacing_px * (len(advances_px) - 1)

        if self._align == "center":
            start_theta = start_theta - direction_sign * (
                total_width_px / (2 * radius_px)
            )
        elif self._align == "end":
            start_theta = start_theta - direction_sign * (total_width_px / radius_px)

        cumulative = 0.0
        for idx, (ch, adv_pt, adv_px, artist) in enumerate(
            zip(line.chars, advances_pt, advances_px, line.artists)
        ):
            center_dist_px = cumulative + (adv_px / 2)
            theta_i = start_theta + direction_sign * (center_dist_px / radius_px)
            x_i = center_x + radius_data * float(np.sin(theta_i))
            y_i = center_y + radius_data * float(np.cos(theta_i))

            if artist is not None:
                rotation = -np.rad2deg(theta_i)
                if direction_sign == -1:
                    rotation += 180

                x_px, y_px = self.axes.transData.transform((x_i, y_i))

                # Anchor each glyph by the centre of its advance box -- the
                # same quantity used to place it along the arc. Anchoring by
                # the ink bounding-box centre instead shifts every glyph by
                # its side-bearing asymmetry (up to ~5% of the em for e.g.
                # 'r'), which makes the letter spacing visibly wobble.
                transform = (
                    Affine2D()
                    .translate(-adv_pt / 2.0, 0.0)
                    .scale(pt_to_px)
                    .rotate_deg(rotation)
                    .translate(x_px, y_px)
                )
                artist.set_transform(transform)

                # Stash the data-space anchor and rotation for tests/debugging.
                artist._mplsoccer_position = (x_i, y_i)  # type: ignore[attr-defined]
                artist._mplsoccer_rotation = float(rotation)  # type: ignore[attr-defined]

            cumulative += adv_px
            if idx < (len(advances_px) - 1):
                cumulative += letter_spacing_px

    def _layout(self) -> None:
        """Set display-space transforms on every glyph patch (no drawing)."""
        direction_sign = self._direction_sign()

        fontsize_points = float(self._template.get_fontsize())
        linespacing = float(self._text_kwargs.get("linespacing", 1.2))
        line_spacing_points = (
            float(self._line_spacing_points)
            if self._line_spacing_points is not None
            else fontsize_points * linespacing
        )
        line_spacing_px = line_spacing_points * self.figure.dpi / 72.0

        num_lines = len(self._lines)
        center_x, center_y = self._center
        r0 = self._radius
        delta_r = max(1e-6, abs(r0) * 1e-3)
        p0_vec = (float(np.sin(self._theta)), float(np.cos(self._theta)))
        p0 = (center_x + r0 * p0_vec[0], center_y + r0 * p0_vec[1])
        p1 = (
            center_x + (r0 + delta_r) * p0_vec[0],
            center_y + (r0 + delta_r) * p0_vec[1],
        )
        p0_px = self.axes.transData.transform(p0)
        p1_px = self.axes.transData.transform(p1)
        outward_is_up = bool(p1_px[1] >= p0_px[1])

        px_per_data_radial = float(np.hypot(*(p1_px - p0_px))) / float(delta_r)
        if not np.isfinite(px_per_data_radial) or px_per_data_radial <= 0:
            return

        line_spacing_data = line_spacing_px / px_per_data_radial

        prop = self._template.get_fontproperties()
        _, lp_h, lp_d = text_to_path.get_text_width_height_descent(
            "lp", prop, ismath=False
        )
        lp_h = float(lp_h)
        lp_d = float(lp_d)

        for line_idx, line in enumerate(self._lines):
            if self._radii == "center":
                # Center the block around the given radius, while keeping the line order
                # consistent with standard multiline text (top-to-bottom in display coords).
                half = (num_lines - 1) / 2
                offset_factor = (
                    (half - line_idx) if outward_is_up else (line_idx - half)
                )
            else:
                if outward_is_up:
                    # At the top half, increasing radius goes up in display coords, so place
                    # the first line outermost to preserve multiline ordering.
                    offset_factor = (num_lines - 1) - line_idx
                else:
                    # At the bottom half, increasing radius goes down in display coords, so
                    # place the first line innermost to preserve multiline ordering.
                    offset_factor = line_idx

            radius_data_center = self._radius + offset_factor * line_spacing_data

            # We draw individual glyphs as vector paths (TextPath -> PathPatch).
            # Convert the caller-provided radius (treated as the visual centerline)
            # to the baseline radius using the line's font metrics.
            text_for_metrics = line.text if line.text else "lp"
            _, h, d = text_to_path.get_text_width_height_descent(
                text_for_metrics, prop, ismath=False
            )
            h = float(max(h, lp_h))
            d = float(max(d, lp_d))
            center_to_baseline_pt = (h / 2.0) - d
            center_to_baseline_px = center_to_baseline_pt * (self.figure.dpi / 72.0)
            center_to_baseline_data = center_to_baseline_px / px_per_data_radial
            radius_data_baseline = (
                radius_data_center - direction_sign * center_to_baseline_data
            )
            self._layout_line(
                line=line,
                radius_data=radius_data_baseline,
                start_theta=self._theta,
                direction_sign=direction_sign,
            )

    def draw(self, renderer) -> None:
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
        """Hit-test against the laid-out glyphs so picking works."""
        if (self.axes is None or self.figure is None
                or mouseevent.canvas is not self.figure.canvas):
            return False, {}
        self._layout()
        inside = any(artist.contains(mouseevent)[0]
                     for artist in self.get_children())
        return inside, {}
