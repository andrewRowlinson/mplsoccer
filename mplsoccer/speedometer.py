"""A Python module for plotting speedometer charts.

Author: Adapted for mplsoccer by PGupta-Git
Original speedo library by @znstrider (https://github.com/znstrider/speedo)

The speedometer chart is useful for displaying player speed metrics
and other performance indicators in a visually intuitive gauge format.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge

__all__ = ["Speedometer"]


def _degree_range(n, start=0, end=180):
    """Calculate start/end angles and midpoints for n segments.
    
    Parameters
    ----------
    n : int
        Number of segments.
    start : float, default 0
        Start angle in degrees.
    end : float, default 180
        End angle in degrees.
    
    Returns
    -------
    tuple
        (angle_ranges, midpoints) where angle_ranges is Nx2 array of start/end angles
        and midpoints is array of segment midpoint angles.
    """
    start_ = np.linspace(start, end, n + 1, endpoint=True)[:-1]
    end_ = np.linspace(start, end, n + 1, endpoint=True)[1:]
    mid_points = start_ + ((end_ - start_) / 2.0)
    return np.c_[start_, end_], mid_points


def _rotate(angle):
    """Convert angle for label rotation."""
    return np.degrees(np.radians(angle) * np.pi / np.pi - np.radians(90))


class Speedometer:
    """A class for plotting speedometer charts in Matplotlib.

    Parameters
    ----------
    start_value : float
        Start of the range of values (minimum value on the gauge).
    end_value : float
        End of the range of values (maximum value on the gauge).
    center : tuple, default (0, 0)
        (x, y) position of the speedometer center.
    radius : float, default 4
        Radius of the speedometer.
    width_ratio : float, default 0.25
        Ratio of wedge width to radius.
    colors : list, default None
        List of colors for the wedge segments. If None, uses a default
        red-yellow-green-blue gradient: ["#d7191c", "#fdae61", "#ffffbf", "#abd9e9", "#2c7bb6"]
    segments_per_color : int, default 5
        Number of segments per color in the gradient.
    start_angle : float, default -30
        Start angle of the speedometer arc in degrees.
    end_angle : float, default 210
        End angle of the speedometer arc in degrees.
    arc_edgecolor : str, default None
        Edge color for the wedges. If None, uses the axis background color.
    fade_alpha : float, default 0.25
        Alpha value for wedges beyond the current value.
    patch_lw : float, default 0.25
        Line width between wedges.
    snap_to_pos : bool, default False
        Whether to snap the arrow to the center of a wedge.
    unit : str, default ''
        Unit string to display with the value annotation.
    label_fontsize : int, default 7
        Font size for value labels around the arc.
    label_fontcolor : str, default None
        Color for the value labels. If None, uses matplotlib default.
    draw_labels : bool, default True
        Whether to draw value labels around the arc.
    labels : list, default None
        Custom labels for the arc. If None, uses evenly spaced values.
    rotate_labels : bool, default False
        Whether to rotate value labels to follow the arc.
    title : str, default None
        Title to display above the speedometer.
    title_fontsize : int, default 18
        Font size for the title.
    title_fontcolor : str, default None
        Color for the title text. If None, uses matplotlib default.
    title_facecolor : str, default None
        Background color for the title bbox. If None, uses axis background.
    title_edgecolor : str, default None
        Edge color for the title bbox. If None, uses axis background.
    title_offset : float, default 1.5
        Offset of title above the speedometer as a factor of radius.
    title_pad : float, default 1
        Padding around the title bbox.
    draw_annotation : bool, default True
        Whether to draw the value annotation below the speedometer.
    annotation_fontsize : int, default 16
        Font size for the value annotation.
    annotation_fontcolor : str, default None
        Color for the annotation text. If None, uses matplotlib default.
    annotation_facecolor : str, default None
        Background color for the annotation bbox. If None, uses axis background.
    annotation_edgecolor : str, default None
        Edge color for the annotation bbox. If None, uses axis background.
    annotation_offset : float, default 0.75
        Offset of annotation below the speedometer as a factor of radius.
    annotation_pad : float, default 0
        Padding around the annotation bbox.
    fade_hatch : str, default None
        Hatch pattern for faded wedges (e.g., 'xxx').
    """

    def __init__(
        self,
        start_value,
        end_value,
        center=(0, 0),
        radius=4,
        width_ratio=0.25,
        colors=None,
        segments_per_color=5,
        start_angle=-30,
        end_angle=210,
        arc_edgecolor=None,
        fade_alpha=0.25,
        patch_lw=0.25,
        snap_to_pos=False,
        unit='',
        label_fontsize=7,
        label_fontcolor=None,
        draw_labels=True,
        labels=None,
        rotate_labels=False,
        title=None,
        title_fontsize=18,
        title_fontcolor=None,
        title_facecolor=None,
        title_edgecolor=None,
        title_offset=1.5,
        title_pad=1,
        draw_annotation=True,
        annotation_fontsize=16,
        annotation_fontcolor=None,
        annotation_facecolor=None,
        annotation_edgecolor=None,
        annotation_offset=0.75,
        annotation_pad=0,
        fade_hatch=None,
    ):
        # Validation
        if end_value <= start_value:
            raise ValueError("end_value must be greater than start_value")
        if colors is not None and len(colors) == 0:
            raise ValueError("colors list cannot be empty")
        if radius <= 0:
            raise ValueError("radius must be positive")

        self.start_value = start_value
        self.end_value = end_value
        self.center = center
        self.radius = radius
        self.width_ratio = width_ratio
        self.colors = colors if colors is not None else [
            "#d7191c", "#fdae61", "#ffffbf", "#abd9e9", "#2c7bb6"
        ]
        self.segments_per_color = segments_per_color
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.arc_edgecolor = arc_edgecolor
        self.fade_alpha = fade_alpha
        self.patch_lw = patch_lw
        self.snap_to_pos = snap_to_pos
        self.unit = unit
        self.label_fontsize = label_fontsize
        self.label_fontcolor = label_fontcolor
        self.draw_labels = draw_labels
        self.labels = labels
        self.rotate_labels = rotate_labels
        self.title = title
        self.title_fontsize = title_fontsize
        self.title_fontcolor = title_fontcolor
        self.title_facecolor = title_facecolor
        self.title_edgecolor = title_edgecolor
        self.title_offset = title_offset
        self.title_pad = title_pad
        self.draw_annotation = draw_annotation
        self.annotation_fontsize = annotation_fontsize
        self.annotation_fontcolor = annotation_fontcolor
        self.annotation_facecolor = annotation_facecolor
        self.annotation_edgecolor = annotation_edgecolor
        self.annotation_offset = annotation_offset
        self.annotation_pad = annotation_pad
        self.fade_hatch = fade_hatch

        # Computed properties
        self.n_colors = len(self.colors)
        self._expanded_colors = np.repeat(self.colors, self.segments_per_color)
        self._n_segments = self.segments_per_color * self.n_colors

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"start_value={self.start_value}, "
            f"end_value={self.end_value}, "
            f"center={self.center}, "
            f"radius={self.radius}, "
            f"start_angle={self.start_angle}, "
            f"end_angle={self.end_angle})"
        )

    def draw(self, value, ax=None, figsize=(8, 6)):
        """Draw the speedometer chart.

        Parameters
        ----------
        value : float
            The current value to display on the speedometer.
        ax : matplotlib.axes.Axes, default None
            Axes to draw on. If None, creates a new figure and axes.
        figsize : tuple, default (8, 6)
            Figure size in inches (width, height). Only used when ax is None.

        Returns
        -------
        tuple or None
            If ax is None, returns (fig, ax). Otherwise returns None.
        """
        return_fig_ax = ax is None
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        # Resolve colors that depend on axis
        arc_edgecolor = self.arc_edgecolor or ax.get_facecolor()
        label_fontcolor = self.label_fontcolor or plt.rcParams.get(
            'axes.labelcolor', 'black'
        )
        title_fontcolor = self.title_fontcolor or plt.rcParams.get(
            'axes.labelcolor', 'black'
        )
        title_facecolor = self.title_facecolor or ax.get_facecolor()
        title_edgecolor = self.title_edgecolor or ax.get_facecolor()
        annotation_fontcolor = self.annotation_fontcolor or plt.rcParams.get(
            'axes.labelcolor', 'black'
        )
        annotation_facecolor = self.annotation_facecolor or ax.get_facecolor()
        annotation_edgecolor = self.annotation_edgecolor or ax.get_facecolor()

        # Compute value positions
        midpoint_values = np.linspace(
            self.start_value, self.end_value, self._n_segments, endpoint=True
        )
        edge_values = np.linspace(
            self.start_value, self.end_value, self._n_segments + 1, endpoint=True
        )

        arrow_index = np.argmin(np.abs(midpoint_values - value))
        arrow_value = midpoint_values[arrow_index]

        # Compute angles
        angle_range, midpoints = _degree_range(
            self._n_segments, start=self.start_angle, end=self.end_angle
        )
        annotation_angles = np.concatenate([angle_range[:, 0], angle_range[-1:, 1]])

        # Build labels
        if self.labels is None:
            labels = ['' for _ in range(self._n_segments + 1)]
            for i, label_val in zip(
                range(0, self._n_segments + 1, self.segments_per_color),
                np.linspace(self.start_value, self.end_value, self.n_colors + 1, endpoint=True)
            ):
                labels[i] = label_val
        else:
            labels = self.labels

        # Draw wedges
        patches = []
        for ang, color, edge_val in zip(
            angle_range, self._expanded_colors, edge_values[-2::-1]
        ):
            if arrow_value <= edge_val:
                alpha = self.fade_alpha
                hatch = self.fade_hatch
            else:
                alpha = 1
                hatch = None

            # Main wedge with color
            patches.append(
                Wedge(
                    self.center,
                    self.radius,
                    *ang,
                    width=self.width_ratio * self.radius,
                    facecolor=color,
                    edgecolor=arc_edgecolor,
                    lw=self.patch_lw,
                    alpha=alpha,
                    hatch=hatch,
                )
            )
            # Edge-only wedge for clean borders
            patches.append(
                Wedge(
                    self.center,
                    self.radius,
                    *ang,
                    width=self.width_ratio * self.radius,
                    facecolor='None',
                    edgecolor=arc_edgecolor,
                    lw=self.patch_lw,
                )
            )

        for patch in patches:
            ax.add_patch(patch)

        # Draw labels
        if self.draw_labels:
            for angle, label in zip(annotation_angles, labels[-1::-1]):
                if self.rotate_labels:
                    radius_factor = 0.625
                    adj = 90 if angle < 90 else -90
                else:
                    radius_factor = 0.65
                    adj = 180 if (angle < 0) or (angle > 180) else 0

                # Format label - handle floating point precision
                if isinstance(label, (float, np.floating)):
                    # Round to avoid floating point display issues
                    label_rounded = round(label, 10)
                    if label_rounded == int(label_rounded):
                        label = int(label_rounded)
                    else:
                        # Format to reasonable precision (max 2 decimal places)
                        label = round(label_rounded, 2)

                ax.text(
                    self.center[0] + radius_factor * self.radius * np.cos(np.radians(angle)),
                    self.center[1] + radius_factor * self.radius * np.sin(np.radians(angle)),
                    label,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=self.label_fontsize,
                    fontweight='bold',
                    color=label_fontcolor,
                    rotation=_rotate(angle) + adj,
                    bbox={'facecolor': arc_edgecolor, 'ec': 'None', 'pad': 0},
                    zorder=10,
                )

        # Calculate arrow angle
        if self.snap_to_pos:
            arrow_angle = midpoints[-1::-1][arrow_index - len(self._expanded_colors)]
        else:
            deg_range = self.end_angle - self.start_angle
            val_range = self.end_value - self.start_value
            arrow_angle = self.end_angle - (value - self.start_value) / val_range * deg_range

        # Draw arrow
        ax.arrow(
            *self.center,
            0.825 * self.radius * np.cos(np.radians(arrow_angle)),
            0.825 * self.radius * np.sin(np.radians(arrow_angle)),
            width=self.radius / 20,
            head_width=self.radius / 10,
            head_length=self.radius / 15,
            fc=ax.get_facecolor(),
            ec=label_fontcolor,
            zorder=9,
            lw=2,
        )

        # Draw center circle
        ax.add_patch(
            Circle(
                self.center,
                radius=self.radius / 20,
                facecolor=ax.get_facecolor(),
                edgecolor=label_fontcolor,
                lw=2.5,
                zorder=10,
            )
        )

        # Draw annotation
        if self.draw_annotation:
            annotation_text = f'{value}{self.unit}'
            ax.text(
                self.center[0],
                self.center[1] - self.annotation_offset * self.radius,
                annotation_text,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=self.annotation_fontsize,
                fontweight='bold',
                color=annotation_fontcolor,
                bbox={
                    'facecolor': annotation_facecolor,
                    'edgecolor': annotation_edgecolor,
                    'pad': self.annotation_pad,
                },
                zorder=11,
            )

        # Draw title
        if self.title is not None:
            ax.text(
                self.center[0],
                self.center[1] + self.title_offset * self.radius,
                self.title,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=self.title_fontsize,
                fontweight='bold',
                color=title_fontcolor,
                bbox={
                    'facecolor': title_facecolor,
                    'edgecolor': title_edgecolor,
                    'pad': self.title_pad,
                },
                zorder=11,
            )

        # Set axis properties
        ax.set_aspect('equal')
        margin = self.radius * 0.3
        ax.set_xlim(
            self.center[0] - self.radius - margin,
            self.center[0] + self.radius + margin
        )
        ax.set_ylim(
            self.center[1] - self.radius - margin,
            self.center[1] + self.radius + margin
        )
        ax.axis('off')

        if return_fig_ax:
            return fig, ax
        return None

    # __str__ is the same as __repr__
    __str__ = __repr__
