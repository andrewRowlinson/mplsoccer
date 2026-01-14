"""Utilities for drawing text along a circular arc (radar convention).

This module is currently used by mplsoccer's radar charts to render curved
parameter labels.

Author: PGupta-Git (https://github.com/PGupta-Git)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from matplotlib.artist import Artist
from matplotlib.text import Text

__all__ = ["CurvedText"]


_Align = Literal["center", "start", "end"]
_Direction = Literal["auto", "clockwise", "counterclockwise"]
_RadiiMode = Literal["outward", "center"]


@dataclass
class _LineGlyphs:
    text: str
    chars: list[str]
    artists: list[Text | None]  # None for whitespace characters


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

        self._text_kwargs = dict(text_kwargs)
        self._text_kwargs.pop("rotation", None)
        self._text_kwargs.pop("ha", None)
        self._text_kwargs.pop("horizontalalignment", None)
        self._text_kwargs.pop("va", None)
        self._text_kwargs.pop("verticalalignment", None)
        self._text_kwargs.pop("transform", None)
        self._text_kwargs.setdefault("parse_math", False)
        self._text_kwargs.setdefault("usetex", False)

        # Match Matplotlib Text default zorder (3) so curved labels layer similarly.
        zorder = self._text_kwargs.pop("zorder", 3)
        self.set_zorder(zorder)

        self._template = Text(0, 0, "", **self._text_kwargs)
        self._template.set_parse_math(False)
        self._template.set_usetex(False)
        self._template.set_figure(ax.figure)
        self._template.axes = ax

        self._lines: list[_LineGlyphs] = []
        self._rebuild()

    def set_text(self, text: str) -> None:
        self._text = "" if text is None else str(text)
        self._rebuild()
        self.stale = True

    def get_text(self) -> str:
        return self._text

    def get_children(self):
        children: list[Artist] = []
        for line in self._lines:
            for artist in line.artists:
                if artist is not None:
                    children.append(artist)
        return children

    def _rebuild(self) -> None:
        self._lines.clear()
        lines = self._text.splitlines() or [""]
        for line in lines:
            chars = list(line)
            artists: list[Text | None] = []
            for ch in chars:
                if ch.isspace():
                    artists.append(None)
                    continue
                artist = Text(0, 0, ch, **self._text_kwargs)
                artist.set_parse_math(False)
                artist.set_usetex(False)
                artist.set_figure(self.figure)
                artist.axes = self.axes
                assert self.axes is not None
                artist.set_transform(self.axes.transData)
                artist.set_horizontalalignment("center")
                artist.set_verticalalignment("center")
                artists.append(artist)
            self._lines.append(_LineGlyphs(text=line, chars=chars, artists=artists))

    def _direction_sign(self) -> int:
        if self._direction == "clockwise":
            return 1
        if self._direction == "counterclockwise":
            return -1
        theta = self._theta % (2 * np.pi)
        return -1 if (np.pi / 2) < theta < (3 * np.pi / 2) else 1

    def _layout_line(
        self,
        renderer,
        line: _LineGlyphs,
        radius_data: float,
        start_theta: float,
        direction_sign: int,
    ) -> None:
        if not line.chars:
            return

        center_x, center_y = self._center
        assert self.axes is not None
        center_px = self.axes.transData.transform((center_x, center_y))
        edge_px = self.axes.transData.transform((center_x + radius_data, center_y))
        radius_px = float(np.hypot(*(edge_px - center_px)))
        if not np.isfinite(radius_px) or radius_px <= 0:
            return

        prop = self._template.get_fontproperties()

        widths = [0.0]
        for i in range(1, len(line.text) + 1):
            w, _, _ = renderer.get_text_width_height_descent(
                line.text[:i], prop, ismath=False
            )
            widths.append(float(w))
        advances_px = [widths[i + 1] - widths[i] for i in range(len(line.text))]

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
        for idx, (ch, adv_px, artist) in enumerate(
            zip(line.chars, advances_px, line.artists)
        ):
            center_dist_px = cumulative + (adv_px / 2)
            theta_i = start_theta + direction_sign * (center_dist_px / radius_px)
            x_i = center_x + radius_data * float(np.sin(theta_i))
            y_i = center_y + radius_data * float(np.cos(theta_i))

            if artist is not None:
                rotation = -np.rad2deg(theta_i)
                if direction_sign == -1:
                    rotation += 180
                artist.set_position((x_i, y_i))
                artist.set_rotation(rotation)
                artist.draw(renderer)

            cumulative += adv_px
            if idx < (len(advances_px) - 1):
                cumulative += letter_spacing_px

    def draw(self, renderer) -> None:
        if not self.get_visible():
            return
        if self.axes is None or self.figure is None:
            return

        direction_sign = self._direction_sign()

        fontsize_points = float(self._template.get_fontsize())
        linespacing = float(self._text_kwargs.get("linespacing", 1.2))
        line_spacing_points = (
            float(self._line_spacing_points)
            if self._line_spacing_points is not None
            else fontsize_points * linespacing
        )
        line_spacing_px = line_spacing_points * self.figure.dpi / 72.0

        center_x, center_y = self._center
        center_px = self.axes.transData.transform((center_x, center_y))
        one_px = self.axes.transData.transform((center_x + 1.0, center_y))
        px_per_data = float(np.hypot(*(one_px - center_px)))
        line_spacing_data = (line_spacing_px / px_per_data) if px_per_data > 0 else 0.0

        num_lines = len(self._lines)
        center_x, center_y = self._center
        r0 = self._radius
        delta_r = max(1e-6, abs(r0) * 1e-3)
        p0 = (
            center_x + r0 * float(np.sin(self._theta)),
            center_y + r0 * float(np.cos(self._theta)),
        )
        p1 = (
            center_x + (r0 + delta_r) * float(np.sin(self._theta)),
            center_y + (r0 + delta_r) * float(np.cos(self._theta)),
        )
        p0_px = self.axes.transData.transform(p0)
        p1_px = self.axes.transData.transform(p1)
        outward_is_up = bool(p1_px[1] >= p0_px[1])

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
            radius_data = self._radius + offset_factor * line_spacing_data
            self._layout_line(
                renderer,
                line=line,
                radius_data=radius_data,
                start_theta=self._theta,
                direction_sign=direction_sign,
            )
